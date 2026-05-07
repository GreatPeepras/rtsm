"""
rtsm.tools.replay — replay a recorded ingest session against a running server.

Reads sessions produced by the rtsm-ingest recorder (commit b2d752d),
which store per-frame triplets:

    <session>/NNNNNN.jpg     # on-wire JPEG bytes from /camera/color/image_raw/compressed
    <session>/NNNNNN.png     # on-wire PNG bytes from /camera/depth/.../compressedDepth
    <session>/NNNNNN.json    # {seq, t_capture_ns, t_received_ns, color_frame_id}
    <session>/meta.json      # {run_id, width, height, intrinsics:{fx,fy,cx,cy}, ...}

Maps each frame to the /ingest/keyframe wire contract and POSTs it at a
configurable rate. Tracks per-request latency and prints a summary.

POSE LIMITATION (Gate 2.e):
    The recorder did not capture /tf, so poses are synthesized as identity
    (tx=ty=tz=0, qw=1). This is fine for exercising the ingress transport
    layer but means projected object coordinates will pile up at the origin.
    Pass --synthetic-pose to acknowledge this.

Requires: requests (host-side dev dep; not bundled in the Docker image).
"""
from __future__ import annotations

import argparse
import base64
import json
import signal
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import requests


DEFAULT_RECORDINGS_ROOT = Path("/mnt/rtsm-data/rtsm-recordings")
IDENTITY_POSE = {"tx": 0.0, "ty": 0.0, "tz": 0.0,
                 "qx": 0.0, "qy": 0.0, "qz": 0.0, "qw": 1.0}


@dataclass
class ReplayStats:
    sent: int = 0
    errors: int = 0
    bytes_sent: int = 0
    latencies_ms: List[float] = field(default_factory=list)
    server_decode_ms: List[float] = field(default_factory=list)  # Gate 2.f.1: timings.total_ms from response body
    first_seq: Optional[int] = None
    last_seq: Optional[int] = None
    wall_start: float = 0.0
    wall_end: float = 0.0

    def summary_lines(self, endpoint: str, total_available: int) -> List[str]:
        elapsed = max(self.wall_end - self.wall_start, 1e-9)
        # Steady-state Hz: frames-per-second if you kept going. For N frames at
        # target period T, elapsed ~ (N-1)*T, so sent/elapsed overshoots at
        # small N. Use mean-interval instead when N>=2.
        if self.sent >= 2:
            hz = (self.sent - 1) / elapsed
        else:
            hz = self.sent / elapsed if self.sent else 0.0
        mb = self.bytes_sent / (1024 * 1024)
        lines = [
            f"Sent:     {self.sent} frames "
            f"(seq {self.first_seq}..{self.last_seq}) / {total_available} available",
            f"Errors:   {self.errors}",
            f"Elapsed:  {elapsed:.2f}s  →  {hz:.2f} Hz (mean interval)",
            f"Bytes:    {mb:.2f} MB total"
            + (f" (avg {self.bytes_sent // self.sent // 1024} KB/frame)" if self.sent else ""),
        ]
        client_p50: Optional[float] = None
        if self.latencies_ms:
            xs = sorted(self.latencies_ms)
            def pct(p: float) -> float:
                i = min(len(xs) - 1, int(round(p * (len(xs) - 1))))
                return xs[i]
            client_p50 = pct(0.50)
            lines.append(
                f"Latency:  p50={pct(0.50):.1f}ms  p95={pct(0.95):.1f}ms  "
                f"p99={pct(0.99):.1f}ms  max={max(xs):.1f}ms  "
                f"(mean={statistics.fmean(xs):.1f}ms, client-observed)"
            )
        # Gate 2.f.1: server-side decode distribution, when the endpoint
        # returns structured timings (decode-only mode). The gap between
        # client latency and server decode is HTTP framing overhead
        # (Pydantic validate + JSON parse + loopback).
        server_p50: Optional[float] = None
        if self.server_decode_ms:
            ys = sorted(self.server_decode_ms)
            def spct(p: float) -> float:
                i = min(len(ys) - 1, int(round(p * (len(ys) - 1))))
                return ys[i]
            server_p50 = spct(0.50)
            lines.append(
                f"Decode:   p50={spct(0.50):.1f}ms  p95={spct(0.95):.1f}ms  "
                f"p99={spct(0.99):.1f}ms  max={max(ys):.1f}ms  "
                f"(mean={statistics.fmean(ys):.1f}ms, server-side, n={len(ys)})"
            )
        if client_p50 is not None and server_p50 is not None:
            lines.append(
                f"Framing:  ~{client_p50 - server_p50:.1f}ms  "
                f"(client p50 - server p50; HTTP + Pydantic + loopback overhead)"
            )
        lines.append(f"Endpoint: {endpoint}")
        return lines


def resolve_session(session_arg: str) -> Path:
    """Accept either a full path or a bare run-id under the default root."""
    p = Path(session_arg)
    if p.is_absolute() and p.exists():
        return p
    candidate = DEFAULT_RECORDINGS_ROOT / session_arg
    if candidate.exists():
        return candidate
    if p.exists():
        return p.resolve()
    raise FileNotFoundError(
        f"Session not found. Tried: {p} and {candidate}"
    )


