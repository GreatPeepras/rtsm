#!/usr/bin/env python3
"""
subscriber.py — rtsm-ingest frame subscriber (sub-gate 2.c).

Subscribes to Albert's D435i color + aligned-depth streams, time-syncs
them, and passes each synced pair to a stub `_emit` method.

Design decisions (see session log 2026-05-03):
  - QoS: RELIABLE, KEEP_LAST depth=5 (matches publisher; our depth > their
    depth=1 so we have a small local buffer before ApproxTimeSync gates).
  - Sync: ApproximateTimeSynchronizer, 50 ms slop. Frame period at
    20-30 Hz is 33-50 ms; 50 ms catches same-frame pairs, rejects
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
"""
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
import rclpy
from cv_bridge import CvBridge
from message_filters import ApproximateTimeSynchronizer, Subscriber
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from sensor_msgs.msg import CameraInfo, Image


# Matches publisher-side QoS as reported by `ros2 topic info --verbose`:
# RELIABLE, KEEP_LAST, VOLATILE.  We use depth=5 (publisher is depth=1)
# so we have a small local buffer for ApproxTimeSync to pair across.
SENSOR_QOS = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=5,
)

COLOR_TOPIC = "/camera/camera/color/image_raw"
DEPTH_TOPIC = "/camera/camera/aligned_depth_to_color/image_raw"
COLOR_INFO_TOPIC = "/camera/camera/color/camera_info"

SYNC_SLOP_SEC = 0.05  # 50 ms; see header comment


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

        self.bridge = CvBridge()
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

        # Time-synced image subscribers via message_filters.
        color_sub = Subscriber(self, Image, COLOR_TOPIC, qos_profile=SENSOR_QOS)
        depth_sub = Subscriber(self, Image, DEPTH_TOPIC, qos_profile=SENSOR_QOS)
        self._sync = ApproximateTimeSynchronizer(
            [color_sub, depth_sub],
            queue_size=10,
            slop=SYNC_SLOP_SEC,
        )
        self._sync.registerCallback(self._on_synced)

        self.get_logger().info(
            f"rtsm_ingest_subscriber up. color={COLOR_TOPIC} "
            f"depth={DEPTH_TOPIC} slop={SYNC_SLOP_SEC*1000:.0f}ms"
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

    def _on_synced(self, color_msg: Image, depth_msg: Image):
        # Encoding sanity checks. If these ever fire, something upstream
        # changed and our downstream assumptions break silently — fail loud.
        if color_msg.encoding != "rgb8":
            self.get_logger().error(
                f"unexpected color encoding: {color_msg.encoding!r} (want rgb8)"
            )
            return
        if depth_msg.encoding != "16UC1":
            self.get_logger().error(
                f"unexpected depth encoding: {depth_msg.encoding!r} (want 16UC1)"
            )
            return

        try:
            rgb = self.bridge.imgmsg_to_cv2(color_msg, desired_encoding="rgb8")
            depth_mm = self.bridge.imgmsg_to_cv2(depth_msg, desired_encoding="passthrough")
        except Exception as e:
            self.get_logger().error(f"cv_bridge conversion failed: {e}")
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
