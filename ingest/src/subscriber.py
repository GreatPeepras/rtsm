#!/usr/bin/env python3
"""
subscriber.py — rtsm-ingest frame subscriber (sub-gate 2.c + live HTTP wire).

Subscribes to Albert's D435i compressed color + compressed-depth streams,
decompresses locally, time-syncs them, and passes each synced pair to a
stub `_emit` method.

Transport:
  - color: /camera/camera/color/image_raw/compressed
           JPEG-encoded, lossy. Fine for RGB; ~5-10x smaller than raw.
  - depth: /camera/camera/aligned_depth_to_color/image_raw/compressedDepth
           PNG-encoded 16UC1 with 12-byte config header prepended.
           Lossless, so depth values survive the round-trip unchanged.

  Switched from raw transport on 2026-05-06 to keep Albert's Wi-Fi
  uplink inside its ~150 Mbps practical budget. Raw RGBD at 640x480@15
  was ~184 Mbps; compressed is ~10 Mbps, leaving headroom for nav, SSH,
  and telemetry.

Design decisions (see session log 2026-05-03):
  - QoS: BEST_EFFORT, KEEP_LAST depth=5 (matches sensor-stream convention;
    our depth > publisher's depth=1 so we have a small local buffer
    before ApproxTimeSync gates).
  - Sync: ApproximateTimeSynchronizer, 50 ms slop. At 15 Hz the frame
    period is ~67 ms, so 50 ms catches same-frame pairs, rejects
    cross-frame drift.
  - Using aligned_depth_to_color, not raw depth: depth is already
    registered to the RGB frame, so no extrinsics work downstream.
  - camera_info fetched once on startup (static), not sync'd per-frame.
  - `_emit(frame)` is the downstream seam. It writes to a Recorder
    (when --record is set) and/or POSTs to rtsm-dev's /ingest/keyframe
    (when --post-to is set). Both sinks may be active at once.

Recording (added 2026-05-06):
  - --record            enable per-frame dump to <record-root>/<run_id>/
  - --max-frames N      stop after N frames (default: run until Ctrl-C)
  - --record-root PATH  override root dir (default: /recordings)
  Writes paired files per synced frame: NNNNNN.jpg (raw on-wire JPEG),
  NNNNNN.png (16-bit depth PNG, on-wire bytes after header strip), and
  NNNNNN.json (timestamps + frame_id). One meta.json per session with
  intrinsics + final frame count.

Live HTTP wire (added 2026-05-14):
  - --post-to URL          POST each synced frame to rtsm-dev's ingest
                           endpoint, with real TF pose attached.
                           Example: http://localhost:8002/ingest/keyframe
  - --world-frame NAME     TF target frame for pose lookup (default: map)
  - --camera-frame NAME    TF source frame    (default: camera_color_optical_frame)
  - --pose-timeout MS      max wait per TF lookup (default: 100 ms)

  When --post-to is set, every synced frame triggers a TF lookup of
  world_frame -> camera_frame at the color image's header stamp.
  If the lookup fails, the frame is dropped (because POSTing without
  real pose is exactly the contamination the May 13 handoff warned
  against). Record-only runs are unaffected.

What this still does NOT do (deferred):
  - No keyframe gating — every synced pair calls _emit.
  - No reconnect logic if Albert's publisher dies.
  - No fallback to raw transport if compressed plugins fail.
"""
import argparse
import csv
import base64  # PATCH 20260514: live TF pose + HTTP emitter
import json
import time
from collections import deque  # PATCH 20260518: post-latency window
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from message_filters import ApproximateTimeSynchronizer, Subscriber
from rclpy.duration import Duration  # PATCH 20260514
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from sensor_msgs.msg import CameraInfo, CompressedImage
# PATCH 20260514: TF and HTTP deps
from tf2_ros import (  # noqa: E402
    Buffer,
    TransformListener,
    LookupException,
    ConnectivityException,
    ExtrapolationException,
    TransformException,
)
import requests


