"""
Live-HTTP tests for /ingest/keyframe (Gate 2.f.1, decode-only).

Runs against the rtsm-dev container on localhost:8002. Module-skips if
the server is not reachable (matches the pattern in test_serve_api.py).

Uses a real recorded frame from the living-room session captured on
2026-05-06. That session is validated-clean (4500 frames, 0 orphans);
using a real frame means the decode path exercises real D435i JPEG/PNG
bytes, not synthetic data that might mask format-specific issues.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any, Dict

import pytest
import requests


BASE_URL = os.environ.get("RTSM_API_URL", "http://localhost:8002")
SESSION_DIR = Path(
    os.environ.get(
        "RTSM_TEST_SESSION",
        "/mnt/rtsm-data/rtsm-recordings/2026-05-06T14-00-15Z",
    )
)


# ---------------------------- module-level skip logic ----------------------------

def _server_reachable() -> bool:
    try:
        r = requests.get(f"{BASE_URL}/healthz", timeout=1.0)
        return r.status_code == 200
    except Exception:
        return False


def _session_available() -> bool:
    return (SESSION_DIR / "meta.json").is_file()


pytestmark = [
    pytest.mark.skipif(not _server_reachable(),
                       reason=f"rtsm-dev not reachable at {BASE_URL}"),
    pytest.mark.skipif(not _session_available(),
                       reason=f"test session missing: {SESSION_DIR}"),
]


# ---------------------------- fixtures / helpers --------------------------------

def _load_frame(seq: int = 100) -> Dict[str, Any]:
    """Build a KeyframePayload-shaped dict from a recorded frame.

    On-disk format (2026-05-06 recorder):
      NNNNNN.jpg   -- color
      NNNNNN.png   -- depth (uint16 mm)
      NNNNNN.json  -- per-frame metadata
      meta.json    -- intrinsics + run-level metadata
    """
    meta = json.loads((SESSION_DIR / "meta.json").read_text())

    # This recording uses intrinsics.{fx,fy,cx,cy} layout (verified 2026-05-07).
    # Fall back to other shapes only if the expected one is missing.
    intr = meta.get("intrinsics", {})
    if "fx" in intr and "fy" in intr and "cx" in intr and "cy" in intr:
        K = [
            float(intr["fx"]), 0.0, float(intr["cx"]),
            0.0, float(intr["fy"]), float(intr["cy"]),
            0.0, 0.0, 1.0,
        ]
    elif "K" in meta:
        K = list(meta["K"])
    elif "K" in intr:
        K = list(intr["K"])
    else:
        raise RuntimeError(f"cannot locate intrinsics in meta.json; keys={list(meta.keys())}")
    assert len(K) == 9, f"intrinsics K has {len(K)} elements, expected 9"

    name = f"{seq:06d}"
    jpg_path = SESSION_DIR / f"{name}.jpg"
    png_path = SESSION_DIR / f"{name}.png"
    js_path = SESSION_DIR / f"{name}.json"
    if not (jpg_path.is_file() and png_path.is_file() and js_path.is_file()):
        pytest.skip(f"frame triplet missing for seq {seq} in {SESSION_DIR}")

    rgb_b64 = base64.b64encode(jpg_path.read_bytes()).decode("ascii")
    depth_b64 = base64.b64encode(png_path.read_bytes()).decode("ascii")
    per_frame = json.loads(js_path.read_text())

    # Synthetic pose (identity). Gate 2.f.1 validates quaternion norm only;
    # pose is not consumed for projection yet. Real /tf capture lands later.
    return {
        "rgb_jpeg": rgb_b64,
        "depth_png": depth_b64,
        "K": K,
        "pose": {
            "tx": 0.0, "ty": 0.0, "tz": 0.0,
            "qx": 0.0, "qy": 0.0, "qz": 0.0, "qw": 1.0,
        },
        "timestamp_ros": float(per_frame.get("t_capture_ns", 0)) / 1e9,
        "frame_id": meta.get("color_frame_id", "camera_color_optical_frame"),
        "sequence": int(per_frame.get("sequence", seq)),
    }


def _post(payload: Dict[str, Any]) -> requests.Response:
    return requests.post(f"{BASE_URL}/ingest/keyframe", json=payload, timeout=10.0)


# ---------------------------- tests ---------------------------------------------

def test_decode_only_mode_with_real_frame():
    """Golden path: a real D435i frame decodes to correct shapes with real timings."""
    payload = _load_frame(seq=100)
    r = _post(payload)
    assert r.status_code == 200, r.text
    body = r.json()

    assert body["status"] == "accepted"
    assert body["mode"] == "decode-only"
    assert body["observations_added"] == 0
    assert body["objects_updated"] == 0
    assert body["sequence"] == payload["sequence"]

    # Session is 640x480 per meta.json.
    assert body["rgb_shape"] == [480, 640, 3]
    assert body["depth_shape"] == [480, 640]

    t = body["timings"]
    assert t["base64_ms"] > 0.0
    assert t["cv2_ms"] > 0.0
    assert t["validate_ms"] >= 0.0    # very fast, can round to 0
    assert t["total_ms"] > 0.0

    # No validation warnings expected for a real frame with identity pose.
    assert body["validation_warnings"] == []


def test_depth_valid_pct_reasonable():
    """Real D435i depth should have a substantial but not perfect valid fraction."""
    payload = _load_frame(seq=100)
    body = _post(payload).json()
    assert body["mode"] == "decode-only"
    # D435i indoor scenes are typically 60-95% valid; accept wide range to
    # tolerate edge frames (camera pointing at a white wall, etc.).
    assert 20.0 <= body["depth_valid_pct"] <= 100.0, \
        f"depth_valid_pct={body['depth_valid_pct']} outside plausible range"


def test_malformed_base64_rgb_padding():
    """Invalid base64 length triggers binascii.Error -> decode-failed/base64."""
    payload = _load_frame(seq=100)
    # "AAA" is 3 chars; valid base64 must be a multiple of 4.
    payload["rgb_jpeg"] = "AAA"
    r = _post(payload)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "decode_failed"
    assert body["mode"] == "decode-failed"
    assert body["error"] == "base64_decode_failed"
    assert body["stage"] == "base64"
    assert "base64_ms" in body["timings"]


def test_malformed_base64_rgb_non_alphabet():
    """Non-alphabet chars with validate=True also hit base64 failure path."""
    payload = _load_frame(seq=100)
    payload["rgb_jpeg"] = "!!!!"  # 4 chars (valid length), none in alphabet
    r = _post(payload)
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "decode-failed"
    assert body["error"] == "base64_decode_failed"


def test_malformed_jpeg_bytes():
    """Valid base64 of random bytes -> cv2.imdecode returns None."""
    payload = _load_frame(seq=100)
    # 32 bytes of zeros: valid base64 length, invalid JPEG.
    payload["rgb_jpeg"] = base64.b64encode(b"\x00" * 32).decode("ascii")
    r = _post(payload)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "decode_failed"
    assert body["mode"] == "decode-failed"
    assert body["error"] == "cv2_decode_failed"
    assert body["stage"] == "cv2"
    assert "base64_ms" in body["timings"]
    assert "cv2_ms" in body["timings"]


def test_invalid_quaternion_norm_yields_warning_not_failure():
    """Bad pose should warn, not fail -- decode still succeeds."""
    payload = _load_frame(seq=100)
    payload["pose"]["qw"] = 2.0   # norm ~2.0, not unit
    r = _post(payload)
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "decode-only"
    assert any("quaternion" in w.lower() for w in body["validation_warnings"]), \
        f"expected quaternion warning, got: {body['validation_warnings']}"


def test_bad_intrinsics_yields_warning():
    """cx out of bounds should warn, not fail."""
    payload = _load_frame(seq=100)
    payload["K"][2] = 99999.0   # K[2] is cx
    body = _post(payload).json()
    assert body["mode"] == "decode-only"
    assert any("cx" in w for w in body["validation_warnings"]), \
        f"expected cx warning, got: {body['validation_warnings']}"


def test_counters_increment_on_success_and_failure():
    """Transport-layer counters must increment regardless of decode outcome."""
    before = requests.get(f"{BASE_URL}/stats/ingest", timeout=5.0).json()

    _post(_load_frame(seq=100))   # success
    bad = _load_frame(seq=100)
    bad["rgb_jpeg"] = base64.b64encode(b"\x00" * 32).decode("ascii")
    _post(bad)                    # decode failure

    after = requests.get(f"{BASE_URL}/stats/ingest", timeout=5.0).json()
    assert after["frames_received"] == before["frames_received"] + 2
    assert after["bytes_received"] > before["bytes_received"]
    assert after["mode"] == "decode-only"


def test_schema_violation_still_returns_422():
    """Missing required field -> FastAPI 422 (Pydantic), never reaches helper."""
    payload = _load_frame(seq=100)
    del payload["K"]
    r = _post(payload)
    assert r.status_code == 422


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
