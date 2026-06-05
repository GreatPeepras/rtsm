"""Self-contained tests for reference snapshot integration (2026-05-29).

Exercises:
1. ObjectState gained reference_image_path + reference_emb (defaults None).
2. set_object_reference() helper: set + clear + dim mismatch.
3. set_object_reference() schedules an LTM upsert for confirmed objects.
4. Force-flush payload includes both reference fields.
5. Normal-path payload includes both reference fields (after heap drain).
6. Rehydrate reads reference fields from sidecar.
7. Rehydrate seeds emb_gallery from reference_emb (the cold-start win).
8. Rehydrate is tolerant of legacy sidecars without reference fields.
9. End-to-end: create -> set reference -> upsert -> save -> load -> rehydrate
   -> reference fields preserved, emb_gallery seeded with the right vector.

Run from the rtsm repo root inside the container:
    docker exec -w /workspace/rtsm rtsm-dev python3 test_reference_image.py
"""
import sys
# Path setup: work both inside the container (/workspace/rtsm)
# and from a host checkout (~/rtsm).
for _p in ("/workspace/rtsm", "."):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import os
import time
import tempfile
import numpy as np

from rtsm.stores.working_memory import WorkingMemory, ObjectState
from rtsm.stores.proximity_index import ProximityIndex, GridSpec
from rtsm.stores.vectors.faiss_client import FaissClient


# --------------------------------------------------------------------------- #
# Test helpers (mirror test_rehydrate.py / test_end_to_end_persistence.py)    #
# --------------------------------------------------------------------------- #

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
        "ltm": {
            "ltm_min_view_bins": 1,
            "min_period_s": 0.001,
            "force_period_s": 0.01,
        },
    }


def _make_wm(cfg):
    grid = GridSpec(cell_m=0.25, use_3d=False, up_axis="z")
    idx = ProximityIndex(grid)
    return WorkingMemory(cfg, index=idx), idx


def _emb(seed, dim):
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(dim).astype(np.float32)
    return v / (np.linalg.norm(v) + 1e-12)


def _promoted_object(wm, *, label="couch", seed=1, xyz=(0.5, 0.5, 0.3)):
    """Create a fully-promoted, confirmed object in WM. Returns oid."""
    e = _emb(seed, 8)
    oid = wm.create_object(
        np.array(xyz, dtype=np.float32),
        e,
        label_topk=[(label, 0.85)],
        view_dir_cam=np.array([0, 0, 1], dtype=np.float32),
    )
    o = wm.get(oid)
    # Force-promote: bypass the gates by directly seeding the state we
    # need. We trust maybe_promote is tested elsewhere (test_rehydrate /
    # test_end_to_end_persistence); here we just need a confirmed object.
    o.confirmed = True
    o.hits = max(5, wm.promote_hits)
    o.stability = 0.95
    o.label_hits[label] = 10
    # Make view_bins satisfy the LTM diversity gate (ltm_min_view_bins=1 in cfg).
    o.view_bins[1] = e.copy()
    return oid


# --------------------------------------------------------------------------- #
# 1. ObjectState dataclass                                                    #
# --------------------------------------------------------------------------- #

def test_objectstate_has_reference_fields():
    print("\n=== test_objectstate_has_reference_fields ===")
    # ObjectState uses slots; defaults must be set by the dataclass machinery.
    annotations = ObjectState.__annotations__
    assert "reference_image_path" in annotations, (
        "ObjectState missing reference_image_path field"
    )
    assert "reference_emb" in annotations, (
        "ObjectState missing reference_emb field"
    )
    # Instantiate one and check defaults.
    o = ObjectState(
        id="x",
        xyz_world=np.zeros(3, dtype=np.float32),
        cov_world=np.array([0.02, 0.02, 0.04], dtype=np.float32),
        emb_mean=_emb(1, 8),
        emb_gallery=np.zeros((0, 8), dtype=np.float16),
        view_bins={},
        label_scores={},
        label_hits={},
        label_primary=None,
        stability=0.0,
        hits=0,
        confirmed=False,
        created_mono=0.0,
        created_wall_utc=0.0,
        last_seen_mono=0.0,
        last_seen_wall_utc=0.0,
        last_seen_px=None,
        last_upsert_wall_utc=0.0,
        last_upsert_mono=0.0,
        last_upsert_emb=None,
        last_upsert_xyz=None,
        image_crops=[],
        last_update_frame_id=None,
        _dim=8,
    )
    assert o.reference_image_path is None, "reference_image_path default must be None"
    assert o.reference_emb is None, "reference_emb default must be None"
    print("  OK: fields present, defaults are None")


