#!/usr/bin/env python3
"""Standalone verifier for /ingest/keyframe -> ingest_q wiring (Gate 2.f.2).

Mirrors tests/test_ingest_pipeline.py but uses no pytest. Exists because the
deployment container has no pytest and no network to install it. Once a
pytest-equipped container/CI is available, this script becomes redundant and
can be removed; the pytest file is the canonical regression test.

Run inside the container:
    docker exec <cid> python3 /workspace/rtsm/scripts/verify_ingest_pipeline.py
"""

from __future__ import annotations

import base64
import json
import queue
import sys
import traceback
from pathlib import Path
from typing import Any, Dict

import numpy as np
from prometheus_client import CollectorRegistry
from starlette.testclient import TestClient

from rtsm.api.server import create_app


SESSION_DIR = Path("/mnt/rtsm-data/rtsm-recordings/2026-05-06T14-00-15Z")


# ---------------------------- stub -----------------------------------------

class _StubWM:
    """Minimal WM stand-in; see tests/test_ingest_pipeline.py for rationale."""
    def stats(self):
        return {}
    def iter_objects(self):
        return iter(())


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


def _make_app(with_queue_maxsize: int | None = None):
    """Build a test app with a fresh prom registry. Returns (app, queue_or_None)."""
    q = queue.Queue(maxsize=with_queue_maxsize) if with_queue_maxsize is not None else None
    kwargs = {"working_memory": _StubWM(), "registry": CollectorRegistry()}
    if q is not None:
        kwargs["ingest_queue"] = q
    return create_app(**kwargs), q


# ---------------------------- assertions ---------------------------------------

class AssertionFailed(Exception):
    pass


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionFailed(msg)


# ---------------------------- checks -------------------------------------------

def check_stats_queued_when_bound():
    app, _q = _make_app(with_queue_maxsize=3)
    with TestClient(app) as c:
        s = c.get("/stats/ingest").json()
    expect(s["mode"] == "queued", f"mode={s['mode']!r}, expected 'queued'")
    expect(s["queue_maxsize"] == 3, f"queue_maxsize={s['queue_maxsize']}")
    expect(s["queue_depth"] == 0, f"queue_depth={s['queue_depth']}")
    expect(s["frames_queued"] == 0, f"frames_queued={s['frames_queued']}")
    expect(s["queue_full_drops"] == 0, f"queue_full_drops={s['queue_full_drops']}")


def check_stats_decode_only_when_unbound():
    app, _ = _make_app()
    with TestClient(app) as c:
        s = c.get("/stats/ingest").json()
    expect(s["mode"] == "decode-only", f"mode={s['mode']!r}")
    # Decode-only mode reports a uniform schema; queue counters are present
    # but must be zero since no queue is bound.
    expect(s.get("frames_queued", 0) == 0, f"frames_queued={s.get('frames_queued')}")
    expect(s.get("queue_full_drops", 0) == 0, f"drops={s.get('queue_full_drops')}")


