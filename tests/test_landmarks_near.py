"""Unit tests for GET /landmarks/near endpoint.

Validates the landmark-eligible spatial query that backs both:
  - on-demand goto_object name resolution (when name is missing/ambiguous)
  - landmark-AMCL pose verification gate

Hard invariant under test: the endpoint NEVER returns objects with
movability_class outside the allow-list, regardless of label or hits.
The landmark consumer must be able to trust the filter completely.

Run with:
    cd ~/rtsm && PYTHONPATH=. python3 tests/test_landmarks_near.py

Or with pytest (if available in container):
    cd ~/rtsm && PYTHONPATH=. pytest tests/test_landmarks_near.py -v
"""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.environ.get("RTSM_REPO", os.path.expanduser("~/rtsm")))

import numpy as np
from fastapi.testclient import TestClient
from prometheus_client import CollectorRegistry

from rtsm.api.server import create_app


# ---------------------------------------------------------------------------
# Minimal stubs
# ---------------------------------------------------------------------------

class _Obj:
    """Duck-typed ObjectState. Only fields the endpoint reads."""
    def __init__(
        self,
        oid: str,
        xyz,
        *,
        movability_class=None,
        label_user=None,
        label_primary=None,
        label_scores=None,
        label_hits=None,
        hits: int = 1,
        stability: float = 0.5,
        confirmed: bool = True,
        last_seen_wall_utc: float = 0.0,
    ):
        self.id = oid
        self.xyz_world = np.asarray(xyz, dtype=np.float32)
        self.movability_class = movability_class
        self.label_user = label_user
        self.label_primary = label_primary
        self.label_scores = label_scores or {}
        self.label_hits = label_hits or {}
        self.hits = hits
        self.stability = stability
        self.confirmed = confirmed
        self.last_seen_wall_utc = last_seen_wall_utc


class _Grid:
    """Duck-typed Grid. Endpoint only reads .cell_m."""
    def __init__(self, cell_m: float = 0.5):
        self.cell_m = cell_m


class _Index:
    """Duck-typed ProximityIndex. Endpoint only calls .nearby_ids()
    and reads .grid.cell_m. We just return every OID we know about
    and let the radius filter in the endpoint do the real work."""
    def __init__(self, oids, cell_m: float = 0.5):
        self._oids = list(oids)
        self.grid = _Grid(cell_m=cell_m)

    def nearby_ids(self, center, rings: int = 1):
        return list(self._oids)


class _WM:
    """Duck-typed WorkingMemory.

    Only fields/methods the endpoint reads:
        .iter_objects(), .get_robot_pose(), .min_label_hits

    (As of 2026-06-03 the endpoint uses iter_objects() rather than the
    proximity index, so .index and .get(oid) are no longer required.)
    """
    min_label_hits = 5

    def __init__(self, objects, *, with_index: bool = True):
        # Preserve the with_index kwarg for backward-compatible test calls.
        # It no longer affects endpoint behavior (the proximity index is
        # not consulted), but we still set self.index so other endpoints
        # that share this stub keep working.
        self._objects = {o.id: o for o in objects}
        self.index = _Index(self._objects.keys()) if with_index else None
        self._with_index = with_index

    def iter_objects(self):
        return list(self._objects.values())

    def get(self, oid):
        return self._objects.get(oid)

    def get_robot_pose(self):
        return {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0}


def _make_client(objects, *, with_index: bool = True) -> TestClient:
    wm = _WM(objects, with_index=with_index)
    # Per-test CollectorRegistry to avoid 'Duplicated timeseries' errors
    # when create_app is called multiple times in the same process.
    app = create_app(working_memory=wm, registry=CollectorRegistry())
    return TestClient(app)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_returns_static_landmark_in_radius():
    """Happy path: a 'static' object within radius is returned."""
    objs = [
        _Obj("couch001", [1.0, 0.0, 0.0], movability_class="static",
             label_user="couch", label_primary="couch"),
    ]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 2.0})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] == 1
    assert body["count"] == 1
    assert body["results"][0]["id"] == "couch001"
    assert body["results"][0]["movability_class"] == "static"
    assert body["results"][0]["display_label"] == "couch"
    assert abs(body["results"][0]["distance_m"] - 1.0) < 1e-3
    assert body["allowed_movability"] == ["permanent", "static"]
    assert body["include_semi_static"] is False


