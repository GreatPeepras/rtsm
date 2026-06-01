"""Unit tests for WorkingMemory.suggest_merges (2026-06-02).

Surfaces high-confidence Mode B duplicate candidates via cosine + spatial
proximity. Read-only operation; does not mutate WM or FAISS.

Test design notes:
  - We bypass the full observation pipeline by directly mutating ObjectState
    fields after create_object. The suggest_merges path only reads fields
    that are populated correctly by create_object (emb_mean, xyz_world,
    label_primary, etc.), so we just need to set hits + confirmed manually
    to skip the normal promote flow.
  - persist_galleries: False keeps tests from touching disk.
"""
from __future__ import annotations

import numpy as np
import pytest

from rtsm.stores.working_memory import WorkingMemory


# --------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------- #

def _make_wm() -> WorkingMemory:
    cfg = {
        "object": {
            "promote_hits": 1,
            "stability_promote": 0.0,
            "promote_min_conf": 0.0,
            "min_label_hits": 1,
            "require_view_bins": 1,
            "persist_galleries": False,
        },
        "view": {"az_bins": 8, "el_bins": 3},
        "pose": {},
        "ltm": {},
        "assoc": {"gate_dist_base_m": 0.20},
    }
    return WorkingMemory(cfg)


def _l2(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float32)
    n = float(np.linalg.norm(v) + 1e-12)
    return (v / n).astype(np.float32)


def _spawn(
    wm: WorkingMemory,
    xyz,
    emb: np.ndarray,
    label: str | None = None,
    *,
    hits: int = 5,
    confirm: bool = True,
    label_user: str | None = None,
    reference_image_path: str | None = None,
) -> str:
    """Create an object and force it into a stable, confirmed state.

    Bypasses the normal multi-observation promote pipeline so individual
    tests can set up exact starting conditions.
    """
    p_world = np.array(xyz, dtype=np.float32)
    emb_vis = _l2(emb)
    label_topk = [(label, 0.5)] if label is not None else None
    oid = wm.create_object(
        p_world,
        emb_vis,
        label_topk=label_topk,
        view_dir_cam=np.array([0.0, 0.0, 1.0], dtype=np.float32),
    )
    assert oid is not None, "create_object returned None (pose_state issue?)"
    o = wm._map[oid]
    o.hits = int(hits)
    o.confirmed = bool(confirm)
    o.stability = 1.0
    if label_user is not None:
        o.label_user = label_user
    if reference_image_path is not None:
        o.reference_image_path = reference_image_path
    return oid


def _perturb(base: np.ndarray, scale: float, rng: np.random.Generator) -> np.ndarray:
    """Make a vector close to `base` with controllable cosine distance.

    Smaller scale => closer to base => higher cosine.
    """
    return _l2(base + rng.standard_normal(base.shape).astype(np.float32) * scale)


# --------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------- #

def test_empty_corpus_returns_empty():
    wm = _make_wm()
    r = wm.suggest_merges()
    assert r["candidates"] == []
    assert r["total_pairs_above_thresholds"] == 0
    assert r["scanned_objects"] == 0
    assert r["returned"] == 0


def test_single_object_returns_empty():
    wm = _make_wm()
    rng = np.random.default_rng(0)
    _spawn(wm, [0, 0, 0], rng.standard_normal(512).astype(np.float32), "chair")
    r = wm.suggest_merges()
    assert r["candidates"] == []
    assert r["scanned_objects"] == 1


def test_far_apart_excluded():
    """Two objects with identical embeddings but 8.6m apart fail the
    distance gate."""
    wm = _make_wm()
    rng = np.random.default_rng(1)
    base = rng.standard_normal(512).astype(np.float32)
    _spawn(wm, [0, 0, 0], base, "chair")
    _spawn(wm, [5, 5, 5], base, "chair")
    r = wm.suggest_merges(cos_threshold=0.95, dist_threshold_m=1.0)
    assert r["candidates"] == []
    assert r["total_pairs_above_thresholds"] == 0


