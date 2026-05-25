"""End-to-end test of the FAISS persistence cycle.

Drives a fake observation through promotion -> heap scheduling -> upsert ->
disk save -> fresh process load -> rehydrate. Catches the 'no heap push on
promote' bug (and any future regression of it).

Run with:
    cd /workspace/rtsm && PYTHONPATH=. python3 test_end_to_end_persistence.py
"""
import sys
sys.path.insert(0, "/home/claude/rtsm")

import os
import tempfile
import numpy as np

from rtsm.stores.working_memory import WorkingMemory
from rtsm.stores.proximity_index import ProximityIndex, GridSpec
from rtsm.stores.vectors.faiss_client import FaissClient


def _cfg(index_path, dim=8):
    return {
        "vectors": {
            "enable": True, "backend": "faiss", "dim": dim,
            "faiss": {"index_path": index_path},
        },
        "sweep_cache": {"grid_size_m": 0.25, "two_d": True, "up_axis": "z"},
        "object": {
            # Loosen promote gates for test purposes so we don't need a
            # huge number of fake observations
            "promote_hits": 2,
            "stability_promote": 0.3,
            "promote_min_conf": 0.10,
            "min_label_hits": 2,
            "require_view_bins": 1,
            "max_gallery": 6,
        },
        "ltm": {"min_period_s": 1.0, "force_period_s": 10.0, "ltm_min_view_bins": 1, "reupsert_pos_m": 0.05},
        "view": {"az_bins": 8, "el_bins": 3},
        "pose": {"meas_var_xyz_cm2": [1.5, 1.5, 3.0], "proc_var_xyz_cm2": [0.2, 0.2, 0.4]},
        "assoc": {"gate_dist_base_m": 0.20},
    }


def _wm(cfg):
    grid = GridSpec(cell_m=0.25, use_3d=False, up_axis="z")
    idx = ProximityIndex(grid)
    return WorkingMemory(cfg, index=idx)


def _emb(seed, dim):
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(dim).astype(np.float32)
    return v / (np.linalg.norm(v) + 1e-12)


class _FakeObs:
    """Minimal duck-typed observation matching what update_object reads."""
    def __init__(self, p_world, emb_vis, view_dir_cam=None, label_topk=None,
                 is_keyframe=True, depth_valid=1.0, quality=1.0,
                 cos_sim=0.95, dist_m=0.02, frame_id="f1", crop=None,
                 centroid_px=None):
        self.p_world = np.asarray(p_world, dtype=np.float32)
        self.emb_vis = emb_vis
        self.view_dir_cam = view_dir_cam
        self.label_topk = label_topk
        self.is_keyframe = is_keyframe
        self.depth_valid = depth_valid
        self.quality = quality
        self.cos_sim = cos_sim
        self.dist_m = dist_m
        self.frame_id = frame_id
        self.crop = crop
        self.centroid_px = centroid_px


def test_promote_then_upsert():
    """An object goes through create -> update -> promote -> heap scheduling
    -> collect_ready_for_upsert returns it -> FAISS receives it."""
    print("\n=== test_promote_then_upsert ===")
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = os.path.join(tmp, "test.flatip")
        cfg = _cfg(idx_path)
        wm = _wm(cfg)
        faiss_c = FaissClient(cfg)

        # Create a proto, then feed it observations until promotion fires
        emb = _emb(1, 8)
        view_dir = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        oid = wm.create_object(
            p_world=np.array([1.0, 2.0, 0.5], dtype=np.float32),
            emb_vis=emb,
            label_topk=[("couch", 0.85), ("chair", 0.05)],
            view_dir_cam=view_dir,
            frame_id="f0",
        )
        assert oid is not None, "create_object must succeed"
        # Two more observations to satisfy promote_hits=2 + min_label_hits=2
        for i in range(3):
            obs = _FakeObs(
                p_world=np.array([1.01, 2.01, 0.5], dtype=np.float32),
                emb_vis=emb,
                view_dir_cam=view_dir,
                label_topk=[("couch", 0.86 + i * 0.01)],
                frame_id=f"f{i+1}",
            )
            wm.update_object(oid, obs)
            wm.maybe_promote(oid)

        o = wm.get(oid)
        assert o is not None
        assert o.confirmed, (
            f"Object should be confirmed by now. State: "
            f"hits={o.hits} stab={o.stability:.3f} bins={len(o.view_bins)} "
            f"label_scores={o.label_scores} label_hits={o.label_hits}"
        )
        print(f"  ok: promoted oid={oid[:8]} hits={o.hits} stab={o.stability:.3f}")

        # *** CRITICAL CHECK ***
        # If maybe_promote forgot to schedule the heap entry, this returns []
        ready = wm.collect_ready_for_upsert()
        assert len(ready) >= 1, (
            "REGRESSION: collect_ready_for_upsert returned empty after "
            "promotion. The maybe_promote function must call "
            "heapq.heappush(self._ltm_heap, ...) when an object becomes "
            "confirmed. Otherwise live ingest persistence is broken."
        )
        print(f"  ok: collect_ready_for_upsert returned {len(ready)} payload(s)")

        # Upsert to FAISS, verify on-disk artifact
        faiss_c.upsert_batch(ready)
        assert os.path.exists(idx_path), "FAISS index must be on disk"
        assert os.path.exists(idx_path + ".meta.json"), "meta sidecar must be on disk"
        print(f"  ok: FAISS artifacts written to {idx_path}")

        # Simulate restart: fresh process -> load -> rehydrate
        faiss_c2 = FaissClient(cfg)
        wm2 = _wm(cfg)
        counts = wm2.rehydrate_from_faiss(faiss_c2)
        assert counts["loaded"] >= 1, f"Expected >=1 loaded, got {counts}"
        o2 = wm2.get(oid)
        assert o2 is not None, "Object should be present after rehydrate"
        assert o2.confirmed, "Rehydrated object should be confirmed"
        assert o2.label_primary == "couch", \
            f"Label mismatch: {o2.label_primary}"
        print(f"  ok: rehydrated oid={oid[:8]} label={o2.label_primary}")


if __name__ == "__main__":
    test_promote_then_upsert()
    print("\nEnd-to-end persistence test passed.")
