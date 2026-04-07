"""Integration tests for the /search/spatial REST endpoint."""
from __future__ import annotations

import numpy as np
import pytest
from fastapi.testclient import TestClient
from prometheus_client import CollectorRegistry

from rtsm.stores.working_memory import WorkingMemory, ObjectState
from rtsm.stores.proximity_index import ProximityIndex, GridSpec
from rtsm.api.server import create_app


def _make_object(oid: str, xyz: list[float], label: str = "object") -> ObjectState:
    """Create a minimal ObjectState for testing."""
    now = 1000.0
    return ObjectState(
        id=oid,
        xyz_world=np.array(xyz, dtype=np.float32),
        cov_world=np.array([0.01, 0.01, 0.01], dtype=np.float32),
        emb_mean=np.zeros(512, dtype=np.float32),
        emb_gallery=np.zeros((0, 512), dtype=np.float16),
        view_bins={},
        label_scores={label: 1.0},
        label_primary=label,
        stability=0.8,
        hits=5,
        confirmed=True,
        created_mono=now,
        created_wall_utc=now,
        last_seen_mono=now,
        last_seen_wall_utc=now,
        last_seen_px=None,
        last_upsert_wall_utc=0.0,
        last_upsert_mono=0.0,
        last_upsert_emb=None,
        last_upsert_xyz=None,
        image_crops=[],
        last_update_frame_id=None,
        _dim=512,
    )


def _build_wm_with_objects(objects: list[ObjectState]) -> WorkingMemory:
    """Build WorkingMemory + ProximityIndex with pre-inserted objects."""
    grid = GridSpec(cell_m=0.25, use_3d=False, up_axis="y")
    pi = ProximityIndex(grid, per_cell_cap=64, neighbors_max=128)
    cfg = {"object": {"stability_hit": 0.05, "confirm_stability": 0.5,
                       "confirm_views": 2, "promo_min_hits": 3,
                       "proto_ttl_s": 30.0, "max_gallery": 5,
                       "gallery_cos_thresh": 0.85, "max_crops": 8},
           "vectors": {"flush_period_s": 10.0, "min_delta_cos": 0.05,
                       "min_delta_m": 0.1}}
    wm = WorkingMemory(cfg, index=pi)
    # Directly insert objects into WM internals for testing
    for obj in objects:
        wm._map[obj.id] = obj
        if pi is not None:
            pi.insert(obj.id, obj.xyz_world)
    return wm


@pytest.fixture
def client_with_objects():
    """TestClient with 3 objects at known positions."""
    objects = [
        _make_object("obj_a", [1.0, 0.0, 1.0], "mug"),
        _make_object("obj_b", [1.3, 0.0, 1.1], "book"),     # ~0.32m from obj_a
        _make_object("obj_c", [5.0, 0.0, 5.0], "chair"),    # ~5.66m from obj_a
    ]
    wm = _build_wm_with_objects(objects)
    app = create_app(working_memory=wm, registry=CollectorRegistry())
    return TestClient(app)


@pytest.fixture
def client_no_index():
    """TestClient with WM that has no ProximityIndex."""
    cfg = {"object": {"stability_hit": 0.05, "confirm_stability": 0.5,
                       "confirm_views": 2, "promo_min_hits": 3,
                       "proto_ttl_s": 30.0, "max_gallery": 5,
                       "gallery_cos_thresh": 0.85, "max_crops": 8},
           "vectors": {"flush_period_s": 10.0, "min_delta_cos": 0.05,
                       "min_delta_m": 0.1}}
    wm = WorkingMemory(cfg, index=None)
    app = create_app(working_memory=wm, registry=CollectorRegistry())
    return TestClient(app)


def test_spatial_basic(client_with_objects):
    """Objects near (1, 0, 1) with radius 0.5m should include obj_a and obj_b."""
    resp = client_with_objects.get("/search/spatial", params={"x": 1.0, "y": 0.0, "z": 1.0, "radius_m": 0.5})
    assert resp.status_code == 200
    data = resp.json()
    assert data["center"] == [1.0, 0.0, 1.0]
    ids = [r["id"] for r in data["results"]]
    assert "obj_a" in ids
    assert "obj_b" in ids
    assert "obj_c" not in ids


def test_spatial_radius_filter(client_with_objects):
    """Tight radius should exclude obj_b (0.32m away)."""
    resp = client_with_objects.get("/search/spatial", params={"x": 1.0, "y": 0.0, "z": 1.0, "radius_m": 0.1})
    assert resp.status_code == 200
    data = resp.json()
    ids = [r["id"] for r in data["results"]]
    assert "obj_a" in ids
    assert "obj_b" not in ids


def test_spatial_sorted_by_distance(client_with_objects):
    """Results should be sorted by distance ascending."""
    resp = client_with_objects.get("/search/spatial", params={"x": 1.0, "y": 0.0, "z": 1.0, "radius_m": 1.0})
    assert resp.status_code == 200
    data = resp.json()
    distances = [r["distance_m"] for r in data["results"]]
    assert distances == sorted(distances)


def test_spatial_no_index(client_no_index):
    """Should return 503 when no ProximityIndex is configured."""
    resp = client_no_index.get("/search/spatial", params={"x": 0, "y": 0, "z": 0})
    assert resp.status_code == 503
