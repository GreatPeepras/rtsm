#!/usr/bin/env python3
"""
deploy_ingest_saturation_2026-07-06.py -- RTSM ingest queue saturation fix.

Run from the rtsm repo root on Execution (.53):
    cd ~/rtsm
    python3 deploy_ingest_saturation_2026-07-06.py --dryrun
    python3 deploy_ingest_saturation_2026-07-06.py --apply
    docker compose -f docker/docker-compose.yml restart rtsm-dev
    docker rm -f rtsm-ingest-sub && <restart subscriber with new flags>

Marker: INGEST_SATURATION_2026-07-06

What it fixes (4 layers, root cause -> symptom):

  L1  subscriber.py  -- motion gate. Don't POST while the camera hasn't
      moved (>5cm / >5deg since last posted frame), except a 2s heartbeat.
      Dwelling on an object was streaming near-identical frames at post-hz
      into a pipeline that drains at ~1-3 Hz. Kills the flood at the
      source; also saves Wi-Fi and decode CPU.

  L2  api/server.py  -- keyframe demotion. The HTTP ingest path hardcoded
      is_keyframe=True on every FramePacket. Keyframes bypass the
      SweepPolicy TTL/parallax gate unconditionally (ingest_gate.py:69),
      so the gate that was built for exactly this dwell scenario never
      fired. Now: every Nth frame (default 10) or after a max interval
      (default 5s) is a KF; the rest are non-KF and get gated cheaply
      after dequeue. NOTE: non-KF observations update WM positions with
      w=0.01-0.1 vs KF w=0.9 (working_memory.py:1492) -- periodic KFs
      still anchor positions.

  L3  io/ingest_queue.py + run.py -- drop-OLDEST, small queue. Old
      behavior kept 512 stale frames and rejected fresh ones; at ~1-3 Hz
      drain the pipeline was processing frames minutes old. New: maxsize
      from cfg ingest.queue_maxsize (default 32), on full evict oldest
      and enqueue newest. Freshness over completeness.

  L4  api/server.py  -- BUG: the 503/queue_full_drops path was dead code.
      IngestQueue.put() swallows queue.Full and returns False; the
      handler's `except _queue.Full` never fired. Full-queue frames were
      dropped SILENTLY while incrementing frames_queued and answering
      "status: queued". Now checks the boolean return.

New rtsm.yaml keys (all optional, defaults shown):
  ingest:
    queue_maxsize: 32
    queue_drop_oldest: true
    http_keyframe_every_n: 10
    http_keyframe_max_interval_s: 5.0

New subscriber flags:
  --min-move-m 0.05   --min-rot-deg 5.0   --still-heartbeat-s 2.0
  (--min-move-m 0 disables the motion gate)

New /stats/ingest fields: queue_evicted_oldest, keyframes_promoted
(and queue_maxsize now reports the real value instead of 0).
"""

import argparse
import ast
import os
import py_compile
import sys
import time

MARKER = "INGEST_SATURATION_2026-07-06"
TS = time.strftime("%Y%m%d-%H%M%S")

# --------------------------------------------------------------------------
# Patch table: (file, name, old, new). Anchors are exact multi-line strings
# taken from repo HEAD 2026-07-06. Abort on any miss or non-unique match.
# CRLF files (ingest_queue.py) are handled by EOL normalization per file.
# --------------------------------------------------------------------------