# --------------------------------------------------------------------------- #
# 2-3. set_object_reference helper                                            #
# --------------------------------------------------------------------------- #

def test_set_object_reference_set_and_clear():
    print("\n=== test_set_object_reference_set_and_clear ===")
    with tempfile.TemporaryDirectory() as tmp:
        cfg = _make_cfg(os.path.join(tmp, "t.flatip"))
        wm, _ = _make_wm(cfg)
        oid = _promoted_object(wm)
        ref_emb = _emb(42, 8)

        o = wm.set_object_reference(
            oid, image_path="/tmp/ref.jpg", embedding=ref_emb,
        )
        assert o is not None, "set_object_reference returned None for existing oid"
        assert o.reference_image_path == "/tmp/ref.jpg"
        assert o.reference_emb is not None
        assert o.reference_emb.shape == (8,)
        # Defensive L2-norm: result should be unit.
        assert abs(float(np.linalg.norm(o.reference_emb)) - 1.0) < 1e-5, (
            f"reference_emb not L2-normalized: norm={np.linalg.norm(o.reference_emb)}"
        )

        # Clear: passing None for both fields wipes them.
        o2 = wm.set_object_reference(oid, image_path=None, embedding=None)
        assert o2.reference_image_path is None
        assert o2.reference_emb is None
        print("  OK: set + clear roundtrip")


def test_set_object_reference_dim_mismatch():
    print("\n=== test_set_object_reference_dim_mismatch ===")
    with tempfile.TemporaryDirectory() as tmp:
        cfg = _make_cfg(os.path.join(tmp, "t.flatip"))
        wm, _ = _make_wm(cfg)
        oid = _promoted_object(wm)
        wrong_dim_emb = _emb(1, 16)  # object dim is 8
        try:
            wm.set_object_reference(
                oid, image_path="/tmp/x.jpg", embedding=wrong_dim_emb,
            )
        except ValueError as e:
            assert "dim" in str(e).lower()
            print(f"  OK: rejected dim mismatch ({e})")
            return
        raise AssertionError("Expected ValueError on dim mismatch, none raised")


def test_set_object_reference_unknown_oid():
    print("\n=== test_set_object_reference_unknown_oid ===")
    with tempfile.TemporaryDirectory() as tmp:
        cfg = _make_cfg(os.path.join(tmp, "t.flatip"))
        wm, _ = _make_wm(cfg)
        result = wm.set_object_reference(
            "no_such_oid", image_path="/tmp/x.jpg", embedding=_emb(1, 8),
        )
        assert result is None, "Expected None for unknown oid"
        print("  OK: returns None for unknown oid")


def test_set_object_reference_schedules_upsert():
    """Setting a reference on a confirmed object should push to _ltm_heap."""
    print("\n=== test_set_object_reference_schedules_upsert ===")
    with tempfile.TemporaryDirectory() as tmp:
        cfg = _make_cfg(os.path.join(tmp, "t.flatip"))
        wm, _ = _make_wm(cfg)
        oid = _promoted_object(wm)
        # Drain whatever's on the heap (the create/promote path may have pushed).
        wm._ltm_heap.clear()
        wm.set_object_reference(
            oid, image_path="/tmp/r.jpg", embedding=_emb(7, 8),
        )
        assert any(entry[1] == oid for entry in wm._ltm_heap), (
            f"Expected oid={oid[:8]} on _ltm_heap after set_object_reference"
        )
        print("  OK: confirmed-object reference triggers LTM upsert")


# --------------------------------------------------------------------------- #
# 4-5. Upsert payloads include reference fields                               #
# --------------------------------------------------------------------------- #

def test_force_flush_payload_includes_reference():
    print("\n=== test_force_flush_payload_includes_reference ===")
    with tempfile.TemporaryDirectory() as tmp:
        cfg = _make_cfg(os.path.join(tmp, "t.flatip"))
        wm, _ = _make_wm(cfg)
        oid = _promoted_object(wm)
        ref_emb = _emb(33, 8)
        wm.set_object_reference(
            oid, image_path="/mnt/rtsm-data/refs/abc.jpg", embedding=ref_emb,
        )
        payloads = wm.collect_ready_for_upsert(force_all=True)
        assert len(payloads) == 1, f"Expected 1 payload, got {len(payloads)}"
        p = payloads[0]
        assert "reference_image_path" in p, "force-flush payload missing reference_image_path"
        assert "reference_emb" in p, "force-flush payload missing reference_emb"
        assert p["reference_image_path"] == "/mnt/rtsm-data/refs/abc.jpg"
        assert isinstance(p["reference_emb"], list), (
            f"reference_emb must serialize as list, got {type(p['reference_emb'])}"
        )
        assert len(p["reference_emb"]) == 8
        # Round-trip the list back to an array and check it's the same vector.
        round_trip = np.asarray(p["reference_emb"], dtype=np.float32)
        cos = float(np.dot(round_trip, wm.get(oid).reference_emb))
        assert cos > 0.999, f"reference_emb survived payload roundtrip (cos={cos})"
        print("  OK: force-flush payload includes reference fields")


