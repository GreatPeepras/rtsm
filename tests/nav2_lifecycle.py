"""
Subprocess-based lifecycle for nav2_bringup navigation_launch.py.

Used by action_service.py's goto_object() to bring up the on-demand
nav2 stack (planner, controller, bt_navigator, costmaps, behaviors,
lifecycle_manager_navigation) only for the duration of a navigation
goal. AMCL + map_server remain always-on via amcl_only.launch.py and
are NOT respawned here.

Per on_demand_nav_and_landmark_gate_design.md (2026-06-02).

Design:
  * Spawn:    subprocess.Popen of `ros2 launch nav2_bringup navigation_launch.py`
              in a new session (own process group) so signals reach all children.
  * Teardown: SIGINT -> wait -> SIGTERM -> wait -> SIGKILL escalation, applied
              to the whole process group via os.killpg(pgid, sig).
              SIGINT is the preferred clean shutdown for ros2 launch.
  * Thread-safe: an internal lock guards start/stop, so concurrent callers
                 cannot leave the proc handle in a partial state.
  * Idempotent stop: safe to call when not running, or repeatedly.

This module does NOT poll the NavigateToPose action server -- the caller
(action_service.py) owns that policy, because the cold-start timeout
depends on caller context (e.g. interactive goto vs. background test).
"""
import os
import signal
import subprocess
import threading
from typing import List, Optional


