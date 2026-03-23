"""Tests for image_rotation snapping, intrinsics rotation, and depth/RGB coherence."""

import numpy as np
import pytest

from rtsm.utils.transforms import (
    snap_rotation_to_k,
    resolve_rot90_k,
    rotate_depth,
    rotate_image,
    rotate_intrinsics,
)


# ── snap_rotation_to_k ──────────────────────────────────────────────

class TestSnapRotationToK:
    """Verify snapping of continuous degrees → rot90 k."""

    @pytest.mark.parametrize("deg, expected_k", [
        # Exact cardinal angles
        (0.0, 0),
        (90.0, 1),
        (-90.0, 3),
        (180.0, 2),
        (-180.0, 2),
        # Just inside boundaries
        (44.9, 0),
        (45.0, 1),
        (-44.9, 0),
        (-45.0, 0),   # boundary: [-45, 45) includes -45
        (-45.1, 3),   # just past boundary into [-135, -45)
        (134.9, 1),
        (135.0, 2),
        (-134.9, 3),
        (-135.0, 3),  # boundary: [-135, -45) includes -135
        (-135.1, 2),  # just past boundary into ±180 bin
        # Slightly tilted real-world values
        (87.3, 1),
        (92.1, 1),
        (-88.0, 3),
        (178.0, 2),
        (-179.0, 2),
        (3.5, 0),
        (-2.0, 0),
    ])
    def test_snap(self, deg: float, expected_k: int):
        assert snap_rotation_to_k(deg) == expected_k

    def test_wrapping_360(self):
        """Values outside [-180, 180] should normalize correctly."""
        assert snap_rotation_to_k(270.0) == 3   # 270 → -90
        assert snap_rotation_to_k(360.0) == 0   # 360 → 0
        assert snap_rotation_to_k(-270.0) == 1  # -270 → +90


# ── resolve_rot90_k ─────────────────────────────────────────────────

class TestResolveRot90K:
    """Verify priority chain: image_rotation > device_orientation > 0."""

    def test_image_rotation_wins(self):
        # image_rotation=90° → k=1 even if device_orientation says something else
        assert resolve_rot90_k(90.0, "landscapeLeft") == 1

    def test_fallback_to_device_orientation(self):
        assert resolve_rot90_k(None, "portrait") == 1
        assert resolve_rot90_k(None, "landscapeLeft") == 2
        assert resolve_rot90_k(None, "portraitUpsideDown") == 3
        assert resolve_rot90_k(None, "landscapeRight") == 0

    def test_both_none(self):
        assert resolve_rot90_k(None, None) == 0

    def test_unknown_orientation_defaults_zero(self):
        assert resolve_rot90_k(None, "unknownValue") == 0


# ── rotate_intrinsics ───────────────────────────────────────────────

class TestRotateIntrinsics:
    """Verify intrinsics remapping for each k value."""

    W, H = 1920, 1440
    FX, FY, CX, CY = 1000.0, 800.0, 960.0, 720.0

    def test_k0_noop(self):
        result = rotate_intrinsics(self.W, self.H, self.FX, self.FY, self.CX, self.CY, 0)
        assert result == (self.W, self.H, self.FX, self.FY, self.CX, self.CY)

    def test_k1_90_ccw(self):
        nw, nh, nfx, nfy, ncx, ncy = rotate_intrinsics(
            self.W, self.H, self.FX, self.FY, self.CX, self.CY, 1,
        )
        assert (nw, nh) == (self.H, self.W)       # dims swap
        assert nfx == self.FY                       # fx' = fy
        assert nfy == self.FX                       # fy' = fx
        assert ncx == self.CY                       # cx' = cy
        assert ncy == self.W - 1 - self.CX          # cy' = W-1-cx

    def test_k2_180(self):
        nw, nh, nfx, nfy, ncx, ncy = rotate_intrinsics(
            self.W, self.H, self.FX, self.FY, self.CX, self.CY, 2,
        )
        assert (nw, nh) == (self.W, self.H)        # dims unchanged
        assert nfx == self.FX
        assert nfy == self.FY
        assert ncx == self.W - 1 - self.CX
        assert ncy == self.H - 1 - self.CY

    def test_k3_270_ccw(self):
        nw, nh, nfx, nfy, ncx, ncy = rotate_intrinsics(
            self.W, self.H, self.FX, self.FY, self.CX, self.CY, 3,
        )
        assert (nw, nh) == (self.H, self.W)        # dims swap
        assert nfx == self.FY
        assert nfy == self.FX
        assert ncx == self.H - 1 - self.CY
        assert ncy == self.CX


# ── depth / RGB coherence ───────────────────────────────────────────

class TestDepthRGBCoherence:
    """Rotating RGB and depth with the same k keeps pixel correspondence."""

    def _make_test_data(self):
        """4×6 RGB and depth where depth[r,c] = r*10 + c."""
        H, W = 4, 6
        depth = np.arange(H * W, dtype=np.float32).reshape(H, W)
        # RGB: encode row in R, col in G (B=0)
        rgb = np.zeros((H, W, 3), dtype=np.uint8)
        for r in range(H):
            for c in range(W):
                rgb[r, c, 0] = r
                rgb[r, c, 1] = c
        return rgb, depth

    @pytest.mark.parametrize("k", [0, 1, 2, 3])
    def test_coherence(self, k: int):
        rgb, depth = self._make_test_data()
        r_rgb = rotate_image(rgb, k)
        r_depth = rotate_depth(depth, k)

        assert r_rgb.shape[:2] == r_depth.shape

        # For every pixel in rotated images, the encoded (row, col) in RGB
        # should correspond to the same original position as depth
        H, W = r_depth.shape
        for r in range(H):
            for c in range(W):
                orig_r = int(r_rgb[r, c, 0])
                orig_c = int(r_rgb[r, c, 1])
                assert r_depth[r, c] == pytest.approx(orig_r * 6 + orig_c), (
                    f"k={k} pixel ({r},{c}): RGB says orig=({orig_r},{orig_c}), "
                    f"depth={r_depth[r, c]}, expected={orig_r * 6 + orig_c}"
                )