def test_force_flush_payload_with_no_reference():
    """Object without a reference should serialize None, not crash."""
    print("\n=== test_force_flush_payload_with_no_reference ===")
    with tempfile.TemporaryDirectory() as tmp:
        cfg = _make_cfg(os.path.join(tmp, "t.flatip"))
        wm, _ = _make_wm(cfg)
        oid = _promoted_object(wm)  # no reference set
        payloads = wm.collect_ready_for_upsert(force_all=True)
        assert len(payloads) == 1
        p = payloads[0]
        assert p["reference_image_path"] is None
        assert p["reference_emb"] is None
        print("  OK: None-references serialize cleanly")


def test_normal_path_payload_includes_reference():
    print("\n=== test_normal_path_payload_includes_reference ===")
    with tempfile.TemporaryDirectory() as tmp:
        cfg = _make_cfg(os.path.join(tmp, "t.flatip"))
        wm, _ = _make_wm(cfg)
        oid = _promoted_object(wm)
        # Set reference (also pushes to _ltm_heap).
        ref_emb = _emb(7, 8)
        wm.set_object_reference(
            oid, image_path="/mnt/rtsm-data/refs/n.jpg", embedding=ref_emb,
        )
        # min_period_s = 0.001 in the test cfg; sleep just past it.
        time.sleep(0.01)
        payloads = wm.collect_ready_for_upsert(force_all=False)
        assert len(payloads) == 1, (
            f"Expected normal-path payload, got {len(payloads)}; _ltm_heap may be empty"
        )
        p = payloads[0]
        assert p["reference_image_path"] == "/mnt/rtsm-data/refs/n.jpg"
        assert isinstance(p["reference_emb"], list)
        assert len(p["reference_emb"]) == 8
        # Normal path also carries "updated_at" — sanity-check we didn't break it.
        assert "updated_at" in p
        print("  OK: normal-path payload includes reference fields")


# --------------------------------------------------------------------------- #
# 6-8. Rehydrate                                                              #
# --------------------------------------------------------------------------- #

def test_rehydrate_reads_reference_fields():
    print("\n=== test_rehydrate_reads_reference_fields ===")
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = os.path.join(tmp, "t.flatip")
        cfg = _make_cfg(idx_path)

        # Session 1: write a confirmed object with a reference to FAISS.
        f1 = FaissClient(cfg)
        ref_emb = _emb(99, 8)
        f1.upsert_batch([{
            "object_id": "ref_obj",
            "emb": _emb(1, 8),
            "xyz": np.array([1.0, 2.0, 0.5], dtype=np.float32),
            "label_primary": "rubber_duck",
            "label_topk": ["rubber_duck"], "label_scores": [0.9], "label_hits": [12],
            "stability": 0.95,
            "reference_image_path": "/mnt/rtsm-data/refs/ref_obj.jpg",
            "reference_emb": ref_emb.tolist(),
        }])
        assert os.path.exists(idx_path), "sidecar must be on disk"

        # Session 2: reload + rehydrate.
        f2 = FaissClient(cfg)
        wm, _ = _make_wm(cfg)
        counts = wm.rehydrate_from_faiss(f2)
        assert counts["loaded"] == 1, f"Expected 1 loaded, got {counts}"
        o = wm.get("ref_obj")
        assert o is not None
        assert o.reference_image_path == "/mnt/rtsm-data/refs/ref_obj.jpg"
        assert o.reference_emb is not None
        assert o.reference_emb.shape == (8,)
        cos = float(np.dot(o.reference_emb, ref_emb))
        assert cos > 0.9999, f"reference_emb survived restart (cos={cos})"
        print(f"  OK: reference fields survived restart (cos={cos:.5f})")


