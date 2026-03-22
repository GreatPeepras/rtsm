"""
TSDF Volumetric Fusion for RTSM Visualization.

Wraps Open3D's ScalableTSDFVolume to fuse RGB-D frames with known poses
into a consistent 3D reconstruction. Replaces per-frame point cloud
accumulation which suffers from visible drift layering.
"""

import threading
import time
import logging
from collections import deque
from dataclasses import dataclass
from typing import Optional, Tuple, Deque, Dict

import numpy as np

logger = logging.getLogger(__name__)

try:
    import open3d as o3d
except ImportError:
    o3d = None
    logger.warning(
        "[tsdf] open3d not installed — TSDF fusion unavailable. "
        "Install with: pip install open3d"
    )


@dataclass
class TSDFConfig:
    """Configuration for TSDF integration."""
    voxel_size: float = 0.01
    sdf_trunc: float = 0.04
    max_depth_m: float = 3.5
    min_depth_m: float = 0.1
    extract_every_n: int = 30
    extract_interval_s: float = 2.0
    frame_buffer_size: int = 200
    correction_reset_threshold_m: float = 0.05


@dataclass
class BufferedFrame:
    """A frame stored in the ring buffer for potential re-integration."""
    frame_id: str
    rgb: np.ndarray           # (H, W, 3) uint8 RGB
    depth_m: np.ndarray       # (H, W) float32 meters
    intrinsic: "o3d.camera.PinholeCameraIntrinsic"
    pose: np.ndarray          # (4, 4) float64 T_wc
    timestamp_ns: int


