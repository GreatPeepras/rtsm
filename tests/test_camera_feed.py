"""
Tests for the camera feed broadcast fix.

Verifies that:
- broadcast_camera_frame sends JPEG via broadcaster (with rgb_jpeg)
- broadcast_camera_frame encodes from RGB when rgb_jpeg is absent
- broadcast_camera_frame is a no-op when loop/running not ready
- on_camera_frame callback fires for every decoded frame in ReplayReceiver
- on_camera_frame callback fires for every decoded frame in WebSocketReceiver
- Camera frame broadcast is NOT gated behind is_keyframe
"""

from __future__ import annotations

import asyncio
import json
import os
import struct
import threading
from unittest.mock import AsyncMock, MagicMock, patch

import cv2
import numpy as np
import pytest

from rtsm.io.ingest_queue import IngestQueue
from rtsm.io.recorder import SessionRecorder


# ── Helpers ──


def _build_test_frame(frame_id: int = 1) -> bytes:
    """Build a minimal valid binary WebSocket frame (same format as test_record_replay)."""
    rgb = np.zeros((48, 64, 3), dtype=np.uint8)
    rgb[10:30, 10:50] = [0, 128, 255]
    _, jpeg_buf = cv2.imencode(".jpg", rgb, [cv2.IMWRITE_JPEG_QUALITY, 80])
    jpeg_bytes = jpeg_buf.tobytes()

    depth_u16 = np.ones((48, 64), dtype=np.uint16) * 1500
    depth_bytes = depth_u16.tobytes()

    header = {
        "session_id": "test-session",
        "frame_id": frame_id,
        "timestamp_ns": 2000000000 + frame_id * 33000000,
        "unix_timestamp": 1700000001.0 + frame_id * 0.033,
        "rgb_format": "jpeg",
        "rgb_width": 64,
        "rgb_height": 48,
        "depth_format": "uint16_mm",
        "depth_width": 64,
        "depth_height": 48,
        "depth_scale": 0.001,
        "fx": 50.0,
        "fy": 50.0,
        "cx": 32.0,
        "cy": 24.0,
        "intrinsics_width": 64,
        "intrinsics_height": 48,
        "pose_format": "quat_translation",
        "T_wc": [0.0, 0.0, 0.0, 1.0, 1.0, 2.0, 3.0],
        "tracking_state": "normal",
    }
    json_bytes = json.dumps(header).encode("utf-8")

    msg = b""
    msg += struct.pack("<I", len(json_bytes))
    msg += json_bytes
    msg += struct.pack("<I", len(jpeg_bytes))
    msg += jpeg_bytes
    msg += struct.pack("<I", len(depth_bytes))
    msg += depth_bytes
    return msg


def _make_mock_pkt(with_jpeg: bool = True):
    """Create a mock FramePacket with optional rgb_jpeg."""
    pkt = MagicMock()
    pkt.rgb = np.zeros((48, 64, 3), dtype=np.uint8)
    if with_jpeg:
        _, jpeg_buf = cv2.imencode(".jpg", pkt.rgb)
        pkt.rgb_jpeg = jpeg_buf.tobytes()
    else:
        pkt.rgb_jpeg = None
    return pkt


# ── broadcast_camera_frame unit tests ──


class TestBroadcastCameraFrame:
    """Test VisualizationServer.broadcast_camera_frame logic."""

    def _make_server_stub(self):
        """Create a minimal mock of VisualizationServer with the real method."""
        from rtsm.visualization.server import VisualizationServer
        from rtsm.visualization.broadcaster import WSBroadcaster

        server = MagicMock(spec=VisualizationServer)
        # Use a real broadcaster with a mock send method so schedule() works
        broadcaster = WSBroadcaster()
        broadcaster.send_camera_frame = AsyncMock()
        server.broadcaster = broadcaster

        server._loop = asyncio.new_event_loop()
        server._running = True
        # Set the broadcaster's client loop so schedule() actually dispatches
        broadcaster._client_loop = server._loop

        # Bind the real method to our mock
        server.broadcast_camera_frame = VisualizationServer.broadcast_camera_frame.__get__(
            server, VisualizationServer
        )
        return server

    def test_forwards_jpeg_directly(self):
        """When pkt has rgb_jpeg, it's forwarded without re-encoding."""
        server = self._make_server_stub()
        pkt = _make_mock_pkt(with_jpeg=True)
        jpeg_bytes = pkt.rgb_jpeg

        server.broadcast_camera_frame(pkt)

        # Give the event loop a tick to process the scheduled coroutine
        server._loop.run_until_complete(asyncio.sleep(0.01))
        server.broadcaster.send_camera_frame.assert_called_once_with(jpeg_bytes)
        server._loop.close()

    def test_encodes_rgb_when_no_jpeg(self):
        """When rgb_jpeg is None, encodes from RGB array."""
        server = self._make_server_stub()
        pkt = _make_mock_pkt(with_jpeg=False)

        server.broadcast_camera_frame(pkt)

        server._loop.run_until_complete(asyncio.sleep(0.01))
        server.broadcaster.send_camera_frame.assert_called_once()
        sent_bytes = server.broadcaster.send_camera_frame.call_args[0][0]
        # Should be valid JPEG (starts with FF D8)
        assert sent_bytes[:2] == b"\xff\xd8"
        server._loop.close()

    def test_noop_when_no_client_loop(self):
        """No crash when broadcaster has no client loop (no clients connected)."""
        server = self._make_server_stub()
        server.broadcaster._client_loop = None  # no clients connected yet
        pkt = _make_mock_pkt()

        server.broadcast_camera_frame(pkt)  # schedule() is a no-op, no crash
        # send_camera_frame coroutine is created but schedule() drops it (no loop)
        server._loop.run_until_complete(asyncio.sleep(0.01))
        server._loop.close()

    def test_noop_when_not_running(self):
        """No broadcast when _running is False."""
        server = self._make_server_stub()
        server._running = False
        pkt = _make_mock_pkt()

        server.broadcast_camera_frame(pkt)
        # Give loop a chance (it won't process anything)
        server._loop.run_until_complete(asyncio.sleep(0.01))
        server.broadcaster.send_camera_frame.assert_not_called()
        server._loop.close()

    def test_noop_when_rgb_is_none_and_no_jpeg(self):
        """No crash when both rgb_jpeg and rgb are None."""
        server = self._make_server_stub()
        pkt = MagicMock()
        pkt.rgb_jpeg = None
        pkt.rgb = None

        server.broadcast_camera_frame(pkt)
        server._loop.run_until_complete(asyncio.sleep(0.01))
        server.broadcaster.send_camera_frame.assert_not_called()
        server._loop.close()