def test_rehydrate_seeds_emb_gallery():
    """The cold-start win: rehydrated named objects have gallery evidence."""
    print("\n=== test_rehydrate_seeds_emb_gallery ===")
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = os.path.join(tmp, "t.flatip")
        cfg = _make_cfg(idx_path)
        f1 = FaissClient(cfg)
        ref_emb = _emb(77, 8)
        # emb_mean and reference_emb are deliberately DIFFERENT so we can
        # tell which one seeded the gallery.
        f1.upsert_batch([{
            "object_id": "seeded",
            "emb": _emb(2, 8),
            "xyz": np.array([0.0, 0.0, 0.0], dtype=np.float32),
            "label_primary": "x",
            "label_topk": ["x"], "label_scores": [0.8], "label_hits": [5],
            "stability": 0.9,
            "reference_image_path": "/dev/null",
            "reference_emb": ref_emb.tolist(),
        }])
        f2 = FaissClient(cfg)
        wm, _ = _make_wm(cfg)
        wm.rehydrate_from_faiss(f2)
        o = wm.get("seeded")
        assert o is not None
        # emb_gallery should now have one row, and it should match reference_emb
        # (not emb_mean), confirming the seeding source.
        assert o.emb_gallery.shape[0] == 1, (
            f"Expected emb_gallery seeded with 1 row, got shape {o.emb_gallery.shape}"
        )
        seeded_row = o.emb_gallery[0].astype(np.float32)
        # float16 round-trip costs a tiny bit of precision.
        seeded_row = seeded_row / (np.linalg.norm(seeded_row) + 1e-12)
        cos_ref = float(np.dot(seeded_row, ref_emb))
        cos_mean = float(np.dot(seeded_row, o.emb_mean))
        assert cos_ref > 0.99, (
            f"emb_gallery should be seeded with reference_emb (cos={cos_ref}), "
            f"not emb_mean (cos={cos_mean})"
        )
        assert cos_ref > cos_mean, (
            "Gallery vector matches reference more closely than emb_mean (expected)"
        )
        print(f"  OK: emb_gallery seeded from reference_emb (cos_ref={cos_ref:.4f})")


def test_rehydrate_legacy_sidecar_no_reference():
    """Sidecar entries without reference fields must rehydrate cleanly."""
    print("\n=== test_rehydrate_legacy_sidecar_no_reference ===")
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = os.path.join(tmp, "t.flatip")
        cfg = _make_cfg(idx_path)
        f1 = FaissClient(cfg)
        # Legacy: no reference_image_path / reference_emb keys at all.
        f1.upsert_batch([{
            "object_id": "legacy",
            "emb": _emb(1, 8),
            "xyz": np.array([0, 0, 0], dtype=np.float32),
            "label_primary": "old_couch",
            "label_topk": ["old_couch"], "label_scores": [0.7], "label_hits": [8],
            "stability": 0.9,
        }])
        f2 = FaissClient(cfg)
        wm, _ = _make_wm(cfg)
        wm.rehydrate_from_faiss(f2)
        o = wm.get("legacy")
        assert o is not None
        assert o.reference_image_path is None
        assert o.reference_emb is None
        # No gallery seeding for legacy: should be empty as before.
        assert o.emb_gallery.shape[0] == 0, (
            f"Legacy rehydrate must leave emb_gallery empty, got {o.emb_gallery.shape}"
        )
        print("  OK: legacy sidecar entries rehydrate without reference fields")


def test_rehydrate_handles_bad_reference_emb():
    """Malformed reference_emb shouldn't crash rehydrate."""
    print("\n=== test_rehydrate_handles_bad_reference_emb ===")
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = os.path.join(tmp, "t.flatip")
        cfg = _make_cfg(idx_path, dim=8)
        f1 = FaissClient(cfg)
        # Wrong-dim reference_emb: must be skipped with a warning, not crash.
        f1.upsert_batch([{
            "object_id": "bad_ref",
            "emb": _emb(1, 8),
            "xyz": np.array([0, 0, 0], dtype=np.float32),
            "label_primary": "x",
            "label_topk": ["x"], "label_scores": [0.7], "label_hits": [5],
            "stability": 0.9,
            "reference_image_path": "/some/path.jpg",
            "reference_emb": [0.1] * 16,   # wrong dim (16 vs 8)
        }])
        f2 = FaissClient(cfg)
        wm, _ = _make_wm(cfg)
        wm.rehydrate_from_faiss(f2)
        o = wm.get("bad_ref")
        assert o is not None, "Object should still be rehydrated"
        # Path should be set (we don't validate it on rehydrate);
        # reference_emb stays None due to dim mismatch.
        assert o.reference_image_path == "/some/path.jpg"
        assert o.reference_emb is None
        assert o.emb_gallery.shape[0] == 0  # no seeding when ref_emb is invalid
        print("  OK: malformed reference_emb skipped without crash")


# --------------------------------------------------------------------------- #
# 9. End-to-end                                                               #
# --------------------------------------------------------------------------- #

