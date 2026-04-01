"""
Tests for the record/replay system.

Verifies that:
- SessionRecorder creates correct files on disk
- Binary data roundtrips perfectly through record → read-back
- index.jsonl has valid format
- ReplayReceiver can feed recorded frames into IngestQueue
"""

from __future__ import annotations

import json
import os
import struct
import tempfile

import cv2
import numpy as np
import pytest

from rtsm.io.recorder import SessionRecorder
from rtsm.io.ingest_queue import IngestQueue


def _build_test_frame(frame_id: int = 1) -> bytes:
    """Build a minimal valid binary WebSocket frame."""
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


class TestSessionRecorder:
    def test_creates_files(self, tmp_path):
        """Recorder creates messages.bin, index.jsonl, meta.json."""
        out_dir = str(tmp_path / "rec")
        rec = SessionRecorder(output_dir=out_dir)

        # Feed a few frames
        for i in range(3):
            rec.on_message("binary", _build_test_frame(i))

        rec.on_handshake(
            {"type": "hello", "session_id": "s1", "device_name": "test"},
            {"type": "hello_ack", "status": "ok"},
        )
        rec.close()

        assert os.path.isfile(os.path.join(out_dir, "messages.bin"))
        assert os.path.isfile(os.path.join(out_dir, "index.jsonl"))
        assert os.path.isfile(os.path.join(out_dir, "meta.json"))

        # meta.json should have correct frame count
        with open(os.path.join(out_dir, "meta.json")) as f:
            meta = json.load(f)
        assert meta["total_binary_messages"] == 3
        assert meta["format_version"] == 1
        assert meta["session_id"] == "s1"

    def test_text_messages_file(self, tmp_path):
        """Text messages create text_messages.jsonl."""
        out_dir = str(tmp_path / "rec")
        rec = SessionRecorder(output_dir=out_dir)

        rec.on_message("binary", _build_test_frame(0))
        rec.on_message("text", '{"type": "pose_corrections", "corrections": {}}')
        rec.close()

        txt_path = os.path.join(out_dir, "text_messages.jsonl")
        assert os.path.isfile(txt_path)
        with open(txt_path) as f:
            entry = json.loads(f.readline())
        assert "t_mono_s" in entry
        assert "payload" in entry
        assert entry["after_seq"] == 1  # after the first binary frame

    def test_no_text_file_if_no_text_messages(self, tmp_path):
        """No text_messages.jsonl if no text messages were sent."""
        out_dir = str(tmp_path / "rec")
        rec = SessionRecorder(output_dir=out_dir)
        rec.on_message("binary", _build_test_frame(0))
        rec.close()

        assert not os.path.isfile(os.path.join(out_dir, "text_messages.jsonl"))

    def test_closed_guard(self, tmp_path):
        """Messages after close() are silently dropped."""
        out_dir = str(tmp_path / "rec")
        rec = SessionRecorder(output_dir=out_dir)
        rec.on_message("binary", _build_test_frame(0))
        rec.close()
        # Should not raise or write
        rec.on_message("binary", _build_test_frame(1))
        rec.close()  # double close is safe

        with open(os.path.join(out_dir, "meta.json")) as f:
            meta = json.load(f)
        assert meta["total_binary_messages"] == 1


class TestBinaryRoundtrip:
    def test_exact_bytes(self, tmp_path):
        """Raw bytes written to messages.bin match what was recorded."""
        out_dir = str(tmp_path / "rec")
        rec = SessionRecorder(output_dir=out_dir)

        frames = [_build_test_frame(i) for i in range(5)]
        for frame in frames:
            rec.on_message("binary", frame)
        rec.close()

        # Read back via index
        with open(os.path.join(out_dir, "index.jsonl")) as f:
            entries = [json.loads(line) for line in f if line.strip()]

        assert len(entries) == 5

        with open(os.path.join(out_dir, "messages.bin"), "rb") as f:
            for i, entry in enumerate(entries):
                f.seek(entry["offset"])
                raw = f.read(entry["length"])
                assert raw == frames[i], f"Frame {i} bytes mismatch"


class TestIndexFormat:
    def test_required_keys(self, tmp_path):
        """Each index.jsonl line has seq, offset, length, t_mono_s."""
        out_dir = str(tmp_path / "rec")
        rec = SessionRecorder(output_dir=out_dir)
        for i in range(3):
            rec.on_message("binary", _build_test_frame(i))
        rec.close()

        with open(os.path.join(out_dir, "index.jsonl")) as f:
            for i, line in enumerate(f):
                entry = json.loads(line)
                assert "seq" in entry
                assert "offset" in entry
                assert "length" in entry
                assert "t_mono_s" in entry
                assert entry["seq"] == i

    def test_offsets_are_contiguous(self, tmp_path):
        """Offsets + lengths form a contiguous range in messages.bin."""
        out_dir = str(tmp_path / "rec")
        rec = SessionRecorder(output_dir=out_dir)
        for i in range(4):
            rec.on_message("binary", _build_test_frame(i))
        rec.close()

        with open(os.path.join(out_dir, "index.jsonl")) as f:
            entries = [json.loads(line) for line in f if line.strip()]

        expected_offset = 0
        for entry in entries:
            assert entry["offset"] == expected_offset
            expected_offset += entry["length"]

        # Total should match file size
        bin_size = os.path.getsize(os.path.join(out_dir, "messages.bin"))
        assert expected_offset == bin_size


class TestReplayReceiver:
    def test_enqueues_frames(self, tmp_path):
        """ReplayReceiver feeds recorded frames into IngestQueue."""
        from rtsm.io.replayer import ReplayReceiver

        # First record some frames
        out_dir = str(tmp_path / "rec")
        rec = SessionRecorder(output_dir=out_dir)
        for i in range(3):
            rec.on_message("binary", _build_test_frame(i))
        rec.close()

        # Replay into a queue
        q = IngestQueue(maxsize=16)
        replayer = ReplayReceiver(
            recording_dir=out_dir,
            ingest_queue=q,
            require_tracking_normal=True,
            keyframe_every_n=1,  # every frame is a keyframe (fast test)
            nonkf_min_interval_s=0.0,
            confidence_threshold=0,
            apply_camera_flip=False,
        )
        replayer.start()
        replayer.wait(timeout=30.0)

        # Should have enqueued frames
        assert q.qsize() > 0
        pkt = q.get(timeout=1.0)
        assert pkt is not None
        assert pkt.rgb.shape == (48, 64, 3)
        assert pkt.depth_m is not None
        assert pkt.pose is not None

    def test_missing_recording_raises(self, tmp_path):
        """ReplayReceiver raises FileNotFoundError for bad path."""
        from rtsm.io.replayer import ReplayReceiver

        with pytest.raises(FileNotFoundError):
            ReplayReceiver(
                recording_dir=str(tmp_path / "nonexistent"),
                ingest_queue=IngestQueue(1),
                require_tracking_normal=True,
                keyframe_every_n=30,
                nonkf_min_interval_s=0.5,
                confidence_threshold=1,
                apply_camera_flip=False,
            )