# ── on_camera_frame callback wiring in ReplayReceiver ──


class TestReplayerCameraCallback:
    """Verify on_camera_frame fires for every frame, not just keyframes."""

    def _record_frames(self, tmp_path, count: int = 5):
        """Record test frames to a temp directory."""
        out_dir = str(tmp_path / "rec")
        rec = SessionRecorder(output_dir=out_dir)
        for i in range(count):
            rec.on_message("binary", _build_test_frame(i))
        rec.close()
        return out_dir

    def test_callback_fires_for_every_frame(self, tmp_path):
        """on_camera_frame called for every decoded frame (not just KFs)."""
        from rtsm.io.replayer import ReplayReceiver

        out_dir = self._record_frames(tmp_path, count=5)
        q = IngestQueue(maxsize=32)
        camera_frames = []

        replayer = ReplayReceiver(
            recording_dir=out_dir,
            ingest_queue=q,
            require_tracking_normal=True,
            keyframe_every_n=3,  # only every 3rd is KF
            nonkf_min_interval_s=0.0,
            confidence_threshold=0,
            apply_camera_flip=False,
            on_camera_frame=lambda pkt: camera_frames.append(pkt),
        )
        replayer.start()
        replayer.wait(timeout=30.0)

        # All 5 frames should trigger camera callback (not just KFs)
        assert len(camera_frames) == 5

    def test_callback_fires_independently_of_keyframe(self, tmp_path):
        """on_camera_frame fires even for non-keyframes."""
        from rtsm.io.replayer import ReplayReceiver

        out_dir = self._record_frames(tmp_path, count=4)
        q = IngestQueue(maxsize=32)
        camera_frames = []
        keyframes = []

        replayer = ReplayReceiver(
            recording_dir=out_dir,
            ingest_queue=q,
            require_tracking_normal=True,
            keyframe_every_n=4,  # only frame 0 is KF
            nonkf_min_interval_s=0.0,
            confidence_threshold=0,
            apply_camera_flip=False,
            on_keyframe=lambda pkt: keyframes.append(pkt),
            on_camera_frame=lambda pkt: camera_frames.append(pkt),
        )
        replayer.start()
        replayer.wait(timeout=30.0)

        # camera_frames should have more entries than keyframes
        assert len(camera_frames) > len(keyframes)
        assert len(keyframes) >= 1  # at least first frame is KF

    def test_none_callback_is_safe(self, tmp_path):
        """on_camera_frame=None doesn't crash."""
        from rtsm.io.replayer import ReplayReceiver

        out_dir = self._record_frames(tmp_path, count=2)
        q = IngestQueue(maxsize=16)

        replayer = ReplayReceiver(
            recording_dir=out_dir,
            ingest_queue=q,
            require_tracking_normal=True,
            keyframe_every_n=1,
            nonkf_min_interval_s=0.0,
            confidence_threshold=0,
            apply_camera_flip=False,
            on_camera_frame=None,
        )
        replayer.start()
        replayer.wait(timeout=30.0)

        assert q.qsize() > 0  # frames still enqueued


# ── WebSocket receiver on_camera_frame parameter acceptance ──


class TestWebSocketReceiverCameraParam:
    """Verify WebSocketReceiver accepts on_camera_frame parameter."""

    def test_accepts_on_camera_frame_param(self):
        """WebSocketReceiver.__init__ accepts on_camera_frame without error."""
        from rtsm.io.websocket import WebSocketReceiver

        cb = MagicMock()
        q = IngestQueue(maxsize=4)
        ws = WebSocketReceiver(
            ingest_queue=q,
            on_camera_frame=cb,
            keyframe_every_n=5,
            nonkf_min_interval_s=0.0,
        )
        assert ws._on_camera_frame is cb

    def test_none_camera_frame_param(self):
        """on_camera_frame=None is the default and works."""
        from rtsm.io.websocket import WebSocketReceiver

        q = IngestQueue(maxsize=4)
        ws = WebSocketReceiver(
            ingest_queue=q,
            keyframe_every_n=5,
            nonkf_min_interval_s=0.0,
        )
        assert ws._on_camera_frame is None
