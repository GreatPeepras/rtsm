"""
Coordinate transform utilities for RTSM.

Provides conversions between rotation representations (Euler angles, quaternions, rotation matrices).
"""

from __future__ import annotations
import math
from typing import Optional, TYPE_CHECKING
import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    import torch


def euler_to_quat_xyzw(roll: float, pitch: float, yaw: float) -> NDArray[np.float32]:
    """
    Convert Euler angles (radians) to quaternion [x, y, z, w].

    Uses ZYX convention (yaw-pitch-roll), which is standard for robotics:
    - First rotate around Z by yaw
    - Then rotate around Y by pitch
    - Then rotate around X by roll

    This matches RTABMap's convention for T_wc = [x, y, z, roll, pitch, yaw].

    Args:
        roll: Rotation around X-axis (radians)
        pitch: Rotation around Y-axis (radians)
        yaw: Rotation around Z-axis (radians)

    Returns:
        Quaternion as numpy array [x, y, z, w] (Hamilton convention)
    """
    # Half angles
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)

    # ZYX convention quaternion multiplication
    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy

    return np.array([x, y, z, w], dtype=np.float32)


def quat_xyzw_to_euler(q: NDArray[np.float32]) -> tuple[float, float, float]:
    """
    Convert quaternion [x, y, z, w] to Euler angles (roll, pitch, yaw) in radians.

    Uses ZYX convention (inverse of euler_to_quat_xyzw).

    Args:
        q: Quaternion as numpy array [x, y, z, w]

    Returns:
        Tuple of (roll, pitch, yaw) in radians
    """
    x, y, z, w = q

    # Roll (x-axis rotation)
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # Pitch (y-axis rotation)
    sinp = 2.0 * (w * y - z * x)
    if abs(sinp) >= 1.0:
        pitch = math.copysign(math.pi / 2.0, sinp)  # Gimbal lock
    else:
        pitch = math.asin(sinp)

    # Yaw (z-axis rotation)
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw


def euler_to_rotation_matrix(roll: float, pitch: float, yaw: float) -> NDArray[np.float32]:
    """
    Convert Euler angles (radians) to 3x3 rotation matrix.

    Uses ZYX convention (same as euler_to_quat_xyzw).

    Args:
        roll: Rotation around X-axis (radians)
        pitch: Rotation around Y-axis (radians)
        yaw: Rotation around Z-axis (radians)

    Returns:
        3x3 rotation matrix as numpy array
    """
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)

    # ZYX: R = Rz(yaw) @ Ry(pitch) @ Rx(roll)
    return np.array([
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp,     cp * sr,                cp * cr               ]
    ], dtype=np.float32)


def rotmat_to_quat_xyzw(R: NDArray[np.float32]) -> NDArray[np.float32]:
    """
    Convert a 3x3 rotation matrix to quaternion [x, y, z, w].

    Uses Shepperd's method for numerical stability (avoids division
    by near-zero when trace is small).

    Args:
        R: 3x3 rotation matrix (SO(3))

    Returns:
        Quaternion as numpy array [x, y, z, w] (Hamilton convention)
    """
    trace = float(R[0, 0] + R[1, 1] + R[2, 2])

    if trace > 0:
        s = 0.5 / math.sqrt(trace + 1.0)
        w = 0.25 / s
        x = (R[2, 1] - R[1, 2]) * s
        y = (R[0, 2] - R[2, 0]) * s
        z = (R[1, 0] - R[0, 1]) * s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = 2.0 * math.sqrt(1.0 + float(R[0, 0]) - float(R[1, 1]) - float(R[2, 2]))
        w = (R[2, 1] - R[1, 2]) / s
        x = 0.25 * s
        y = (R[0, 1] + R[1, 0]) / s
        z = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = 2.0 * math.sqrt(1.0 + float(R[1, 1]) - float(R[0, 0]) - float(R[2, 2]))
        w = (R[0, 2] - R[2, 0]) / s
        x = (R[0, 1] + R[1, 0]) / s
        y = 0.25 * s
        z = (R[1, 2] + R[2, 1]) / s
    else:
        s = 2.0 * math.sqrt(1.0 + float(R[2, 2]) - float(R[0, 0]) - float(R[1, 1]))
        w = (R[1, 0] - R[0, 1]) / s
        x = (R[0, 2] + R[2, 0]) / s
        y = (R[1, 2] + R[2, 1]) / s
        z = 0.25 * s

    q = np.array([x, y, z, w], dtype=np.float32)
    q /= float(np.linalg.norm(q) + 1e-12)
    return q