def check_post_enqueues_packet():
    app, q = _make_app(with_queue_maxsize=3)
    payload = _load_frame(100)
    with TestClient(app) as c:
        r = c.post("/ingest/keyframe", json=payload)
        expect(r.status_code == 200, f"status={r.status_code} body={r.text}")
        b = r.json()
        expect(b["status"] == "queued", f"status field={b['status']!r}")
        expect("queue_put_ms" in b["timings"], f"timings keys={list(b['timings'])}")

        expect(q.qsize() == 1, f"qsize={q.qsize()}")
        pkt = q.get_nowait()
        expect(pkt.rgb.dtype == np.uint8, f"rgb dtype={pkt.rgb.dtype}")
        expect(pkt.rgb.ndim == 3 and pkt.rgb.shape[2] == 3,
               f"rgb shape={pkt.rgb.shape}")
        expect(pkt.depth_m is not None, "depth_m missing")
        expect(pkt.depth_m.dtype == np.float32, f"depth_m dtype={pkt.depth_m.dtype}")
        expect(pkt.depth_m.ndim == 2, f"depth_m shape={pkt.depth_m.shape}")
        expect(pkt.rgb.shape[:2] == pkt.depth_m.shape,
               f"rgb {pkt.rgb.shape[:2]} vs depth_m {pkt.depth_m.shape}")
        # Unit sanity: indoor depth in meters << 20; mm would be thousands.
        # nan* ignores the invalid-depth sentinel (0mm -> NaN).
        finite_max = float(np.nanmax(pkt.depth_m))
        expect(0.0 < finite_max < 20.0,
               f"depth_m max={finite_max} outside plausible meter range")
        expect(pkt.intr is not None, "intr missing")
        K = pkt.intr.K()  # note: K is a method on PinholeIntrinsics
        expect(K.shape == (3, 3), f"intr.K() shape={K.shape}")
        expect(pkt.time.seq == payload["sequence"], f"seq mismatch: {pkt.time.seq} vs {payload['sequence']}")

        s = c.get("/stats/ingest").json()
        expect(s["frames_received"] == 1, f"frames_received={s['frames_received']}")
        expect(s["frames_queued"] == 1, f"frames_queued={s['frames_queued']}")
        expect(s["queue_full_drops"] == 0, f"drops={s['queue_full_drops']}")


def check_queue_full_returns_503():
    app, q = _make_app(with_queue_maxsize=3)
    payloads = [_load_frame(s) for s in range(100, 104)]
    with TestClient(app) as c:
        for i, p in enumerate(payloads[:3]):
            r = c.post("/ingest/keyframe", json=p)
            expect(r.status_code == 200, f"fill #{i}: {r.status_code} {r.text}")
        expect(q.qsize() == 3, f"after fill qsize={q.qsize()}")

        r = c.post("/ingest/keyframe", json=payloads[3])
        expect(r.status_code == 503,
               f"expected 503 on full queue, got {r.status_code}: {r.text}")

        s = c.get("/stats/ingest").json()
        expect(s["frames_received"] == 4, f"received={s['frames_received']}")
        expect(s["frames_queued"] == 3, f"queued={s['frames_queued']}")
        expect(s["queue_full_drops"] == 1, f"drops={s['queue_full_drops']}")
        expect(s["queue_depth"] == 3, f"depth={s['queue_depth']}")


def check_decode_only_fallback():
    app, _ = _make_app()
    payload = _load_frame(100)
    with TestClient(app) as c:
        r = c.post("/ingest/keyframe", json=payload)
        expect(r.status_code == 200, f"status={r.status_code} body={r.text}")
        b = r.json()
        expect(b["status"] == "accepted", f"status field={b['status']!r}")
        expect(b.get("mode") == "decode-only", f"mode={b.get('mode')!r}")
        expect("queue_put_ms" not in b["timings"],
               f"unexpected queue_put_ms in decode-only path: {b['timings']}")


# ---------------------------- driver -------------------------------------------

CHECKS = [
    ("stats reports queued mode when queue bound",     check_stats_queued_when_bound),
    ("stats reports decode-only when no queue",        check_stats_decode_only_when_unbound),
    ("POST real frame enqueues FramePacket",           check_post_enqueues_packet),
    ("queue full returns 503 and increments drops",    check_queue_full_returns_503),
    ("decode-only fallback when no queue",             check_decode_only_fallback),
]


def main() -> int:
    if not (SESSION_DIR / "meta.json").is_file():
        print(f"SKIP: test session missing: {SESSION_DIR}", file=sys.stderr)
        return 77

    passed = failed = 0
    for name, fn in CHECKS:
        try:
            fn()
        except AssertionFailed as e:
            failed += 1
            print(f"  FAIL  {name}")
            print(f"        {e}")
        except Exception:
            failed += 1
            print(f"  ERROR {name}")
            traceback.print_exc()
        else:
            passed += 1
            print(f"  PASS  {name}")
    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
