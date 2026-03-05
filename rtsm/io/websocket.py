"""
WebSocket Receiver for RTSM — Calabi Lens ARKit Client Integration.

Accepts binary frames over ws://host:port/stream from the Calabi Lens iOS app.
Each frame contains bundled RGB + depth + pose + intrinsics.

Protocol:
1. Client connects to /stream
2. Client sends JSON text hello: {"type": "hello", "protocol_version": 1, ...}
3. Server replies with JSON text ack: {"type": "hello_ack", "status": "ok", ...}
4. Client streams binary frames (length-prefixed: [json][rgb][depth])
"""

from __future__ import annotations
import asyncio
import json
import struct
import time
import threading
import logging
from typing import Optional, Tuple

import numpy as np
import cv2

from rtsm.core.datamodel import (
    FramePacket, TimeBundle, PoseStamped, PinholeIntrinsics,
)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from rtsm.io.ingest_queue import IngestQueue
from rtsm.utils.transforms import rotmat_to_quat_xyzw

logger = logging.getLogger(__name__)

# Current handshake protocol version
PROTOCOL_VERSION = 1

# Supported format values
_RGB_FORMATS = {"jpeg", "png", "bgra"}
_DEPTH_FORMATS = {"uint16_mm", "float32_m", "png_uint16"}
_POSE_FORMATS = {"matrix4x4_col_major", "quat_translation"}


# ─────────────────── Data Conversion Functions ───────────────────


def decode_rgb(raw: bytes, fmt: str, width: int, height: int) -> np.ndarray:
    """
    Decode RGB bytes into (H, W, 3) uint8 BGR array (OpenCV convention).

    Args:
        raw: Raw byte payload.
        fmt: ``"jpeg"`` | ``"png"`` | ``"bgra"``.
        width, height: Expected image dimensions.

    Returns:
        (H, W, 3) uint8 BGR array.

    Raises:
        ValueError: On unsupported format or decode failure.
    """
    if fmt in ("jpeg", "png"):
        buf = np.frombuffer(raw, dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"cv2.imdecode failed for {fmt} ({len(raw)} bytes)")
        return img
    elif fmt == "bgra":
        expected = height * width * 4
        if len(raw) != expected:
            raise ValueError(
                f"bgra buffer size mismatch: got {len(raw)}, "
                f"expected {expected} ({width}x{height}x4)"
            )
        img = np.frombuffer(raw, dtype=np.uint8).reshape(height, width, 4)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    else:
        raise ValueError(f"Unsupported rgb_format: {fmt!r}")


def decode_depth(
    raw: bytes,
    fmt: Optional[str],
    width: int,
    height: int,
    depth_scale: Optional[float] = None,
) -> Optional[np.ndarray]:
    """
    Decode depth bytes into (H, W) float32 meters with NaN for invalid pixels.

    Wire convention: 0 = invalid.  After this function: NaN = invalid.

    Args:
        raw: Raw byte payload (may be empty if no depth).
        fmt: ``"uint16_mm"`` | ``"float32_m"`` | ``"png_uint16"`` | ``None``.
        width, height: Expected depth dimensions.
        depth_scale: Scale factor (0.001 for mm→m).  Used for uint16 formats.

    Returns:
        (H, W) float32 array in meters (NaN = invalid), or ``None``.
    """
    if fmt is None or len(raw) == 0:
        return None

    if depth_scale is None:
        depth_scale = 0.001  # default: millimeters

    if fmt == "uint16_mm":
        depth_u16 = np.frombuffer(raw, dtype=np.uint16).reshape(height, width)
        depth_m = depth_u16.astype(np.float32) * depth_scale
        depth_m[depth_u16 == 0] = np.nan
        return depth_m

    elif fmt == "float32_m":
        depth_m = np.frombuffer(raw, dtype=np.float32).reshape(height, width).copy()
        depth_m[depth_m == 0.0] = np.nan
        return depth_m

    elif fmt == "png_uint16":
        buf = np.frombuffer(raw, dtype=np.uint8)
        depth_u16 = cv2.imdecode(buf, cv2.IMREAD_UNCHANGED)
        if depth_u16 is None:
            logger.warning("[websocket] failed to decode PNG depth")
            return None
        depth_m = depth_u16.astype(np.float32) * depth_scale
        depth_m[depth_u16 == 0] = np.nan
        return depth_m

    else:
        logger.warning(f"[websocket] unsupported depth_format: {fmt!r}")
        return None