# ─────────────── Image orientation utilities ───────────────

_ORIENTATION_TO_K = {
    "portrait": 1,            # 90° CCW to upright
    "landscapeLeft": 2,       # 180°
    "portraitUpsideDown": 3,  # 270° CCW
}


def orientation_to_rot90_k(device_orientation: Optional[str]) -> int:
    """Map device orientation string to np.rot90 k value.

    Returns 0 (no rotation) for landscapeRight, unknown, or None.
    """
    return _ORIENTATION_TO_K.get(device_orientation, 0)


def rotate_image(img: NDArray[np.uint8], k: int) -> NDArray[np.uint8]:
    """Rotate image by k*90° CCW. k=0 returns unchanged."""
    if k == 0:
        return img
    return np.rot90(img, k=k).copy()


def unrotate_masks(masks: torch.Tensor, k: int) -> torch.Tensor:
    """Reverse a k*90°-CCW rotation on masks [N,H,W].

    Applies (4-k)*90° CCW = k*90° CW to bring masks back to sensor space.
    """
    import torch

    if k == 0:
        return masks
    return torch.rot90(masks, k=4 - k, dims=[1, 2]).contiguous()


# ─────────────── Gravity-aligned rotation utilities ───────────────

def snap_rotation_to_k(image_rotation_deg: float) -> int:
    """Snap continuous image_rotation (degrees) to the nearest 90° step.

    Ranges (each centered on the target angle, ±45° half-width):
        [-45, 45)       → k=0  (0°, already aligned)
        [45, 135)       → k=1  (+90°, portrait)
        [-135, -45)     → k=3  (-90° / 270° CCW, portrait upside-down)
        [135, 180] ∪ [-180, -135) → k=2  (±180°, landscape-left)

    Args:
        image_rotation_deg: Clockwise degrees to gravity-align the image.

    Returns:
        np.rot90 k value (0–3).
    """
    # Normalize to [-180, 180)
    angle = image_rotation_deg % 360
    if angle >= 180:
        angle -= 360

    if -45 <= angle < 45:
        return 0
    elif 45 <= angle < 135:
        return 1
    elif -135 <= angle < -45:
        return 3
    else:  # [135, 180] or [-180, -135)
        return 2


def resolve_rot90_k(
    image_rotation: Optional[float],
    device_orientation: Optional[str],
) -> int:
    """Determine rot90 k from available rotation info.

    Priority: image_rotation (continuous degrees) > device_orientation (string) > 0.
    """
    if image_rotation is not None:
        return snap_rotation_to_k(image_rotation)
    return orientation_to_rot90_k(device_orientation)


def rotate_depth(depth: NDArray[np.float32], k: int) -> NDArray[np.float32]:
    """Rotate depth map by k*90° CCW. k=0 returns unchanged."""
    if k == 0:
        return depth
    return np.rot90(depth, k=k).copy()


def rotate_intrinsics(
    width: int, height: int,
    fx: float, fy: float, cx: float, cy: float,
    k: int,
) -> tuple[int, int, float, float, float, float]:
    """Adjust pinhole intrinsics for a k*90° CCW rotation (np.rot90 convention).

    After np.rot90(img, k), the pixel grid is reindexed.  The intrinsics
    must be remapped so that back-projection remains consistent.

    Args:
        width, height: Original image dimensions.
        fx, fy, cx, cy: Original pinhole intrinsics.
        k: np.rot90 k value (0–3).

    Returns:
        (new_width, new_height, new_fx, new_fy, new_cx, new_cy)
    """
    if k == 0:
        return width, height, fx, fy, cx, cy

    W, H = width, height
    if k == 1:  # 90° CCW: (x,y) → (y, W-1-x)  →  new image is (H, W)
        return H, W, fy, fx, cy, W - 1 - cx
    elif k == 2:  # 180°: (x,y) → (W-1-x, H-1-y)  →  same dims
        return W, H, fx, fy, W - 1 - cx, H - 1 - cy
    else:  # k == 3, 270° CCW: (x,y) → (H-1-y, x)  →  new image is (H, W)
        return H, W, fy, fx, H - 1 - cy, cx
