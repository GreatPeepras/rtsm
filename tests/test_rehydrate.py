"""Self-contained test of WorkingMemory.rehydrate_from_faiss().

Exercises:
1. Happy path: round-trip FAISS upsert -> save -> load -> rehydrate.
2. Edge: cold start (no persisted state) is a no-op.
3. Edge: missing embedding for an oid in metadata -> skipped.
4. Edge: bad xyz -> skipped.
5. Edge: dim mismatch -> skipped.
6. Edge: idempotency -> calling rehydrate twice doesn't double-insert.

Run from repo root with:
    PYTHONPATH=. python /home/claude/test_rehydrate.py
"""
import sys
sys.path.insert(0, "/home/claude/rtsm")

import os
import tempfile
import numpy as np

from rtsm.stores.working_memory import WorkingMemory
from rtsm.stores.proximity_index import ProximityIndex, GridSpec
from rtsm.stores.vectors.faiss_client import FaissClient


def _make_cfg(index_path, dim=8):
    return {
        "vectors": {
            "enable": True,
            "backend": "faiss",
            "dim": dim,
            "faiss": {"index_path": index_path},
        },
        "sweep_cache": {"grid_size_m": 0.25, "two_d": True, "up_axis": "z"},
        "object": {
            "promote_hits": 2,
            "stability_promote": 0.5,
            "promote_min_conf": 0.18,
            "min_label_hits": 5,
            "require_view_bins": 2,
            "max_gallery": 6,
        },
    }


def _make_wm(cfg):
    grid = GridSpec(cell_m=0.25, use_3d=False, up_axis="z")
    idx = ProximityIndex(grid)
    return WorkingMemory(cfg, index=idx), idx


def _make_emb(seed, dim):
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(dim).astype(np.float32)
    return v / (np.linalg.norm(v) + 1e-12)


def test_happy_path():
    """Persist 3 confirmed objects, restart, verify all 3 are rehydrated."""
    print("\n=== test_happy_path ===")
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = os.path.join(tmp, "test.flatip")
        cfg = _make_cfg(idx_path)

        # Session 1: insert into FAISS
        f1 = FaissClient(cfg)
        records = [
            {
                "object_id": "obj_aaa",
                "emb": _make_emb(1, 8),
                "xyz": np.array([1.0, 2.0, 0.5], dtype=np.float32),
                "label_primary": "couch",
                "label_user": None,
                "display_label": "couch",
                "movability_class": "static",
                "label_topk": ["couch", "chair"],
                "label_scores": [0.85, 0.10],
                "label_hits": [7, 2],
                "stability": 0.95,
                "created_at": 1000.0,
                "created_mono": 0.0,
            },
            {
                "object_id": "obj_bbb",
                "emb": _make_emb(2, 8),
                "xyz": np.array([3.0, 1.0, 0.4], dtype=np.float32),
                "label_primary": "table",
                "label_user": "dining_table",
                "display_label": "dining_table",
                "movability_class": "semi_static",
                "label_topk": ["table"],
                "label_scores": [0.78],
                "label_hits": [9],
                "stability": 0.88,
                "created_at": 1100.0,
                "created_mono": 0.0,
            },
            {
                "object_id": "obj_ccc",
                "emb": _make_emb(3, 8),
                "xyz": np.array([-2.0, 0.5, 0.45], dtype=np.float32),
                "label_primary": "lamp",
                "label_user": None,
                "display_label": "lamp",
                "movability_class": None,
                "label_topk": ["lamp"],
                "label_scores": [0.65],
                "label_hits": [6],
                "stability": 0.72,
                "created_at": 1200.0,
                "created_mono": 0.0,
            },
        ]
        f1.upsert_batch(records)
        assert len(f1._embeddings) == 3, f"FAISS should have 3, has {len(f1._embeddings)}"
        # Auto-save to disk via persistent_path
        assert os.path.exists(idx_path), "FAISS index should be on disk"
        assert os.path.exists(idx_path + ".meta.json"), "meta sidecar should be on disk"

        # Session 2: simulate restart - fresh FaissClient loads from disk,
        # fresh WM is empty, then rehydrate.
        f2 = FaissClient(cfg)
        assert len(f2._embeddings) == 3, f"After reload FAISS should have 3, has {len(f2._embeddings)}"
        wm, idx = _make_wm(cfg)
        assert len(list(wm.iter_objects())) == 0, "WM should start empty"

        counts = wm.rehydrate_from_faiss(f2)
        assert counts["loaded"] == 3, f"Expected 3 loaded, got {counts}"
        assert counts["skipped_no_emb"] == 0
        assert counts["skipped_bad_xyz"] == 0
        assert counts["skipped_dim_mismatch"] == 0

        # Verify each rehydrated object
        for oid, expected_label, expected_user in [
            ("obj_aaa", "couch", None),
            ("obj_bbb", "table", "dining_table"),
            ("obj_ccc", "lamp", None),
        ]:
            o = wm.get(oid)
            assert o is not None, f"oid {oid} should exist in WM"
            assert o.confirmed is True, f"oid {oid} should be confirmed"
            assert o.label_primary == expected_label
            assert o.label_user == expected_user
            assert o.emb_mean.shape == (8,)
            assert o.xyz_world.shape == (3,)
            # Proximity index should know about it (queryable)

        # Idempotency: second call should skip dups
        counts2 = wm.rehydrate_from_faiss(f2)
        assert counts2["loaded"] == 0
        assert counts2["skipped_dup"] == 3
        print(f"  OK: 3 objects rehydrated, idempotent on re-call")