# Sensor-stream QoS: BEST_EFFORT, KEEP_LAST, VOLATILE.
# Depth=5 gives us a small local buffer for ApproxTimeSync.
SENSOR_QOS = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=5,
)

COLOR_TOPIC = "/camera/camera/color/image_raw/compressed"
DEPTH_TOPIC = "/camera/camera/aligned_depth_to_color/image_raw/compressedDepth"
COLOR_INFO_TOPIC = "/camera/camera/color/camera_info"

SYNC_SLOP_SEC = 0.05  # 50 ms; see header comment

# compressedDepth message layout:
#   12 bytes ConfigHeader, then PNG bytes.
# ConfigHeader (little-endian):
#   int32   compression_format  (0=PNG, 1=RVL)
#   float32 depth_quantization_A
#   float32 depth_quantization_B
# For 16UC1 depth (our case), A/B are unused; PNG is a straight 16-bit
# grayscale image in millimeters. If upstream ever switches to RVL,
# this decoder raises loudly — good.
COMPRESSED_DEPTH_HEADER_SIZE = 12


@dataclass
class Frame:
    """One synced RGB+depth capture. Camera-frame coordinates."""
    seq: int
    t_capture_ns: int       # header stamp of the color image, nanoseconds
    t_received_ns: int      # time_monotonic_ns when we received it
    rgb: np.ndarray         # (H, W, 3) uint8, RGB order
    depth_mm: np.ndarray    # (H, W)   uint16, millimeters, 0 = invalid
    color_frame_id: str     # ROS frame_id from header; for future TF work
    # Raw wire bytes, only populated when a Recorder or HttpEmitter is attached.
    # color_jpeg: the on-wire JPEG, unchanged.
    # depth_png:  the PNG payload AFTER the 12-byte compressedDepth header.
    color_jpeg: Optional[bytes] = None
    depth_png: Optional[bytes] = None
    # PATCH 20260514: real TF pose (world_frame -> camera_frame) at t_capture.
    # None for record-only runs. Required for HTTP emit.
    pose: Optional[dict] = None


class Recorder:
    """Writes synced frames to <root>/<run_id>/ as paired jpg+png+json.

    Design:
      - Writes the compressed bytes straight from the wire. JPEG from
        color_msg.data, PNG from depth_msg.data[12:]. Zero re-encode,
        bit-exact fidelity, viewer-compatible.
      - Per-frame JSON: stamps + frame_id. Tiny, debug-friendly.
      - meta.json: intrinsics + session info. Written on first frame
        where camera_info is available; frame count appended on close().
      - Filename: 6-digit zero-padded sequence. 999,999 frames at 15 Hz
        = ~18.5 h. Fine for manual sessions.
    """

    def __init__(self, root: Path, max_frames: Optional[int]):
        self.run_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        self.dir = root / self.run_id
        self.dir.mkdir(parents=True, exist_ok=False)
        self.max_frames = max_frames
        self.written = 0
        self._meta_written = False

    def write(self, frame: Frame, camera_info: Optional[CameraInfo]) -> bool:
        """Returns True if we should continue, False if max_frames is hit."""
        if self.max_frames is not None and self.written >= self.max_frames:
            return False
        if frame.color_jpeg is None or frame.depth_png is None:
            raise RuntimeError(
                "Recorder.write called on a Frame without raw bytes attached"
            )

        if not self._meta_written and camera_info is not None:
            self._write_meta(camera_info, frame.color_frame_id)
            self._meta_written = True

        stem = f"{self.written:06d}"
        (self.dir / f"{stem}.jpg").write_bytes(frame.color_jpeg)
        (self.dir / f"{stem}.png").write_bytes(frame.depth_png)
        (self.dir / f"{stem}.json").write_text(json.dumps({
            "seq": frame.seq,
            "t_capture_ns": frame.t_capture_ns,
            "t_received_ns": frame.t_received_ns,
            "color_frame_id": frame.color_frame_id,
        }))
        self.written += 1
        return True

    def _write_meta(self, info: CameraInfo, color_frame_id: str):
        (self.dir / "meta.json").write_text(json.dumps({
            "run_id": self.run_id,
            "source": "rtsm-ingest subscriber",
            "transport": "compressed (JPEG color, PNG compressedDepth)",
            "rate_hz_nominal": 15,
            "width": info.width,
            "height": info.height,
            "intrinsics": {
                "fx": info.k[0], "fy": info.k[4],
                "cx": info.k[2], "cy": info.k[5],
            },
            "distortion_model": info.distortion_model,
            "distortion_coeffs": list(info.d),
            "color_frame_id": color_frame_id,
        }, indent=2))

    def close(self):
        """Append final frame count to meta.json."""
        meta_path = self.dir / "meta.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            meta["frames_written"] = self.written
            meta_path.write_text(json.dumps(meta, indent=2))