def test_e2e_reference_roundtrip():
    """Full lifecycle: create -> set ref -> upsert -> save -> load -> rehydrate.

    Verifies that an object set up live with a reference snapshot survives a
    full restart with everything preserved AND the gallery is seeded.
    """
    print("\n=== test_e2e_reference_roundtrip ===")
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = os.path.join(tmp, "t.flatip")
        cfg = _make_cfg(idx_path)

        # Session 1: build, set ref, upsert, save (FaissClient saves on
        # upsert_batch via the persistent_path mechanism per test_rehydrate).
        f1 = FaissClient(cfg)
        wm1, _ = _make_wm(cfg)
        oid = _promoted_object(wm1, label="rubber_duck", seed=1)
        ref_emb = _emb(123, 8)
        wm1.set_object_reference(
            oid, image_path="/mnt/rtsm-data/refs/e2e.jpg", embedding=ref_emb,
        )
        time.sleep(0.01)
        payloads = wm1.collect_ready_for_upsert(force_all=False)
        # If the normal path skipped (change-detection), force-flush.
        if not payloads:
            payloads = wm1.collect_ready_for_upsert(force_all=True)
        assert payloads, "Expected at least one payload"
        f1.upsert_batch(payloads)
        assert os.path.exists(idx_path), "FAISS sidecar must be on disk"

        # Session 2: simulate restart.
        f2 = FaissClient(cfg)
        wm2, _ = _make_wm(cfg)
        counts = wm2.rehydrate_from_faiss(f2)
        assert counts["loaded"] >= 1, f"Expected >=1 rehydrated, got {counts}"
        o2 = wm2.get(oid)
        assert o2 is not None, "Object should be present after rehydrate"
        assert o2.reference_image_path == "/mnt/rtsm-data/refs/e2e.jpg"
        assert o2.reference_emb is not None
        cos_ref = float(np.dot(o2.reference_emb, ref_emb))
        assert cos_ref > 0.9999, f"reference_emb roundtrip (cos={cos_ref})"

        # And the headline win: emb_gallery is seeded with reference_emb.
        assert o2.emb_gallery.shape[0] == 1, (
            f"emb_gallery should be seeded after rehydrate; "
            f"got shape {o2.emb_gallery.shape}"
        )
        gallery_vec = o2.emb_gallery[0].astype(np.float32)
        gallery_vec = gallery_vec / (np.linalg.norm(gallery_vec) + 1e-12)
        cos_gal = float(np.dot(gallery_vec, ref_emb))
        assert cos_gal > 0.99, f"gallery seeded from reference (cos={cos_gal})"
        print(f"  OK: e2e roundtrip; ref cos={cos_ref:.5f}, gallery cos={cos_gal:.4f}")


# --------------------------------------------------------------------------- #
# Pre-existing regression checks                                              #
# --------------------------------------------------------------------------- #

def test_no_regression_on_legacy_payload_fields():
    """Make sure our payload additions didn't disturb the existing fields."""
    print("\n=== test_no_regression_on_legacy_payload_fields ===")
    with tempfile.TemporaryDirectory() as tmp:
        cfg = _make_cfg(os.path.join(tmp, "t.flatip"))
        wm, _ = _make_wm(cfg)
        oid = _promoted_object(wm)
        payloads = wm.collect_ready_for_upsert(force_all=True)
        p = payloads[0]
        # Spot-check the fields that should still be present.
        for required in (
            "object_id", "emb", "xyz", "label_primary", "label_user",
            "display_label", "movability_class", "pose_state_at_observation",
            "label_topk", "label_scores", "label_hits", "stability",
            "last_seen_wall_utc", "created_at", "created_mono",
        ):
            assert required in p, f"Pre-existing field {required!r} missing from payload"
        print(f"  OK: all {len(p)} expected payload fields present")


# --------------------------------------------------------------------------- #
# Runner                                                                      #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    test_objectstate_has_reference_fields()
    test_set_object_reference_set_and_clear()
    test_set_object_reference_dim_mismatch()
    test_set_object_reference_unknown_oid()
    test_set_object_reference_schedules_upsert()
    test_force_flush_payload_includes_reference()
    test_force_flush_payload_with_no_reference()
    test_normal_path_payload_includes_reference()
    test_rehydrate_reads_reference_fields()
    test_rehydrate_seeds_emb_gallery()
    test_rehydrate_legacy_sidecar_no_reference()
    test_rehydrate_handles_bad_reference_emb()
    test_e2e_reference_roundtrip()
    test_no_regression_on_legacy_payload_fields()
    print("\nAll reference-snapshot tests passed.")