PATCHES = [
    # ---------------- L3: rtsm/io/ingest_queue.py ----------------
    ("rtsm/io/ingest_queue.py", "queue-init-drop-oldest",
     '''    def __init__(self, maxsize: int = 256) -> None:
        self._q: "queue.Queue[FramePacket]" = queue.Queue(maxsize=maxsize)
''',
     '''    # INGEST_SATURATION_2026-07-06: drop-oldest mode + eviction accounting.
    def __init__(self, maxsize: int = 256, drop_oldest: bool = False) -> None:
        self._q: "queue.Queue[FramePacket]" = queue.Queue(maxsize=maxsize)
        self.maxsize = int(maxsize)
        self.drop_oldest = bool(drop_oldest)
        self.evicted_oldest = 0
'''),

    ("rtsm/io/ingest_queue.py", "queue-put-drop-oldest",
     '''    def put(self, pkt: FramePacket, block: bool = False, timeout: Optional[float] = None) -> bool:
        try:
            self._q.put(pkt, block=block, timeout=0.0 if timeout is None else timeout)
            return True
        except queue.Full:
            return False
''',
     '''    def put(self, pkt: FramePacket, block: bool = False, timeout: Optional[float] = None) -> bool:
        try:
            self._q.put(pkt, block=block, timeout=0.0 if timeout is None else timeout)
            return True
        except queue.Full:
            # INGEST_SATURATION_2026-07-06: freshness over completeness.
            # Evict the oldest queued frame and enqueue the new one so the
            # pipeline always works on the most recent view of the world.
            if not self.drop_oldest:
                return False
            try:
                self._q.get_nowait()
                self.evicted_oldest += 1
            except queue.Empty:
                pass
            try:
                self._q.put_nowait(pkt)
                return True
            except queue.Full:
                return False
'''),

    # ---------------- L3: rtsm/run.py ----------------
    ("rtsm/run.py", "run-queue-cfg",
     '''    # Prepare ingest plumbing
    # Note: Intrinsics are now dynamic per-frame from camera.rgbd topic
    ingest_q = IngestQueue(maxsize=512)
''',
     '''    # Prepare ingest plumbing
    # Note: Intrinsics are now dynamic per-frame from camera.rgbd topic
    # INGEST_SATURATION_2026-07-06: small drop-oldest queue. A 512-deep FIFO
    # at ~1-3 Hz drain meant frames were minutes stale by processing time.
    _ing_cfg = cfg.get("ingest", {})
    ingest_q = IngestQueue(
        maxsize=int(_ing_cfg.get("queue_maxsize", 32)),
        drop_oldest=bool(_ing_cfg.get("queue_drop_oldest", True)),
    )
'''),

    ("rtsm/run.py", "run-create-app-ingest-cfg",
     '''        vectors=vectors,
        ingest_queue=ingest_q,
        extra_stats_provider=lambda: {
''',
     '''        vectors=vectors,
        ingest_queue=ingest_q,
        ingest_cfg=_ing_cfg,  # INGEST_SATURATION_2026-07-06
        extra_stats_provider=lambda: {
'''),

    # ---------------- L2 + L4: rtsm/api/server.py ----------------
    ("rtsm/api/server.py", "server-signature-ingest-cfg",
     '''    static_dir: Optional[str] = None,
    ingest_queue: Optional[Any] = None,
) -> FastAPI:
''',
     '''    static_dir: Optional[str] = None,
    ingest_queue: Optional[Any] = None,
    ingest_cfg: Optional[Dict[str, Any]] = None,  # INGEST_SATURATION_2026-07-06
) -> FastAPI:
'''),

    ("rtsm/api/server.py", "server-kf-state",
     '''    _ingest_queue = ingest_queue  # closure ref; None in --serve mode
''',
     '''    _ingest_queue = ingest_queue  # closure ref; None in --serve mode
    # INGEST_SATURATION_2026-07-06: HTTP keyframe demotion config + state.
    _ing_cfg = dict(ingest_cfg or {})
    _kf_every_n = max(1, int(_ing_cfg.get("http_keyframe_every_n", 10)))
    _kf_max_interval_s = float(_ing_cfg.get("http_keyframe_max_interval_s", 5.0))
    _kf_state = {"since_kf": 0, "last_kf_mono": 0.0}
'''),

    ("rtsm/api/server.py", "server-kf-demotion",
     '''        pkt = FramePacket(
            time=tb, rgb=rgb, depth_m=depth_m,
            pose=pose, intr=intr,
            is_keyframe=True,
        )
''',
     '''        # INGEST_SATURATION_2026-07-06: keyframe demotion. Hardcoding
        # is_keyframe=True bypassed the SweepPolicy TTL/parallax gate for
        # every HTTP frame (keyframes are accepted unconditionally in
        # ingest_gate.should_accept), so dwell floods ran the full heavy
        # pipeline per frame. Promote every Nth frame, or after a max
        # interval, to KF; the rest are non-KF and get gated post-dequeue.
        _now_mono = time.monotonic()
        _kf_state["since_kf"] += 1
        _is_kf = (
            _kf_state["since_kf"] >= _kf_every_n
            or (_now_mono - _kf_state["last_kf_mono"]) >= _kf_max_interval_s
        )
        if _is_kf:
            _kf_state["since_kf"] = 0
            _kf_state["last_kf_mono"] = _now_mono
            _ingest_counters["keyframes_promoted"] = (
                _ingest_counters.get("keyframes_promoted", 0) + 1
            )
        pkt = FramePacket(
            time=tb, rgb=rgb, depth_m=depth_m,
            pose=pose, intr=intr,
            is_keyframe=_is_kf,
        )
'''),

    ("rtsm/api/server.py", "server-put-bool-fix",
     '''        # Queue put (non-blocking). Full -> 503.
        t_q0 = time.perf_counter()
        try:
            _ingest_queue.put(pkt, block=False)
        except _queue.Full:
            _ingest_counters["queue_full_drops"] += 1
''',
     '''        # Queue put (non-blocking). Full -> 503.
        # INGEST_SATURATION_2026-07-06: BUG FIX. IngestQueue.put() swallows
        # queue.Full and returns False -- the old `except _queue.Full` was
        # dead code. Full-queue frames were dropped silently while counted
        # as frames_queued and answered "status: queued". Check the bool.
        # (With drop_oldest=True on the queue, put() now rarely fails.)
        t_q0 = time.perf_counter()
        _put_ok = _ingest_queue.put(pkt, block=False)
        if not _put_ok:
            _ingest_counters["queue_full_drops"] += 1
'''),

    ("rtsm/api/server.py", "server-stats-evictions",
     '''            out["queue_depth"] = int(_ingest_queue.qsize())
            out["queue_maxsize"] = int(getattr(_ingest_queue, "maxsize", 0))
            out["mode"] = "queued"
''',
     '''            out["queue_depth"] = int(_ingest_queue.qsize())
            out["queue_maxsize"] = int(getattr(_ingest_queue, "maxsize", 0))
            # INGEST_SATURATION_2026-07-06: drop-oldest eviction accounting.
            out["queue_evicted_oldest"] = int(
                getattr(_ingest_queue, "evicted_oldest", 0)
            )
            out["keyframes_promoted"] = int(
                _ingest_counters.get("keyframes_promoted", 0)
            )
            out["mode"] = "queued"
'''),

    # ---------------- L1: ingest/src/subscriber.py ----------------
    ("ingest/src/subscriber.py", "sub-init-signature",
     '''        post_hz: float = 2.0,  # PATCH 20260518: default tuned for bursty workload, see backpressure-2026-05-18
        watchdog_no_frame_s: float = 180.0,  # PATCH 20260603: subscription-staleness watchdog
    ):
''',
     '''        post_hz: float = 2.0,  # PATCH 20260518: default tuned for bursty workload, see backpressure-2026-05-18
        watchdog_no_frame_s: float = 180.0,  # PATCH 20260603: subscription-staleness watchdog
        min_move_m: float = 0.05,        # INGEST_SATURATION_2026-07-06
        min_rot_deg: float = 5.0,        # INGEST_SATURATION_2026-07-06
        still_heartbeat_s: float = 2.0,  # INGEST_SATURATION_2026-07-06
    ):
'''),

    ("ingest/src/subscriber.py", "sub-init-state",
     '''        self._last_post_ns = 0
        self._post_skipped = 0
        self._last_pose_stale_ms = 0.0
''',
     '''        self._last_post_ns = 0
        self._post_skipped = 0
        self._last_pose_stale_ms = 0.0
        # INGEST_SATURATION_2026-07-06: motion gate. Don't POST while the
        # camera hasn't moved -- dwelling streams near-identical frames that
        # saturate rtsm-dev's ingest queue. A heartbeat still posts one
        # frame every still_heartbeat_s so persistence monitoring continues.
        self._min_move_m = float(min_move_m)
        self._min_rot_cos_half = float(
            np.cos(np.radians(max(0.0, min_rot_deg)) / 2.0)
        )
        self._still_heartbeat_ns = (
            int(still_heartbeat_s * 1e9) if still_heartbeat_s > 0 else 0
        )
        self._last_posted_pose = None
        self._post_skipped_still = 0
'''),

    ("ingest/src/subscriber.py", "sub-gate-helper",
     '''    def _emit(self, frame: Frame):
        """Downstream seam. Writes to recorder and/or POSTs to rtsm-dev."""
''',
     '''    def _motion_gate_says_skip(self, frame: "Frame", now_ns: int) -> bool:
        """INGEST_SATURATION_2026-07-06: True = suppress this POST.

        Skip iff the camera moved < min_move_m AND rotated < min_rot_deg
        since the last successfully posted frame, unless the still-heartbeat
        interval has elapsed. |dot(q1,q2)| = cos(theta/2) for unit quats.
        Disabled when min_move_m <= 0, when no pose is attached, or before
        the first successful post.
        """
        if self._min_move_m <= 0.0 or frame.pose is None:
            return False
        if self._last_posted_pose is None:
            return False
        if (self._still_heartbeat_ns > 0
                and now_ns - self._last_post_ns >= self._still_heartbeat_ns):
            return False
        p, q = frame.pose, self._last_posted_pose
        dx = p["tx"] - q["tx"]
        dy = p["ty"] - q["ty"]
        dz = p["tz"] - q["tz"]
        if (dx * dx + dy * dy + dz * dz) >= self._min_move_m ** 2:
            return False
        dot = abs(p["qx"] * q["qx"] + p["qy"] * q["qy"]
                  + p["qz"] * q["qz"] + p["qw"] * q["qw"])
        if dot < self._min_rot_cos_half:
            return False
        return True

    def _emit(self, frame: Frame):
        """Downstream seam. Writes to recorder and/or POSTs to rtsm-dev."""
'''),

    ("ingest/src/subscriber.py", "sub-emit-gate",
     '''            if (self._post_interval_ns == 0
                    or now_ns - self._last_post_ns >= self._post_interval_ns):
                ok, err = self._http_emitter.post(frame, list(self._camera_info.k))
                if ok:
                    self._post_ok += 1
''',
     '''            if (self._post_interval_ns == 0
                    or now_ns - self._last_post_ns >= self._post_interval_ns):
                # INGEST_SATURATION_2026-07-06: motion gate, after the hz
                # decimator. On skip, _last_post_ns is NOT advanced so the
                # still-heartbeat measures time since the last real POST.
                if self._motion_gate_says_skip(frame, now_ns):
                    self._post_skipped_still += 1
                    return
                ok, err = self._http_emitter.post(frame, list(self._camera_info.k))
                if ok:
                    self._post_ok += 1
                    self._last_posted_pose = frame.pose  # INGEST_SATURATION_2026-07-06
'''),

    ("ingest/src/subscriber.py", "sub-stats-line",
     '''                f" post_ok={self._post_ok} post_fail={self._post_fail}"
                f" post_skip={self._post_skipped}"
''',
     '''                f" post_ok={self._post_ok} post_fail={self._post_fail}"
                f" post_skip={self._post_skipped}"
                f" post_skip_still={self._post_skipped_still}"
'''),

    ("ingest/src/subscriber.py", "sub-argparse",
     '''    parser.add_argument(
        "--watchdog-no-frame-s", type=float, default=180.0,
        help="Exit (so container can restart) if no synced frame arrives "
             "for this many seconds. 0 disables. Default: 180.",
    )
    args = parser.parse_args()
''',
     '''    parser.add_argument(
        "--watchdog-no-frame-s", type=float, default=180.0,
        help="Exit (so container can restart) if no synced frame arrives "
             "for this many seconds. 0 disables. Default: 180.",
    )
    # INGEST_SATURATION_2026-07-06: motion gate flags.
    parser.add_argument(
        "--min-move-m", type=float, default=0.05,
        help="Skip POSTs when the camera moved less than this (meters) "
             "since the last posted frame. 0 disables the motion gate. "
             "Default: 0.05.",
    )
    parser.add_argument(
        "--min-rot-deg", type=float, default=5.0,
        help="Rotation threshold (degrees) paired with --min-move-m. "
             "Default: 5.0.",
    )
    parser.add_argument(
        "--still-heartbeat-s", type=float, default=2.0,
        help="While stationary, still POST one frame every this many "
             "seconds (persistence monitoring). 0 = never post while "
             "still. Default: 2.0.",
    )
    args = parser.parse_args()
'''),

    ("ingest/src/subscriber.py", "sub-node-kwargs",
     '''        post_hz=args.post_hz,
        watchdog_no_frame_s=args.watchdog_no_frame_s,  # PATCH 20260603
    )
''',
     '''        post_hz=args.post_hz,
        watchdog_no_frame_s=args.watchdog_no_frame_s,  # PATCH 20260603
        min_move_m=args.min_move_m,                    # INGEST_SATURATION_2026-07-06
        min_rot_deg=args.min_rot_deg,                  # INGEST_SATURATION_2026-07-06
        still_heartbeat_s=args.still_heartbeat_s,      # INGEST_SATURATION_2026-07-06
    )
'''),
]