def test_dissimilar_embeddings_excluded():
    """Two objects 10cm apart but orthogonal in embedding space fail the
    cosine gate."""
    wm = _make_wm()
    a_emb = np.zeros(512, dtype=np.float32); a_emb[0] = 1.0
    b_emb = np.zeros(512, dtype=np.float32); b_emb[1] = 1.0
    _spawn(wm, [0, 0, 0], a_emb, "chair")
    _spawn(wm, [0.1, 0, 0], b_emb, "chair")
    r = wm.suggest_merges()
    assert r["candidates"] == []


def test_close_in_both_returns_pair():
    """Happy path: two objects close in both embedding and position."""
    wm = _make_wm()
    rng = np.random.default_rng(2)
    base = _l2(rng.standard_normal(512).astype(np.float32))
    perturbed = _perturb(base, scale=0.02, rng=rng)
    a = _spawn(wm, [0, 0, 0], base, "chair", hits=10)
    b = _spawn(wm, [0.5, 0, 0], perturbed, "chair", hits=3)

    r = wm.suggest_merges()
    assert r["returned"] == 1
    assert r["total_pairs_above_thresholds"] == 1
    cand = r["candidates"][0]
    assert {cand["a_oid"], cand["b_oid"]} == {a, b}
    assert cand["cosine"] >= 0.95
    assert cand["distance_m"] < 1.0
    # Hits-weighted suggested winner = a (10 vs 3, no other signals).
    assert cand["suggested_winner_oid"] == a


def test_require_same_label_filters_different_primaries():
    """Two close objects with different label_primary are filtered when
    require_same_label=True."""
    wm = _make_wm()
    rng = np.random.default_rng(3)
    base = _l2(rng.standard_normal(512).astype(np.float32))
    _spawn(wm, [0, 0, 0], base, "chair", hits=5)
    _spawn(wm, [0.3, 0, 0], base, "stool", hits=5)

    r_loose = wm.suggest_merges(require_same_label=False)
    assert r_loose["returned"] == 1
    assert r_loose["candidates"][0]["same_display_label"] is False

    r_strict = wm.suggest_merges(require_same_label=True)
    assert r_strict["candidates"] == []


def test_same_label_user_satisfies_same_label_gate():
    """label_user is checked alongside label_primary -- pinned names
    can rescue a pair whose primary labels disagree."""
    wm = _make_wm()
    rng = np.random.default_rng(4)
    base = _l2(rng.standard_normal(512).astype(np.float32))
    _spawn(wm, [0, 0, 0], base, "chair", hits=5, label_user="reading chair")
    _spawn(wm, [0.3, 0, 0], base, "stool", hits=5, label_user="reading chair")

    r = wm.suggest_merges(require_same_label=True)
    assert r["returned"] == 1
    cand = r["candidates"][0]
    assert cand["same_display_label"] is True
    assert cand["a_display_label"] == "reading chair"
    assert cand["b_display_label"] == "reading chair"


def test_unconfirmed_excluded_by_default():
    """Proto objects are out of scope unless include_unconfirmed=True."""
    wm = _make_wm()
    rng = np.random.default_rng(5)
    base = _l2(rng.standard_normal(512).astype(np.float32))
    _spawn(wm, [0, 0, 0], base, "chair", hits=5, confirm=False)
    _spawn(wm, [0.3, 0, 0], base, "chair", hits=5, confirm=True)

    r = wm.suggest_merges()
    assert r["scanned_objects"] == 1
    assert r["candidates"] == []


def test_include_unconfirmed_includes_proto():
    wm = _make_wm()
    rng = np.random.default_rng(6)
    base = _l2(rng.standard_normal(512).astype(np.float32))
    _spawn(wm, [0, 0, 0], base, "chair", hits=5, confirm=False)
    _spawn(wm, [0.3, 0, 0], base, "chair", hits=5, confirm=True)

    r = wm.suggest_merges(include_unconfirmed=True)
    assert r["scanned_objects"] == 2
    assert r["returned"] == 1


def test_limit_truncates_but_total_count_preserved():
    """5 colocated identical-embedding objects -> 10 pairs; limit=3 only
    truncates the response, total stays accurate."""
    wm = _make_wm()
    rng = np.random.default_rng(7)
    base = _l2(rng.standard_normal(512).astype(np.float32))
    for i in range(5):
        _spawn(wm, [i * 0.05, 0, 0], base, "chair", hits=5)

    r = wm.suggest_merges(limit=3)
    assert r["returned"] == 3
    assert len(r["candidates"]) == 3
    assert r["total_pairs_above_thresholds"] == 10  # C(5, 2)
    assert r["scanned_objects"] == 5


