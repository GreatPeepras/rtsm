"""Round-trip test: last_seen_wall_utc survives the FAISS sidecar.

Mirrors test_rehydrate.py::test_pose_state_round_trip. Two cases:
  (a) sidecar WITH the field          -> rehydrated value preserved (not now()).
  (b) sidecar WITHOUT the field (legacy) -> falls back to now_w, no crash.

Run:  cd /path/to/rtsm && python3 test_last_seen_persist.py
"""
from __future__ import annotations
import os, tempfile, time
import numpy as np

from rtsm.stores.working_memory import WorkingMemory
from rtsm.stores.proximity_index import ProximityIndex, GridSpec
from rtsm.stores.vectors.faiss_client import FaissClient

DAY = 86400.0

def _cfg(index_path, dim=8):
    return {
        "vectors": {"enable": True, "backend": "faiss", "dim": dim,
                    "faiss": {"index_path": index_path}},
        "sweep_cache": {"grid_size_m": 0.25, "two_d": True, "up_axis": "z"},
        "object": {"promote_hits": 2, "stability_promote": 0.3,
                   "promote_min_conf": 0.10, "min_label_hits": 2,
                   "require_view_bins": 1, "max_gallery": 6},
        "ltm": {"min_period_s": 1.0, "force_period_s": 10.0,
                "ltm_min_view_bins": 1, "reupsert_pos_m": 0.05},
        "view": {"az_bins": 8, "el_bins": 3},
        "pose": {"meas_var_xyz_cm2": [1.5, 1.5, 3.0], "proc_var_xyz_cm2": [0.2, 0.2, 0.4]},
        "assoc": {"gate_dist_base_m": 0.20},
    }

def _wm(cfg):
    grid = GridSpec(cell_m=0.25, use_3d=False, up_axis="z")
    return WorkingMemory(cfg, index=ProximityIndex(grid))

def _emb(seed, dim):
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(dim).astype(np.float32)
    return v / (np.linalg.norm(v) + 1e-12)

results = []
def check(name, cond, detail=""):
    results.append((name, cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))
    assert cond, f"{name}: {detail}"


print("=== test_last_seen_persist.py ===\n")

print("[1] write side: collect_ready_for_upsert emits last_seen_wall_utc")
with tempfile.TemporaryDirectory() as tmp:
    cfg = _cfg(os.path.join(tmp, "t.flatip"))
    wm = _wm(cfg)
    oid = wm.create_object(
        p_world=np.array([1.0, 2.0, 0.5], dtype=np.float32),
        emb_vis=_emb(1, 8),
        label_topk=[("couch", 0.9), ("chair", 0.05)],
        view_dir_cam=np.array([1.0, 0.0, 0.0], dtype=np.float32),
        frame_id="f0",
    )
    for i in range(3):
        from types import SimpleNamespace
        wm.update_object(oid, SimpleNamespace(
            p_world=np.array([1.0, 2.0, 0.5], dtype=np.float32),
            emb_vis=_emb(1, 8),
            view_dir_cam=np.array([1.0, 0.0, 0.0], dtype=np.float32),
            label_topk=[("couch", 0.9 + i * 0.01)],
            frame_id=f"f{i+1}",
        ))
        wm.maybe_promote(oid)
    ready = wm.collect_ready_for_upsert(force_all=True)
    check("1a at least one payload", len(ready) >= 1, f"got {len(ready)}")
    pay = next(p for p in ready if p["object_id"] == oid)
    check("1b payload has last_seen_wall_utc", "last_seen_wall_utc" in pay)
    check("1c value matches object", pay["last_seen_wall_utc"] == wm.get(oid).last_seen_wall_utc)

print("\n[2] round-trip: explicit last_seen preserved; legacy falls back")
with tempfile.TemporaryDirectory() as tmp:
    cfg = _cfg(os.path.join(tmp, "t.flatip"))
    f = FaissClient(cfg)
    explicit_ts = 1_700_000_000.0  # a fixed past wall time
    f.upsert_batch([
        {   # (a) explicit last_seen
            "object_id": "ts_obj", "emb": _emb(1, 8),
            "xyz": np.array([0.5, 0.5, 0.5], dtype=np.float32),
            "label_primary": "couch", "label_topk": ["couch"],
            "label_scores": [0.9], "label_hits": [6], "stability": 0.85,
            "last_seen_wall_utc": explicit_ts,
        },
        {   # (b) legacy: no last_seen_wall_utc key at all
            "object_id": "legacy_obj", "emb": _emb(2, 8),
            "xyz": np.array([1.0, 1.0, 0.3], dtype=np.float32),
            "label_primary": "rug", "label_topk": ["rug"],
            "label_scores": [0.7], "label_hits": [8], "stability": 0.9,
        },
    ])
    # Restart: fresh client + WM, rehydrate from disk
    f2 = FaissClient(cfg)
    wm = _wm(cfg)
    before = time.time()
    wm.rehydrate_from_faiss(f2)
    after = time.time()
    ts = wm.get("ts_obj"); leg = wm.get("legacy_obj")
    check("2a both rehydrated", ts is not None and leg is not None)
    check("2b explicit last_seen preserved (not reset to now)",
          ts.last_seen_wall_utc == explicit_ts,
          f"got {ts.last_seen_wall_utc}")
    check("2c legacy falls back to ~now (no crash)",
          before <= leg.last_seen_wall_utc <= after,
          f"got {leg.last_seen_wall_utc}")

print("\n[3] integration with eviction: rehydrated stale object IS evictable")
with tempfile.TemporaryDirectory() as tmp:
    cfg = _cfg(os.path.join(tmp, "t.flatip"))
    cfg["eviction"] = {"enabled": True}
    f = FaissClient(cfg)
    old_ts = time.time() - 40 * DAY  # 40 days ago
    f.upsert_batch([{
        "object_id": "stale", "emb": _emb(3, 8),
        "xyz": np.array([0.2, 0.2, 0.2], dtype=np.float32),
        "label_primary": "mug", "label_topk": ["mug"],
        "label_scores": [0.8], "label_hits": [6], "stability": 0.8,
        "movability_class": "movable",      # 3-day TTL
        "last_seen_wall_utc": old_ts,
    }])
    f2 = FaissClient(cfg)
    wm = _wm(cfg)
    wm.rehydrate_from_faiss(f2)
    sel = {d["oid"] for d in wm.select_evictable()}
    check("3a rehydrated stale object is evictable (TTL clock survived restart)",
          "stale" in sel, f"selected={sel}")
    # Counter-check: BEFORE the fix this would have failed, because last_seen
    # would be stamped to 'now' on rehydrate and the 40-day age would be lost.

print(f"\n=== {sum(c for _,c in results)}/{len(results)} checks passed ===")