def parse_arkit_pose(
    T_wc_data: list,
    pose_format: str,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Parse ARKit pose into canonical (t_wc, q_xyzw) format.

    Args:
        T_wc_data: 16 floats (col-major 4×4) or 7 floats [qx, qy, qz, qw, tx, ty, tz].
        pose_format: ``"matrix4x4_col_major"`` | ``"quat_translation"``.

    Returns:
        ``(t_wc, q_xyzw)`` — both ``np.float32`` arrays, shapes (3,) and (4,).

    Raises:
        ValueError: On unsupported format or wrong element count.
    """
    if pose_format == "quat_translation":
        if len(T_wc_data) != 7:
            raise ValueError(
                f"quat_translation expects 7 elements, got {len(T_wc_data)}"
            )
        qx, qy, qz, qw, tx, ty, tz = (float(v) for v in T_wc_data)
        t_wc = np.array([tx, ty, tz], dtype=np.float32)
        q_xyzw = np.array([qx, qy, qz, qw], dtype=np.float32)
        return t_wc, q_xyzw

    elif pose_format == "matrix4x4_col_major":
        if len(T_wc_data) != 16:
            raise ValueError(
                f"matrix4x4_col_major expects 16 elements, got {len(T_wc_data)}"
            )
        # Column-major → numpy array with Fortran order
        mat = np.array(T_wc_data, dtype=np.float64).reshape(4, 4, order="F")
        t_wc = mat[:3, 3].astype(np.float32)
        R = mat[:3, :3].astype(np.float32)
        q_xyzw = rotmat_to_quat_xyzw(R)
        return t_wc, q_xyzw

    else:
        raise ValueError(f"Unsupported pose_format: {pose_format!r}")


# ─────────────────── WebSocket Receiver Class ───────────────────


class WebSocketReceiver:
    """
    WebSocket receiver for Calabi Lens ARKit iOS client.

    Accepts binary frames over ``ws://host:port/stream``, decodes them,
    and enqueues canonical ``FramePacket`` objects to the ingest queue.
    """

    def __init__(
        self,
        ingest_queue: IngestQueue,
        *,
        host: str = "0.0.0.0",
        port: int = 8765,
        require_tracking_normal: bool = True,
        keyframe_every_n: int = 30,
        nonkf_min_interval_s: float = 0.5,
    ) -> None:
        self.ingest_q = ingest_queue
        self._host = host
        self._port = port
        self._require_tracking_normal = require_tracking_normal
        self._keyframe_every_n = max(1, keyframe_every_n)
        self._nonkf_min_interval_s = nonkf_min_interval_s

        # Per-session state (reset on each new client connection)
        self._frame_count: int = 0
        self._last_nonkf_enq_mono: float = 0.0
        self._last_enq_ts_ns: Optional[int] = None
        self._active_session_id: Optional[str] = None

        # Threading
        self._server_thread: Optional[threading.Thread] = None
        self._shutdown_event = asyncio.Event()

    # ── FastAPI app creation ──

    def _create_app(self):
        app = FastAPI(title="RTSM WebSocket Receiver")

        @app.get("/health")
        def health():
            return JSONResponse({"status": "ok", "receiver": "websocket"})

        @app.websocket("/stream")
        async def stream_endpoint(ws: WebSocket):
            await self._handle_stream(ws)

        return app

    # ── Handshake + receive loop ──

    async def _handle_stream(self, ws) -> None:
        await ws.accept()
        client_addr = ws.client.host if ws.client else "unknown"
        logger.info(f"[websocket] Client connected from {client_addr}")

        # ── Handshake: wait for hello ──
        try:
            hello_raw = await asyncio.wait_for(ws.receive_text(), timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning(f"[websocket] Handshake timeout from {client_addr}")
            await ws.close(code=4002, reason="handshake timeout")
            return
        except Exception:
            logger.warning(f"[websocket] Connection lost during handshake from {client_addr}")
            return

        try:
            hello = json.loads(hello_raw)
        except json.JSONDecodeError:
            await ws.close(code=4001, reason="invalid hello JSON")
            return

        if hello.get("type") != "hello":
            await ws.close(code=4001, reason="expected hello message")
            return

        proto_ver = hello.get("protocol_version", 0)
        if proto_ver != PROTOCOL_VERSION:
            ack = {
                "type": "hello_ack",
                "status": "error",
                "reason": f"unsupported protocol_version: {proto_ver}",
            }
            await ws.send_json(ack)
            await ws.close(code=4001, reason=ack["reason"])
            return

        session_id = hello.get("session_id", "unknown")
        device_name = hello.get("device_name", "unknown")
        self._active_session_id = session_id

        ack = {
            "type": "hello_ack",
            "status": "ok",
            "protocol_version": PROTOCOL_VERSION,
            "server": "rtsm",
            "session_id": session_id,
        }
        await ws.send_json(ack)
        logger.info(
            f"[websocket] Handshake OK: session={session_id}, device={device_name}"
        )

        # Reset per-session state
        self._frame_count = 0
        self._last_nonkf_enq_mono = 0.0
        self._last_enq_ts_ns = None
        frames_received = 0
        frames_enqueued = 0
        t_start = time.monotonic()

        # ── Binary receive loop ──
        try:
            while True:
                data = await ws.receive_bytes()
                frames_received += 1
                try:
                    pkt = self._parse_binary_message(data)
                    if pkt is not None:
                        ok = self.ingest_q.put(pkt, block=False)
                        if ok:
                            frames_enqueued += 1
                            self._last_enq_ts_ns = pkt.time.t_sensor_ns
                            if not pkt.is_keyframe:
                                self._last_nonkf_enq_mono = time.monotonic()
                            frame_type = "KF" if pkt.is_keyframe else "frame"
                            logger.debug(
                                f"[websocket] enqueued {frame_type} "
                                f"-> queue={self.ingest_q.qsize()}"
                            )
                        else:
                            logger.warning(
                                "[websocket] ingest queue full; dropping frame"
                            )
                except Exception as e:
                    logger.error(f"[websocket] frame parse error: {e}")
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"[websocket] connection error: {e}")
        finally:
            elapsed = time.monotonic() - t_start
            logger.info(
                f"[websocket] Session {session_id} ended: "
                f"{frames_received} received, {frames_enqueued} enqueued, "
                f"{elapsed:.1f}s duration"
            )
            self._active_session_id = None

    # ── Binary message parsing ──

    def _parse_binary_message(self, data: bytes) -> Optional[FramePacket]:
        """Parse a single binary WebSocket message into a FramePacket."""
        offset = 0
        n = len(data)

        # 1. JSON header
        if n < 4:
            logger.warning("[websocket] message too short for json_len")
            return None
        (json_len,) = struct.unpack_from("<I", data, offset)
        offset += 4
        if n < offset + json_len:
            logger.warning("[websocket] message truncated at JSON payload")
            return None
        header = json.loads(data[offset : offset + json_len].decode("utf-8"))
        offset += json_len

        # 2. RGB payload
        if n < offset + 4:
            logger.warning("[websocket] message truncated at rgb_len")
            return None
        (rgb_len,) = struct.unpack_from("<I", data, offset)
        offset += 4
        if n < offset + rgb_len:
            logger.warning("[websocket] message truncated at RGB payload")
            return None
        rgb_bytes = data[offset : offset + rgb_len]
        offset += rgb_len

        # 3. Depth payload
        if n < offset + 4:
            logger.warning("[websocket] message truncated at depth_len")
            return None
        (depth_len,) = struct.unpack_from("<I", data, offset)
        offset += 4
        if n < offset + depth_len:
            logger.warning("[websocket] message truncated at depth payload")
            return None
        depth_bytes = data[offset : offset + depth_len]

        # 4. Tracking state filter
        tracking_state = header.get("tracking_state", "not_available")
        if self._require_tracking_normal and tracking_state != "normal":
            logger.debug(
                f"[websocket] dropping frame: tracking_state={tracking_state}"
            )
            return None

        self._frame_count += 1

        # 5. Keyframe decision
        is_keyframe = (
            self._frame_count == 1
            or self._frame_count % self._keyframe_every_n == 0
        )

        # 6. Non-KF throttle
        if not is_keyframe:
            now_mono = time.monotonic()
            if (now_mono - self._last_nonkf_enq_mono) < self._nonkf_min_interval_s:
                return None

        # 7. Decode RGB
        rgb_fmt = header.get("rgb_format", "jpeg")
        rgb_w = int(header.get("rgb_width", 0))
        rgb_h = int(header.get("rgb_height", 0))
        rgb = decode_rgb(rgb_bytes, fmt=rgb_fmt, width=rgb_w, height=rgb_h)

        # 8. Decode depth (native resolution, NaN for invalid)
        depth_fmt = header.get("depth_format")
        depth_w = int(header.get("depth_width", 0) or 0)
        depth_h = int(header.get("depth_height", 0) or 0)
        depth_scale = float(header.get("depth_scale", 0.001) or 0.001)
        depth_m = decode_depth(
            depth_bytes, fmt=depth_fmt, width=depth_w, height=depth_h,
            depth_scale=depth_scale,
        )

        # 9. Parse pose
        t_wc, q_xyzw = parse_arkit_pose(
            T_wc_data=header["T_wc"],
            pose_format=header.get("pose_format", "matrix4x4_col_major"),
        )

        # 10. Build intrinsics (scale if intrinsics resolution differs from RGB)
        intr_w = int(header.get("intrinsics_width", rgb_w))
        intr_h = int(header.get("intrinsics_height", rgb_h))
        fx = float(header["fx"])
        fy = float(header["fy"])
        cx = float(header["cx"])
        cy = float(header["cy"])

        if intr_w > 0 and intr_h > 0 and rgb_w > 0 and rgb_h > 0:
            if intr_w != rgb_w or intr_h != rgb_h:
                scale_x = rgb_w / intr_w
                scale_y = rgb_h / intr_h
                fx *= scale_x
                fy *= scale_y
                cx *= scale_x
                cy *= scale_y

        intr = PinholeIntrinsics(
            width=rgb_w, height=rgb_h,
            fx=fx, fy=fy, cx=cx, cy=cy,
        )

        # 11. Build TimeBundle
        timestamp_ns = int(header.get("timestamp_ns", 0))
        unix_ts = float(header.get("unix_timestamp", time.time()))

        tb = TimeBundle(
            t_mono_s=time.monotonic(),
            t_wall_utc_s=unix_ts,
            t_sensor_ns=timestamp_ns,
            seq=int(header.get("frame_id", 0)),
        )

        # 12. Build PoseStamped
        pose = PoseStamped(
            stamp_ns=timestamp_ns,
            frame_id="arkit",
            t_wc=t_wc,
            q_wc_xyzw=q_xyzw,
        )

        # 13. Build FramePacket
        return FramePacket(
            time=tb,
            rgb=rgb,
            depth_m=depth_m,
            pose=pose,
            intr=intr,
            is_keyframe=is_keyframe,
        )

    # ── Server lifecycle ──

    def _run_server(self) -> None:
        """Run uvicorn in a background thread with its own event loop."""
        import uvicorn

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop

        app = self._create_app()
        config = uvicorn.Config(
            app,
            host=self._host,
            port=self._port,
            log_level="warning",
            ws_max_size=16 * 1024 * 1024,  # 16 MB max message
        )
        server = uvicorn.Server(config)
        server.install_signal_handlers = lambda: None  # no signals in child thread
        loop.run_until_complete(server.serve())

    def start(self) -> None:
        """Start the WebSocket receiver in a daemon thread."""
        if self._server_thread and self._server_thread.is_alive():
            logger.warning("[websocket] Server already running")
            return
        self._server_thread = threading.Thread(
            target=self._run_server,
            daemon=True,
            name="websocket-receiver",
        )
        self._server_thread.start()

    def stop(self) -> None:
        """Signal shutdown (best-effort; daemon thread exits with process)."""
        logger.info("[websocket] Stop requested")
