"""Tests for WorkingMemory.merge_objects.

Run with:
    cd /workspace/rtsm && PYTHONPATH=. python3 tests/test_merge_objects.py

Or via docker:
    docker exec rtsm-dev bash -c \
      'cd /workspace/rtsm && PYTHONPATH=. python3 tests/test_merge_objects.py'

Covers:
  - happy path: two confirmed objects merge with correct field semantics
  - dry_run leaves both objects intact
  - label_user inheritance from loser
  - persistent gallery rewritten for winner, removed for loser
  - audit log written
  - cross-restart: rehydrate after merge shows only winner
  - error: winner == loser raises ValueError
  - error: missing oid returns {"error": "not_found"}
"""
import os
import sys
import json
import shutil
import tempfile

import numpy as np

# Allow running both from the repo root and from inside the package.
_ROOT = os.environ.get("RTSM_ROOT", "/workspace/rtsm")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from rtsm.stores.working_memory import WorkingMemory, ObjectState
from rtsm.stores.proximity_index import ProximityIndex, GridSpec
from rtsm.stores.vectors.faiss_client import FaissClient


# ----------------------- helpers -----------------------

def _make_cfg(*, dim: int = 8, crops_root: str, merge_log_dir: str,
              max_gallery: int = 10, max_image_crops: int = 10):
    return {
        "vectors": {
            "enable": True, "backend": "faiss", "dim": dim,
            "faiss": {"index_path": os.path.join(crops_root, "..",
                                                 "faiss", "index.flatip")},
        },
        "sweep_cache": {"grid_size_m": 0.25, "two_d": True, "up_axis": "z"},
        "object": {
            "promote_hits": 2,
            "stability_promote": 0.3,
            "promote_min_conf": 0.10,
            "min_label_hits": 2,
            "require_view_bins": 1,
            "max_gallery": max_gallery,
            "max_image_crops": max_image_crops,
            "gallery_dupe_cos": 0.995,
            "crops_root": crops_root,
            "persist_galleries": True,
            "merge_log_dir": merge_log_dir,
            "default_movability": "movable",
        },
        "ltm": {"min_period_s": 1.0, "force_period_s": 10.0,
                "ltm_min_view_bins": 1, "reupsert_pos_m": 0.05},
        "view": {"az_bins": 8, "el_bins": 3},
        "pose": {"meas_var_xyz_cm2": [1.5, 1.5, 3.0],
                 "proc_var_xyz_cm2": [0.2, 0.2, 0.4]},
        "assoc": {"gate_dist_base_m": 0.20},
    }


def _make_wm(cfg):
    grid = GridSpec(cell_m=0.25, use_3d=False, up_axis="z")
    idx = ProximityIndex(grid)
    return WorkingMemory(cfg, index=idx)


