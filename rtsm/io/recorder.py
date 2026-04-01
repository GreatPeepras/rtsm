"""
Session Recorder — captures raw WebSocket messages to disk for replay.

Recording format (self-contained directory):
    meta.json            session info + handshake + rtsm.yaml snapshot
    messages.bin         concatenated raw binary WebSocket messages
    index.jsonl          one JSON line per binary msg: {seq, offset, length, t_mono_s}
    text_messages.jsonl  pose_corrections etc: {t_mono_s, after_seq, payload}
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)

FORMAT_VERSION = 1


class SessionRecorder:
    """Records raw WebSocket binary/text messages to disk.

    All binary data is flushed after each write so that Ctrl+C never
    loses already-received frames.
    """

    def __init__(
        self,
        output_dir: str,
        config_snapshot: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._output_dir = os.path.abspath(output_dir)
        os.makedirs(self._output_dir, exist_ok=True)

        self._bin_path = os.path.join(self._output_dir, "messages.bin")
        self._idx_path = os.path.join(self._output_dir, "index.jsonl")
        self._txt_path = os.path.join(self._output_dir, "text_messages.jsonl")
        self._meta_path = os.path.join(self._output_dir, "meta.json")

        self._bin_f = open(self._bin_path, "wb")
        self._idx_f = open(self._idx_path, "w", encoding="utf-8")
        self._txt_f: Optional[Any] = None  # opened lazily on first text msg

        self._t0 = time.monotonic()
        self._bin_offset: int = 0
        self._bin_seq: int = 0
        self._config_snapshot = config_snapshot

        self._hello: Optional[Dict] = None
        self._ack: Optional[Dict] = None

        self._closed = False

        logger.info(f"[recorder] Recording to {self._output_dir}")

    # ── Callbacks (called from WebSocket thread) ──

    def on_handshake(self, hello: dict, ack: dict) -> None:
        """Store handshake exchange for meta.json and reset clock."""
        self._hello = hello
        self._ack = ack
        # Reset t0 so t_mono_s=0.0 aligns with session start, not process start
        self._t0 = time.monotonic()

    def on_message(self, msg_type: str, payload: Union[bytes, str]) -> None:
        """Callback compatible with WebSocketReceiver.on_raw_message."""
        if self._closed:
            return

        t_mono = time.monotonic() - self._t0

        if msg_type == "binary" and isinstance(payload, bytes):
            self._bin_f.write(payload)
            self._bin_f.flush()

            idx_entry = {
                "seq": self._bin_seq,
                "offset": self._bin_offset,
                "length": len(payload),
                "t_mono_s": round(t_mono, 6),
            }
            self._idx_f.write(json.dumps(idx_entry) + "\n")
            self._idx_f.flush()

            self._bin_offset += len(payload)
            self._bin_seq += 1

        elif msg_type == "text" and isinstance(payload, str):
            if self._txt_f is None:
                self._txt_f = open(self._txt_path, "w", encoding="utf-8")

            txt_entry = {
                "t_mono_s": round(t_mono, 6),
                "after_seq": self._bin_seq,
                "payload": payload,
            }
            self._txt_f.write(json.dumps(txt_entry) + "\n")
            self._txt_f.flush()

    # ── Shutdown ──

    def close(self) -> None:
        """Flush all files and write meta.json. Safe to call multiple times."""
        if self._closed:
            return
        self._closed = True

        duration = time.monotonic() - self._t0

        # Close data files
        self._bin_f.close()
        self._idx_f.close()
        if self._txt_f is not None:
            self._txt_f.close()

        # Write meta.json
        session_id = (self._hello or {}).get("session_id", "unknown")
        device_name = (self._hello or {}).get("device_name", "unknown")

        meta = {
            "format_version": FORMAT_VERSION,
            "session_id": session_id,
            "device_name": device_name,
            "hello": self._hello,
            "ack": self._ack,
            "total_binary_messages": self._bin_seq,
            "duration_s": round(duration, 3),
            "rtsm_config_snapshot": self._config_snapshot,
        }
        with open(self._meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        logger.info(
            f"[recorder] Recording saved: {self._bin_seq} frames, "
            f"{duration:.1f}s, {self._bin_offset} bytes"
        )