class HttpEmitter:  # PATCH 20260514
    """POSTs synced frames (with real TF pose) to rtsm-dev's /ingest/keyframe.

    Mirrors the payload shape built by rtsm.tools.replay.build_payload
    (replay.py around line 173), so rtsm-dev cannot tell live ingest
    from replayed ingest at the wire level. Fields:
        rgb_jpeg, depth_png   -- base64 of on-wire bytes
        K                     -- 9-float intrinsics, row-major
        pose                  -- {tx,ty,tz,qx,qy,qz,qw}
        timestamp_ros         -- float seconds (t_capture_ns / 1e9)
        frame_id              -- color header frame_id
        sequence              -- int from frame.seq

    Uses a persistent requests.Session for TCP keep-alive. Never raises;
    logs and counts failures (node stays up if rtsm-dev briefly restarts).
    """

    def __init__(self, url: str, timeout_s: float = 2.0,
                 instrument_csv: Optional[str] = None):
        self.url = url
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.sent = 0
        self.failed = 0
        self.bytes_out = 0
        # PATCH 20260518: per-POST latency capture for backpressure
        # instrumentation. Sliding window of (most recent) wall-clock
        # POST durations in ms. 2048 ~ 5+ min at 6 Hz, plenty for
        # 60-second sweeps. Mixed ok/fail in one window (B1).
        self.latencies_ms: deque = deque(maxlen=2048)
        # PATCH 20260518: optional per-POST CSV record for backpressure
        # sweeps. Paired with stats-poller.py (joinable on t_wall_ns).
        # Line-buffered + explicit flush per row so SIGINT/SIGKILL
        # loses at most the in-flight row.
        self._csv_file = None
        self._csv_writer = None
        if instrument_csv is not None:
            self._csv_file = open(instrument_csv, "w", newline="", buffering=1)
            self._csv_writer = csv.DictWriter(
                self._csv_file,
                fieldnames=[
                    "t_wall_ns",   # POST start, joins to stats-poller.csv
                    "seq",         # frame sequence
                    "t_sensor_ns", # camera capture time
                    "latency_ms",  # POST roundtrip
                    "status",      # int code or "exc:<ClassName>"
                    "bytes_out",   # JPEG+PNG payload bytes
                    "ok",          # 1 if 2xx, else 0
                ],
            )
            self._csv_writer.writeheader()
            self._csv_file.flush()

    def post(self, frame: Frame, K_flat):
        """POST one frame. Returns (ok: bool, err: Optional[str])."""
        if frame.color_jpeg is None or frame.depth_png is None:
            raise RuntimeError("HttpEmitter.post called without wire bytes")
        if frame.pose is None:
            raise RuntimeError("HttpEmitter.post called without pose")
        payload = {
            "rgb_jpeg": base64.b64encode(frame.color_jpeg).decode("ascii"),
            "depth_png": base64.b64encode(frame.depth_png).decode("ascii"),
            "K": list(K_flat),
            "pose": frame.pose,
            "timestamp_ros": frame.t_capture_ns / 1e9,
            "frame_id": frame.color_frame_id or "camera_color_optical_frame",
            "sequence": frame.seq,
        }
        # PATCH 20260518: wall-clock latency around the POST call only
        # (excludes payload build + base64). Recorded for both success
        # and failure paths so timeout/error latencies are visible too.
        # t_wall_ns captured for CSV join with stats-poller output.
        t_wall_ns = time.time_ns()
        t0 = time.perf_counter()
        payload_bytes = len(frame.color_jpeg) + len(frame.depth_png)
        try:
            r = self.session.post(self.url, json=payload, timeout=self.timeout_s)
        except requests.exceptions.RequestException as e:
            lat_ms = (time.perf_counter() - t0) * 1000.0
            self.latencies_ms.append(lat_ms)
            self.failed += 1
            self._record_csv(
                t_wall_ns=t_wall_ns, frame=frame, lat_ms=lat_ms,
                status=f"exc:{type(e).__name__}",
                bytes_out=payload_bytes, ok=0,
            )
            return False, str(e)
        lat_ms = (time.perf_counter() - t0) * 1000.0
        self.latencies_ms.append(lat_ms)
        ok = (r.status_code == 200)
        if not ok:
            self.failed += 1
            self._record_csv(
                t_wall_ns=t_wall_ns, frame=frame, lat_ms=lat_ms,
                status=r.status_code, bytes_out=payload_bytes, ok=0,
            )
            return False, f"HTTP {r.status_code}: {r.text[:200]}"
        self.sent += 1
        # Conservative byte counter (wire bytes, not base64-inflated).
        self.bytes_out += payload_bytes
        self._record_csv(
            t_wall_ns=t_wall_ns, frame=frame, lat_ms=lat_ms,
            status=200, bytes_out=payload_bytes, ok=1,
        )
        return True, None

    def _record_csv(self, *, t_wall_ns, frame, lat_ms, status, bytes_out, ok):
        """Write one POST record to the instrument CSV, if enabled.
        PATCH 20260518."""
        if self._csv_writer is None:
            return
        self._csv_writer.writerow({
            "t_wall_ns": t_wall_ns,
            "seq": frame.seq,
            "t_sensor_ns": frame.t_capture_ns,
            "latency_ms": f"{lat_ms:.3f}",
            "status": status,
            "bytes_out": bytes_out,
            "ok": ok,
        })
        self._csv_file.flush()

    def close(self):
        """Flush and close instrument CSV + requests session.
        PATCH 20260518."""
        if self._csv_file is not None:
            try:
                self._csv_file.flush()
                self._csv_file.close()
            except Exception:
                pass
            self._csv_file = None
            self._csv_writer = None
        try:
            self.session.close()
        except Exception:
            pass

    def percentiles(self):
        '''Return {p50, p95, p99, max, n} from the sliding window, in ms.

        Returns Nones if the window is empty. Cheap: a sort over <=2048
        floats; called only from the 2-second log tick.
        PATCH 20260518.
        '''
        n = len(self.latencies_ms)
        if n == 0:
            return {"p50": None, "p95": None, "p99": None, "max": None, "n": 0}
        s = sorted(self.latencies_ms)

        def pct(p):
            # nearest-rank, clamped. Good enough for ops; not for stats papers.
            idx = max(0, min(n - 1, int(round(p * (n - 1)))))
            return s[idx]

        return {
            "p50": pct(0.50),
            "p95": pct(0.95),
            "p99": pct(0.99),
            "max": s[-1],
            "n": n,
        }