class TSDFIntegrator:
    """
    Thread-safe TSDF volume integrator using Open3D ScalableTSDFVolume.

    Integrates incoming RGB-D frames with camera poses and periodically
    extracts a fused point cloud for visualization.
    """

    def __init__(self, config: Optional[TSDFConfig] = None):
        if o3d is None:
            raise RuntimeError(
                "open3d is required for TSDF fusion. "
                "Install with: pip install open3d"
            )

        self.cfg = config or TSDFConfig()
        self._lock = threading.Lock()

        # Create TSDF volume
        self._volume = self._create_volume()

        # Frame counter and timing for extraction triggers
        self._frames_since_extract: int = 0
        self._last_extract_time: float = 0.0
        self._total_integrated: int = 0

        # Ring buffer of raw frames for re-integration
        self._frame_buffer: Deque[BufferedFrame] = deque(
            maxlen=self.cfg.frame_buffer_size
        )

        # Latest extracted mesh data (positions + colors)
        self._latest_positions: Optional[np.ndarray] = None
        self._latest_colors: Optional[np.ndarray] = None
        self._mesh_version: int = 0

        logger.info(
            f"[tsdf] Initialized: voxel={self.cfg.voxel_size}m, "
            f"trunc={self.cfg.sdf_trunc}m, "
            f"depth=[{self.cfg.min_depth_m}, {self.cfg.max_depth_m}]m, "
            f"buffer={self.cfg.frame_buffer_size}"
        )

    def _create_volume(self) -> "o3d.pipelines.integration.ScalableTSDFVolume":
        """Create a fresh Open3D ScalableTSDFVolume."""
        return o3d.pipelines.integration.ScalableTSDFVolume(
            voxel_length=self.cfg.voxel_size,
            sdf_trunc=self.cfg.sdf_trunc,
            color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8,
        )

    def _prepare_depth(self, depth_m: np.ndarray) -> np.ndarray:
        """Clamp depth range and replace NaN with 0 for Open3D."""
        depth_clean = depth_m.copy()
        invalid = (
            ~np.isfinite(depth_clean)
            | (depth_clean < self.cfg.min_depth_m)
            | (depth_clean > self.cfg.max_depth_m)
        )
        depth_clean[invalid] = 0.0
        return depth_clean

    def _make_intrinsic(
        self, K: np.ndarray, width: int, height: int
    ) -> "o3d.camera.PinholeCameraIntrinsic":
        """Build Open3D intrinsic from 3x3 K matrix."""
        return o3d.camera.PinholeCameraIntrinsic(
            width, height,
            float(K[0, 0]), float(K[1, 1]),
            float(K[0, 2]), float(K[1, 2]),
        )

    def _integrate_single(
        self,
        rgb: np.ndarray,
        depth_clean: np.ndarray,
        intrinsic: "o3d.camera.PinholeCameraIntrinsic",
        T_wc: np.ndarray,
    ) -> None:
        """Integrate a single frame into the volume (caller holds lock)."""
        color_o3d = o3d.geometry.Image(
            np.ascontiguousarray(rgb).astype(np.uint8)
        )
        depth_o3d = o3d.geometry.Image(
            np.ascontiguousarray(depth_clean).astype(np.float32)
        )
        rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
            color_o3d, depth_o3d,
            depth_scale=1.0,        # already in meters
            depth_trunc=self.cfg.max_depth_m,
            convert_rgb_to_intensity=False,
        )

        # Open3D backprojects in OpenCV camera convention (Z-forward, Y-down).
        # ARKit→OpenCV camera flip is applied at ingestion (WebSocketReceiver)
        # so T_wc is already in OpenCV convention.
        # Open3D expects T_cw (camera-from-world) = inverse of T_wc
        T_cw = np.linalg.inv(T_wc.astype(np.float64))
        self._volume.integrate(rgbd, intrinsic, T_cw)

    def integrate(
        self,
        frame_id: str,
        rgb: np.ndarray,
        depth_m: np.ndarray,
        K: np.ndarray,
        pose_T_wc: np.ndarray,
        width: int,
        height: int,
        timestamp_ns: int = 0,
    ) -> bool:
        """
        Integrate a single RGB-D frame into the TSDF volume.

        Args:
            frame_id: Unique identifier for this frame.
            rgb: (H, W, 3) uint8 RGB image.
            depth_m: (H, W) float32 depth in meters (NaN = invalid).
            K: (3, 3) camera intrinsics matrix.
            pose_T_wc: (4, 4) world-from-camera transform.
            width: Image width.
            height: Image height.
            timestamp_ns: Frame timestamp.

        Returns:
            True if extraction should be triggered after this integration.
        """
        depth_clean = self._prepare_depth(depth_m)
        intrinsic = self._make_intrinsic(K, width, height)
        T_wc = pose_T_wc.astype(np.float64)

        with self._lock:
            self._integrate_single(rgb, depth_clean, intrinsic, T_wc)
            self._total_integrated += 1
            self._frames_since_extract += 1

            # Store in ring buffer for re-integration on loop closure
            self._frame_buffer.append(BufferedFrame(
                frame_id=frame_id,
                rgb=rgb.copy(),
                depth_m=depth_m.copy(),
                intrinsic=intrinsic,
                pose=T_wc.copy(),
                timestamp_ns=timestamp_ns,
            ))

        # Check if extraction should be triggered
        now = time.monotonic()
        should_extract = (
            self._frames_since_extract >= self.cfg.extract_every_n
            or (now - self._last_extract_time) >= self.cfg.extract_interval_s
        )
        return should_extract

    def extract_point_cloud(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract the fused point cloud from the TSDF volume.

        Returns:
            positions: (N, 3) float32 XYZ in world frame.
            colors: (N, 3) uint8 RGB.
        """
        with self._lock:
            pcd = self._volume.extract_point_cloud()
            self._frames_since_extract = 0
            self._last_extract_time = time.monotonic()

        if pcd.is_empty():
            return (
                np.zeros((0, 3), dtype=np.float32),
                np.zeros((0, 3), dtype=np.uint8),
            )

        positions = np.asarray(pcd.points, dtype=np.float32)
        colors = (np.asarray(pcd.colors) * 255).astype(np.uint8)

        self._latest_positions = positions
        self._latest_colors = colors
        self._mesh_version += 1

        return positions, colors

    def get_latest_mesh(self) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Return the latest extracted mesh, or None if never extracted."""
        if self._latest_positions is None:
            return None
        return self._latest_positions, self._latest_colors

    def handle_pose_corrections(
        self, corrections: Dict[str, np.ndarray]
    ) -> bool:
        """
        Handle pose corrections from RTAB-Map loop closure.

        Args:
            corrections: dict mapping frame_id -> corrected 4x4 T_wc pose.

        Returns:
            True if the volume was reset and re-integrated.
        """
        with self._lock:
            # Find max correction magnitude among buffered frames
            max_delta = 0.0
            updated_count = 0
            for bf in self._frame_buffer:
                if bf.frame_id in corrections:
                    old_t = bf.pose[:3, 3]
                    new_t = corrections[bf.frame_id][:3, 3]
                    delta = float(np.linalg.norm(new_t - old_t))
                    max_delta = max(max_delta, delta)
                    updated_count += 1

            if updated_count == 0:
                return False

            # Update poses in the buffer
            for bf in self._frame_buffer:
                if bf.frame_id in corrections:
                    bf.pose = corrections[bf.frame_id].astype(np.float64)

            # If corrections are small, TSDF averaging handles it
            if max_delta < self.cfg.correction_reset_threshold_m:
                logger.info(
                    f"[tsdf] Small correction (max {max_delta:.4f}m, "
                    f"{updated_count} frames), keeping volume"
                )
                return False

            # Large correction: reset and re-integrate from buffer
            logger.info(
                f"[tsdf] Large correction (max {max_delta:.4f}m, "
                f"{updated_count} frames), resetting volume and "
                f"re-integrating {len(self._frame_buffer)} frames"
            )
            self._volume = self._create_volume()
            self._total_integrated = 0

            for bf in self._frame_buffer:
                depth_clean = self._prepare_depth(bf.depth_m)
                self._integrate_single(
                    bf.rgb, depth_clean, bf.intrinsic, bf.pose
                )
                self._total_integrated += 1

            # Trigger extraction on next opportunity
            self._frames_since_extract = self.cfg.extract_every_n
            return True

    def reset(self) -> None:
        """Reset the TSDF volume and frame buffer."""
        with self._lock:
            self._volume = self._create_volume()
            self._frame_buffer.clear()
            self._total_integrated = 0
            self._frames_since_extract = 0
            self._latest_positions = None
            self._latest_colors = None
            self._mesh_version = 0
        logger.info("[tsdf] Volume reset")

    @property
    def total_integrated(self) -> int:
        return self._total_integrated

    @property
    def mesh_version(self) -> int:
        return self._mesh_version

    def stats(self) -> dict:
        return {
            "tsdf_total_integrated": self._total_integrated,
            "tsdf_buffer_size": len(self._frame_buffer),
            "tsdf_buffer_capacity": self.cfg.frame_buffer_size,
            "tsdf_mesh_version": self._mesh_version,
            "tsdf_frames_since_extract": self._frames_since_extract,
        }
