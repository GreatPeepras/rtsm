"""
Unit tests for demo-related components.

Tests cover:
- Demo clip extraction functions
- FramePacket rgb_jpeg field
- Broadcaster camera_frame pack/unpack
- Broadcaster concurrent broadcast
- Config loader (cfg_path, load_config)
"""

from __future__ import annotations

import asyncio
import json
import os
import struct
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import cv2
import numpy as np
import pytest

# ── Demo clip extraction tests ──


class TestExtractDemoClip:
    """Tests for scripts/extract_demo_clip.py functions."""

    def _make_nv12_frame(self, width: int = 64, height: int = 48) -> tuple:
        """Create a synthetic NV12-encoded binary frame."""
        # Create a simple BGR image
        bgr = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)

        # Convert BGR -> YUV NV12
        yuv = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV_I420)
        # I420 has Y plane (H*W) + U plane (H/2 * W/2) + V plane (H/2 * W/2)
        # NV12 has Y plane (H*W) + interleaved UV plane (H/2 * W)
        y_plane = yuv[:height, :]
        u_plane = yuv[height : height + height // 4, :].reshape(height // 2, width // 2)
        v_plane = yuv[height + height // 4 :, :].reshape(height // 2, width // 2)
        uv_interleaved = np.empty((height // 2, width), dtype=np.uint8)
        uv_interleaved[:, 0::2] = u_plane
        uv_interleaved[:, 1::2] = v_plane
        nv12_bytes = np.concatenate([y_plane.flatten(), uv_interleaved.flatten()]).tobytes()

        # Build header
        header = {
            "rgb_format": "nv12",
            "rgb_width": width,
            "rgb_height": height,
            "depth_format": "uint16_mm",
            "depth_width": width,
            "depth_height": height,
            "T_wc": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            "tracking_state": "normal",
            "pose_format": "matrix4x4_col_major",
        }
        header_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")

        # Depth: random uint16
        depth_bytes = np.random.randint(100, 3000, (height, width), dtype=np.uint16).tobytes()

        # Confidence: all high
        conf_bytes = np.full((height, width), 2, dtype=np.uint8).tobytes()

        # Assemble frame
        frame = b"".join([
            struct.pack("<I", len(header_bytes)),
            header_bytes,
            struct.pack("<I", len(nv12_bytes)),
            nv12_bytes,
            struct.pack("<I", len(depth_bytes)),
            depth_bytes,
            struct.pack("<I", len(conf_bytes)),
            conf_bytes,
        ])

        return frame, header, depth_bytes, conf_bytes

    def test_extract_frame_nv12_to_jpeg(self):
        """NV12 frame transcoded to valid JPEG."""
        from scripts.extract_demo_clip import parse_frame, transcode_rgb_to_jpeg

        frame, header, _, _ = self._make_nv12_frame(64, 48)
        parsed = parse_frame(frame)

        assert parsed["header"]["rgb_format"] == "nv12"

        jpeg_bytes = transcode_rgb_to_jpeg(
            parsed["rgb_bytes"], "nv12", 64, 48, quality=85
        )

        # Verify it's valid JPEG (starts with FFD8)
        assert jpeg_bytes[:2] == b"\xff\xd8"

        # Verify it decodes
        buf = np.frombuffer(jpeg_bytes, dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        assert img is not None
        assert img.shape == (48, 64, 3)

    def test_extract_preserves_depth(self):
        """Depth payload unchanged after extraction."""
        from scripts.extract_demo_clip import parse_frame, reassemble_frame, transcode_rgb_to_jpeg

        frame, header, original_depth, original_conf = self._make_nv12_frame(64, 48)
        parsed = parse_frame(frame)

        # Depth bytes should be identical
        assert parsed["depth_bytes"] == original_depth

        # After reassembly, depth should still be identical
        jpeg = transcode_rgb_to_jpeg(parsed["rgb_bytes"], "nv12", 64, 48)
        parsed["header"]["rgb_format"] = "jpeg"
        new_frame = reassemble_frame(
            parsed["header"], jpeg, parsed["depth_bytes"], parsed["conf_bytes"]
        )
        reparsed = parse_frame(new_frame)
        assert reparsed["depth_bytes"] == original_depth

    def test_extract_rezeros_timestamps(self):
        """Extract script re-zeros timestamps."""
        from scripts.extract_demo_clip import extract_demo_clip

        # Create a minimal recording with 3 frames
        with tempfile.TemporaryDirectory() as tmpdir:
            in_dir = os.path.join(tmpdir, "input")
            out_dir = os.path.join(tmpdir, "output")
            os.makedirs(in_dir)

            frames = []
            for i in range(3):
                frame, _, _, _ = self._make_nv12_frame(64, 48)
                frames.append(frame)

            # Write messages.bin
            with open(os.path.join(in_dir, "messages.bin"), "wb") as f:
                offset = 0
                entries = []
                for i, frame in enumerate(frames):
                    f.write(frame)
                    entries.append({
                        "seq": i,
                        "offset": offset,
                        "length": len(frame),
                        "t_mono_s": 100.0 + i * 0.5,  # Non-zero start
                    })
                    offset += len(frame)

            # Write index.jsonl
            with open(os.path.join(in_dir, "index.jsonl"), "w") as f:
                for e in entries:
                    f.write(json.dumps(e) + "\n")

            # Write meta.json
            with open(os.path.join(in_dir, "meta.json"), "w") as f:
                json.dump({"format_version": 1, "total_binary_messages": 3}, f)

            # Extract
            stats = extract_demo_clip(in_dir, out_dir, num_frames=3)

            # Verify re-zeroed timestamps
            with open(os.path.join(out_dir, "index.jsonl")) as f:
                out_entries = [json.loads(l) for l in f if l.strip()]

            assert out_entries[0]["t_mono_s"] == 0.0
            assert out_entries[1]["t_mono_s"] == pytest.approx(0.5)
            assert out_entries[2]["t_mono_s"] == pytest.approx(1.0)

    def test_extract_index_offsets_contiguous(self):
        """Offsets in output index are contiguous."""
        from scripts.extract_demo_clip import extract_demo_clip

        with tempfile.TemporaryDirectory() as tmpdir:
            in_dir = os.path.join(tmpdir, "input")
            out_dir = os.path.join(tmpdir, "output")
            os.makedirs(in_dir)

            frames = []
            for i in range(3):
                frame, _, _, _ = self._make_nv12_frame(64, 48)
                frames.append(frame)

            with open(os.path.join(in_dir, "messages.bin"), "wb") as f:
                offset = 0
                entries = []
                for i, frame in enumerate(frames):
                    f.write(frame)
                    entries.append({"seq": i, "offset": offset, "length": len(frame), "t_mono_s": float(i)})
                    offset += len(frame)

            with open(os.path.join(in_dir, "index.jsonl"), "w") as f:
                for e in entries:
                    f.write(json.dumps(e) + "\n")
            with open(os.path.join(in_dir, "meta.json"), "w") as f:
                json.dump({"format_version": 1}, f)

            extract_demo_clip(in_dir, out_dir, num_frames=3)

            with open(os.path.join(out_dir, "index.jsonl")) as f:
                out_entries = [json.loads(l) for l in f if l.strip()]

            for i in range(1, len(out_entries)):
                expected = out_entries[i - 1]["offset"] + out_entries[i - 1]["length"]
                assert out_entries[i]["offset"] == expected, f"Gap at frame {i}"


# ── FramePacket rgb_jpeg tests ──


class TestFramePacketRgbJpeg:
    def test_rgb_jpeg_default_none(self):
        """FramePacket rgb_jpeg defaults to None."""
        from rtsm.core.datamodel import FramePacket, TimeBundle

        pkt = FramePacket(
            time=TimeBundle(t_mono_s=0, t_wall_utc_s=0, t_sensor_ns=0),
            rgb=np.zeros((48, 64, 3), dtype=np.uint8),
            depth_m=None,
            pose=None,
            intr=None,
        )
        assert pkt.rgb_jpeg is None

    def test_rgb_jpeg_can_be_set(self):
        """FramePacket rgb_jpeg can hold bytes."""
        from rtsm.core.datamodel import FramePacket, TimeBundle

        fake_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        pkt = FramePacket(
            time=TimeBundle(t_mono_s=0, t_wall_utc_s=0, t_sensor_ns=0),
            rgb=np.zeros((48, 64, 3), dtype=np.uint8),
            depth_m=None,
            pose=None,
            intr=None,
            rgb_jpeg=fake_jpeg,
        )
        assert pkt.rgb_jpeg == fake_jpeg


# ── Broadcaster camera_frame tests ──


class TestBroadcasterCameraFrame:
    def test_pack_camera_frame_magic(self):
        """Magic bytes are 'CAMF'."""
        from rtsm.visualization.broadcaster import WSBroadcaster

        data = WSBroadcaster.pack_camera_frame(b"\xff\xd8test")
        assert data[:4] == b"CAMF"

    def test_pack_camera_frame_length(self):
        """Length field matches JPEG data."""
        from rtsm.visualization.broadcaster import WSBroadcaster

        jpeg = b"\xff\xd8" + b"\x00" * 100
        data = WSBroadcaster.pack_camera_frame(jpeg)
        length = struct.unpack_from("<I", data, 4)[0]
        assert length == len(jpeg)

    def test_pack_camera_frame_roundtrip(self):
        """Pack then unpack yields original JPEG."""
        from rtsm.visualization.broadcaster import WSBroadcaster

        jpeg = b"\xff\xd8" + os.urandom(200)
        packed = WSBroadcaster.pack_camera_frame(jpeg)
        unpacked = WSBroadcaster.unpack_camera_frame(packed)
        assert unpacked == jpeg

    def test_unpack_invalid_magic_returns_none(self):
        """Invalid magic returns None."""
        from rtsm.visualization.broadcaster import WSBroadcaster

        bad_data = b"XXXX" + struct.pack("<I", 10) + b"\x00" * 10
        assert WSBroadcaster.unpack_camera_frame(bad_data) is None

    def test_unpack_truncated_returns_none(self):
        """Truncated data returns None."""
        from rtsm.visualization.broadcaster import WSBroadcaster

        assert WSBroadcaster.unpack_camera_frame(b"CAM") is None


# ── Broadcaster concurrent broadcast tests ──


class TestBroadcasterConcurrency:
    @pytest.fixture
    def broadcaster(self):
        from rtsm.visualization.broadcaster import WSBroadcaster
        return WSBroadcaster()

    def _make_mock_ws(self, delay: float = 0.0, fail: bool = False):
        """Create a mock WebSocket client."""
        ws = AsyncMock()
        if fail:
            ws.send_bytes.side_effect = ConnectionError("disconnected")
            ws.send_json.side_effect = ConnectionError("disconnected")
        elif delay > 0:
            async def slow_send(*args, **kwargs):
                await asyncio.sleep(delay)
            ws.send_bytes.side_effect = slow_send
            ws.send_json.side_effect = slow_send
        return ws

    @pytest.mark.asyncio
    async def test_broadcast_delivers_to_all(self, broadcaster):
        """All clients receive the message."""
        c1 = self._make_mock_ws()
        c2 = self._make_mock_ws()
        await broadcaster.connect(c1)
        await broadcaster.connect(c2)

        await broadcaster._broadcast_bytes(b"hello")
        c1.send_bytes.assert_called_once_with(b"hello")
        c2.send_bytes.assert_called_once_with(b"hello")

    @pytest.mark.asyncio
    async def test_broadcast_dead_client_removed(self, broadcaster):
        """Failed client is removed from set."""
        good = self._make_mock_ws()
        bad = self._make_mock_ws(fail=True)
        await broadcaster.connect(good)
        await broadcaster.connect(bad)

        assert broadcaster.client_count == 2
        await broadcaster._broadcast_bytes(b"test")
        assert broadcaster.client_count == 1

    @pytest.mark.asyncio
    async def test_camera_frame_broadcast(self, broadcaster):
        """send_camera_frame packs and sends to all clients."""
        c1 = self._make_mock_ws()
        await broadcaster.connect(c1)

        jpeg = b"\xff\xd8test"
        await broadcaster.send_camera_frame(jpeg)
        c1.send_bytes.assert_called_once()

        # Verify the packed data starts with CAMF
        sent_data = c1.send_bytes.call_args[0][0]
        assert sent_data[:4] == b"CAMF"


# ── Config loader tests ──


class TestConfigLoader:
    def test_cfg_path_finds_package_config(self):
        """cfg_path resolves rtsm.yaml."""
        from rtsm.cfg import cfg_path
        path = cfg_path("rtsm.yaml")
        assert path.is_file()
        assert path.name == "rtsm.yaml"

    def test_cfg_path_finds_vocab(self):
        """cfg_path resolves clip/vocab.yaml."""
        from rtsm.cfg import cfg_path
        path = cfg_path("clip/vocab.yaml")
        assert path.is_file()

    def test_load_config_valid_yaml(self):
        """load_config returns dict with expected keys."""
        from rtsm.cfg import load_config
        cfg = load_config("rtsm.yaml")
        assert isinstance(cfg, dict)
        assert "segmentation" in cfg
        assert "api" in cfg
        assert "visualization" in cfg

    def test_demo_config_grounded_sam2(self):
        """Demo config uses grounded_sam2 backend."""
        from rtsm.cfg import load_config
        cfg = load_config("demo_config.yaml")
        assert cfg["segmentation"]["backend"] == "grounded_sam2"

    def test_demo_config_speed_params(self):
        """Demo config has speed-tuned params."""
        from rtsm.cfg import load_config
        cfg = load_config("demo_config.yaml")
        assert cfg["staging"]["topk_preclip"] < 15
        assert cfg["visualization"]["tsdf"]["enable"] is False
        assert cfg["mcp"]["enable"] is False

    def test_cfg_path_missing_raises(self):
        """cfg_path raises for nonexistent file."""
        from rtsm.cfg import cfg_path
        with pytest.raises(FileNotFoundError):
            cfg_path("nonexistent_config_file.yaml")
