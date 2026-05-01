"""
Integration tests for the live serve-mode HTTP API.

Runs against a running rtsm-dev container on http://localhost:8002.
Does NOT import any rtsm.* modules — pure HTTP client tests, so this
file won't be affected by missing in-container deps (faiss, torch, etc.)
when pytest collects from the host.

Covers regressions for:
- Patch I   (staleness visibility fields in /stats)
- Patch II  (sidecar freshness check at startup — indirect: /stats non-empty)
- Patch III (POST /reload endpoint)
- Patch IV  (CLIP loaded in serve mode, /search/semantic returns results)
- Patch H   (empty-index guard — /stats reports objects > 0 after restart)
- P8        (semantic results include xyz_world)

Usage (from repo root):
    pytest tests/test_serve_api.py -v

Requires: rtsm-dev container running, serve mode, API on :8002.
Tests will be SKIPPED (not failed) if the API isn't reachable, so this
file is safe to include in a broader `pytest tests/` run.
"""
from __future__ import annotations

import pytest
import requests

API = "http://localhost:8002"
TIMEOUT = 5.0


# ── module-level reachability guard ────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def _api_reachable():
    """Skip the entire module cleanly if the serve API isn't up."""
    try:
        r = requests.get(f"{API}/stats", timeout=2.0)
        r.raise_for_status()
    except (requests.RequestException, ValueError) as e:
        pytest.skip(f"serve API not reachable at {API}: {e}")


# ── /stats ─────────────────────────────────────────────────────────

class TestStats:
    def test_stats_returns_200(self):
        r = requests.get(f"{API}/stats", timeout=TIMEOUT)
        assert r.status_code == 200

    def test_stats_has_core_fields(self):
        s = requests.get(f"{API}/stats", timeout=TIMEOUT).json()
        for key in ("objects", "confirmed", "serve_mode"):
            assert key in s, f"missing {key!r} in /stats"

    def test_stats_serve_mode_true(self):
        s = requests.get(f"{API}/stats", timeout=TIMEOUT).json()
        assert s["serve_mode"] is True, "expected serve_mode=True"

    def test_stats_objects_nonzero(self):
        """Patch H regression: empty-index guard must NOT have nuked persisted objects."""
        s = requests.get(f"{API}/stats", timeout=TIMEOUT).json()
        assert s["objects"] > 0, f"FrozenWM empty; expected >=1 object, got {s['objects']}"

    def test_stats_has_freshness_fields(self):
        """Patch I regression: staleness visibility fields must be present."""
        s = requests.get(f"{API}/stats", timeout=TIMEOUT).json()
        for key in ("frozen_loaded_utc", "frozen_age_seconds", "frozen_source", "frozen_stale"):
            assert key in s, f"Patch I field {key!r} missing from /stats"

    def test_stats_frozen_stale_is_bool(self):
        s = requests.get(f"{API}/stats", timeout=TIMEOUT).json()
        assert isinstance(s["frozen_stale"], bool)

    def test_stats_frozen_age_reasonable(self):
        s = requests.get(f"{API}/stats", timeout=TIMEOUT).json()
        age = s["frozen_age_seconds"]
        assert isinstance(age, (int, float))
        assert age >= 0


# ── /reload (Patch III) ────────────────────────────────────────────

class TestReload:
    def test_reload_returns_200(self):
        r = requests.post(f"{API}/reload", timeout=TIMEOUT)
        assert r.status_code == 200

    def test_reload_response_schema(self):
        r = requests.post(f"{API}/reload", timeout=TIMEOUT).json()
        for key in ("status", "old_objects", "new_objects", "duration_ms"):
            assert key in r, f"missing {key!r} in /reload response"
        assert r["status"] == "ok"

    def test_reload_preserves_object_count(self):
        """With no new ingest, reload should be a no-op count-wise."""
        before = requests.get(f"{API}/stats", timeout=TIMEOUT).json()["objects"]
        reload_resp = requests.post(f"{API}/reload", timeout=TIMEOUT).json()
        after = requests.get(f"{API}/stats", timeout=TIMEOUT).json()["objects"]
        assert reload_resp["new_objects"] == before == after, (
            f"object count drifted: before={before} "
            f"reload={reload_resp['new_objects']} after={after}"
        )

    def test_reload_is_fast(self):
        """Sidecar reload is in-memory; should be well under 500ms for small counts."""
        r = requests.post(f"{API}/reload", timeout=TIMEOUT).json()
        assert r["duration_ms"] < 500, f"reload took {r['duration_ms']}ms, suspicious"


# ── /search/semantic (Patch IV + P8) ───────────────────────────────

class TestSemanticSearch:
    @pytest.fixture
    def sample_result(self):
        r = requests.get(
            f"{API}/search/semantic",
            params={"query": "toilet", "top_k": 3},
            timeout=TIMEOUT,
        )
        assert r.status_code == 200, (
            f"semantic search returned {r.status_code}: {r.text[:200]}"
        )
        body = r.json()
        assert "results" in body
        assert len(body["results"]) > 0, "expected at least one semantic result"
        return body["results"][0]

    def test_semantic_endpoint_not_503(self):
        """Patch IV regression: if CLIP didn't load, this returns 503."""
        r = requests.get(
            f"{API}/search/semantic",
            params={"query": "chair", "top_k": 1},
            timeout=TIMEOUT,
        )
        assert r.status_code != 503, "CLIP not loaded — Patch IV regression"
        assert r.status_code == 200

    def test_semantic_result_schema(self, sample_result):
        for key in ("id", "score", "confirmed", "stability", "xyz_world", "source"):
            assert key in sample_result, f"missing {key!r} in semantic result"

    def test_semantic_result_has_xyz_world(self, sample_result):
        """P8 resolution guard: xyz_world must be populated, not null."""
        xyz = sample_result["xyz_world"]
        assert xyz is not None, "xyz_world is null (P8 regression)"
        assert isinstance(xyz, list) and len(xyz) == 3
        assert all(isinstance(c, (int, float)) for c in xyz)

    def test_semantic_score_in_range(self, sample_result):
        """Guard against 0.0 (empty embed) or >1.0 (broken normalization)."""
        s = sample_result["score"]
        assert 0.0 < s < 1.0, f"score {s} out of sane range"

    @pytest.mark.parametrize("query", ["toilet", "chair", "wall", "sink"])
    def test_semantic_multiple_queries(self, query):
        r = requests.get(
            f"{API}/search/semantic",
            params={"query": query, "top_k": 3},
            timeout=TIMEOUT,
        )
        assert r.status_code == 200
        body = r.json()
        assert body["query"] == query
        assert len(body["results"]) > 0


# ── /objects (label_primary exposure) ──────────────────────────────

class TestObjects:
    def test_objects_returns_200(self):
        r = requests.get(f"{API}/objects", params={"limit": 1}, timeout=TIMEOUT)
        assert r.status_code == 200

    def test_objects_schema_includes_label_primary(self):
        body = requests.get(f"{API}/objects", params={"limit": 1}, timeout=TIMEOUT).json()
        assert "objects" in body
        assert len(body["objects"]) > 0
        obj = body["objects"][0]
        for key in ("id", "xyz_world", "label_primary", "confirmed", "stability"):
            assert key in obj, f"missing {key!r} in /objects item"
