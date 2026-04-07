"""Tests for the embedded MCP server (direct Python dispatch)."""
from __future__ import annotations

import numpy as np
import pytest
from prometheus_client import CollectorRegistry

from rtsm.stores.working_memory import WorkingMemory, ObjectState
from rtsm.stores.proximity_index import ProximityIndex, GridSpec
from rtsm.io.mcp_embedded import _dispatch


def _make_object(oid: str, xyz: list[float], label: str = "object") -> ObjectState:
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


def _build_wm(objects: list[ObjectState]) -> WorkingMemory:
    grid = GridSpec(cell_m=0.25, use_3d=False, up_axis="y")
    pi = ProximityIndex(grid, per_cell_cap=64, neighbors_max=128)
    cfg = {
        "object": {"stability_hit": 0.05, "confirm_stability": 0.5,
                    "confirm_views": 2, "promo_min_hits": 3,
                    "proto_ttl_s": 30.0, "max_gallery": 5,
                    "gallery_cos_thresh": 0.85, "max_crops": 8},
        "vectors": {"flush_period_s": 10.0, "min_delta_cos": 0.05,
                    "min_delta_m": 0.1},
    }
    wm = WorkingMemory(cfg, index=pi)
    for obj in objects:
        wm._map[obj.id] = obj
        pi.insert(obj.id, obj.xyz_world)
    return wm


@pytest.fixture
def wm():
    return _build_wm([
        _make_object("obj_mug", [1.0, 0.0, 1.0], "mug"),
        _make_object("obj_book", [1.2, 0.0, 1.1], "book"),
        _make_object("obj_chair", [5.0, 0.0, 5.0], "chair"),
    ])


# ── list_objects ──

def test_list_objects(wm):
    result = _dispatch("rtsm.list_objects", {}, wm, None, None)
    assert result["count"] == 3
    ids = {o["id"] for o in result["objects"]}
    assert ids == {"obj_mug", "obj_book", "obj_chair"}


# ── get_object ──

def test_get_object_found(wm):
    result = _dispatch("rtsm.get_object", {"object_id": "obj_mug"}, wm, None, None)
    assert result["id"] == "obj_mug"
    assert result["label_primary"] == "mug"
    assert result["confirmed"] is True
    assert "cov_world" in result


def test_get_object_not_found(wm):
    result = _dispatch("rtsm.get_object", {"object_id": "nonexistent"}, wm, None, None)
    assert result["error"] == "not_found"


def test_get_object_with_vectors(wm):
    result = _dispatch("rtsm.get_object", {"object_id": "obj_mug", "include_vectors": True}, wm, None, None)
    assert "emb_mean" in result
    assert isinstance(result["emb_mean"], list)
    assert len(result["emb_mean"]) == 512


# ── spatial_query ──

def test_spatial_query_finds_nearby(wm):
    result = _dispatch("rtsm.spatial_query", {"x": 1.0, "y": 0.0, "z": 1.0, "radius_m": 0.5}, wm, None, None)
    ids = [r["id"] for r in result["results"]]
    assert "obj_mug" in ids
    assert "obj_book" in ids
    assert "obj_chair" not in ids


def test_spatial_query_sorted_by_distance(wm):
    result = _dispatch("rtsm.spatial_query", {"x": 1.0, "y": 0.0, "z": 1.0, "radius_m": 1.0}, wm, None, None)
    distances = [r["distance_m"] for r in result["results"]]
    assert distances == sorted(distances)


def test_spatial_query_tight_radius(wm):
    result = _dispatch("rtsm.spatial_query", {"x": 1.0, "y": 0.0, "z": 1.0, "radius_m": 0.05}, wm, None, None)
    ids = [r["id"] for r in result["results"]]
    assert "obj_mug" in ids
    assert "obj_book" not in ids


def test_spatial_query_no_index():
    cfg = {
        "object": {"stability_hit": 0.05, "confirm_stability": 0.5,
                    "confirm_views": 2, "promo_min_hits": 3,
                    "proto_ttl_s": 30.0, "max_gallery": 5,
                    "gallery_cos_thresh": 0.85, "max_crops": 8},
        "vectors": {"flush_period_s": 10.0, "min_delta_cos": 0.05,
                    "min_delta_m": 0.1},
    }
    wm = WorkingMemory(cfg, index=None)
    result = _dispatch("rtsm.spatial_query", {"x": 0, "y": 0, "z": 0}, wm, None, None)
    assert result["error"] == "unavailable"


# ── semantic_query (no CLIP/vectors) ──

def test_semantic_query_no_clip(wm):
    result = _dispatch("rtsm.semantic_query", {"query": "mug"}, wm, None, None)
    assert result["error"] == "unavailable"


# ── relational_query (no CLIP/vectors) ──

def test_relational_query_no_clip(wm):
    result = _dispatch("rtsm.relational_query", {"query": "mug"}, wm, None, None)
    assert result["error"] == "unavailable"


# ── status ──

def test_status(wm):
    result = _dispatch("rtsm.status", {}, wm, None, None)
    assert result["health"]["status"] == "ok"
    assert "stats" in result


# ── unknown tool ──

def test_unknown_tool(wm):
    with pytest.raises(ValueError, match="Unknown tool"):
        _dispatch("rtsm.nonexistent", {}, wm, None, None)


# ── MCP mount on FastAPI ──

def test_mcp_mount_on_fastapi(wm):
    """Verify MCP routes are mounted when mcp_enabled=True."""
    from fastapi.testclient import TestClient
    from rtsm.api.server import create_app

    app = create_app(
        working_memory=wm,
        registry=CollectorRegistry(),
        mcp_enabled=True,
    )
    # Check that the /mcp route exists by looking at app routes
    route_paths = []
    for route in app.routes:
        path = getattr(route, "path", None)
        if path:
            route_paths.append(path)
    assert "/mcp" in route_paths or any("/mcp" in str(r) for r in app.routes)


def test_mcp_not_mounted_when_disabled(wm):
    """Verify MCP routes are NOT mounted when mcp_enabled=False."""
    from fastapi.testclient import TestClient
    from rtsm.api.server import create_app

    app = create_app(
        working_memory=wm,
        registry=CollectorRegistry(),
        mcp_enabled=False,
    )
    route_paths = [getattr(r, "path", "") for r in app.routes]
    assert "/mcp" not in route_paths
