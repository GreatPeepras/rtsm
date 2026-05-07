"""Tests for /ingest/keyframe -> ingest_q wiring (Gate 2.f.2).

Run under pytest once a pytest-equipped environment is available.
For now, see scripts/verify_ingest_pipeline.py for a pytest-free driver
that exercises the same cases inside the deployment container.
"""

from __future__ import annotations

import base64
import json
import queue
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pytest
from prometheus_client import CollectorRegistry
from starlette.testclient import TestClient

from rtsm.api.server import create_app


SESSION_DIR = Path("/mnt/rtsm-data/rtsm-recordings/2026-05-06T14-00-15Z")

pytestmark = pytest.mark.skipif(
    not (SESSION_DIR / "meta.json").is_file(),
    reason=f"test session missing: {SESSION_DIR}",
)


# ---------------------------- stub -----------------------------------------

class _StubWM:
    """Minimal working-memory stand-in for ingest-path tests.

    create_app requires working_memory, but /ingest/keyframe and /stats/ingest
    never touch it. Methods here exist only so unrelated endpoints would fail
    loudly rather than cryptically if accidentally hit.
    """
    def stats(self):
        return {}
    def iter_objects(self):
        return iter(())


# ---------------------------- fixtures ------------------------------------------

def _load_frame(seq: int) -> Dict[str, Any]:
    meta = json.loads((SESSION_DIR / "meta.json").read_text())
    intr = meta.get("intrinsics", {})
    if "fx" in intr:
        K = [float(intr["fx"]), 0.0, float(intr["cx"]),
             0.0, float(intr["fy"]), float(intr["cy"]),
             0.0, 0.0, 1.0]
    else:
        K = list(meta.get("K") or intr["K"])
    assert len(K) == 9

    name = f"{seq:06d}"
    jpg = (SESSION_DIR / f"{name}.jpg").read_bytes()
    png = (SESSION_DIR / f"{name}.png").read_bytes()
    per = json.loads((SESSION_DIR / f"{name}.json").read_text())

    return {
        "rgb_jpeg": base64.b64encode(jpg).decode("ascii"),
        "depth_png": base64.b64encode(png).decode("ascii"),
        "K": K,
        "pose": {"tx": 0.0, "ty": 0.0, "tz": 0.0,
                 "qx": 0.0, "qy": 0.0, "qz": 0.0, "qw": 1.0},
        "timestamp_ros": float(per.get("t_capture_ns", 0)) / 1e9,
        "frame_id": meta.get("color_frame_id", "camera_color_optical_frame"),
        "sequence": int(per.get("sequence", seq)),
    }


@pytest.fixture
def app_with_queue():
    q: queue.Queue = queue.Queue(maxsize=3)
    app = create_app(
        working_memory=_StubWM(),
        ingest_queue=q,
        registry=CollectorRegistry(),
    )
    return app, q


@pytest.fixture
def app_without_queue():
    return create_app(
        working_memory=_StubWM(),
        registry=CollectorRegistry(),
    )


# ---------------------------- tests --------------------------------------------

def test_stats_reports_queued_mode_when_queue_bound(app_with_queue):
    app, _q = app_with_queue
    with TestClient(app) as c:
        s = c.get("/stats/ingest").json()
    assert s["mode"] == "queued"
    assert s["queue_maxsize"] == 3
    assert s["queue_depth"] == 0
    assert s["frames_queued"] == 0
    assert s["queue_full_drops"] == 0


def test_stats_reports_decode_only_when_no_queue(app_without_queue):
    with TestClient(app_without_queue) as c:
        s = c.get("/stats/ingest").json()
    assert s["mode"] == "decode-only"
    # Decode-only mode reports a uniform schema; queue counters are present
    # but must be zero since no queue is bound.
    assert s.get("frames_queued", 0) == 0
    assert s.get("queue_full_drops", 0) == 0


def test_post_real_frame_enqueues_packet(app_with_queue):
    app, q = app_with_queue
    payload = _load_frame(100)
    with TestClient(app) as c:
        r = c.post("/ingest/keyframe", json=payload)
        assert r.status_code == 200, r.text
        b = r.json()
        assert b["status"] == "queued"
        assert "queue_put_ms" in b["timings"]

        assert q.qsize() == 1
        pkt = q.get_nowait()
        assert pkt.rgb.dtype == np.uint8
        assert pkt.rgb.ndim == 3 and pkt.rgb.shape[2] == 3
        assert pkt.depth_m is not None
        assert pkt.depth_m.dtype == np.float32
        assert pkt.depth_m.ndim == 2
        assert pkt.rgb.shape[:2] == pkt.depth_m.shape
        # Unit sanity: indoor depth in meters; 0mm invalids -> NaN.
        finite_max = float(np.nanmax(pkt.depth_m))
        assert 0.0 < finite_max < 20.0, f"depth_m max={finite_max} outside meters"
        assert pkt.intr is not None
        K = pkt.intr.K()  # method, not attribute
        assert K.shape == (3, 3)
        assert pkt.time.seq == payload["sequence"]

        s = c.get("/stats/ingest").json()
        assert s["frames_received"] == 1
        assert s["frames_queued"] == 1
        assert s["queue_full_drops"] == 0


def test_queue_full_returns_503_and_increments_drops(app_with_queue):
    app, q = app_with_queue
    payloads = [_load_frame(s) for s in range(100, 104)]
    with TestClient(app) as c:
        for i, p in enumerate(payloads[:3]):
            r = c.post("/ingest/keyframe", json=p)
            assert r.status_code == 200, f"fill #{i}: {r.status_code} {r.text}"
        assert q.qsize() == 3

        r = c.post("/ingest/keyframe", json=payloads[3])
        assert r.status_code == 503, r.text

        s = c.get("/stats/ingest").json()
        assert s["frames_received"] == 4
        assert s["frames_queued"] == 3
        assert s["queue_full_drops"] == 1
        assert s["queue_depth"] == 3


def test_decode_only_fallback_when_no_queue(app_without_queue):
    payload = _load_frame(100)
    with TestClient(app_without_queue) as c:
        r = c.post("/ingest/keyframe", json=payload)
        assert r.status_code == 200, r.text
        b = r.json()
        assert b["status"] == "accepted"
        assert b.get("mode") == "decode-only"
        assert "queue_put_ms" not in b["timings"]


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