def test_returns_permanent_landmark():
    """'permanent' is also in the default allow-list."""
    objs = [
        _Obj("wall001", [0.5, 0.5, 0.0], movability_class="permanent"),
    ]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 2.0})
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_excludes_movable():
    """movable -> filtered out. This is the safety invariant."""
    objs = [
        _Obj("trash001", [1.0, 0.0, 0.0], movability_class="movable",
             label_user="trash can"),
    ]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 5.0})
    assert r.status_code == 200
    assert r.json()["total"] == 0


def test_excludes_roaming():
    """roaming -> filtered out."""
    objs = [
        _Obj("cat001", [1.0, 0.0, 0.0], movability_class="roaming"),
    ]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 5.0})
    assert r.json()["total"] == 0


def test_excludes_ephemeral():
    """ephemeral -> filtered out."""
    objs = [
        _Obj("bottle001", [1.0, 0.0, 0.0], movability_class="ephemeral"),
    ]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 5.0})
    assert r.json()["total"] == 0


def test_excludes_null_movability_class():
    """None -> filtered out. Default-spawned objects have None until
    classified; they must not be treated as landmarks."""
    objs = [
        _Obj("unclassified001", [1.0, 0.0, 0.0], movability_class=None),
    ]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 5.0})
    assert r.json()["total"] == 0


def test_excludes_semi_static_by_default():
    """semi_static is NOT a landmark by default. Must be opted in."""
    objs = [
        _Obj("printer001", [1.0, 0.0, 0.0], movability_class="semi_static",
             label_user="3D printer"),
    ]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 5.0})
    assert r.json()["total"] == 0


def test_includes_semi_static_when_requested():
    """include_semi_static=true widens the allow-list."""
    objs = [
        _Obj("printer001", [1.0, 0.0, 0.0], movability_class="semi_static",
             label_user="3D printer"),
        _Obj("couch001",   [0.5, 0.0, 0.0], movability_class="static",
             label_user="couch"),
    ]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={
        "x": 0.0, "y": 0.0, "z": 0.0, "radius_m": 5.0,
        "include_semi_static": "true",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["include_semi_static"] is True
    assert body["allowed_movability"] == ["permanent", "semi_static", "static"]
    assert body["total"] == 2


def test_radius_filter_excludes_far_landmarks():
    """A 'static' object outside radius is NOT returned even though the
    proximity index returned it (defense-in-depth)."""
    objs = [
        _Obj("near_couch",  [0.5, 0.0, 0.0], movability_class="static"),
        _Obj("far_couch",   [10.0, 0.0, 0.0], movability_class="static"),
    ]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 1.0})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["results"][0]["id"] == "near_couch"


def test_results_sorted_by_distance():
    """Results are sorted ascending by distance."""
    objs = [
        _Obj("c", [3.0, 0.0, 0.0], movability_class="static"),
        _Obj("a", [1.0, 0.0, 0.0], movability_class="static"),
        _Obj("b", [2.0, 0.0, 0.0], movability_class="static"),
    ]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 5.0})
    ids = [row["id"] for row in r.json()["results"]]
    assert ids == ["a", "b", "c"]


def test_pagination():
    """offset + limit pagination matches /search/spatial shape."""
    objs = [
        _Obj(f"l{i:02d}", [float(i) * 0.1, 0.0, 0.0], movability_class="static")
        for i in range(1, 11)
    ]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={
        "x": 0.0, "y": 0.0, "z": 0.0,
        "radius_m": 5.0,
        "offset": 3, "limit": 2,
    })
    body = r.json()
    assert body["total"] == 10
    assert body["offset"] == 3
    assert body["limit"] == 2
    assert body["count"] == 2
    assert len(body["results"]) == 2


def test_limit_capped_at_200():
    """limit is clamped to [1, 200]."""
    objs = [_Obj("l", [1.0, 0.0, 0.0], movability_class="static")]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 5.0, "limit": 9999})
    assert r.json()["limit"] == 200


def test_offset_negative_clamped():
    """Negative offset clamped to 0."""
    objs = [_Obj("l", [1.0, 0.0, 0.0], movability_class="static")]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 5.0, "offset": -10})
    assert r.json()["offset"] == 0


