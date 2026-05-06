#!/usr/bin/env python3
"""
subscriber.py — rtsm-ingest frame subscriber (sub-gate 2.c).

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
  - `_emit(frame)` is the downstream seam. Today it logs and drops.
    Tomorrow it becomes the HTTP POST or ring-buffer write.

What this does NOT do (deliberately deferred):
  - No keyframe gating — every synced pair calls _emit.
  - No storage, no HTTP, no serialization.
  - No TF lookups. Camera-frame coords only.
  - No reconnect logic if Albert's publisher dies.
  - No fallback to raw transport if compressed plugins fail.
"""
import time
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np
import rclpy
from message_filters import ApproximateTimeSynchronizer, Subscriber
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from sensor_msgs.msg import CameraInfo, CompressedImage


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


class IngestSubscriber(Node):
    def __init__(self):
        super().__init__("rtsm_ingest_subscriber")

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

        self.get_logger().info(
            f"rtsm_ingest_subscriber up (compressed transport). "
            f"color={COLOR_TOPIC} depth={DEPTH_TOPIC} "
            f"slop={SYNC_SLOP_SEC*1000:.0f}ms"
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

        frame = Frame(
            seq=self._seq,
            t_capture_ns=t_capture_ns,
            t_received_ns=time.monotonic_ns(),
            rgb=rgb,
            depth_mm=depth_mm,
            color_frame_id=color_msg.header.frame_id,
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

    def _emit(self, frame: Frame):
        """Downstream seam. Replace this when wiring to rtsm-dev."""
        # Today: drop. Tomorrow: HTTP POST / storage / keyframe gate.
        pass

    def _maybe_log(self):
        """Log aggregate stats every ~2 s so we don't spam."""
        now = time.monotonic()
        if now - self._last_log_t < 2.0:
            return
        dt = now - self._last_log_t
        d_count = self._seq - self._last_log_count
        inst_rate = d_count / dt if dt > 0 else 0.0
        avg_rate = self._seq / (now - self._t_start)
        self.get_logger().info(
            f"synced_frames={self._seq} inst={inst_rate:.1f}Hz "
            f"avg={avg_rate:.1f}Hz info={'yes' if self._camera_info else 'no'}"
        )
        self._last_log_t = now
        self._last_log_count = self._seq


def main():
    rclpy.init()
    node = IngestSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