def test_cold_start_noop():
    """Empty FAISS -> rehydrate is a clean no-op."""
    print("\n=== test_cold_start_noop ===")
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = os.path.join(tmp, "test.flatip")
        cfg = _make_cfg(idx_path)
        # No save yet - FaissClient starts empty
        f = FaissClient(cfg)
        wm, _ = _make_wm(cfg)
        counts = wm.rehydrate_from_faiss(f)
        assert counts["loaded"] == 0
        assert len(list(wm.iter_objects())) == 0
        print(f"  OK: cold start no-op, counts={counts}")


def test_missing_embedding():
    """Metadata has oid that's missing from embeddings dict -> skipped."""
    print("\n=== test_missing_embedding ===")
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = os.path.join(tmp, "test.flatip")
        cfg = _make_cfg(idx_path)
        f = FaissClient(cfg)
        # Inject a metadata-only entry directly (simulates corrupt state)
        f._metadata["orphan"] = {"xyz": [0, 0, 0], "label_primary": "ghost"}
        wm, _ = _make_wm(cfg)
        counts = wm.rehydrate_from_faiss(f)
        assert counts["loaded"] == 0
        assert counts["skipped_no_emb"] == 1
        assert wm.get("orphan") is None
        print(f"  OK: orphan metadata skipped, counts={counts}")


def test_bad_xyz():
    """Object with malformed xyz -> skipped, doesn't crash."""
    print("\n=== test_bad_xyz ===")
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = os.path.join(tmp, "test.flatip")
        cfg = _make_cfg(idx_path)
        f = FaissClient(cfg)
        f._embeddings["bad"] = _make_emb(99, 8)
        f._metadata["bad"] = {"xyz": "not_a_list", "label_primary": "x"}
        wm, _ = _make_wm(cfg)
        counts = wm.rehydrate_from_faiss(f)
        assert counts["loaded"] == 0
        assert counts["skipped_bad_xyz"] == 1
        print(f"  OK: bad xyz skipped, counts={counts}")


def test_dim_mismatch():
    """Embedding with wrong dim -> skipped."""
    print("\n=== test_dim_mismatch ===")
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = os.path.join(tmp, "test.flatip")
        cfg = _make_cfg(idx_path, dim=8)
        f = FaissClient(cfg)
        # First insert a valid one to set f.dim
        f.upsert_batch([{
            "object_id": "valid",
            "emb": _make_emb(1, 8),
            "xyz": np.array([0, 0, 0], dtype=np.float32),
            "label_primary": "x",
        }])
        # Now inject a bad-dim entry directly
        f._embeddings["bad"] = _make_emb(2, 16)  # wrong dim
        f._metadata["bad"] = {
            "xyz": [1, 1, 1],
            "label_primary": "y",
            "label_topk": [], "label_scores": [], "label_hits": [],
        }
        wm, _ = _make_wm(cfg)
        counts = wm.rehydrate_from_faiss(f)
        assert counts["loaded"] == 1  # the valid one
        assert counts["skipped_dim_mismatch"] == 1
        assert wm.get("valid") is not None
        assert wm.get("bad") is None
        print(f"  OK: dim mismatch skipped, counts={counts}")