def load_meta(session: Path) -> dict:
    meta_path = session / "meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing {meta_path} — is this a recorder session?")
    with meta_path.open() as f:
        return json.load(f)


def k_from_intrinsics(meta: dict) -> List[float]:
    intr = meta["intrinsics"]
    fx, fy, cx, cy = intr["fx"], intr["fy"], intr["cx"], intr["cy"]
    # Row-major 3x3 camera matrix
    return [fx, 0.0, cx,
            0.0, fy, cy,
            0.0, 0.0, 1.0]


def list_frames(session: Path) -> List[int]:
    """Return sorted list of frame indices (from *.jpg filenames)."""
    jpgs = sorted(session.glob("*.jpg"))
    return [int(p.stem) for p in jpgs]


def preflight(endpoint: str, timeout: float) -> None:
    """Confirm the server is reachable and the ingest route is registered."""
    # /stats is guaranteed to exist; derive base URL from the ingest endpoint.
    base = endpoint.rsplit("/ingest/keyframe", 1)[0]
    try:
        r = requests.get(f"{base}/stats", timeout=timeout)
        r.raise_for_status()
    except Exception as e:
        raise SystemExit(f"[replay] preflight failed: GET {base}/stats → {e}")
    # Sanity-ping the ingest route with an intentionally-invalid payload.
    # We expect 422 (schema rejection), which proves the route is registered.
    try:
        r = requests.post(endpoint, json={}, timeout=timeout)
    except Exception as e:
        raise SystemExit(f"[replay] preflight failed: POST {endpoint} → {e}")
    if r.status_code != 422:
        raise SystemExit(
            f"[replay] preflight: expected 422 on empty POST, got {r.status_code}. "
            f"Is /ingest/keyframe really registered?"
        )


def build_payload(session: Path, idx: int, K: List[float]) -> dict:
    jpg = (session / f"{idx:06d}.jpg").read_bytes()
    png = (session / f"{idx:06d}.png").read_bytes()
    with (session / f"{idx:06d}.json").open() as f:
        sidecar = json.load(f)
    return {
        "rgb_jpeg": base64.b64encode(jpg).decode("ascii"),
        "depth_png": base64.b64encode(png).decode("ascii"),
        "K": K,
        "pose": IDENTITY_POSE,
        "timestamp_ros": sidecar["t_capture_ns"] / 1e9,
        "frame_id": sidecar.get("color_frame_id", "camera_color_optical_frame"),
        "sequence": sidecar["seq"],
    }