def test_empty_when_no_landmarks():
    """No matching landmarks -> empty results, total=0, 200 OK."""
    objs = [
        _Obj("a", [1.0, 0.0, 0.0], movability_class="movable"),
        _Obj("b", [2.0, 0.0, 0.0], movability_class="ephemeral"),
    ]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 5.0})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert body["count"] == 0
    assert body["results"] == []


def test_works_in_serve_mode_without_proximity_index():
    """As of 2026-06-03, /landmarks/near uses iter_objects() rather than
    the proximity index, so it works in serve-mode (frozen WM with no
    proximity index). Used to 503, now returns results."""
    objs = [_Obj("a", [1.0, 0.0, 0.0], movability_class="static")]
    client = _make_client(objs, with_index=False)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 5.0})
    assert r.status_code == 200, r.text
    assert r.json()["total"] == 1


def test_response_includes_label_fields():
    """Response includes label_user, label_primary, display_label —
    consumers need these for resolution and narration."""
    objs = [
        _Obj("k1", [1.0, 0.0, 0.0],
             movability_class="static",
             label_user="Kallax shelf",
             label_primary="bookshelf",
             label_scores={"bookshelf": 0.9},
             label_hits={"bookshelf": 12}),
    ]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 5.0})
    row = r.json()["results"][0]
    assert row["label_user"] == "Kallax shelf"
    assert row["label_primary"] == "bookshelf"
    assert row["display_label"] == "Kallax shelf"  # user pin wins
    assert "xyz_world" in row
    assert "distance_m" in row
    assert "movability_class" in row


def test_response_top_level_shape():
    """Top-level response shape matches /search/spatial conventions plus
    the landmark-specific fields."""
    objs = [_Obj("a", [1.0, 0.0, 0.0], movability_class="static")]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.5, "y": 0.5, "z": 0.0,
                                              "radius_m": 3.0})
    body = r.json()
    # Inherited from /search/spatial
    for k in ("center", "radius_m", "robot_pose",
              "total", "offset", "limit", "count", "results"):
        assert k in body, f"missing top-level key: {k}"
    # Landmark-specific
    assert "include_semi_static" in body
    assert "allowed_movability" in body
    assert body["center"] == [0.5, 0.5, 0.0]
    assert body["radius_m"] == 3.0


def test_hard_invariant_chimera_movability_class_excluded():
    """Defense in depth: even if WM somehow carries a bizarre
    movability_class value (e.g., from a buggy import or a hand-edited
    sidecar), the endpoint must NOT return it. The allow-list is
    positive matching only."""
    objs = [
        _Obj("weird1", [1.0, 0.0, 0.0], movability_class="STATIC"),  # wrong case
        _Obj("weird2", [1.0, 0.0, 0.0], movability_class="landmark"),  # not a real class
        _Obj("weird3", [1.0, 0.0, 0.0], movability_class=""),  # empty
        _Obj("weird4", [1.0, 0.0, 0.0], movability_class="static "),  # trailing space
    ]
    client = _make_client(objs)
    r = client.get("/landmarks/near", params={"x": 0.0, "y": 0.0, "z": 0.0,
                                              "radius_m": 5.0,
                                              "include_semi_static": "true"})
    assert r.status_code == 200
    assert r.json()["total"] == 0, (
        "Hard invariant violated: non-canonical movability_class values "
        "must NOT be returned. Got: " + str(r.json())
    )


# ---------------------------------------------------------------------------
# Standalone runner (when pytest isn't available in container)
# ---------------------------------------------------------------------------

def _run_all():
    tests = [
        test_returns_static_landmark_in_radius,
        test_returns_permanent_landmark,
        test_excludes_movable,
        test_excludes_roaming,
        test_excludes_ephemeral,
        test_excludes_null_movability_class,
        test_excludes_semi_static_by_default,
        test_includes_semi_static_when_requested,
        test_radius_filter_excludes_far_landmarks,
        test_results_sorted_by_distance,
        test_pagination,
        test_limit_capped_at_200,
        test_offset_negative_clamped,
        test_empty_when_no_landmarks,
        test_works_in_serve_mode_without_proximity_index,
        test_response_includes_label_fields,
        test_response_top_level_shape,
        test_hard_invariant_chimera_movability_class_excluded,
    ]
    passed = 0
    failed = 0
    for t in tests:
        name = t.__name__
        try:
            t()
            print(f"  PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERR   {name}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed (of {len(tests)} total)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(_run_all())
