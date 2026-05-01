"""
FrozenWorkingMemory — read-only view over persisted LTM state.

Used in serve mode. Loads object records from the FAISS meta sidecar
(`<index_path>.meta.json`) and exposes the subset of the WorkingMemory
API that the HTTP server reads: stats(), iter_objects(), get(), exists(),
get_robot_pose(), lookup_min().

Tracking-pipeline methods (create_object, update_object, decay_unmatched,
collect_ready_for_upsert, apply_pose_corrections, etc.) are intentionally
NOT implemented — serve mode has no pipeline. Calling them will raise
AttributeError, which is the desired loud failure.
"""
from __future__ import annotations

import json
import logging
import os
import threading  # PATCH III 20260501
import time  # PATCH I 20260501
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


def _record_to_object(rec: Dict[str, Any]) -> SimpleNamespace:
    """Turn a meta.json record into a duck-typed object matching the
    subset of ObjectState attributes that api/server.py reads via getattr."""
    xyz = np.asarray(rec.get("xyz", [0.0, 0.0, 0.0]), dtype=np.float32)

    label_topk_raw = rec.get("label_topk", []) or []
    label_scores_raw = rec.get("label_scores", []) or []
    # ObjectState.label_scores is Dict[str, float]; build one from the parallel lists
    label_scores: Dict[str, float] = {}
    for name, score in zip(label_topk_raw, label_scores_raw):
        label_scores[str(name)] = float(score)

    return SimpleNamespace(
        id=str(rec.get("object_id", "")),
        xyz_world=xyz,
        cov_world=np.zeros(3, dtype=np.float32),
        emb_mean=np.zeros(0, dtype=np.float32),
        emb_gallery=np.zeros((0, 0), dtype=np.float16),
        view_bins={},
        label_scores=label_scores,
        label_primary=rec.get("label_primary"),
        stability=float(rec.get("stability", 1.0)),
        hits=int(rec.get("hits", 1)),
        confirmed=True,  # persisted ⇒ was promoted
        created_mono=float(rec.get("created_at", 0.0)),
        created_wall_utc=float(rec.get("created_wall_utc", 0.0)),
        last_seen_mono=float(rec.get("last_seen_mono", 0.0)),
        last_seen_wall_utc=float(rec.get("last_seen_wall_utc", 0.0)),
        last_seen_px=None,
        last_upsert_wall_utc=float(rec.get("last_upsert_wall_utc", 0.0)),
        last_upsert_mono=0.0,
        last_upsert_emb=None,
        last_upsert_xyz=None,
        image_crops=[],
        last_update_frame_id=None,
        _dim=0,
        # extras that some endpoints read
        label_confidence=float(rec.get("label_confidence", 0.0)),
        label_topk=list(label_topk_raw),
    )


