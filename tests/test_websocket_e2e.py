"""
End-to-end integration test for the WebSocket receiver.

Starts a real WebSocketReceiver on a test port, connects with the
``websockets`` library, sends a handshake + binary frame, and verifies
that a FramePacket arrives in the IngestQueue.

Requires: ``pip install websockets``
"""

from __future__ import annotations
import asyncio
import json
import struct
import time

import numpy as np
import cv2
import pytest

from rtsm.io.websocket import WebSocketReceiver
from rtsm.io.ingest_queue import IngestQueue

TEST_PORT = 9876


def _build_test_frame() -> bytes:
    """Build a minimal valid binary frame."""
    rgb = np.zeros((48, 64, 3), dtype=np.uint8)
    rgb[10:30, 10:50] = [0, 128, 255]
    _, jpeg_buf = cv2.imencode(".jpg", rgb, [cv2.IMWRITE_JPEG_QUALITY, 80])
    jpeg_bytes = jpeg_buf.tobytes()

    depth_u16 = np.ones((48, 64), dtype=np.uint16) * 1500
    depth_u16[0, 0] = 0
    depth_bytes = depth_u16.tobytes()

    header = {
        "session_id": "e2e-test",
        "frame_id": 1,
        "timestamp_ns": 2000000000,
        "unix_timestamp": 1700000001.0,
        "rgb_format": "jpeg",
        "rgb_width": 64,
        "rgb_height": 48,
        "image_orientation": "landscapeRight",
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
        "tracking_reason": None,
        "pose_source": "arkit_vio",
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


@pytest.fixture(scope="module")
def ws_receiver():
    """Start a WebSocketReceiver on a test port for the module."""
    q = IngestQueue(maxsize=16)
    recv = WebSocketReceiver(
        ingest_queue=q,
        port=TEST_PORT,
        keyframe_every_n=5,
        nonkf_min_interval_s=0.0,
    )
    recv.start()
    time.sleep(1.0)  # let uvicorn bind
    yield recv, q
    recv.stop()


@pytest.mark.asyncio
async def test_handshake_and_one_frame(ws_receiver):
    websockets = pytest.importorskip("websockets")
    recv, q = ws_receiver

    async with websockets.connect(f"ws://127.0.0.1:{TEST_PORT}/stream") as ws:
        # Send hello
        hello = {
            "type": "hello",
            "client": "calabi-lens",
            "protocol_version": 1,
            "session_id": "e2e-test",
            "device_name": "pytest",
        }
        await ws.send(json.dumps(hello))

        # Receive ack
        ack_raw = await ws.recv()
        ack = json.loads(ack_raw)
        assert ack["type"] == "hello_ack"
        assert ack["status"] == "ok"
        assert ack["session_id"] == "e2e-test"

        # Send a binary frame
        frame = _build_test_frame()
        await ws.send(frame)

    # Allow time for async processing
    await asyncio.sleep(0.2)

    # Check queue
    pkt = q.get(timeout=2.0)
    assert pkt is not None, "FramePacket should have been enqueued"
    assert pkt.rgb.shape == (48, 64, 3)
    assert pkt.depth_m is not None
    assert pkt.depth_m.shape == (48, 64)
    np.testing.assert_array_almost_equal(pkt.pose.t_wc, [1.0, 2.0, 3.0])


@pytest.mark.asyncio
async def test_bad_handshake_rejected(ws_receiver):
    websockets = pytest.importorskip("websockets")
    recv, q = ws_receiver

    async with websockets.connect(f"ws://127.0.0.1:{TEST_PORT}/stream") as ws:
        # Send wrong protocol version
        hello = {
            "type": "hello",
            "protocol_version": 99,
            "session_id": "bad-test",
        }
        await ws.send(json.dumps(hello))

        # Should receive error ack
        ack_raw = await ws.recv()
        ack = json.loads(ack_raw)
        assert ack["status"] == "error"

        # Connection should be closed by server
        try:
            await ws.recv()
        except websockets.ConnectionClosed:
            pass  # expected