class IngestSubscriber(Node):
    def __init__(
        self,
        recorder: Optional[Recorder] = None,
        http_emitter: Optional[HttpEmitter] = None,           # PATCH 20260514
        world_frame: str = "map",                              # PATCH 20260514
        camera_frame: str = "camera_color_optical_frame",      # PATCH 20260514
        pose_timeout_s: float = 0.10,                          # PATCH 20260514
        post_hz: float = 2.0,  # PATCH 20260518: default tuned for bursty workload, see backpressure-2026-05-18
    ):
        super().__init__("rtsm_ingest_subscriber")

        self._recorder = recorder
        # PATCH 20260514:
        self._http_emitter = http_emitter
        self._world_frame = world_frame
        self._camera_frame = camera_frame
        self._pose_timeout = Duration(seconds=pose_timeout_s)
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)
        self._tf_success = 0
        self._tf_fail = 0
        self._post_ok = 0
        self._post_fail = 0
        # PATCH 20260514 (fix 20260514b): decimator + pose-staleness state
        # belong on IngestSubscriber, not Recorder. _emit reads _post_interval_ns;
        # _lookup_pose writes _last_pose_stale_ms; _maybe_log reads it.
        self._post_hz = post_hz
        self._post_interval_ns = int(1e9 / post_hz) if post_hz > 0 else 0
        self._last_post_ns = 0
        self._post_skipped = 0
        self._last_pose_stale_ms = 0.0

        self._seq = 0
        self._t_start = time.monotonic()
        self._last_log_t = self._t_start
        self._last_log_count = 0
        self._camera_info: Optional[CameraInfo] = None

        # One-shot subscriber for camera_info. Intrinsics are static;
        # we grab one message and unsubscribe.
        self._info_sub = self.create_subscription(
            CameraInfo,
            COLOR_INFO_TOPIC,
            self._on_camera_info,
            SENSOR_QOS,
        )

        # Time-synced compressed-image subscribers via message_filters.
        color_sub = Subscriber(
            self, CompressedImage, COLOR_TOPIC, qos_profile=SENSOR_QOS
        )
        depth_sub = Subscriber(
            self, CompressedImage, DEPTH_TOPIC, qos_profile=SENSOR_QOS
        )

        # queue_size sized for worst-case arrival lag.
        # Raw-transport investigation (2026-05-03) measured color lag
        # growing to ~1 s under USB 2.1 bottleneck. Compressed transport
        # should eliminate that — frames are 5-10x smaller, transfer
        # time proportionally shorter — but we keep queue_size=60
        # conservatively until we've observed the new steady-state.
        # At 15 Hz, queue_size=60 holds 4 s of history.
        self._sync = ApproximateTimeSynchronizer(
            [color_sub, depth_sub],
            queue_size=60,
            slop=SYNC_SLOP_SEC,
        )
        self._sync.registerCallback(self._on_synced)

        # --- MINIMAL RATE PROBE (remove after 2.c closes) ---
        self._diag_c = 0
        self._diag_d = 0
        self._diag_s = 0

        def _dc(m):
            self._diag_c += 1
            if self._diag_c % 60 == 0:
                self.get_logger().info(f"DIAG color_seen={self._diag_c}")

        def _dd(m):
            self._diag_d += 1
            if self._diag_d % 60 == 0:
                self.get_logger().info(f"DIAG depth_seen={self._diag_d}")

        color_sub.registerCallback(_dc)
        depth_sub.registerCallback(_dd)

        def _ds(c, d):
            self._diag_s += 1
            if self._diag_s % 30 == 0:
                off = abs(
                    (c.header.stamp.sec + c.header.stamp.nanosec * 1e-9)
                    - (d.header.stamp.sec + d.header.stamp.nanosec * 1e-9)
                ) * 1000
                self.get_logger().info(
                    f"DIAG sync_seen={self._diag_s} offset={off:.1f}ms"
                )

        self._sync.registerCallback(_ds)
        # --- END MINIMAL PROBE ---

        rec_status = (
            f"yes -> {self._recorder.dir}"
            if self._recorder is not None
            else "no"
        )
        http_status = (
            f"yes -> {self._http_emitter.url}"
            if self._http_emitter is not None
            else "no"
        )
        self.get_logger().info(
            f"rtsm_ingest_subscriber up (compressed transport). "
            f"color={COLOR_TOPIC} depth={DEPTH_TOPIC} "
            f"slop={SYNC_SLOP_SEC*1000:.0f}ms "
            f"recording={rec_status} http={http_status} "
            f"tf={self._world_frame}->{self._camera_frame}"
        )

    def _on_camera_info(self, msg: CameraInfo):
        if self._camera_info is not None:
            return
        self._camera_info = msg
        self.get_logger().info(
            f"camera_info captured: {msg.width}x{msg.height} "
            f"fx={msg.k[0]:.2f} fy={msg.k[4]:.2f} "
            f"cx={msg.k[2]:.2f} cy={msg.k[5]:.2f} "
            f"distortion_model={msg.distortion_model}"
        )
        # Unsubscribe; intrinsics are static.
        self.destroy_subscription(self._info_sub)
        self._info_sub = None

    def _on_synced(self, color_msg: CompressedImage, depth_msg: CompressedImage):
        try:
            rgb = self._decode_jpeg(color_msg.data)
        except Exception as e:
            self.get_logger().error(
                f"color JPEG decode failed (format={color_msg.format!r}): {e}"
            )
            return

        try:
            depth_mm = self._decode_compressed_depth(
                depth_msg.data, depth_msg.format
            )
        except Exception as e:
            self.get_logger().error(
                f"depth compressedDepth decode failed (format={depth_msg.format!r}): {e}"
            )
            return

        t_capture_ns = (
            color_msg.header.stamp.sec * 1_000_000_000
            + color_msg.header.stamp.nanosec
        )

        # Only copy wire bytes if we have somewhere to put them.
        # bytes(msg.data) is a copy; skipping it when no sink is attached
        # keeps the no-op path zero-cost.
        # PATCH 20260514: HttpEmitter also needs wire bytes.
        if self._recorder is not None or self._http_emitter is not None:
            color_jpeg = bytes(color_msg.data)
            depth_png = bytes(depth_msg.data[COMPRESSED_DEPTH_HEADER_SIZE:])
        else:
            color_jpeg = None
            depth_png = None

        # PATCH 20260514: look up TF pose at the color stamp.
        # Record-only runs don't strictly need pose, but the lookup is
        # cheap (<1 ms when TF is populated) and we attach it for the
        # session log either way. HTTP runs require it; if it fails
        # AND http_emitter is attached, drop the frame.
        pose = self._lookup_pose(color_msg.header.stamp)
        if pose is None and self._http_emitter is not None:
            return

        frame = Frame(
            seq=self._seq,
            t_capture_ns=t_capture_ns,
            t_received_ns=time.monotonic_ns(),
            rgb=rgb,
            depth_mm=depth_mm,
            color_frame_id=color_msg.header.frame_id,
            color_jpeg=color_jpeg,
            depth_png=depth_png,
            pose=pose,
        )
        self._seq += 1
        self._emit(frame)
        self._maybe_log()

    @staticmethod
    def _decode_jpeg(data: bytes) -> np.ndarray:
        """JPEG bytes -> (H, W, 3) uint8 RGB."""
        buf = np.frombuffer(data, dtype=np.uint8)
        bgr = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        if bgr is None:
            raise ValueError("cv2.imdecode returned None on color JPEG")
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    @staticmethod
    def _decode_compressed_depth(data: bytes, fmt: str) -> np.ndarray:
        """compressedDepth bytes -> (H, W) uint16 millimeters.

        Format string varies by publisher version:
          - "16UC1; compressedDepth"       -> implicit PNG (older default)
          - "16UC1; compressedDepth png"   -> explicit PNG
          - "16UC1; compressedDepth rvl"   -> RVL (not supported here)
        We accept both PNG variants and reject RVL loudly.
        """
        fmt_lower = fmt.lower()
        if "rvl" in fmt_lower:
            raise ValueError(f"RVL compressedDepth not supported: fmt={fmt!r}")
        # Otherwise assume PNG (explicit or implicit). If it's neither,
        # cv2.imdecode below will return None and we'll raise.

        if len(data) < COMPRESSED_DEPTH_HEADER_SIZE:
            raise ValueError(f"depth buffer too short: {len(data)} bytes")

        png_bytes = data[COMPRESSED_DEPTH_HEADER_SIZE:]
        buf = np.frombuffer(png_bytes, dtype=np.uint8)
        depth = cv2.imdecode(buf, cv2.IMREAD_UNCHANGED)
        if depth is None:
            raise ValueError(
                f"cv2.imdecode returned None on depth payload (fmt={fmt!r}, "
                f"payload_bytes={len(png_bytes)})"
            )
        if depth.dtype != np.uint16:
            raise ValueError(f"expected uint16 depth, got {depth.dtype}")
        return depth

    def _lookup_pose(self, stamp):  # PATCH 20260514
        """Return {tx,ty,tz,qx,qy,qz,qw} for world->camera, or None.

        Uses rclpy.time.Time() (zero) instead of the image stamp, which
        means "latest available transform" rather than "transform at this
        exact stamp." For room-scale 15 Hz mapping this is the right
        semantic: SLAM stacks publish map->odom on loop closure (slow,
        seconds-scale), and stamp-exact lookups would drop frames whenever
        TF data lags image data by even a few ms — which is essentially
        always for a fresh image stamp.

        We track the staleness (image stamp - TF stamp) so downstream can
        decide whether a pose is "fresh enough" if it ever needs to.
        """
        import rclpy.time as _rclpy_time
        try:
            t = self._tf_buffer.lookup_transform(
                self._world_frame,
                self._camera_frame,
                _rclpy_time.Time(),  # latest available
                timeout=self._pose_timeout,
            )
        except (LookupException, ConnectivityException,
                ExtrapolationException, TransformException) as e:
            self._tf_fail += 1
            if self._tf_fail % 30 == 1:
                self.get_logger().warn(
                    f"TF {self._world_frame}->{self._camera_frame} failed: {e} "
                    f"({self._tf_fail} fails, {self._tf_success} ok)"
                )
            return None
        self._tf_success += 1
        # Track staleness: image stamp ns vs TF stamp ns.
        img_ns = stamp.sec * 1_000_000_000 + stamp.nanosec
        tf_ns = (t.header.stamp.sec * 1_000_000_000
                 + t.header.stamp.nanosec)
        self._last_pose_stale_ms = (img_ns - tf_ns) / 1e6
        return {
            "tx": t.transform.translation.x,
            "ty": t.transform.translation.y,
            "tz": t.transform.translation.z,
            "qx": t.transform.rotation.x,
            "qy": t.transform.rotation.y,
            "qz": t.transform.rotation.z,
            "qw": t.transform.rotation.w,
        }

    def _emit(self, frame: Frame):
        """Downstream seam. Writes to recorder and/or POSTs to rtsm-dev."""
        # PATCH 20260514: recorder and http_emitter are independent sinks.
        if self._recorder is not None:
            if not self._recorder.write(frame, self._camera_info):
                self.get_logger().info(
                    f"max_frames reached ({self._recorder.written}), shutting down"
                )
                raise SystemExit(0)
        if self._http_emitter is not None and self._camera_info is not None:
            # PATCH 20260514: time-based decimation. Recorder above gets every
            # frame; only the HTTP wire is throttled.
            now_ns = self.get_clock().now().nanoseconds
            if (self._post_interval_ns == 0
                    or now_ns - self._last_post_ns >= self._post_interval_ns):
                ok, err = self._http_emitter.post(frame, list(self._camera_info.k))
                if ok:
                    self._post_ok += 1
                else:
                    self._post_fail += 1
                    if self._post_fail % 30 == 1:
                        self.get_logger().warn(
                            f"POST to rtsm-dev failed: {err} "
                            f"({self._post_fail} fails, {self._post_ok} ok)"
                        )
                self._last_post_ns = now_ns
            else:
                self._post_skipped += 1

    def _maybe_log(self):
        """Log aggregate stats every ~2 s so we don't spam."""
        now = time.monotonic()
        if now - self._last_log_t < 2.0:
            return
        dt = now - self._last_log_t
        d_count = self._seq - self._last_log_count
        inst_rate = d_count / dt if dt > 0 else 0.0
        avg_rate = self._seq / (now - self._t_start)
        rec_info = (
            f" rec={self._recorder.written}"
            if self._recorder is not None
            else ""
        )
        # PATCH 20260514: aggregate TF + HTTP counters in periodic log
        http_info = ""
        if self._http_emitter is not None:
            # PATCH 20260518: latency percentiles from HttpEmitter window.
            lat = self._http_emitter.percentiles()
            if lat["n"] > 0:
                lat_str = (
                    f" lat_p50={lat['p50']:.0f}ms"
                    f" lat_p95={lat['p95']:.0f}ms"
                    f" lat_p99={lat['p99']:.0f}ms"
                    f" lat_max={lat['max']:.0f}ms"
                    f" lat_n={lat['n']}"
                )
            else:
                lat_str = " lat=none"
            http_info = (
                f" tf_ok={self._tf_success} tf_fail={self._tf_fail}"
                f" tf_stale={self._last_pose_stale_ms:.0f}ms"
                f" post_ok={self._post_ok} post_fail={self._post_fail}"
                f" post_skip={self._post_skipped}"
                f"{lat_str}"
            )
        self.get_logger().info(
            f"synced_frames={self._seq} inst={inst_rate:.1f}Hz "
            f"avg={avg_rate:.1f}Hz info={'yes' if self._camera_info else 'no'}"
            f"{rec_info}{http_info}"
        )
        self._last_log_t = now
        self._last_log_count = self._seq