class FrozenWorkingMemory:
    """Read-only WorkingMemory replacement for serve mode."""

    def __init__(self, meta_path: str) -> None:
        self._map: Dict[str, SimpleNamespace] = {}
        self._meta_path = meta_path
        self._lock = threading.RLock()  # PATCH III 20260501: serialize reload writes
        self._load(meta_path)
        # PATCH I 20260501: staleness visibility
        self._loaded_wall_utc = __import__("time").time()
        self._loaded_mono = __import__("time").monotonic()

    def _load(self, path: str) -> None:
        if not os.path.exists(path):
            logger.warning("[FrozenWM] meta sidecar not found: %s", path)
            return
        with open(path, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            logger.error("[FrozenWM] unexpected meta shape: %s", type(data).__name__)
            return
        for oid, rec in data.items():
            try:
                self._map[str(oid)] = _record_to_object(rec)
            except Exception as e:
                logger.warning("[FrozenWM] skipping %s: %s", oid, e)
        logger.info("[FrozenWM] loaded %d objects from %s", len(self._map), path)

    # ---- read API mirrored from WorkingMemory ----
    def exists(self, oid: str) -> bool:
        return oid in self._map

    def get(self, oid: str) -> Optional[SimpleNamespace]:
        return self._map.get(oid)

    def lookup_min(self, oid: str) -> Optional[Tuple[bool, float, float]]:
        o = self._map.get(oid)
        if o is None:
            return None
        return (bool(o.confirmed), float(o.stability), float(o.hits))

    def iter_objects(self) -> List[SimpleNamespace]:
        # WorkingMemory.iter_objects returns an Iterable; server code does
        # `objs = wm.iter_objects()` then `len(objs)` and slicing, so return a list.
        return list(self._map.values())

    def get_robot_pose(self) -> Optional[Dict[str, Any]]:
        return None

    def stats(self) -> Dict[str, Any]:
        # PATCH III 20260501: snapshot _map once so a concurrent reload cannot mix counts
        m = self._map
        n = len(m)
        c = sum(1 for o in m.values() if o.confirmed)
        avg_hits = (sum(o.hits for o in m.values()) / n) if n else 0.0
        return {
            "objects": n,
            "confirmed": c,
            "avg_hits": avg_hits,
            "upserts_total": n,  # everything persisted was upserted at least once
            "robot_pose": None,
            "serve_mode": True,
            # PATCH I 20260501
            "frozen_loaded_utc": self._loaded_wall_utc,
            "frozen_age_seconds": __import__("time").monotonic() - self._loaded_mono,
            "frozen_source": self._meta_path,
            "frozen_stale": self._is_stale(),
        }

    def _is_stale(self) -> bool:
        # PATCH I 20260501: true iff sidecar on disk is newer than our load
        try:
            import os as _os
            return _os.path.getmtime(self._meta_path) > self._loaded_wall_utc
        except OSError:
            return False

    # PATCH III 20260501: in-place reload from on-disk sidecar.
    # Enables /reload endpoint to refresh object state without a container restart.
    def reload(self, meta_path: Optional[str] = None) -> Dict[str, Any]:
        """Re-read the sidecar and atomically swap in the new object map.

        Raises FileNotFoundError if the sidecar is missing, or other exceptions
        if parsing fails. On failure, existing state is preserved (staging-then-swap).
        """
        path = meta_path or self._meta_path
        t0 = time.monotonic()
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        # Parse into a staging dict first; do not touch self._map until success.
        with open(path, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"unexpected meta shape: {type(data).__name__}")

        new_map: Dict[str, SimpleNamespace] = {}
        skipped = 0
        for oid, rec in data.items():
            try:
                new_map[str(oid)] = _record_to_object(rec)
            except Exception as e:
                skipped += 1
                logger.warning("[FrozenWM] reload: skipping %s: %s", oid, e)

        # Atomic swap under lock. Readers that already took a ref to the old
        # self._map keep seeing old data for the duration of their call.
        with self._lock:
            old_n = len(self._map)
            old_loaded_utc = self._loaded_wall_utc
            self._map = new_map
            self._meta_path = path
            self._loaded_wall_utc = time.time()
            self._loaded_mono = time.monotonic()
            new_n = len(self._map)
            new_loaded_utc = self._loaded_wall_utc

        duration_ms = (time.monotonic() - t0) * 1000.0
        logger.info(
            "[FrozenWM] reloaded %d→%d objects from %s in %.1fms (skipped=%d)",
            old_n, new_n, path, duration_ms, skipped,
        )
        return {
            "old_objects": old_n,
            "new_objects": new_n,
            "old_loaded_utc": old_loaded_utc,
            "new_loaded_utc": new_loaded_utc,
            "path": path,
            "duration_ms": duration_ms,
            "skipped": skipped,
        }

    # ---- tracking/mutation API: deliberately absent ----
    # Any attempt to call create_object/update_object/decay/etc. will
    # AttributeError, which is the correct behavior in read-only mode.