class Nav2Subprocess:
    """Owns the lifetime of a single nav2 navigation_launch.py subprocess.

    Not designed for multiple concurrent nav2 instances -- one launch per
    process. If start() is called while a previous launch is still alive,
    it logs and returns True without re-spawning (idempotent).
    """

    # Signal escalation timing (seconds). Tunable via constructor.
    DEFAULT_SIGINT_GRACE = 5.0   # ros2 launch usually exits within ~3s on SIGINT
    DEFAULT_SIGTERM_GRACE = 3.0  # secondary escalation
    DEFAULT_SIGKILL_REAP = 2.0   # how long to wait for SIGKILL to take effect

    def __init__(
        self,
        logger,
        params_file: Optional[str] = None,
        autostart: bool = True,
        sigint_grace_sec: float = DEFAULT_SIGINT_GRACE,
        sigterm_grace_sec: float = DEFAULT_SIGTERM_GRACE,
        sigkill_reap_sec: float = DEFAULT_SIGKILL_REAP,
    ):
        """
        Args:
            logger: rclpy logger (e.g. node.get_logger()). Must support
                    .info / .warn / .error.
            params_file: optional nav2 params YAML; passed verbatim to
                         navigation_launch.py as params_file:=<path>.
                         None = use nav2_bringup defaults.
            autostart: whether the launch file should activate lifecycle
                       nodes immediately (default True; recommended for V1).
            sigint_grace_sec / sigterm_grace_sec / sigkill_reap_sec:
                signal escalation timeouts; override mainly for tests.
        """
        self.logger = logger
        self.params_file = params_file
        self.autostart = autostart
        self.sigint_grace_sec = float(sigint_grace_sec)
        self.sigterm_grace_sec = float(sigterm_grace_sec)
        self.sigkill_reap_sec = float(sigkill_reap_sec)

        self._lock = threading.Lock()
        self._proc: Optional[subprocess.Popen] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_running(self) -> bool:
        """Return True if a subprocess is alive (poll() is None)."""
        with self._lock:
            return self._proc is not None and self._proc.poll() is None

    def start(self) -> bool:
        """Spawn nav2 navigation_launch.py.

        Returns True on Popen success (process spawned) OR if already running.
        Returns False if the spawn itself failed (e.g. ros2 not on PATH).

        Does NOT block on the NavigateToPose action server -- the caller
        polls with the timeout policy of its choice.
        """
        with self._lock:
            if self._proc is not None and self._proc.poll() is None:
                self._log_info(
                    f"nav2_lifecycle: already running (pid={self._proc.pid}); "
                    f"start() is a no-op"
                )
                return True

            cmd = self._build_cmd()

            try:
                # start_new_session=True puts the process in its own session
                # and process group, so signals sent via killpg(pgid, sig) hit
                # all children (planner, controller, bt_navigator, costmaps,
                # behavior_server, smoother_server, lifecycle_manager, etc.).
                self._proc = subprocess.Popen(
                    cmd,
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self._log_info(
                    f"nav2_lifecycle: started (pid={self._proc.pid}) cmd={' '.join(cmd)}"
                )
                return True
            except FileNotFoundError as e:
                self._log_error(f"nav2_lifecycle: ros2 launch not found: {e}")
                self._proc = None
                return False
            except Exception as e:
                self._log_error(f"nav2_lifecycle: start failed: {e}")
                self._proc = None
                return False

    def stop(self) -> None:
        """Stop nav2 cleanly. Escalates SIGINT -> SIGTERM -> SIGKILL.

        Idempotent: safe to call when not running, or repeatedly.
        Sends each signal to the full process group via killpg.
        Returns after the process is reaped (or after SIGKILL window passes).
        """
        # Snapshot the proc + pgid under the lock, then release so callers
        # can poll is_running() during the wait (which can take seconds).
        with self._lock:
            proc = self._proc
            if proc is None:
                return
            if proc.poll() is not None:
                self._log_info(
                    f"nav2_lifecycle: already exited (rc={proc.returncode})"
                )
                self._proc = None
                return
            try:
                pgid = os.getpgid(proc.pid)
            except ProcessLookupError:
                self._proc = None
                return

        # Stage 1: SIGINT (preferred clean shutdown for ros2 launch)
        if self._signal_and_wait(proc, pgid, signal.SIGINT,
                                 self.sigint_grace_sec, "SIGINT"):
            self._clear_proc()
            return

        # Stage 2: SIGTERM
        self._log_warn(
            f"nav2_lifecycle: SIGINT timed out after "
            f"{self.sigint_grace_sec}s; escalating to SIGTERM"
        )
        if self._signal_and_wait(proc, pgid, signal.SIGTERM,
                                 self.sigterm_grace_sec, "SIGTERM"):
            self._clear_proc()
            return

        # Stage 3: SIGKILL (last resort)
        self._log_error(
            f"nav2_lifecycle: SIGTERM timed out after "
            f"{self.sigterm_grace_sec}s; escalating to SIGKILL"
        )
        self._signal_and_wait(proc, pgid, signal.SIGKILL,
                              self.sigkill_reap_sec, "SIGKILL")
        # Regardless of whether SIGKILL was acknowledged, clear our handle.
        # If the process truly didn't die, it's now orphaned and there's
        # nothing more this helper can do.
        self._clear_proc()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _build_cmd(self) -> List[str]:
        cmd = [
            "ros2", "launch", "nav2_bringup", "navigation_launch.py",
            f"autostart:={'true' if self.autostart else 'false'}",
            "use_sim_time:=false",
        ]
        if self.params_file:
            cmd.append(f"params_file:={self.params_file}")
        return cmd

    def _signal_and_wait(
        self,
        proc: subprocess.Popen,
        pgid: int,
        sig: int,
        timeout_sec: float,
        label: str,
    ) -> bool:
        """Send a signal to the process group, wait up to timeout_sec for exit.

        Returns True if the process exited within the timeout, False otherwise.
        Treats ProcessLookupError as "already gone" -> True.
        """
        try:
            os.killpg(pgid, sig)
            self._log_info(
                f"nav2_lifecycle: sent {label} to pgid={pgid}, "
                f"waiting up to {timeout_sec:.1f}s"
            )
        except ProcessLookupError:
            return True  # already gone

        try:
            proc.wait(timeout=timeout_sec)
            self._log_info(
                f"nav2_lifecycle: exited on {label} (rc={proc.returncode})"
            )
            return True
        except subprocess.TimeoutExpired:
            return False

    def _clear_proc(self) -> None:
        with self._lock:
            self._proc = None

    # Logger compatibility shims: rclpy logger uses .warn (not .warning),
    # but stdlib logging has .warning. Tests pass a mock; either works.
    def _log_info(self, msg: str) -> None:
        try:
            self.logger.info(msg)
        except Exception:
            pass

    def _log_warn(self, msg: str) -> None:
        for attr in ("warn", "warning"):
            fn = getattr(self.logger, attr, None)
            if fn is not None:
                try:
                    fn(msg)
                except Exception:
                    pass
                return

    def _log_error(self, msg: str) -> None:
        try:
            self.logger.error(msg)
        except Exception:
            pass