def _make_emb(seed: int, dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(dim).astype(np.float32)
    v = v / (np.linalg.norm(v) + 1e-12)
    return v.astype(np.float32)


def _make_confirmed_object(
    wm: WorkingMemory,
    *,
    seed: int,
    xyz=(0.0, 0.0, 0.0),
    label: str = "couch",
    label_user=None,
    hits: int = 10,
    n_gallery: int = 4,
    n_crops: int = 3,
    view_bins=(0, 1),
) -> str:
    """Hand-construct a confirmed ObjectState directly (bypassing the
    full promotion machinery to keep tests fast and deterministic)."""
    dim = int(wm.cfg["vectors"]["dim"])

    # Build a small gallery of distinct embs.
    gallery_embs = np.zeros((n_gallery, dim), dtype=np.float16)
    for i in range(n_gallery):
        gallery_embs[i] = _make_emb(seed + i, dim).astype(np.float16)
    emb_mean = _make_emb(seed, dim)

    vb = {}
    for b in view_bins:
        vb[int(b)] = _make_emb(seed + 100 + b, dim)

    crops = [bytes([0xff, 0xd8, 0xff] + [i] * 5) for i in range(n_crops)]

    import time as _time
    now_m = _time.monotonic()
    now_w = _time.time()
    oid = f"oid{seed:08x}"

    o = ObjectState(
        id=oid,
        xyz_world=np.asarray(xyz, dtype=np.float32),
        cov_world=np.array([0.02, 0.02, 0.04], dtype=np.float32),
        emb_mean=emb_mean,
        emb_gallery=gallery_embs,
        view_bins=vb,
        label_scores={label: 0.85},
        label_hits={label: hits},
        label_primary=label,
        stability=0.9,
        hits=hits,
        confirmed=True,
        created_mono=now_m - 100.0,
        created_wall_utc=now_w - 100.0,
        last_seen_mono=now_m - 1.0,
        last_seen_wall_utc=now_w - 1.0,
        last_seen_px=None,
        last_upsert_wall_utc=0.0,
        last_upsert_mono=0.0,
        last_upsert_emb=None,
        last_upsert_xyz=None,
        image_crops=list(crops),
        last_update_frame_id=None,
        _dim=dim,
        label_user=label_user,
        movability_class=wm.default_movability,
        pose_state_at_observation="on_floor",
    )
    with wm._lock:
        wm._map[oid] = o
    if wm.index is not None:
        wm.index.insert(oid, o.xyz_world, wm_lookup=wm.lookup_min)
    # Persist the initial gallery state to disk so subsequent merge ops
    # operate against realistic on-disk artifacts.
    for jb in crops:
        wm._gallery.write_crop(oid, jb, wm.max_image_crops)
    wm._gallery.write_embs(oid, gallery_embs)
    return oid


# ----------------------- tests -----------------------

def test_happy_path():
    print("\n=== test_happy_path ===")
    with tempfile.TemporaryDirectory() as tmp:
        crops_root = os.path.join(tmp, "crops")
        log_dir = os.path.join(tmp, "merge_log")
        cfg = _make_cfg(crops_root=crops_root, merge_log_dir=log_dir)
        wm = _make_wm(cfg)

        winner_oid = _make_confirmed_object(
            wm, seed=1, xyz=(0.3, -0.3, 0.3),
            label="desk", hits=5, n_gallery=4, n_crops=3,
            view_bins=(0, 1),
        )
        loser_oid = _make_confirmed_object(
            wm, seed=20, xyz=(-0.3, -1.3, 1.1),
            label="window", hits=6, n_gallery=4, n_crops=3,
            view_bins=(2, 3),
        )

        assert wm.get(winner_oid) is not None
        assert wm.get(loser_oid) is not None

        result = wm.merge_objects(winner_oid, loser_oid)
        assert result["dry_run"] is False, result
        assert result["winner_oid"] == winner_oid
        assert result["loser_oid"] == loser_oid

        # Loser gone.
        assert wm.get(loser_oid) is None, "loser should be removed"
        # Winner present and updated.
        w = wm.get(winner_oid)
        assert w is not None, "winner should still exist"
        assert w.hits == 11, f"hits should sum: {w.hits}"
        # view_bins union (disjoint here: 0,1 + 2,3).
        assert sorted(w.view_bins.keys()) == [0, 1, 2, 3], \
            f"view_bins union failed: {sorted(w.view_bins.keys())}"
        # Both labels survive.
        assert "desk" in w.label_scores and "window" in w.label_scores
        # label_hits summed correctly.
        assert w.label_hits["desk"] == 5
        assert w.label_hits["window"] == 6
        # Gallery within cap.
        assert 0 < w.emb_gallery.shape[0] <= wm.max_gallery

        # Disk: winner dir present, loser dir gone.
        w_dir = wm._gallery._dir(winner_oid)
        l_dir = wm._gallery._dir(loser_oid)
        assert os.path.isdir(w_dir), "winner gallery dir should exist"
        assert not os.path.isdir(l_dir), "loser gallery dir should be gone"

        # Audit log written.
        assert os.path.isdir(log_dir), "merge_log dir should exist"
        logs = [f for f in os.listdir(log_dir) if f.endswith(".json")]
        assert len(logs) == 1, f"expected 1 audit log, got {logs}"
        with open(os.path.join(log_dir, logs[0])) as fp:
            audit = json.load(fp)
        assert audit["winner_oid"] == winner_oid
        assert audit["loser_oid"] == loser_oid
        assert audit["stats"]["hits_after"] == 11

        print("  OK: happy path merge succeeded")


def test_dry_run_leaves_state_unchanged():
    print("\n=== test_dry_run_leaves_state_unchanged ===")
    with tempfile.TemporaryDirectory() as tmp:
        crops_root = os.path.join(tmp, "crops")
        log_dir = os.path.join(tmp, "merge_log")
        cfg = _make_cfg(crops_root=crops_root, merge_log_dir=log_dir)
        wm = _make_wm(cfg)

        winner_oid = _make_confirmed_object(wm, seed=1, hits=5)
        loser_oid = _make_confirmed_object(wm, seed=2, hits=7,
                                           xyz=(1.0, 0.0, 0.0))

        wpre = wm.get(winner_oid)
        lpre = wm.get(loser_oid)
        winner_hits_before = wpre.hits
        loser_hits_before = lpre.hits

        result = wm.merge_objects(winner_oid, loser_oid, dry_run=True)
        assert result["dry_run"] is True
        assert result["audit_log_path"] is None

        # Both objects still present, unchanged.
        wpost = wm.get(winner_oid)
        lpost = wm.get(loser_oid)
        assert wpost is not None and lpost is not None
        assert wpost.hits == winner_hits_before
        assert lpost.hits == loser_hits_before
        # Stats should still be computed.
        assert result["stats"]["hits_after"] == \
            winner_hits_before + loser_hits_before

        print("  OK: dry_run reported stats without mutating state")


def test_label_user_inherited_from_loser():
    print("\n=== test_label_user_inherited_from_loser ===")
    with tempfile.TemporaryDirectory() as tmp:
        crops_root = os.path.join(tmp, "crops")
        log_dir = os.path.join(tmp, "merge_log")
        cfg = _make_cfg(crops_root=crops_root, merge_log_dir=log_dir)
        wm = _make_wm(cfg)

        winner_oid = _make_confirmed_object(
            wm, seed=1, hits=5, label_user=None,
        )
        loser_oid = _make_confirmed_object(
            wm, seed=2, hits=7, label_user="my_couch",
            xyz=(1.0, 0.0, 0.0),
        )

        result = wm.merge_objects(winner_oid, loser_oid)
        w = wm.get(winner_oid)
        assert w.label_user == "my_couch", \
            f"label_user should inherit: got {w.label_user!r}"
        assert result["stats"]["label_user_inherited_from_loser"] is True

        print("  OK: label_user inherited from loser when winner has none")


def test_label_user_winner_takes_precedence():
    print("\n=== test_label_user_winner_takes_precedence ===")
    with tempfile.TemporaryDirectory() as tmp:
        crops_root = os.path.join(tmp, "crops")
        log_dir = os.path.join(tmp, "merge_log")
        cfg = _make_cfg(crops_root=crops_root, merge_log_dir=log_dir)
        wm = _make_wm(cfg)

        winner_oid = _make_confirmed_object(
            wm, seed=1, hits=5, label_user="canonical",
        )
        loser_oid = _make_confirmed_object(
            wm, seed=2, hits=7, label_user="discarded",
            xyz=(1.0, 0.0, 0.0),
        )

        result = wm.merge_objects(winner_oid, loser_oid)
        w = wm.get(winner_oid)
        assert w.label_user == "canonical", \
            f"winner's label_user should win: got {w.label_user!r}"
        assert result["stats"]["label_user_inherited_from_loser"] is False

        print("  OK: winner's label_user kept when both set")


def test_error_winner_equals_loser():
    print("\n=== test_error_winner_equals_loser ===")
    with tempfile.TemporaryDirectory() as tmp:
        crops_root = os.path.join(tmp, "crops")
        log_dir = os.path.join(tmp, "merge_log")
        cfg = _make_cfg(crops_root=crops_root, merge_log_dir=log_dir)
        wm = _make_wm(cfg)

        oid = _make_confirmed_object(wm, seed=1, hits=5)
        try:
            wm.merge_objects(oid, oid)
            raise AssertionError("Expected ValueError")
        except ValueError as e:
            assert "differ" in str(e).lower(), str(e)
        print("  OK: ValueError raised when winner == loser")


def test_error_missing_oid():
    print("\n=== test_error_missing_oid ===")
    with tempfile.TemporaryDirectory() as tmp:
        crops_root = os.path.join(tmp, "crops")
        log_dir = os.path.join(tmp, "merge_log")
        cfg = _make_cfg(crops_root=crops_root, merge_log_dir=log_dir)
        wm = _make_wm(cfg)

        winner_oid = _make_confirmed_object(wm, seed=1, hits=5)
        result = wm.merge_objects(winner_oid, "nonexistent_oid")
        assert result.get("error") == "not_found"
        assert result.get("missing_oid") == "nonexistent_oid"
        # Winner still present.
        assert wm.get(winner_oid) is not None
        print("  OK: missing oid returns not_found without mutating winner")


def test_gallery_dedup_gate_respected():
    """Loser's gallery contains a near-duplicate of winner's emb_mean;
    merge should drop the dup per gallery_dupe_cos."""
    print("\n=== test_gallery_dedup_gate_respected ===")
    with tempfile.TemporaryDirectory() as tmp:
        crops_root = os.path.join(tmp, "crops")
        log_dir = os.path.join(tmp, "merge_log")
        cfg = _make_cfg(crops_root=crops_root, merge_log_dir=log_dir)
        wm = _make_wm(cfg)

        winner_oid = _make_confirmed_object(
            wm, seed=1, hits=5, n_gallery=3,
        )
        # Build a loser whose gallery includes an identical copy of one
        # of the winner's gallery entries.
        loser_oid = _make_confirmed_object(
            wm, seed=2, hits=5, n_gallery=3,
            xyz=(1.0, 0.0, 0.0),
        )
        # Inject a duplicate of winner's first gallery vector into
        # loser's gallery in-place.
        w = wm.get(winner_oid)
        l = wm.get(loser_oid)
        l.emb_gallery[0] = w.emb_gallery[0].copy()

        before_combined = w.emb_gallery.shape[0] + l.emb_gallery.shape[0]
        wm.merge_objects(winner_oid, loser_oid)
        merged = wm.get(winner_oid)
        # At least one duplicate should have been gated out, so merged
        # size < naive concat size.
        assert merged.emb_gallery.shape[0] <= before_combined, \
            "gallery should not exceed naive concat size"
        # And since one exact dup was injected, count should be strictly
        # less (3 + 3 - 1 dup = 5 max; could be lower if other near-dups).
        assert merged.emb_gallery.shape[0] <= 5, \
            f"dedup gate didn't fire: {merged.emb_gallery.shape[0]}"
        print(f"  OK: gallery dedup gate held "
              f"(combined={before_combined} -> merged="
              f"{merged.emb_gallery.shape[0]})")


def test_persistent_gallery_survives_simulated_restart():
    print("\n=== test_persistent_gallery_survives_simulated_restart ===")
    with tempfile.TemporaryDirectory() as tmp:
        crops_root = os.path.join(tmp, "crops")
        log_dir = os.path.join(tmp, "merge_log")
        cfg = _make_cfg(crops_root=crops_root, merge_log_dir=log_dir)

        # ---- Session 1 ----
        wm1 = _make_wm(cfg)
        winner_oid = _make_confirmed_object(
            wm1, seed=1, hits=5,
        )
        loser_oid = _make_confirmed_object(
            wm1, seed=2, hits=7, xyz=(1.0, 0.0, 0.0),
        )
        wm1.merge_objects(winner_oid, loser_oid)
        assert wm1.get(loser_oid) is None
        merged_hits = wm1.get(winner_oid).hits

        # ---- Simulate process restart: fresh WM reading from same crops_root ----
        # FaissClient isn't involved in this test (we test the gallery
        # disk only). Instead, we directly load winner from disk via
        # the gallery and confirm the loser dir is gone.
        wm2 = _make_wm(cfg)  # fresh, empty WM with same crops_root

        crops, embs = wm2._gallery.load(winner_oid)
        assert len(crops) > 0, "winner crops should persist"
        assert embs is not None and embs.shape[0] > 0, \
            "winner embs should persist"
        loser_crops, loser_embs = wm2._gallery.load(loser_oid)
        assert loser_crops == [] and loser_embs is None, \
            "loser disk gallery should be gone"

        print(f"  OK: winner gallery survived restart (crops="
              f"{len(crops)}, embs={embs.shape[0]}), loser gone. "
              f"merged_hits captured: {merged_hits}")


# ----------------------- main -----------------------

if __name__ == "__main__":
    test_happy_path()
    test_dry_run_leaves_state_unchanged()
    test_label_user_inherited_from_loser()
    test_label_user_winner_takes_precedence()
    test_error_winner_equals_loser()
    test_error_missing_oid()
    test_gallery_dedup_gate_respected()
    test_persistent_gallery_survives_simulated_restart()
    print("\nAll merge_objects tests passed.")