FILES = sorted({p[0] for p in PATCHES})


def read(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def eol_of(text):
    return "\r\n" if "\r\n" in text else "\n"


def adapt(s, eol):
    return s.replace("\n", eol) if eol == "\r\n" else s


def validate_py(path):
    import tempfile
    fd, cfile = tempfile.mkstemp(suffix=".pyc")
    os.close(fd)
    try:
        py_compile.compile(path, cfile=cfile, doraise=True)
    finally:
        try:
            os.remove(cfile)
        except OSError:
            pass
    with open(path, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=path)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dryrun", action="store_true")
    g.add_argument("--apply", action="store_true")
    g.add_argument("--revert", action="store_true")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if not os.path.isfile("rtsm/run.py"):
        sys.exit("ERROR: run from repo root (cd ~/rtsm)")

    if args.check:
        bad = 0
        for f in FILES:
            n = read(f).count(MARKER)
            print(f"[check] {f}: marker x{n}")
            if n == 0:
                bad += 1
        sys.exit(1 if bad else 0)

    if args.revert:
        rc = 0
        for f in FILES:
            baks = sorted(
                x for x in os.listdir(os.path.dirname(f) or ".")
                if x.startswith(os.path.basename(f) + ".bak.")
            )
            if not baks:
                print(f"[revert] {f}: NO BACKUP FOUND")
                rc = 1
                continue
            src = os.path.join(os.path.dirname(f) or ".", baks[-1])
            with open(src, "rb") as s, open(f + ".tmp", "wb") as d:
                d.write(s.read())
            os.replace(f + ".tmp", f)
            validate_py(f)
            print(f"[revert] {f}: restored from {baks[-1]}")
        sys.exit(rc)

    # --dryrun / --apply
    contents = {}
    failures = 0
    for f in FILES:
        contents[f] = read(f)
        if MARKER in contents[f]:
            print(f"[skip] {f}: marker already present (idempotent no-op)")

    plan = []
    for f, name, old, new in PATCHES:
        c = contents[f]
        if MARKER in c:
            continue
        eol = eol_of(c)
        o, n = adapt(old, eol), adapt(new, eol)
        cnt = c.count(o)
        if cnt == 1:
            print(f"[ok]   {f} :: {name}")
            plan.append((f, o, n))
        else:
            print(f"[FAIL] {f} :: {name} -- anchor count={cnt} (need 1). "
                  f"Live file has drifted from expected text; ABORTING.")
            failures += 1

    if failures:
        sys.exit(f"\n{failures} anchor failure(s). Nothing written.")

    if args.dryrun:
        print("\nDRYRUN OK: all anchors unique. Re-run with --apply.")
        return

    # apply
    for f in FILES:
        if MARKER in contents[f]:
            continue
        bak = f + ".bak." + TS
        with open(bak, "wb") as d:
            d.write(contents[f].encode("utf-8"))
        c = contents[f]
        for pf, o, n in plan:
            if pf == f:
                c = c.replace(o, n, 1)
        with open(f + ".tmp", "w", encoding="utf-8", newline="") as d:
            d.write(c)
        try:
            validate_py(f + ".tmp")
        except Exception as e:
            os.remove(f + ".tmp")
            sys.exit(f"[ABORT] {f}: post-patch validation failed: {e}. "
                     f"Original untouched; backup at {bak}")
        os.replace(f + ".tmp", f)
        print(f"[write] {f} (backup: {bak})")

    for f in FILES:
        n = read(f).count(MARKER)
        print(f"[verify] {f}: marker x{n}")
    print("\nAPPLYED " + MARKER)
    print("Next: docker compose -f docker/docker-compose.yml restart rtsm-dev")
    print("      restart rtsm-ingest-sub (new flags are defaulted; explicit:")
    print("      --min-move-m 0.05 --min-rot-deg 5 --still-heartbeat-s 2)")


if __name__ == "__main__":
    main()