def parse_rate(rate_str: str) -> Optional[float]:
    """Return Hz as float, None for 'max', or raise for bad input.
       'realtime' is handled separately (returns sentinel -1.0)."""
    if rate_str == "max":
        return None
    if rate_str == "realtime":
        return -1.0
    try:
        hz = float(rate_str)
        if hz <= 0:
            raise ValueError
        return hz
    except ValueError:
        raise SystemExit(f"[replay] invalid --rate {rate_str!r}; "
                         f"expected a positive number, 'max', or 'realtime'")


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="rtsm.tools.replay",
        description="Replay a recorded ingest session against /ingest/keyframe.",
    )
    ap.add_argument("--session", required=True,
                    help="Run-id (e.g. 2026-05-06T14-00-15Z) or full path.")
    ap.add_argument("--endpoint", default="http://localhost:8002/ingest/keyframe",
                    help="Ingest endpoint URL.")
    ap.add_argument("--rate", default="2",
                    help="Hz as number, or 'realtime' (use t_capture spacing), "
                         "or 'max' (no sleep). Default: 2")
    ap.add_argument("--limit", type=int, default=None,
                    help="Max frames to send (default: all).")
    ap.add_argument("--start", type=int, default=0,
                    help="Skip the first N frames (default: 0).")
    ap.add_argument("--timeout", type=float, default=5.0,
                    help="Per-request timeout in seconds (default: 5.0).")
    ap.add_argument("--synthetic-pose", action="store_true",
                    help="REQUIRED. Acknowledge that poses are identity (recorder "
                         "did not capture /tf). Without this flag replay refuses.")
    ap.add_argument("--progress", type=int, default=10,
                    help="Print rolling progress every N frames (0 to disable).")
    ap.add_argument("--verbose", action="store_true",
                    help="Print per-frame latency.")
    args = ap.parse_args()

    if not args.synthetic_pose:
        print(
            "[replay] refusing to run without --synthetic-pose.\n"
            "  The recorder (commit b2d752d) does not capture /tf, so every\n"
            "  frame will be sent with pose = identity (tx=ty=tz=0, qw=1).\n"
            "  Pass --synthetic-pose to acknowledge this. Real-pose replay\n"
            "  requires extending the recorder (scoped as a follow-up gate).",
            file=sys.stderr,
        )
        return 2

    session = resolve_session(args.session)
    meta = load_meta(session)
    K = k_from_intrinsics(meta)
    all_frames = list_frames(session)
    if not all_frames:
        print(f"[replay] no frames found in {session}", file=sys.stderr)
        return 1

    # Apply --start / --limit
    frames = all_frames[args.start:]
    if args.limit is not None:
        frames = frames[:args.limit]
    if not frames:
        print("[replay] no frames to send after --start/--limit filtering",
              file=sys.stderr)
        return 1

    rate_hz = parse_rate(args.rate)  # float, None=max, -1.0=realtime
    period_s = (1.0 / rate_hz) if (rate_hz and rate_hz > 0) else 0.0

    print(f"[replay] session  = {session}")
    print(f"[replay] frames   = {len(frames)} of {len(all_frames)} "
          f"(start={args.start}, limit={args.limit})")
    print(f"[replay] rate     = {args.rate} "
          f"({'max' if rate_hz is None else 'realtime' if rate_hz == -1.0 else f'{rate_hz:.2f} Hz'})")
    print(f"[replay] endpoint = {args.endpoint}")
    print(f"[replay] K        = [fx={meta['intrinsics']['fx']:.2f}, "
          f"fy={meta['intrinsics']['fy']:.2f}, "
          f"cx={meta['intrinsics']['cx']:.2f}, "
          f"cy={meta['intrinsics']['cy']:.2f}]")

    preflight(args.endpoint, timeout=args.timeout)
    print("[replay] preflight OK")

    stats = ReplayStats()
    stats.wall_start = time.perf_counter()

    # Graceful Ctrl-C: print partial summary and exit clean.
    interrupted = {"flag": False}
    def _sigint(_signum, _frame):
        interrupted["flag"] = True
    signal.signal(signal.SIGINT, _sigint)

    session_conn = requests.Session()
    prev_t_capture_s: Optional[float] = None
    next_wall_send = time.perf_counter()

    for i, idx in enumerate(frames):
        if interrupted["flag"]:
            print("\n[replay] interrupted — printing partial summary")
            break

        payload = build_payload(session, idx, K)
        if stats.first_seq is None:
            stats.first_seq = payload["sequence"]

        # --- rate pacing ---
        if rate_hz is None:
            pass  # max: no sleep
        elif rate_hz == -1.0:
            cur_t = payload["timestamp_ros"]
            if prev_t_capture_s is not None:
                dt = max(0.0, cur_t - prev_t_capture_s)
                time.sleep(dt)
            prev_t_capture_s = cur_t
        else:
            now = time.perf_counter()
            if now < next_wall_send:
                time.sleep(next_wall_send - now)
            next_wall_send += period_s

        # --- send ---
        t0 = time.perf_counter()
        try:
            r = session_conn.post(args.endpoint, json=payload, timeout=args.timeout)
            lat_ms = (time.perf_counter() - t0) * 1000.0
            if r.status_code == 200:
                stats.sent += 1
                stats.bytes_sent += len(payload["rgb_jpeg"]) + len(payload["depth_png"])
                stats.latencies_ms.append(lat_ms)
                stats.last_seq = payload["sequence"]
                # Gate 2.f.1: capture server-side decode timing when available.
                # Only decode-only responses have full timings; decode-failed
                # and older stub responses are silently skipped.
                try:
                    body = r.json()
                    if body.get("mode") == "decode-only":
                        total_ms = body.get("timings", {}).get("total_ms")
                        if isinstance(total_ms, (int, float)):
                            stats.server_decode_ms.append(float(total_ms))
                except (ValueError, KeyError, TypeError):
                    pass  # malformed body; not fatal for the replay run
                if args.verbose:
                    print(f"  seq={payload['sequence']:06d}  {lat_ms:6.1f} ms  "
                          f"→ {r.status_code}")
            else:
                stats.errors += 1
                print(f"\n[replay] HTTP {r.status_code} on seq={payload['sequence']}: "
                      f"{r.text[:200]}", file=sys.stderr)
        except requests.RequestException as e:
            stats.errors += 1
            print(f"\n[replay] request failed on seq={payload['sequence']}: {e}",
                  file=sys.stderr)

        # rolling progress
        if args.progress and not args.verbose and (i + 1) % args.progress == 0:
            sent = stats.sent
            errs = stats.errors
            last_lat = stats.latencies_ms[-1] if stats.latencies_ms else 0.0
            sys.stdout.write(
                f"\r[replay] {i+1}/{len(frames)}  sent={sent}  errs={errs}  "
                f"last={last_lat:5.1f}ms"
            )
            sys.stdout.flush()

    stats.wall_end = time.perf_counter()
    if args.progress and not args.verbose:
        sys.stdout.write("\n")

    print()
    print("=" * 60)
    for line in stats.summary_lines(args.endpoint, total_available=len(all_frames)):
        print(line)
    print("=" * 60)

    return 0 if stats.errors == 0 and not interrupted["flag"] else 1


if __name__ == "__main__":
    sys.exit(main())