def test_sort_order_cosine_desc_then_dist_asc():
    """Three objects: pair (a,b) has higher cosine than pair (a,c). The
    response should list (a,b) before (a,c)."""
    wm = _make_wm()
    rng = np.random.default_rng(8)
    base = _l2(rng.standard_normal(512).astype(np.float32))
    very_close = _perturb(base, scale=0.005, rng=rng)
    less_close = _perturb(base, scale=0.05, rng=rng)
    _spawn(wm, [0, 0, 0], base, "chair", hits=5)
    _spawn(wm, [0.1, 0, 0], very_close, "chair", hits=5)
    _spawn(wm, [0.2, 0, 0], less_close, "chair", hits=5)

    r = wm.suggest_merges(cos_threshold=0.5, dist_threshold_m=2.0)
    assert r["returned"] >= 2
    cosines = [c["cosine"] for c in r["candidates"]]
    assert cosines == sorted(cosines, reverse=True), (
        f"candidates not sorted by cosine desc: {cosines}"
    )


def test_thresholds_echoed_in_response():
    """Thresholds block round-trips so callers can confirm what they got."""
    wm = _make_wm()
    r = wm.suggest_merges(
        cos_threshold=0.97,
        dist_threshold_m=0.5,
        require_same_label=True,
        limit=10,
        include_unconfirmed=True,
    )
    t = r["thresholds"]
    assert t["cos_threshold"] == 0.97
    assert t["dist_threshold_m"] == 0.5
    assert t["require_same_label"] is True
    assert t["limit"] == 10
    assert t["include_unconfirmed"] is True


# --------------------------------------------------------------------- #
# suggested_winner heuristic
# --------------------------------------------------------------------- #

def test_suggested_winner_prefers_reference_image():
    """Reference image trumps hits."""
    wm = _make_wm()
    rng = np.random.default_rng(9)
    base = _l2(rng.standard_normal(512).astype(np.float32))
    a = _spawn(wm, [0, 0, 0], base, "chair", hits=5,
               reference_image_path="/tmp/canonical.jpg")
    b = _spawn(wm, [0.3, 0, 0], base, "chair", hits=50)  # way more hits

    r = wm.suggest_merges()
    assert r["candidates"][0]["suggested_winner_oid"] == a


def test_suggested_winner_prefers_label_user_over_hits():
    """label_user pin trumps hits."""
    wm = _make_wm()
    rng = np.random.default_rng(10)
    base = _l2(rng.standard_normal(512).astype(np.float32))
    a = _spawn(wm, [0, 0, 0], base, "chair", hits=50)
    b = _spawn(wm, [0.3, 0, 0], base, "chair", hits=5,
               label_user="reading chair")

    r = wm.suggest_merges()
    assert r["candidates"][0]["suggested_winner_oid"] == b


def test_suggested_winner_falls_back_to_hits():
    """No reference, no label_user -- highest hits wins."""
    wm = _make_wm()
    rng = np.random.default_rng(11)
    base = _l2(rng.standard_normal(512).astype(np.float32))
    a = _spawn(wm, [0, 0, 0], base, "chair", hits=20)
    b = _spawn(wm, [0.3, 0, 0], base, "chair", hits=5)

    r = wm.suggest_merges()
    assert r["candidates"][0]["suggested_winner_oid"] == a


def test_suggested_winner_reference_precedence_both_or_neither():
    """When both have references, the heuristic falls through to label_user
    / hits / stability."""
    wm = _make_wm()
    rng = np.random.default_rng(12)
    base = _l2(rng.standard_normal(512).astype(np.float32))
    a = _spawn(wm, [0, 0, 0], base, "chair", hits=5,
               reference_image_path="/tmp/a.jpg")
    b = _spawn(wm, [0.3, 0, 0], base, "chair", hits=20,
               reference_image_path="/tmp/b.jpg")

    r = wm.suggest_merges()
    # Both have refs -> tied -> falls through to hits -> b wins.
    assert r["candidates"][0]["suggested_winner_oid"] == b