def test_label_dicts_reconstructed():
    """Verify label_scores and label_hits dicts are correctly rebuilt
    from the parallel lists stored in the sidecar."""
    print("\n=== test_label_dicts_reconstructed ===")
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = os.path.join(tmp, "test.flatip")
        cfg = _make_cfg(idx_path)
        f = FaissClient(cfg)
        f.upsert_batch([{
            "object_id": "multi_label",
            "emb": _make_emb(1, 8),
            "xyz": np.array([0, 0, 0], dtype=np.float32),
            "label_primary": "couch",
            "label_topk": ["couch", "sofa", "chair"],
            "label_scores": [0.82, 0.71, 0.18],
            "label_hits": [12, 9, 3],
            "stability": 0.9,
        }])
        # Reload from disk
        f2 = FaissClient(cfg)
        wm, _ = _make_wm(cfg)
        wm.rehydrate_from_faiss(f2)
        o = wm.get("multi_label")
        assert o is not None
        assert o.label_scores == {"couch": 0.82, "sofa": 0.71, "chair": 0.18}
        assert o.label_hits == {"couch": 12, "sofa": 9, "chair": 3}
        print(f"  OK: label dicts reconstructed correctly")


def test_rehydrated_objects_are_findable_by_association_path():
    """Rehydrated objects must be discoverable via the proximity index.
    This is the actual mechanism association uses to find candidates."""
    print("\n=== test_rehydrated_objects_are_findable_by_association_path ===")
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = os.path.join(tmp, "test.flatip")
        cfg = _make_cfg(idx_path)
        f = FaissClient(cfg)
        f.upsert_batch([{
            "object_id": "findme",
            "emb": _make_emb(1, 8),
            "xyz": np.array([1.5, 2.0, 0.4], dtype=np.float32),
            "label_primary": "couch",
            "label_topk": ["couch"], "label_scores": [0.8], "label_hits": [10],
            "stability": 0.9,
        }])
        f2 = FaissClient(cfg)
        wm, pi = _make_wm(cfg)
        wm.rehydrate_from_faiss(f2)
        # Query the proximity index near the object's position
        query_xyz = np.array([1.6, 2.1, 0.4], dtype=np.float32)  # 14cm away
        # Use nearby_ids - this is what association uses to fetch candidates
        nearby_oids = pi.nearby_ids(query_xyz, rings=1)
        assert "findme" in nearby_oids, (
            f"Rehydrated object should be in proximity index, got: {nearby_oids}"
        )
        print(f"  OK: rehydrated object discoverable via proximity index")


def test_pose_state_round_trip():
    """pose_state_at_observation tag must survive across persistence.

    Two cases:
      (a) Metadata WITH the field -> rehydrated value preserved.
      (b) Metadata WITHOUT the field (legacy sidecar) -> defaults to 'on_floor'.
    """
    print("\n=== test_pose_state_round_trip ===")
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = os.path.join(tmp, "test.flatip")
        cfg = _make_cfg(idx_path)
        f = FaissClient(cfg)
        # (a) Object with explicit elevated tag
        # (b) Object with no tag at all (legacy)
        f.upsert_batch([
            {
                "object_id": "elev_obj",
                "emb": _make_emb(1, 8),
                "xyz": np.array([0.5, 0.5, 1.2], dtype=np.float32),
                "label_primary": "pencil_holder",
                "label_topk": ["pencil_holder"], "label_scores": [0.9], "label_hits": [4],
                "stability": 0.85,
                "pose_state_at_observation": "elevated",  # the tag
            },
            {
                "object_id": "legacy_obj",
                "emb": _make_emb(2, 8),
                "xyz": np.array([1.0, 1.0, 0.3], dtype=np.float32),
                "label_primary": "rug",
                "label_topk": ["rug"], "label_scores": [0.7], "label_hits": [8],
                "stability": 0.9,
                # no pose_state_at_observation field
            },
        ])
        # Reload + rehydrate
        f2 = FaissClient(cfg)
        wm, _ = _make_wm(cfg)
        wm.rehydrate_from_faiss(f2)
        elev = wm.get("elev_obj")
        legacy = wm.get("legacy_obj")
        assert elev is not None and legacy is not None
        assert elev.pose_state_at_observation == "elevated", \
            f"Expected 'elevated', got {elev.pose_state_at_observation!r}"
        assert legacy.pose_state_at_observation == "on_floor", \
            f"Expected default 'on_floor', got {legacy.pose_state_at_observation!r}"
        print(f"  OK: elevated tag preserved, legacy defaults to on_floor")


if __name__ == "__main__":
    test_happy_path()
    test_cold_start_noop()
    test_missing_embedding()
    test_bad_xyz()
    test_dim_mismatch()
    test_label_dicts_reconstructed()
    test_rehydrated_objects_are_findable_by_association_path()
    test_pose_state_round_trip()
    print("\nAll tests passed.")