def main():
    parser = argparse.ArgumentParser(description="rtsm-ingest subscriber")
    parser.add_argument(
        "--record", action="store_true",
        help="Dump every synced frame to <record-root>/<run_id>/"
    )
    parser.add_argument(
        "--max-frames", type=int, default=None,
        help="Stop after N frames (default: run until Ctrl-C)"
    )
    parser.add_argument(
        "--record-root", type=Path, default=Path("/recordings"),
        help="Root directory for recordings (default: /recordings)"
    )
    # PATCH 20260514: live HTTP wire args
    parser.add_argument(
        "--post-to", default=None,
        help="rtsm-dev URL to POST each synced frame to "
             "(e.g. http://localhost:8002/ingest/keyframe). "
             "When set, real TF pose is attached. Default: off (no POST)."
    )
    parser.add_argument(
        "--world-frame", default="map",
        help="TF target frame for pose lookup (default: map)"
    )
    parser.add_argument(
        "--camera-frame", default="camera_color_optical_frame",
        help="TF source frame for pose lookup "
             "(default: camera_color_optical_frame)"
    )
    parser.add_argument(
        "--pose-timeout-ms", type=int, default=100,
        help="Max wait per TF lookup, milliseconds (default: 100)"
    )
    parser.add_argument(
        "--post-hz", type=float, default=2.0,
        help="Decimate HTTP POSTs to this rate (Hz). Recorder is unaffected. "
             "Default: 6.0. Set 0 to disable decimation.",
    )
    # PATCH 20260518: per-POST CSV for backpressure sweeps. Pairs with
    # stats-poller.py via t_wall_ns column. If unset, no CSV is written.
    parser.add_argument(
        "--instrument", type=str, default=None,
        help="Path to per-POST CSV record (for backpressure analysis). "
             "Joinable with stats-poller.py output on t_wall_ns. "
             "Default: off.",
    )
    args = parser.parse_args()

    recorder = None
    if args.record:
        recorder = Recorder(root=args.record_root, max_frames=args.max_frames)

    http_emitter = None  # PATCH 20260514
    if args.post_to:
        http_emitter = HttpEmitter(
            url=args.post_to,
            instrument_csv=args.instrument,  # PATCH 20260518
        )

    rclpy.init()
    node = IngestSubscriber(
        recorder=recorder,
        http_emitter=http_emitter,
        world_frame=args.world_frame,
        camera_frame=args.camera_frame,
        pose_timeout_s=args.pose_timeout_ms / 1000.0,
        post_hz=args.post_hz,
    )
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit, ExternalShutdownException):
        pass
    finally:
        if recorder is not None:
            recorder.close()
            node.get_logger().info(
                f"recording complete: {recorder.written} frames in {recorder.dir}"
            )
        if http_emitter is not None:
            node.get_logger().info(
                f"http emit complete: sent={http_emitter.sent} "
                f"failed={http_emitter.failed} "
                f"bytes_out={http_emitter.bytes_out}"
            )
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
