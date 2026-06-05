"""
Working Memory (WM)

Authoritative in-memory store for *live* objects (proto + confirmed).
- Owns lifecycle: create, update, merge, confirm (promote), expire.
- Holds embeddings (mean + small gallery), label EWMA, stability, pose, timestamps.
- Mirrors spatial membership via an injected ObjectIndex (proximity index).
- Prepares compact payloads to upsert into Milvus (LTM) when objects are ready.
- 2026-05-31: per-object image_crops + emb_gallery are MIRRORED TO DISK
  under cfg.object.crops_root (default /mnt/rtsm-data/rtsm-workdir/crops).
  Rehydrate restores both from disk, closing the cross-restart matching gap
  that caused new OIDs to spawn for re-observed physical objects.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, List, Iterable, Any, Callable, Protocol
import numpy as np
import time
import uuid
import threading
import heapq
import logging
import os
import shutil
import json

logger = logging.getLogger(__name__)

# --- type aliases ---
Vec3 = np.ndarray  # shape (3,), float32
Emb = np.ndarray   # shape (D,), float32 L2-normalized unless stated

# Sentinel for update_user_fields(): distinguishes "field omitted"
# (leave unchanged) from "field set to None" (clear). Module-level so
# server.py can import it for the PATCH /objects/{oid} handler.
_UNSET: Any = object()

# --- helpers ---

def _l2norm(v: Emb) -> Emb:
    n = float(np.linalg.norm(v) + 1e-12)
    return (v / n).astype(np.float32)


def _cos(a: Emb, b: Emb) -> float:
    return float(np.dot(a, b))


def _now_mono() -> float:
    return time.monotonic()


def _now_wall_utc() -> float:
    return time.time()


def _compress_crop_jpeg(crop: np.ndarray, quality: int = 75) -> bytes:
    """Compress 224x224x3 uint8 crop to JPEG bytes."""
    import cv2
    if crop is None or crop.size == 0:
        return b''
    try:
        if len(crop.shape) == 3 and crop.shape[-1] == 3:
            crop_bgr = crop[..., ::-1].copy()
        else:
            crop_bgr = crop
        ok, buf = cv2.imencode('.jpg', crop_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if ok:
            return bytes(buf)
    except Exception:
        pass
    return b''


def _view_bin_id(view_dir_cam: Optional[np.ndarray], AZ_BINS: int, EL_BINS: int) -> Optional[int]:
    if view_dir_cam is None:
        return None
    v = view_dir_cam.astype(np.float32)
    n = np.linalg.norm(v)
    if n < 1e-6:
        return None
    v = v / n
    x, y, z = float(v[0]), float(v[1]), float(v[2])
    az = np.arctan2(x, z)
    el = np.arctan2(-y, np.hypot(x, z))
    az_i = int(np.floor((az + np.pi) / (2*np.pi) * AZ_BINS))
    el_i = int(np.floor((el + np.pi/2) / np.pi    * EL_BINS))
    az_i = max(0, min(AZ_BINS-1, az_i))
    el_i = max(0, min(EL_BINS-1, el_i))
    return el_i * AZ_BINS + az_i


# ------------------------- persistent gallery (2026-05-31) -------------------------

class _PersistentGallery:
    """Disk-backed mirror of (image_crops, emb_gallery) per OID.

    Layout under `root`:
        <root>/<oid>/
            0001.jpg, 0002.jpg, ...   FIFO-numbered crops (zero-padded)
            embs.npy                  (M, D) float16 -- emb_gallery contents
            manifest.json             {"next_counter": int}

    Crops and embeddings are tracked as independent FIFO buffers because
    emb_gallery has dedup gating (gallery_dupe_cos) while image_crops
    appends every observed crop -- they can have different lengths in
    steady state.

    All methods are best-effort: any I/O failure logs and continues. Disk
    state is a cache that improves cross-restart matching; corruption
    degrades to the "empty gallery on rehydrate" behavior, never crashes
    the ingest path.

    Atomic writes via .tmp + os.replace so a crash mid-write cannot leave
    a partial embs.npy that would fail np.load on rehydrate. Per-crop
    JPEGs use the same pattern (individual JPEGs are also separate files,
    so a partial write can't poison sibling crops).
    """

    def __init__(self, root: str, enabled: bool) -> None:
        self.root = str(root) if root else ""
        self.enabled = bool(enabled and self.root)
        if self.enabled:
            try:
                os.makedirs(self.root, exist_ok=True)
            except Exception:
                logger.exception(
                    "[gallery] cannot create root %r; disabling persistence",
                    self.root,
                )
                self.enabled = False

    def _dir(self, oid: str) -> str:
        return os.path.join(self.root, oid)

    def _manifest_path(self, oid: str) -> str:
        return os.path.join(self._dir(oid), "manifest.json")

    def _embs_path(self, oid: str) -> str:
        return os.path.join(self._dir(oid), "embs.npy")

    def _read_manifest(self, oid: str) -> Dict[str, Any]:
        path = self._manifest_path(oid)
        if not os.path.exists(path):
            return {"next_counter": 1}
        try:
            with open(path, "r") as fp:
                m = json.load(fp)
            if not isinstance(m, dict) or "next_counter" not in m:
                return {"next_counter": 1}
            return m
        except Exception:
            return {"next_counter": 1}

    def _write_manifest(self, oid: str, manifest: Dict[str, Any]) -> None:
        path = self._manifest_path(oid)
        tmp = path + ".tmp"
        try:
            with open(tmp, "w") as fp:
                json.dump(manifest, fp)
            os.replace(tmp, path)
        except Exception:
            logger.exception("[gallery] manifest write failed for %s", oid[:8])
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass

    def write_crop(self, oid: str, jpeg_bytes: bytes, max_crops: int) -> None:
        """Append jpeg_bytes as the next FIFO crop; prune to max_crops."""
        if not self.enabled or not jpeg_bytes:
            return
        try:
            d = self._dir(oid)
            os.makedirs(d, exist_ok=True)
            manifest = self._read_manifest(oid)
            counter = int(manifest.get("next_counter", 1))
            fname = f"{counter:04d}.jpg"
            path = os.path.join(d, fname)
            tmp = path + ".tmp"
            with open(tmp, "wb") as fp:
                fp.write(jpeg_bytes)
            os.replace(tmp, path)
            manifest["next_counter"] = counter + 1
            self._write_manifest(oid, manifest)
            # FIFO prune: sort by filename (zero-padded -> chronological)
            jpegs = sorted(f for f in os.listdir(d) if f.endswith(".jpg"))
            excess = len(jpegs) - int(max_crops)
            for old in jpegs[:max(0, excess)]:
                try:
                    os.remove(os.path.join(d, old))
                except Exception:
                    pass
        except Exception:
            logger.exception("[gallery] crop write failed for %s", oid[:8])

    def write_embs(self, oid: str, embs: np.ndarray) -> None:
        """Atomically overwrite embs.npy with the full current emb_gallery."""
        if not self.enabled:
            return
        if embs is None or embs.size == 0:
            # Empty gallery: ensure no stale file is left behind
            try:
                p = self._embs_path(oid)
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass
            return
        try:
            d = self._dir(oid)
            os.makedirs(d, exist_ok=True)
            path = self._embs_path(oid)
            # numpy's .npy auto-extension forces this detour: write to
            # <path>.tmp.npy (which IS .npy-terminated, so np.save uses
            # it exactly), then atomic rename to <path>.
            tmp = path + ".tmp.npy"
            np.save(tmp, embs.astype(np.float16, copy=False))
            os.replace(tmp, path)
        except Exception:
            logger.exception("[gallery] embs write failed for %s", oid[:8])

    def load(self, oid: str) -> Tuple[List[bytes], Optional[np.ndarray]]:
        """Load (crops_bytes_list, emb_gallery_or_None) from disk."""
        if not self.enabled:
            return [], None
        d = self._dir(oid)
        if not os.path.isdir(d):
            return [], None
        crops: List[bytes] = []
        try:
            jpegs = sorted(f for f in os.listdir(d) if f.endswith(".jpg"))
            for fname in jpegs:
                try:
                    with open(os.path.join(d, fname), "rb") as fp:
                        crops.append(fp.read())
                except Exception:
                    continue
        except Exception:
            logger.exception("[gallery] crop scan failed for %s", oid[:8])
        embs: Optional[np.ndarray] = None
        emb_path = self._embs_path(oid)
        if os.path.exists(emb_path):
            try:
                arr = np.load(emb_path)
                if arr.ndim == 2 and arr.shape[0] > 0:
                    embs = arr
            except Exception:
                logger.exception("[gallery] embs load failed for %s", oid[:8])
        return crops, embs

    def remove(self, oid: str) -> None:
        if not self.enabled:
            return
        d = self._dir(oid)
        if os.path.isdir(d):
            try:
                shutil.rmtree(d)
            except Exception:
                logger.exception("[gallery] remove failed for %s", oid[:8])

    def clear_all(self) -> None:
        if not self.enabled:
            return
        if os.path.isdir(self.root):
            try:
                shutil.rmtree(self.root)
                os.makedirs(self.root, exist_ok=True)
            except Exception:
                logger.exception("[gallery] clear_all failed")

    def list_oids(self) -> List[str]:
        """List OIDs that have on-disk gallery data. For diagnostic/cleanup."""
        if not self.enabled or not os.path.isdir(self.root):
            return []
        try:
            return [d for d in os.listdir(self.root)
                    if os.path.isdir(os.path.join(self.root, d))]
        except Exception:
            return []


# --- minimal observation contract (duck-typed) ---
# Association should pass an object with these attributes. A simple dataclass works too.
#   obs.p_world: Vec3 (world meters)                  [required]
#   obs.emb_vis: Emb (float32, L2)                    [required]
#   obs.view_dir_cam: np.ndarray, shape (3,) or None  [optional]
#   obs.centroid_px: tuple[int,int] or None           [optional]
#   obs.label_topk: list[tuple[str,float]] or None    [optional]
#   obs.depth_valid: float in [0,1]                   [optional]
#   obs.quality: float in [0,1]                       [optional]


# ------------------------- object state -------------------------
@dataclass(slots=True)
class ObjectState:
    id: str
    xyz_world: Vec3
    cov_world: Vec3                      # diag variance (m^2), shape (3,)

    emb_mean: Emb                        # float32 L2-normalized
    emb_gallery: np.ndarray              # float16, shape (N,D)

    view_bins: Dict[int, Emb]            # bin_id -> mean emb (float32 L2)

    label_scores: Dict[str, float]       # EWMA label scores
    label_hits:   Dict[str, int]         # per-label observation count (precision gate)
    label_primary: Optional[str]

    stability: float                     # [0,1]
    hits: int

    confirmed: bool

    created_mono: float
    created_wall_utc: float

    last_seen_mono: float
    last_seen_wall_utc: float
    last_seen_px: Optional[Tuple[float, float]]

    last_upsert_wall_utc: float          # 0 if never upserted
    last_upsert_mono: float              # 0 if never upserted (monotonic seconds)
    last_upsert_emb: Optional[Emb]
    last_upsert_xyz: Optional[Vec3]

    # RGB crop gallery (JPEG-compressed bytes, most recent last).
    # 2026-05-31: mirrored to disk via _PersistentGallery; survives restart.
    image_crops: List[bytes]

    # Frame tracking for precise pose corrections
    last_update_frame_id: Optional[str]

    # cache
    _dim: int

    # --- 2026-05-11 PR: user override + lifecycle hooks ---
    label_user: Optional[str] = None
    movability_class: Optional[str] = None
    pose_state_at_observation: str = "on_floor"

    # --- 2026-05-29: reference snapshot (named-moment ground truth) ---
    reference_image_path: Optional[str] = None
    reference_emb: Optional[Emb] = None

# ------------------------- Proximity index interface -------------------------

class ProximityIndexLike(Protocol):
    """Protocol for the minimal methods WorkingMemory needs from the ProximityIndex."""

    def insert(self, oid: str, xyz_world: Vec3, wm_lookup: Optional[Callable[[str], Optional[Tuple[bool, float, float]]]] = None) -> None: ...

    def update(self, oid: str, old_xyz_world: Vec3, new_xyz_world: Vec3, wm_lookup: Optional[Callable[[str], Optional[Tuple[bool, float, float]]]] = None) -> None: ...

    def remove(self, oid: str, last_xyz_world: Optional[Vec3] = None) -> None: ...

# ------------------------- Working Memory -------------------------

class WorkingMemory:
    def __init__(self, cfg: Dict[str, Any], *, index: Optional[ProximityIndexLike] = None) -> None:
        self.cfg = cfg
        self.index = index

        self._map: Dict[str, ObjectState] = {}
        self._lock = threading.RLock()
        self._latest_pose: Optional[Dict[str, Any]] = None
        self._frame_to_objects: Dict[str, set] = {}
        self._proto_heap: List[Tuple[float, str]] = []
        self._ltm_heap: List[Tuple[float, str]] = []
        self._upsert_count_total: int = 0

        # configs (with defaults)
        obj_cfg = cfg.get("object", {})
        self.proto_ttl_s: float = float(obj_cfg.get("proto_ttl_s", 10.0))
        self.promote_hits: int = int(obj_cfg.get("promote_hits", 2))
        self.stability_promote: float = float(obj_cfg.get("stability_promote", 0.50))
        self.promote_min_conf: float = float(obj_cfg.get("promote_min_conf", 0.18))
        self.min_label_hits: int = int(obj_cfg.get("min_label_hits", 5))
        self.require_view_bins: int = int(obj_cfg.get("require_view_bins", 2))
        self.stab_k: float = float(obj_cfg.get("stab_k", 0.45))
        self.miss_decay: float = float(obj_cfg.get("miss_decay", 0.92))

        self.az_bins: int = int(cfg.get("view", {}).get("az_bins", 8))
        self.el_bins: int = int(cfg.get("view", {}).get("el_bins", 3))

        pose_cfg = cfg.get("pose", {})
        self.meas_var_xyz_cm2 = np.array(pose_cfg.get("meas_var_xyz_cm2", [1.5, 1.5, 3.0]), dtype=np.float32) / 1e4
        self.proc_var_xyz_cm2 = np.array(pose_cfg.get("proc_var_xyz_cm2", [0.2, 0.2, 0.4]), dtype=np.float32) / 1e4
        self.pose_demote_thresh_m: float = float(pose_cfg.get("demote_thresh_m", 0.30))

        ltm_cfg = cfg.get("ltm", {})
        self.reupsert_cos_max: float = float(ltm_cfg.get("reupsert_cos_max", 0.995))
        self.reupsert_pos_m: float = float(ltm_cfg.get("reupsert_pos_m", 0.05))
        self.ltm_min_view_bins: int = int(ltm_cfg.get("ltm_min_view_bins", 2))
        self.ltm_min_period_s: float = float(ltm_cfg.get("min_period_s", 1.0))
        self.ltm_force_period_s: float = float(ltm_cfg.get("force_period_s", 10.0))

        # 2026-05-31: gallery caps bumped from 6 to 10. With persistent
        # storage, 10 viewpoints per object is ~30 KB/crop * 10 = ~300 KB,
        # which is negligible (100 objects = ~30 MB, 1000 = ~300 MB).
        # Larger N gives stronger cross-restart matching and survives
        # individual bad crops (occlusion, blur, lighting).
        self.max_gallery: int = int(obj_cfg.get("max_gallery", 10))
        self.gallery_dupe_cos: float = float(obj_cfg.get("gallery_dupe_cos", 0.995))
        self.max_image_crops: int = int(obj_cfg.get("max_image_crops", 10))
        self.emb_mean_hits_threshold: int = int(obj_cfg.get("emb_mean_hits_threshold", 20))
        self.emb_mean_ewma_alpha: float = float(obj_cfg.get("emb_mean_ewma_alpha", 0.05))

        # 2026-05-30: coarse-default movability_class on proto spawn.
        _raw_default_mov = obj_cfg.get("default_movability", "movable")
        if _raw_default_mov is None:
            self.default_movability: Optional[str] = None
        elif _raw_default_mov in self._AUTO_DEFAULT_MOVABILITY_OK:
            self.default_movability = str(_raw_default_mov)
        else:
            logger.warning(
                "[WM] object.default_movability=%r is not auto-assignable "
                "(must be one of %s, or null). static/permanent are "
                "landmark-eligible and require manual PATCH. Falling back to "
                "'movable'. See movability_assignment_design.md.",
                _raw_default_mov, sorted(self._AUTO_DEFAULT_MOVABILITY_OK),
            )
            self.default_movability = "movable"

        # 2026-05-31: persistent gallery. Disk-backed mirror of
        # image_crops + emb_gallery per OID. Default ON. Set
        # cfg.object.persist_galleries = false to revert to RAM-only.
        crops_root = str(obj_cfg.get(
            "crops_root", "/mnt/rtsm-data/rtsm-workdir/crops"
        ))
        persist_galleries = bool(obj_cfg.get("persist_galleries", True))
        self._gallery = _PersistentGallery(crops_root, persist_galleries)
        if self._gallery.enabled:
            logger.info(
                "[WM] persistent gallery enabled at %s "
                "(max_gallery=%d max_image_crops=%d)",
                crops_root, self.max_gallery, self.max_image_crops,
            )
        else:
            logger.info("[WM] persistent gallery disabled")

        self._pose_state: str = "on_floor"
        self._current_observation_tag: str = "on_floor"
        self._writes_skipped_lifted: int = 0
        self._writes_skipped_unknown: int = 0



    # ---------- CRUD ----------

    def set_pose_state(self, state: str) -> Dict[str, Any]:
        valid = {"on_floor", "lifted", "unknown", "confirmed_elevated"}
        old_state = self._pose_state

        if state not in valid:
            logger.warning(
                "[WM] set_pose_state: invalid state '%s'; clamping to 'unknown'",
                state,
            )
            state = "unknown"

        with self._lock:
            self._pose_state = state
            if state == "confirmed_elevated":
                self._current_observation_tag = "elevated"
            else:
                self._current_observation_tag = "on_floor"

        logger.info(
            "[WM] pose_state %s -> %s (tag=%s)",
            old_state, state, self._current_observation_tag,
        )
        return {
            "old_state": old_state,
            "new_state": state,
            "current_tag": self._current_observation_tag,
            "writes_skipped_lifted": self._writes_skipped_lifted,
            "writes_skipped_unknown": self._writes_skipped_unknown,
        }

    def get_pose_state(self) -> str:
        return self._pose_state



    def exists(self, oid: str) -> bool:
        with self._lock:
            return oid in self._map

    def get(self, oid: str) -> Optional[ObjectState]:
        with self._lock:
            return self._map.get(oid)

    def lookup_min(self, oid: str) -> Optional[Tuple[bool, float, float]]:
        """Tiny tuple used by ProximityIndex eviction ranking: (confirmed, stability, last_seen_mono)."""
        with self._lock:
            o = self._map.get(oid)
            if o is None:
                return None
            return (o.confirmed, o.stability, o.last_seen_mono)

    _VALID_MOVABILITY = frozenset({
        "permanent", "static", "semi_static",
        "movable", "roaming", "ephemeral",
    })
    _AUTO_DEFAULT_MOVABILITY_OK = frozenset({
        "semi_static", "movable", "roaming", "ephemeral",
    })

    def update_user_fields(
        self,
        oid: str,
        *,
        label_user: Any = _UNSET,
        movability_class: Any = _UNSET,
    ) -> Optional["ObjectState"]:
        """Thread-safe update of user-controllable fields on an ObjectState."""
        with self._lock:
            o = self._map.get(oid)
            if o is None:
                return None
            if label_user is not _UNSET:
                if label_user is not None:
                    if not isinstance(label_user, str) or not label_user.strip():
                        raise ValueError(
                            "label_user must be a non-empty string or None"
                        )
                    o.label_user = label_user.strip()
                else:
                    o.label_user = None
            if movability_class is not _UNSET:
                if movability_class is not None and movability_class not in self._VALID_MOVABILITY:
                    raise ValueError(
                        f"movability_class must be one of "
                        f"{sorted(self._VALID_MOVABILITY)} or None, "
                        f"got {movability_class!r}"
                    )
                o.movability_class = movability_class
            return o


    # ------------------------------------------------------------------ #
    # 2026-05-28: Tier-2 time-based eviction policy (movability-aware).
    # ------------------------------------------------------------------ #

    _DEFAULT_EVICTION_TTL_S = {
        "permanent":   None,
        "static":      90.0 * 86400.0,
        "semi_static": 14.0 * 86400.0,
        "movable":      3.0 * 86400.0,
        "roaming":      1.0 * 86400.0,
        "ephemeral":   12.0 * 3600.0,
    }
    _EVICTION_FALLBACK_CLASS = "semi_static"

    def _eviction_ttl_s(self, cls: Optional[str]) -> Optional[float]:
        if cls not in self._VALID_MOVABILITY:
            cls = self._EVICTION_FALLBACK_CLASS
        ttl = dict(self._DEFAULT_EVICTION_TTL_S)
        override = (self.cfg.get("eviction", {}) or {}).get("ttl_s", {}) or {}
        for k, v in override.items():
            if k in self._VALID_MOVABILITY:
                ttl[k] = (None if v is None else float(v))
        return ttl.get(cls)

    def _compute_evictable_locked(self, now_wall: float) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for oid, o in self._map.items():
            if not getattr(o, "confirmed", False):
                continue
            if getattr(o, "label_user", None) is not None:
                continue
            raw_cls = getattr(o, "movability_class", None)
            eff_cls = (raw_cls if raw_cls in self._VALID_MOVABILITY
                       else self._EVICTION_FALLBACK_CLASS)
            ttl = self._eviction_ttl_s(eff_cls)
            if ttl is None:
                continue
            ls = float(getattr(o, "last_seen_wall_utc", 0.0) or 0.0)
            if ls <= 0.0:
                continue
            age = now_wall - ls
            if age > ttl:
                out.append({
                    "oid": oid,
                    "movability_class": eff_cls,
                    "movability_class_raw": raw_cls,
                    "age_s": round(age, 3),
                    "ttl_s": ttl,
                    "label": (getattr(o, "label_user", None)
                              or getattr(o, "label_primary", None)),
                })
        out.sort(key=lambda d: d["age_s"], reverse=True)
        return out

    def select_evictable(self, now_wall: Optional[float] = None) -> List[Dict[str, Any]]:
        if now_wall is None:
            now_wall = _now_wall_utc()
        with self._lock:
            return self._compute_evictable_locked(now_wall)

    def evict_stale(
        self,
        now_wall: Optional[float] = None,
        *,
        dry_run: Optional[bool] = None,
        ghost_sink: Optional[Callable[[str, "ObjectState"], None]] = None,
    ) -> Dict[str, Any]:
        evic_cfg = self.cfg.get("eviction", {}) or {}
        enabled = bool(evic_cfg.get("enabled", False))
        if dry_run is None:
            dry_run = bool(evic_cfg.get("dry_run", False))
        if now_wall is None:
            now_wall = _now_wall_utc()

        result: Dict[str, Any] = {
            "enabled": enabled,
            "dry_run": bool(dry_run),
            "ts_wall": now_wall,
            "scanned": 0,
            "evicted": [],
            "by_class": {},
        }
        if not enabled:
            return result

        removed: List[str] = []
        with self._lock:
            result["scanned"] = sum(
                1 for o in self._map.values() if getattr(o, "confirmed", False)
            )
            candidates = self._compute_evictable_locked(now_wall)
            result["evicted"] = candidates
            for c in candidates:
                cls = c["movability_class"]
                result["by_class"][cls] = result["by_class"].get(cls, 0) + 1
            if dry_run:
                return result
            for c in candidates:
                oid = c["oid"]
                o = self._map.get(oid)
                if o is None:
                    continue
                if getattr(o, "label_user", None) is not None:
                    continue
                if ghost_sink is not None:
                    try:
                        ghost_sink(oid, o)
                    except Exception:
                        logger.exception("eviction ghost_sink failed for %s", oid)
                fid = getattr(o, "last_update_frame_id", None)
                if fid is not None:
                    fset = self._frame_to_objects.get(fid)
                    if fset is not None:
                        fset.discard(oid)
                        if not fset:
                            del self._frame_to_objects[fid]
                del self._map[oid]
                removed.append(oid)
        if self.index is not None:
            for oid in removed:
                try:
                    self.index.remove(oid, None)
                except Exception:
                    logger.exception("eviction index.remove failed for %s", oid)
        # 2026-05-31: clean disk gallery for evicted OIDs (outside the lock)
        for oid in removed:
            self._gallery.remove(oid)
        return result

    # 2026-06-01: Mode B duplicate consolidation.
    #
    # POST /objects/merge calls merge_objects(winner_oid, loser_oid).
    # The winner's id and xyz survive; the loser is dissolved into the
    # winner (galleries unioned with dedup, hits summed, view_bins
    # unioned, label_scores hits-weighted averaged, user-pinned fields
    # preserved). Disk gallery for loser is removed; winner's is rewritten
    # to match merged state.
    #
    # The merge is an in-WM operation. The caller (POST /objects/merge in
    # server.py) is responsible for syncing the change to FAISS by
    # calling faiss_client.delete([loser_oid]) followed by
    # faiss_client.upsert_batch([winner_record]) using the helper
    # build_faiss_record_for_merge() below.
    # ------------------------------------------------------------------ #

    def merge_objects(
        self,
        winner_oid: str,
        loser_oid: str,
        *,
        dry_run: bool = False,
        audit_log_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Consolidate loser_oid into winner_oid.

        Returns a result dict with stats and the audit log path (if written).
        Raises ValueError on winner==loser, dim mismatch, etc.
        Returns {"error": "not_found", ...} if either oid is unknown.

        Side effects on success (non-dry-run):
          - winner's ObjectState in WM gets the merged values
          - loser is removed from WM map, spatial index, frame tracking
          - winner's persistent gallery directory is rewritten on disk
          - loser's persistent gallery directory is removed
          - audit log JSON written under audit_log_dir (best-effort)

        FAISS is NOT touched here. The caller must sync separately.
        """
        if winner_oid == loser_oid:
            raise ValueError("winner_oid and loser_oid must differ")

        # Snapshot both states under the lock so we have a consistent
        # picture for the audit log AND the merge computation. We hold the
        # lock for the whole modify-and-remove phase to keep the operation
        # atomic from the WM's perspective.
        with self._lock:
            winner = self._map.get(winner_oid)
            loser = self._map.get(loser_oid)
            if winner is None:
                return {"error": "not_found", "missing_oid": winner_oid}
            if loser is None:
                return {"error": "not_found", "missing_oid": loser_oid}
            if winner._dim != loser._dim:
                raise ValueError(
                    f"dim mismatch: winner={winner._dim} loser={loser._dim}"
                )

            # Pre-merge snapshots for the audit log (taken before any mutation).
            winner_pre = self._snapshot_for_audit(winner)
            loser_pre = self._snapshot_for_audit(loser)

            # Compute the merged values as a pure function over the two
            # ObjectStates. No side effects yet.
            merged = self._compute_merge_locked(winner, loser)

            stats = {
                "hits_before": {"winner": winner.hits, "loser": loser.hits},
                "hits_after": merged["hits"],
                "emb_gallery_before": {
                    "winner": int(winner.emb_gallery.shape[0]),
                    "loser": int(loser.emb_gallery.shape[0]),
                },
                "emb_gallery_after": int(merged["emb_gallery"].shape[0]),
                "image_crops_before": {
                    "winner": len(winner.image_crops),
                    "loser": len(loser.image_crops),
                },
                "image_crops_after": len(merged["image_crops"]),
                "view_bins_before": {
                    "winner": len(winner.view_bins),
                    "loser": len(loser.view_bins),
                },
                "view_bins_after": len(merged["view_bins"]),
                "label_user_inherited_from_loser":
                    merged["_label_user_inherited_from_loser"],
                "winner_xyz": winner.xyz_world.tolist(),
                "loser_xyz": loser.xyz_world.tolist(),
                "spatial_distance_m": float(
                    np.linalg.norm(winner.xyz_world - loser.xyz_world)
                ),
            }

            if dry_run:
                return {
                    "winner_oid": winner_oid,
                    "loser_oid": loser_oid,
                    "dry_run": True,
                    "stats": stats,
                    "audit_log_path": None,
                    "winner_pre": winner_pre,
                    "loser_pre": loser_pre,
                }

            # ---- Apply merge to winner in-place ----
            winner.emb_mean = merged["emb_mean"]
            winner.emb_gallery = merged["emb_gallery"]
            winner.view_bins = merged["view_bins"]
            winner.label_scores = merged["label_scores"]
            winner.label_hits = merged["label_hits"]
            winner.label_primary = merged["label_primary"]
            winner.label_user = merged["label_user"]
            winner.movability_class = merged["movability_class"]
            winner.reference_image_path = merged["reference_image_path"]
            winner.reference_emb = merged["reference_emb"]
            winner.hits = merged["hits"]
            winner.stability = merged["stability"]
            winner.image_crops = merged["image_crops"]
            winner.created_mono = merged["created_mono"]
            winner.created_wall_utc = merged["created_wall_utc"]
            winner.last_seen_mono = merged["last_seen_mono"]
            winner.last_seen_wall_utc = merged["last_seen_wall_utc"]
            # xyz / cov / pose_state stay as winner's (the canonical position).
            # last_upsert_* stay as winner's; the caller is expected to
            # re-upsert to FAISS, which will overwrite these on success.

            # ---- Remove loser from WM (mirrors evict_stale pattern) ----
            loser_frame_id = loser.last_update_frame_id
            if loser_frame_id is not None:
                fset = self._frame_to_objects.get(loser_frame_id)
                if fset is not None:
                    fset.discard(loser_oid)
                    if not fset:
                        del self._frame_to_objects[loser_frame_id]
            del self._map[loser_oid]

            # Take a snapshot of the merged winner for the audit log.
            winner_post = self._snapshot_for_audit(winner)

        # ---- Outside the lock: spatial index + disk persistence ----
        if self.index is not None:
            try:
                self.index.remove(loser_oid, None)
            except Exception:
                logger.exception(
                    "[WM] merge: index.remove failed for loser %s",
                    loser_oid[:8],
                )

        # Rewrite winner's gallery on disk to match the merged state.
        # We do this by clearing winner's directory first, then writing
        # all merged crops and the merged embs. Atomic enough for our
        # purposes -- if a crash occurs mid-rewrite, rehydrate falls back
        # to whatever's on disk and the next observation rebuilds it.
        try:
            self._rewrite_gallery_after_merge(winner_oid, winner)
        except Exception:
            logger.exception(
                "[WM] merge: gallery rewrite failed for winner %s",
                winner_oid[:8],
            )

        # Remove loser's disk gallery.
        try:
            self._gallery.remove(loser_oid)
        except Exception:
            logger.exception(
                "[WM] merge: gallery.remove failed for loser %s",
                loser_oid[:8],
            )

        # ---- Audit log (best-effort) ----
        audit_log_path: Optional[str] = None
        try:
            audit_log_path = self._write_merge_audit(
                audit_log_dir, winner_oid, loser_oid,
                winner_pre, loser_pre, winner_post, stats,
            )
        except Exception:
            logger.exception("[WM] merge: audit log write failed")

        logger.info(
            "[WM] merge: %s <- %s | hits %d->%d, gallery %d->%d, bins %d->%d",
            winner_oid[:8], loser_oid[:8],
            winner_pre.get("hits", 0), stats["hits_after"],
            winner_pre.get("emb_gallery_n", 0), stats["emb_gallery_after"],
            len(winner_pre.get("view_bin_keys", [])), stats["view_bins_after"],
        )

        return {
            "winner_oid": winner_oid,
            "loser_oid": loser_oid,
            "dry_run": False,
            "stats": stats,
            "audit_log_path": audit_log_path,
            "winner_pre": winner_pre,
            "loser_pre": loser_pre,
            "winner_post": winner_post,
        }

    # ---- Merge internals (private; safe to call only under self._lock) ----

    def _compute_merge_locked(
        self,
        winner: "ObjectState",
        loser: "ObjectState",
    ) -> Dict[str, Any]:
        """Compute the merged field values. Pure: no side effects.

        Caller must hold self._lock (we read multiple fields from both
        ObjectStates and the read needs to be consistent).
        """
        w_hits = max(1, int(winner.hits))
        l_hits = max(1, int(loser.hits))

        # emb_mean: hits-weighted, renormalized.
        new_emb_mean = _l2norm(
            winner.emb_mean.astype(np.float32) * w_hits
            + loser.emb_mean.astype(np.float32) * l_hits
        )

        # emb_gallery: combine with the same dedup + FIFO gate that
        # update_object enforces, so the merged gallery satisfies the
        # invariant that all entries are >= gallery_dupe_cos apart.
        new_gallery = self._merge_galleries(winner.emb_gallery, loser.emb_gallery)

        # view_bins: union. On bin collision, average and renormalize
        # (same rule as update_object's per-bin update).
        new_view_bins: Dict[int, Emb] = {}
        for bin_id, emb in winner.view_bins.items():
            new_view_bins[bin_id] = emb.astype(np.float32).copy()
        for bin_id, emb in loser.view_bins.items():
            if bin_id in new_view_bins:
                new_view_bins[bin_id] = _l2norm(
                    0.5 * new_view_bins[bin_id]
                    + 0.5 * emb.astype(np.float32)
                )
            else:
                new_view_bins[bin_id] = emb.astype(np.float32).copy()

        # label_scores: per-key hits-weighted average. label_hits: sum.
        all_label_keys = (
            set(winner.label_scores.keys()) | set(loser.label_scores.keys())
        )
        new_label_scores: Dict[str, float] = {}
        new_label_hits: Dict[str, int] = {}
        for k in all_label_keys:
            w_s = float(winner.label_scores.get(k, 0.0))
            l_s = float(loser.label_scores.get(k, 0.0))
            w_k = int(winner.label_hits.get(k, 0))
            l_k = int(loser.label_hits.get(k, 0))
            denom = max(1, w_k + l_k)
            new_label_scores[k] = (w_s * w_k + l_s * l_k) / denom
            new_label_hits[k] = w_k + l_k

        # label_primary: recomputed from the merged scores. Gate on
        # min_label_hits to match the surfacing rule used elsewhere.
        gated = {
            k: v for k, v in new_label_scores.items()
            if new_label_hits.get(k, 0) >= self.min_label_hits
        }
        if gated:
            new_label_primary = max(gated, key=gated.get)
        elif new_label_scores:
            new_label_primary = max(
                new_label_scores.items(), key=lambda kv: kv[1]
            )[0]
        else:
            new_label_primary = winner.label_primary

        # image_crops: concat + FIFO truncate.
        new_crops = list(winner.image_crops) + list(loser.image_crops)
        if len(new_crops) > self.max_image_crops:
            new_crops = new_crops[-self.max_image_crops:]

        # User-pinned fields: winner wins if set, else inherit from loser.
        label_user_winner = winner.label_user
        label_user_loser = loser.label_user
        new_label_user = label_user_winner or label_user_loser
        label_user_inherited = (
            label_user_winner is None and label_user_loser is not None
        )

        new_movability = winner.movability_class or loser.movability_class

        new_ref_path = winner.reference_image_path or loser.reference_image_path
        new_ref_emb = (
            winner.reference_emb if winner.reference_image_path is not None
            else loser.reference_emb
        )

        return {
            "emb_mean": new_emb_mean,
            "emb_gallery": new_gallery,
            "view_bins": new_view_bins,
            "label_scores": new_label_scores,
            "label_hits": new_label_hits,
            "label_primary": new_label_primary,
            "label_user": new_label_user,
            "_label_user_inherited_from_loser": label_user_inherited,
            "movability_class": new_movability,
            "reference_image_path": new_ref_path,
            "reference_emb": new_ref_emb,
            "hits": winner.hits + loser.hits,
            "stability": max(winner.stability, loser.stability),
            "image_crops": new_crops,
            "created_mono": min(winner.created_mono, loser.created_mono),
            "created_wall_utc": min(
                winner.created_wall_utc, loser.created_wall_utc
            ),
            "last_seen_mono": max(winner.last_seen_mono, loser.last_seen_mono),
            "last_seen_wall_utc": max(
                winner.last_seen_wall_utc, loser.last_seen_wall_utc
            ),
        }

    def _merge_galleries(
        self,
        winner_emb: np.ndarray,
        loser_emb: np.ndarray,
    ) -> np.ndarray:
        """Combine two emb_galleries respecting dedup + FIFO.

        Same gate as update_object: each candidate emb is dropped if it's
        within gallery_dupe_cos of any existing entry. Survivors are
        appended with FIFO truncation to max_gallery.

        Returns float16 array of shape (M, D), 0 <= M <= max_gallery.
        """
        if (winner_emb is None or winner_emb.size == 0) and \
           (loser_emb is None or loser_emb.size == 0):
            # Both empty -- preserve dimensionality from whichever exists.
            ref = winner_emb if winner_emb is not None else loser_emb
            if ref is None:
                # Truly nothing; return a zero-row float16 with unknown D.
                # Shouldn't happen for confirmed objects but defensive.
                return np.zeros((0, 1), dtype=np.float16)
            return np.zeros((0, ref.shape[-1]), dtype=np.float16)

        # Start with winner's gallery as the base (preserves winner's
        # observation order at the front of the FIFO).
        if winner_emb is None or winner_emb.size == 0:
            combined = np.zeros((0, loser_emb.shape[-1]), dtype=np.float16)
        else:
            combined = winner_emb.astype(np.float16).copy()

        if loser_emb is None or loser_emb.size == 0:
            return combined

        # Append loser's entries one by one, applying the same dedup
        # gate as update_object's per-observation accumulation.
        for i in range(int(loser_emb.shape[0])):
            e32 = loser_emb[i].astype(np.float32)
            if combined.shape[0] > 0:
                cos_max = float(np.max(
                    combined.astype(np.float32) @ e32
                ))
                if cos_max >= self.gallery_dupe_cos:
                    continue  # near-duplicate; drop it
            e16 = e32.astype(np.float16)[None, :]
            if combined.shape[0] < self.max_gallery:
                combined = np.vstack([combined, e16])
            else:
                combined = np.vstack([combined[1:], e16])

        return combined

    def _rewrite_gallery_after_merge(
        self,
        oid: str,
        o: "ObjectState",
    ) -> None:
        """After in-memory merge, sync winner's disk gallery to match.

        Strategy: clear winner's directory, then re-write all current
        image_crops (numbered fresh from 1) and the merged embs.npy.
        This is simpler than trying to in-place-extend and avoids
        FIFO-numbering drift.

        Best-effort -- exceptions are logged but don't propagate. The
        in-memory state is the source of truth; disk is a cache.
        """
        if not self._gallery.enabled:
            return
        # Remove anything currently in winner's dir (.jpg, embs.npy,
        # manifest.json). Then write the merged contents fresh.
        self._gallery.remove(oid)
        # Re-create dir lazily via write_crop / write_embs.
        for jpeg_bytes in o.image_crops:
            self._gallery.write_crop(oid, jpeg_bytes, self.max_image_crops)
        if o.emb_gallery.shape[0] > 0:
            self._gallery.write_embs(oid, o.emb_gallery)

    def _snapshot_for_audit(
        self,
        o: "ObjectState",
    ) -> Dict[str, Any]:
        """Compact JSON-safe snapshot of an ObjectState for audit logs.

        Excludes embeddings (too large) but records their shapes. Keeps
        everything needed to identify and partially reconstruct the
        object if a merge needs to be manually reversed.
        """
        return {
            "id": o.id,
            "xyz_world": o.xyz_world.tolist(),
            "cov_world": o.cov_world.tolist(),
            "emb_mean_norm": float(np.linalg.norm(o.emb_mean)),
            "emb_gallery_n": int(o.emb_gallery.shape[0]),
            "view_bin_keys": sorted(int(k) for k in o.view_bins.keys()),
            "label_scores": dict(o.label_scores),
            "label_hits": dict(o.label_hits),
            "label_primary": o.label_primary,
            "label_user": o.label_user,
            "movability_class": o.movability_class,
            "pose_state_at_observation": o.pose_state_at_observation,
            "reference_image_path": o.reference_image_path,
            "hits": int(o.hits),
            "stability": float(o.stability),
            "confirmed": bool(o.confirmed),
            "created_wall_utc": float(o.created_wall_utc),
            "last_seen_wall_utc": float(o.last_seen_wall_utc),
            "image_crops_count": len(o.image_crops),
            "last_update_frame_id": o.last_update_frame_id,
        }

    def _write_merge_audit(
        self,
        audit_log_dir: Optional[str],
        winner_oid: str,
        loser_oid: str,
        winner_pre: Dict[str, Any],
        loser_pre: Dict[str, Any],
        winner_post: Dict[str, Any],
        stats: Dict[str, Any],
    ) -> Optional[str]:
        """Write merge audit JSON. Returns path written, or None."""
        # Resolve audit log directory. Caller-provided takes precedence;
        # else read from cfg.object.merge_log_dir; else default under
        # the persistent gallery's parent (so it sits alongside crops).
        if audit_log_dir is None:
            audit_log_dir = self.cfg.get("object", {}).get(
                "merge_log_dir", "/workspace/workdir/merge_log"
            )
        if not audit_log_dir:
            return None
        os.makedirs(audit_log_dir, exist_ok=True)

        ts = time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())
        fname = f"{ts}_{winner_oid[:8]}_{loser_oid[:8]}.json"
        path = os.path.join(audit_log_dir, fname)

        payload = {
            "timestamp_iso": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            ),
            "timestamp_wall_utc": _now_wall_utc(),
            "winner_oid": winner_oid,
            "loser_oid": loser_oid,
            "stats": stats,
            "winner_pre": winner_pre,
            "loser_pre": loser_pre,
            "winner_post": winner_post,
        }
        tmp = path + ".tmp"
        with open(tmp, "w") as fp:
            json.dump(payload, fp, indent=2, default=str)
        os.replace(tmp, path)
        return path

    # ---- FAISS record builder for the merge endpoint ----

    def build_faiss_record_for_merge(
        self,
        winner_oid: str,
    ) -> Optional[Dict[str, Any]]:
        """Construct the payload that the endpoint should upsert into
        FaissClient after a merge. Returns None if winner is gone.

        Mirrors the shape collect_ready_for_upsert produces. Read this
        AFTER merge_objects has completed; the values reflect merged
        state.
        """
        with self._lock:
            o = self._map.get(winner_oid)
            if o is None:
                return None
            label_topk = sorted(
                o.label_scores.items(), key=lambda kv: kv[1], reverse=True
            )
            label_topk_keys = [k for k, _ in label_topk]
            label_topk_scores = [float(v) for _, v in label_topk]
            label_topk_hits = [
                int(o.label_hits.get(k, 0)) for k in label_topk_keys
            ]
            return {
                "object_id": winner_oid,
                "emb": o.emb_mean.astype(np.float32),
                "xyz": o.xyz_world.astype(np.float32),
                "label_primary": o.label_primary,
                "label_user": o.label_user,
                "display_label": o.label_user or o.label_primary,
                "movability_class": o.movability_class,
                "label_topk": label_topk_keys,
                "label_scores": label_topk_scores,
                "label_hits": label_topk_hits,
                "stability": float(o.stability),
                "created_at": float(o.created_wall_utc),
                "created_mono": float(o.created_mono),
                "pose_state_at_observation": o.pose_state_at_observation,
            }

    # 2026-06-02: suggest_merges -- surface high-cosine + co-located pairs
    # for human review. Read-only sweep; does NOT mutate WM or FAISS.
    # The endpoint exists to make the manual merge pass systematic instead
    # of eyeballing. Conservative defaults (cos>=0.95, dist<=1.0m) match
    # the calibration finding that auto-merge is not safe at the storage
    # layer with emb_mean cosine alone, but human review of these
    # candidates is high-signal -- and each confirmed merge produces a
    # labeled positive pair as a side effect.

    def suggest_merges(
        self,
        *,
        cos_threshold: float = 0.95,
        dist_threshold_m: float = 1.0,
        require_same_label: bool = False,
        limit: int = 50,
        include_unconfirmed: bool = False,
    ) -> Dict[str, Any]:
        """Find candidate Mode B duplicate pairs by visual + spatial proximity.

        Returns pairs (a, b) where cosine(a.emb_mean, b.emb_mean) >=
        cos_threshold AND ||a.xyz - b.xyz|| <= dist_threshold_m.

        emb_mean is L2-normalized on every ObjectState, so dot product
        equals cosine similarity. The sweep is O(N^2); at the current
        corpus size (~230 OIDs) this is microseconds. Backlog: swap to
        FAISS range search when N > ~2000.

        Pairs are sorted by cosine descending (best matches first), then
        distance ascending. The response includes a suggested_winner_oid
        heuristic (reference-image > label_user > hits > stability), but
        the caller is free to ignore it -- POST /objects/merge accepts any
        winner_oid the user chooses.

        Read-only. Does not mutate WM or persist anything. The caller is
        responsible for reviewing snapshots (e.g., via
        /objects/{oid}/snapshots) and explicitly POSTing /objects/merge
        for each pair they confirm.
        """
        # Snapshot all relevant fields under the lock; do all compute on
        # local copies so we don't hold the lock during the O(N^2) sweep.
        with self._lock:
            if include_unconfirmed:
                pool = list(self._map.values())
            else:
                pool = [o for o in self._map.values() if o.confirmed]
            snapshots = [
                {
                    "oid": o.id,
                    "emb": o.emb_mean.astype(np.float32),
                    "xyz": o.xyz_world.astype(np.float32).copy(),
                    "label_primary": o.label_primary,
                    "label_user": o.label_user,
                    "hits": int(o.hits),
                    "stability": float(o.stability),
                    "has_reference": o.reference_image_path is not None,
                    "last_seen_wall_utc": float(o.last_seen_wall_utc),
                }
                for o in pool
            ]

        thresholds = {
            "cos_threshold": float(cos_threshold),
            "dist_threshold_m": float(dist_threshold_m),
            "require_same_label": bool(require_same_label),
            "include_unconfirmed": bool(include_unconfirmed),
            "limit": int(limit),
        }

        n = len(snapshots)
        if n < 2:
            return {
                "candidates": [],
                "total_pairs_above_thresholds": 0,
                "returned": 0,
                "scanned_objects": n,
                "thresholds": thresholds,
            }

        # Stack embeddings + compute one big cosine matrix. Embeddings
        # are pre-normalized so cos = dot. Float32 throughout to match
        # the numerics in update_object / _compute_merge_locked.
        embs = np.stack([s["emb"] for s in snapshots], axis=0)
        xyzs = np.stack([s["xyz"] for s in snapshots], axis=0)
        cos_mat = embs @ embs.T

        pairs: List[Dict[str, Any]] = []
        total_above = 0

        for i in range(n):
            a = snapshots[i]
            a_disp = a["label_user"] or a["label_primary"]
            for j in range(i + 1, n):
                cos_ij = float(cos_mat[i, j])
                if cos_ij < cos_threshold:
                    continue
                dist_ij = float(np.linalg.norm(xyzs[i] - xyzs[j]))
                if dist_ij > dist_threshold_m:
                    continue
                b = snapshots[j]
                b_disp = b["label_user"] or b["label_primary"]
                same_label = (
                    a_disp is not None
                    and b_disp is not None
                    and a_disp == b_disp
                )
                if require_same_label and not same_label:
                    continue

                total_above += 1
                suggested = self._suggest_merge_winner(a, b)
                pairs.append({
                    "a_oid": a["oid"],
                    "b_oid": b["oid"],
                    "suggested_winner_oid": suggested,
                    "cosine": round(cos_ij, 4),
                    "distance_m": round(dist_ij, 4),
                    "same_display_label": same_label,
                    "a_label_primary": a["label_primary"],
                    "b_label_primary": b["label_primary"],
                    "a_label_user": a["label_user"],
                    "b_label_user": b["label_user"],
                    "a_display_label": a_disp,
                    "b_display_label": b_disp,
                    "a_hits": a["hits"],
                    "b_hits": b["hits"],
                    "a_stability": round(a["stability"], 3),
                    "b_stability": round(b["stability"], 3),
                    "a_has_reference": a["has_reference"],
                    "b_has_reference": b["has_reference"],
                    "a_xyz": xyzs[i].tolist(),
                    "b_xyz": xyzs[j].tolist(),
                    "a_last_seen_wall_utc": a["last_seen_wall_utc"],
                    "b_last_seen_wall_utc": b["last_seen_wall_utc"],
                })

        # Sort: highest cosine first, then closest distance.
        pairs.sort(key=lambda p: (-p["cosine"], p["distance_m"]))
        truncated = pairs[: max(0, int(limit))]

        return {
            "candidates": truncated,
            "total_pairs_above_thresholds": total_above,
            "returned": len(truncated),
            "scanned_objects": n,
            "thresholds": thresholds,
        }

    @staticmethod
    def _suggest_merge_winner(
        a: Dict[str, Any], b: Dict[str, Any],
    ) -> str:
        """Pick a suggested winner OID for a candidate merge pair.

        Heuristic priority (mirrors what survives in _compute_merge_locked,
        so the suggested winner is the one that would lose the least state
        in the merge):
          1. Reference image set -> keep that one (canonical photo).
          2. label_user set      -> keep that one (human pin).
          3. More hits           -> keep that one (more observations).
          4. Higher stability    -> tiebreak.
        Caller can ignore -- /objects/merge accepts any winner_oid.
        """
        if a["has_reference"] and not b["has_reference"]:
            return a["oid"]
        if b["has_reference"] and not a["has_reference"]:
            return b["oid"]
        a_lu = a["label_user"] is not None
        b_lu = b["label_user"] is not None
        if a_lu and not b_lu:
            return a["oid"]
        if b_lu and not a_lu:
            return b["oid"]
        if a["hits"] > b["hits"]:
            return a["oid"]
        if b["hits"] > a["hits"]:
            return b["oid"]
        if a["stability"] >= b["stability"]:
            return a["oid"]
        return b["oid"]

    def iter_objects(self) -> Iterable[ObjectState]:
        with self._lock:
            return list(self._map.values())

    # ---------- create / spawn ----------

    def create_object(self, p_world: Vec3, emb_vis: Emb, *, t_mono: Optional[float] = None,
                      label_topk: Optional[List[Tuple[str, float]]] = None,
                      view_dir_cam: Optional[np.ndarray] = None,
                      centroid_px: Optional[Tuple[float, float]] = None,
                      crop: Optional[np.ndarray] = None,
                      frame_id: Optional[str] = None) -> Optional[str]:
        """Spawn a new proto object. Index is updated here as well."""
        ps = self._pose_state
        if ps == "lifted":
            self._writes_skipped_lifted += 1
            return None
        if ps == "unknown":
            self._writes_skipped_unknown += 1
            return None
        t_mono = _now_mono() if t_mono is None else t_mono
        wall_now = _now_wall_utc()
        emb_vis = emb_vis.astype(np.float32)
        D = int(emb_vis.shape[0])

        bounds_cfg = self.cfg.get("object", {}).get("position_bounds_m", None)
        if bounds_cfg is not None:
            x_bounds = bounds_cfg.get("x", [-100, 100])
            y_bounds = bounds_cfg.get("y", [-100, 100])
            z_bounds = bounds_cfg.get("z", [-100, 100])
            px, py, pz = float(p_world[0]), float(p_world[1]), float(p_world[2])
            if not (x_bounds[0] <= px <= x_bounds[1] and
                    y_bounds[0] <= py <= y_bounds[1] and
                    z_bounds[0] <= pz <= z_bounds[1]):
                logger.warning(
                    f"[WM] create_object rejected: position out of bounds "
                    f"xyz=[{px:.2f},{py:.2f},{pz:.2f}] "
                    f"bounds=x{x_bounds} y{y_bounds} z{z_bounds}"
                )
                return None

        oid = uuid.uuid4().hex[:16]
        emb_mean = emb_vis.copy()
        gallery = emb_vis.astype(np.float16)[None, :]
        view_bins: Dict[int, Emb] = {}
        b = _view_bin_id(view_dir_cam, self.az_bins, self.el_bins)
        if b is not None:
            view_bins[b] = emb_vis.copy()

        label_scores: Dict[str, float] = {}
        label_hits:   Dict[str, int]   = {}
        if label_topk:
            for lbl, sc in label_topk:
                label_scores[lbl] = max(label_scores.get(lbl, 0.0), float(sc))
                label_hits[lbl]   = label_hits.get(lbl, 0) + 1
        label_primary = max(label_scores.items(), key=lambda kv: kv[1])[0] if label_scores else None

        image_crops: List[bytes] = []
        initial_crop_bytes: Optional[bytes] = None
        if crop is not None:
            jpeg_quality = int(self.cfg.get("object", {}).get("crop_jpeg_quality", 75))
            jpeg_bytes = _compress_crop_jpeg(crop, quality=jpeg_quality)
            if jpeg_bytes:
                image_crops.append(jpeg_bytes)
                initial_crop_bytes = jpeg_bytes

        o = ObjectState(
            id=oid,
            xyz_world=p_world.astype(np.float32),
            cov_world=np.array([0.02, 0.02, 0.04], dtype=np.float32),
            emb_mean=emb_mean,
            emb_gallery=gallery,
            view_bins=view_bins,
            label_scores=label_scores,
            label_hits=label_hits,
            label_primary=label_primary,
            stability=0.25,
            hits=1,
            confirmed=False,
            created_mono=t_mono,
            created_wall_utc=wall_now,
            last_seen_mono=t_mono,
            last_seen_wall_utc=wall_now,
            last_seen_px=centroid_px,
            last_upsert_wall_utc=0.0,
            last_upsert_mono=0.0,
            last_upsert_emb=None,
            last_upsert_xyz=None,
            image_crops=image_crops,
            last_update_frame_id=frame_id,
            _dim=D,
            pose_state_at_observation=self._current_observation_tag,
            movability_class=self.default_movability,
        )
        with self._lock:
            self._map[oid] = o
            if frame_id is not None:
                self._frame_to_objects.setdefault(frame_id, set()).add(oid)
            self._schedule_proto(oid, o)
        if self.index is not None:
            self.index.insert(oid, o.xyz_world, wm_lookup=self.lookup_min)
        # 2026-05-31: persist initial gallery state to disk (outside the lock)
        if initial_crop_bytes is not None:
            self._gallery.write_crop(oid, initial_crop_bytes, self.max_image_crops)
        if o.emb_gallery.shape[0] > 0:
            self._gallery.write_embs(oid, o.emb_gallery)
        logger.debug(
            f"[WM] create oid={oid} label={label_primary if label_primary else '-'} "
            f"xyz=[{p_world[0]:.2f},{p_world[1]:.2f},{p_world[2]:.2f}]"
        )
        return oid


    def update_object(self, oid: str, obs: Any, *, dt_s: Optional[float] = None) -> None:
        """Update state from a matched observation."""
        with self._lock:
            o = self._map.get(oid)
            if o is None:
                return
            old_xyz = o.xyz_world.copy()

        now_m = _now_mono()
        now_w = _now_wall_utc()
        dt_s = float(dt_s if dt_s is not None else max(1e-3, now_m - o.last_seen_mono))

        depth_valid = float(getattr(obs, "depth_valid", 1.0) or 0.0)
        quality = float(getattr(obs, "quality", 1.0) or 0.0)
        is_kf = bool(getattr(obs, "is_keyframe", False))
        if is_kf:
            w = float(np.clip(0.9 + 0.09 * depth_valid * quality, 0.9, 0.99))
        else:
            w = float(np.clip(0.01 + 0.09 * depth_valid * quality, 0.01, 0.1))
        z_world = obs.p_world.astype(np.float32)
        xyz_new = (1.0 - w) * o.xyz_world + w * z_world
        R = self.meas_var_xyz_cm2
        o_cov = (1.0 - w) ** 2 * o.cov_world + (w ** 2) * R
        o_cov = o_cov + self.proc_var_xyz_cm2 * dt_s

        # --- embeddings (gallery, mean, view bin) ---
        e = obs.emb_vis.astype(np.float32)
        add_to_gallery = True
        if o.emb_gallery.shape[0] > 0:
            cos_max = float(np.max((o.emb_gallery.astype(np.float32) @ e).astype(np.float32)))
            add_to_gallery = cos_max < self.gallery_dupe_cos or o.emb_gallery.shape[0] < 1
        if add_to_gallery:
            if o.emb_gallery.shape[0] < self.max_gallery:
                o.emb_gallery = np.vstack([o.emb_gallery, e.astype(np.float16)])
            else:
                o.emb_gallery = np.vstack([o.emb_gallery[1:], e.astype(np.float16)])

        if o.hits < self.emb_mean_hits_threshold:
            emb_mean = _l2norm(o.emb_mean * o.hits + e)
        else:
            alpha = self.emb_mean_ewma_alpha
            emb_mean = _l2norm((1.0 - alpha) * o.emb_mean + alpha * e)

        b = _view_bin_id(getattr(obs, "view_dir_cam", None), self.az_bins, self.el_bins)
        if b is not None:
            prev = o.view_bins.get(b)
            o.view_bins[b] = e if prev is None else _l2norm(0.5 * prev + 0.5 * e)

        topk = getattr(obs, "label_topk", None)
        if topk:
            for lbl, sc in topk:
                s_old = o.label_scores.get(lbl, 0.0)
                beta = 0.5
                o.label_scores[lbl] = (1 - beta) * s_old + beta * float(sc)
                o.label_hits[lbl] = o.label_hits.get(lbl, 0) + 1
        if o.label_scores:
            o.label_primary = max(o.label_scores.items(), key=lambda kv: kv[1])[0]

        # --- image crop gallery (FIFO, max_image_crops) ---
        crop = getattr(obs, 'crop', None)
        crop_to_persist: Optional[bytes] = None
        if crop is not None:
            jpeg_quality = int(self.cfg.get("object", {}).get("crop_jpeg_quality", 75))
            jpeg_bytes = _compress_crop_jpeg(crop, quality=jpeg_quality)
            if jpeg_bytes:
                o.image_crops.append(jpeg_bytes)
                if len(o.image_crops) > self.max_image_crops:
                    o.image_crops = o.image_crops[-self.max_image_crops:]
                crop_to_persist = jpeg_bytes

        cos_sim = float(getattr(obs, "cos_sim", 0.9))
        dist_m = float(getattr(obs, "dist_m", 0.0))
        gate = float(self.cfg.get("assoc", {}).get("gate_dist_base_m", 0.20))
        cos_n = max(0.0, min(1.0, (cos_sim - 0.5) / 0.5))
        dist_n = 1.0 - min(1.0, dist_m / max(1e-6, gate))
        quality_n = quality
        gain = max(0.0, 0.6 * cos_n + 0.3 * dist_n + 0.1 * quality_n)
        prev_stab = float(o.stability)
        prev_hits = int(o.hits)
        stab = min(1.0, o.stability + self.stab_k * gain * (1.0 - o.stability))

        new_frame_id = getattr(obs, "frame_id", None)
        with self._lock:
            o.xyz_world = xyz_new.astype(np.float32)
            o.cov_world = o_cov.astype(np.float32)
            o.emb_mean = emb_mean
            o.hits += 1
            o.stability = stab
            o.last_seen_mono = now_m
            o.last_seen_wall_utc = now_w
            o.last_seen_px = getattr(obs, "centroid_px", None)
            if new_frame_id is not None:
                old_frame_id = o.last_update_frame_id
                if old_frame_id is not None and old_frame_id != new_frame_id:
                    old_set = self._frame_to_objects.get(old_frame_id)
                    if old_set is not None:
                        old_set.discard(oid)
                        if not old_set:
                            del self._frame_to_objects[old_frame_id]
                self._frame_to_objects.setdefault(new_frame_id, set()).add(oid)
                o.last_update_frame_id = new_frame_id
            if not o.confirmed:
                self._schedule_proto(oid, o)

        if self.index is not None and np.any(self.index.grid.cell(old_xyz) != self.index.grid.cell(o.xyz_world)):
            self.index.update(oid, old_xyz, o.xyz_world, wm_lookup=self.lookup_min)

        # 2026-05-31: persist gallery deltas to disk (outside the lock).
        # Crop writes happen every observation that has a crop. Embs
        # writes are gated by add_to_gallery (dedup-check), so they
        # fire rarely once an object has a few samples -- the steady-
        # state I/O cost is dominated by crops, not embs.
        if crop_to_persist is not None:
            self._gallery.write_crop(oid, crop_to_persist, self.max_image_crops)
        if add_to_gallery:
            self._gallery.write_embs(oid, o.emb_gallery)

        lbl = getattr(o, 'label_primary', None)
        logger.debug(
            f"[WM] match oid={oid} hits={prev_hits}->{prev_hits+1} "
            f"stab={prev_stab:.3f}->{stab:.3f} cos={cos_sim:.3f} dist_m={dist_m:.3f} "
            f"label={lbl if lbl is not None else '-'}"
        )


    # ---------- miss / decay (call for unmatched objects) ----------

    def decay_unmatched(self, dt_s: float) -> None:
        if dt_s <= 0:
            return
        decay = float(self.miss_decay ** max(1.0, dt_s * 30.0))
        with self._lock:
            for o in self._map.values():
                o.stability *= decay

    # ---------- promotion & readiness ----------

    def maybe_promote(self, oid: str) -> None:
        with self._lock:
            o = self._map.get(oid)
            if o is None or o.confirmed:
                return

            gate_hits = o.hits >= self.promote_hits
            gate_stab = o.stability >= self.stability_promote
            gate_bins = len(o.view_bins) >= self.require_view_bins

            top_lbl = max(o.label_scores, key=o.label_scores.get) if o.label_scores else None
            top_conf = (o.label_scores.get(top_lbl, 0.0) if top_lbl else 0.0)

            top_hits = o.label_hits.get(top_lbl, 0) if top_lbl else 0
            gate_label_score = (top_lbl is not None) and (top_conf >= self.promote_min_conf)
            gate_label_evid  = (top_lbl is not None) and (top_hits >= self.min_label_hits)
            gate_label = gate_label_score and gate_label_evid

            structural_pass = gate_hits and gate_stab and gate_bins
            all_pass = structural_pass and gate_label

            logger.info(
                f"[promote-gate] oid={oid[:8]} "
                f"hits={o.hits}/{self.promote_hits}({int(gate_hits)}) "
                f"stab={o.stability:.3f}/{self.stability_promote}({int(gate_stab)}) "
                f"bins={len(o.view_bins)}/{self.require_view_bins}({int(gate_bins)}) "
                f"label={top_lbl} conf={top_conf:.3f}({int(gate_label_score)}) "
                f"lhits={top_hits}/{self.min_label_hits}({int(gate_label_evid)}) "
                f"decision={int(all_pass)}"
            )

            if all_pass:
                o.confirmed = True
                logger.info(
                    f"[WM] promote oid={oid} label={top_lbl} "
                    f"conf={top_conf:.3f} hits={o.hits} stab={o.stability:.3f}"
                )
                heapq.heappush(self._ltm_heap, (_now_mono(), oid))

    def collect_ready_for_upsert(self, force_all: bool = False) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        m_now = _now_mono()
        wall_now = _now_wall_utc()

        def _schedule_next_due(o: ObjectState, now_m: float) -> None:
            last_m = float(o.last_upsert_mono or 0.0)
            next_regular = max(now_m, last_m + self.ltm_min_period_s)
            heapq.heappush(self._ltm_heap, (next_regular, o.id))

        with self._lock:
            if force_all:
                for o in self._map.values():
                    if not o.confirmed or o.emb_mean is None:
                        continue
                    label_topk = sorted(o.label_scores.items(), key=lambda kv: kv[1], reverse=True)[:5]
                    out.append({
                        "object_id": o.id,
                        "emb": o.emb_mean.astype(np.float32),
                        "xyz": o.xyz_world.astype(np.float32),
                        "label_primary": o.label_primary,
                        "label_user": o.label_user,
                        "display_label": o.label_user or o.label_primary,
                        "movability_class": o.movability_class,
                        "pose_state_at_observation": o.pose_state_at_observation,
                        "reference_image_path": o.reference_image_path,
                        "reference_emb": (
                            o.reference_emb.astype(np.float32).tolist()
                            if o.reference_emb is not None else None
                        ),
                        "label_confidence": (o.label_scores.get(o.label_primary, 0.0) if o.label_primary else 0.0),
                        "label_topk": [k for k, _ in label_topk],
                        "label_scores": [float(v) for _, v in label_topk],
                        "label_hits":   [int(o.label_hits.get(k, 0)) for k, _ in label_topk],
                        "stability": float(o.stability),
                        "last_seen_wall_utc": o.last_seen_wall_utc,
                        "created_at": o.created_wall_utc,
                        "created_mono": o.created_mono,
                    })
                    o.last_upsert_mono = m_now
                    o.last_upsert_emb = o.emb_mean.copy()
                    o.last_upsert_xyz = o.xyz_world.copy()
                    self._upsert_count_total += 1
                return out

            while self._ltm_heap and self._ltm_heap[0][0] <= m_now:
                _, oid = heapq.heappop(self._ltm_heap)
                o = self._map.get(oid)
                if o is None or not o.confirmed:
                    continue
                if len(o.view_bins) < max(self.ltm_min_view_bins, 1):
                    heapq.heappush(self._ltm_heap, (m_now + self.ltm_min_period_s, oid))
                    continue
                elapsed_m = m_now - float(o.last_upsert_mono or 0.0)
                if elapsed_m < self.ltm_min_period_s:
                    heapq.heappush(self._ltm_heap, (float(o.last_upsert_mono or 0.0) + self.ltm_min_period_s, oid))
                    continue
                changed = True
                if o.last_upsert_emb is not None:
                    cos_same = _cos(o.emb_mean, o.last_upsert_emb)
                    ref_xyz = o.last_upsert_xyz if o.last_upsert_xyz is not None else o.xyz_world
                    pos_delta = float(np.linalg.norm(o.xyz_world - ref_xyz))
                    changed = (cos_same <= self.reupsert_cos_max) or (pos_delta >= self.reupsert_pos_m) or (elapsed_m >= self.ltm_force_period_s)
                if not changed:
                    remaining_to_force = max(0.0, (float(o.last_upsert_mono or m_now) + self.ltm_force_period_s) - m_now)
                    delay = min(self.ltm_min_period_s, remaining_to_force)
                    heapq.heappush(self._ltm_heap, (m_now + delay, oid))
                    continue

                label_topk = sorted(o.label_scores.items(), key=lambda kv: kv[1], reverse=True)[:5]
                payload = {
                    "object_id": o.id,
                    "emb": o.emb_mean.astype(np.float32),
                    "xyz": o.xyz_world.astype(np.float32),
                    "label_primary": o.label_primary,
                    "label_user": o.label_user,
                    "display_label": o.label_user or o.label_primary,
                    "movability_class": o.movability_class,
                    "pose_state_at_observation": o.pose_state_at_observation,
                    "reference_image_path": o.reference_image_path,
                    "reference_emb": (
                        o.reference_emb.astype(np.float32).tolist()
                        if o.reference_emb is not None else None
                    ),
                    "label_confidence": (o.label_scores.get(o.label_primary, 0.0) if o.label_primary else 0.0),
                    "label_topk": [k for k, _ in label_topk],
                    "label_scores": [float(v) for _, v in label_topk],
                    "label_hits":   [int(o.label_hits.get(k, 0)) for k, _ in label_topk],
                    "stability": float(o.stability),
                    "last_seen_wall_utc": o.last_seen_wall_utc,
                    "created_at": o.created_wall_utc,
                    "created_mono": o.created_mono,
                    "updated_at": wall_now,
                }
                out.append(payload)
                o.last_upsert_wall_utc = wall_now
                o.last_upsert_mono = m_now
                o.last_upsert_emb = o.emb_mean.copy()
                o.last_upsert_xyz = o.xyz_world.copy()
                self._upsert_count_total += 1

                reason = "first_upsert" if o.last_upsert_emb is None else (
                    "force_period" if elapsed_m >= self.ltm_force_period_s else (
                        "emb_changed" if cos_same <= self.reupsert_cos_max else "pos_changed"
                    )
                )
                logger.debug(
                    f"[WM] upsert oid={o.id} label={o.label_primary if o.label_primary else '-'} "
                    f"views={len(o.view_bins)} stab={o.stability:.3f} reason={reason} total={self._upsert_count_total}"
                )

                _schedule_next_due(o, m_now)
        return out

    # ---------- expiry / pruning ----------

    def expire_timeouts(self) -> List[str]:
        now_m = _now_mono()
        removed: List[str] = []
        with self._lock:
            while self._proto_heap and self._proto_heap[0][0] <= now_m:
                _, oid = heapq.heappop(self._proto_heap)
                o = self._map.get(oid)
                if o is None or o.confirmed:
                    continue
                true_deadline = o.last_seen_mono + self.proto_ttl_s
                if true_deadline > now_m:
                    heapq.heappush(self._proto_heap, (true_deadline, oid))
                    continue
                if o.last_update_frame_id is not None:
                    fset = self._frame_to_objects.get(o.last_update_frame_id)
                    if fset is not None:
                        fset.discard(oid)
                        if not fset:
                            del self._frame_to_objects[o.last_update_frame_id]
                removed.append(oid)
                del self._map[oid]
        if self.index is not None:
            for oid in removed:
                self.index.remove(oid, None)
        # 2026-05-31: clean disk gallery for expired protos (outside the lock)
        for oid in removed:
            self._gallery.remove(oid)
        return removed

    # ---------- internal: proto scheduling ----------
    def _schedule_proto(self, oid: str, o: ObjectState) -> None:
        deadline = o.last_seen_mono + self.proto_ttl_s
        heapq.heappush(self._proto_heap, (deadline, oid))

    # ---------- demotion (bad-pose recovery) ----------

    def _demote_object(self, o: ObjectState) -> None:
        was_confirmed = o.confirmed
        o.confirmed = False
        o.hits = 0
        o.stability = 0.0
        self._schedule_proto(o.id, o)
        if was_confirmed:
            logger.info(
                f"[WM] demoted oid={o.id} label={o.label_primary or '-'} "
                f"back to proto (large pose correction)"
            )

    # ---------- pose corrections (loop closure) ----------

    def apply_pose_corrections(
        self,
        frame_corrections: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]],
    ) -> int:
        if not frame_corrections:
            return 0

        corrected_oids: set = set()
        demoted_oids: list = []
        corrected = 0
        thresh = self.pose_demote_thresh_m

        with self._lock:
            for frame_id, (_, delta_R, delta_t) in frame_corrections.items():
                linked_oids = self._frame_to_objects.get(frame_id, set())
                for oid in linked_oids:
                    o = self._map.get(oid)
                    if o is None:
                        continue
                    old_xyz = o.xyz_world.copy()
                    new_xyz = (delta_R @ old_xyz + delta_t).astype(np.float32)
                    shift_m = float(np.linalg.norm(new_xyz - old_xyz))
                    o.xyz_world = new_xyz
                    corrected += 1
                    corrected_oids.add(oid)

                    if shift_m >= thresh:
                        self._demote_object(o)
                        demoted_oids.append(oid)

                    if self.index is not None:
                        old_cell = self.index.grid.cell(old_xyz)
                        new_cell = self.index.grid.cell(new_xyz)
                        if old_cell != new_cell:
                            self.index.update(oid, old_xyz, new_xyz, wm_lookup=self.lookup_min)

            uncorrected = [o for o in self._map.values() if o.id not in corrected_oids]
            if uncorrected:
                cam_positions = np.array(
                    [v[0] for v in frame_corrections.values()], dtype=np.float32
                )
                deltas_list = list(frame_corrections.values())
                for o in uncorrected:
                    old_xyz = o.xyz_world.copy()
                    diffs = cam_positions - old_xyz[None, :]
                    dists = np.linalg.norm(diffs, axis=1)
                    nearest_idx = int(np.argmin(dists))
                    _, delta_R, delta_t = deltas_list[nearest_idx]
                    new_xyz = (delta_R @ old_xyz + delta_t).astype(np.float32)
                    shift_m = float(np.linalg.norm(new_xyz - old_xyz))
                    o.xyz_world = new_xyz
                    corrected += 1

                    if shift_m >= thresh:
                        self._demote_object(o)
                        demoted_oids.append(o.id)

                    if self.index is not None:
                        old_cell = self.index.grid.cell(old_xyz)
                        new_cell = self.index.grid.cell(new_xyz)
                        if old_cell != new_cell:
                            self.index.update(o.id, old_xyz, new_xyz, wm_lookup=self.lookup_min)

        if corrected > 0:
            direct = len(corrected_oids)
            fallback = corrected - direct
            logger.info(
                f"[WM] Applied pose corrections to {corrected} objects "
                f"({direct} direct, {fallback} fallback) "
                f"from {len(frame_corrections)} frame deltas"
                f"{f', demoted {len(demoted_oids)} back to proto' if demoted_oids else ''}"
            )
        return corrected

    # ---------- utilities ----------

    def update_robot_pose(self, t_wc: np.ndarray, q_wc_xyzw: np.ndarray, timestamp: float) -> None:
        self._latest_pose = {
            "xyz": t_wc.tolist() if hasattr(t_wc, 'tolist') else list(t_wc),
            "quaternion_xyzw": q_wc_xyzw.tolist() if hasattr(q_wc_xyzw, 'tolist') else list(q_wc_xyzw),
            "timestamp": float(timestamp),
        }

    def get_robot_pose(self) -> Optional[Dict[str, Any]]:
        return self._latest_pose

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            n = len(self._map)
            c = sum(1 for o in self._map.values() if o.confirmed)
            avg_hits = (sum(o.hits for o in self._map.values()) / n) if n else 0.0
            # 2026-05-31: gallery telemetry
            on_disk_oids = len(self._gallery.list_oids()) if self._gallery.enabled else 0
            return {
                "objects": n,
                "confirmed": c,
                "avg_hits": avg_hits,
                "upserts_total": int(self._upsert_count_total),
                "robot_pose": self._latest_pose,
                "gallery_enabled": self._gallery.enabled,
                "gallery_on_disk_oids": on_disk_oids,
                "gallery_root": self._gallery.root if self._gallery.enabled else None,
            }

    def clear(self) -> Dict[str, int]:
        """Clear all objects from working memory (and their disk galleries)."""
        with self._lock:
            obj_count = len(self._map)
            confirmed_count = sum(1 for o in self._map.values() if o.confirmed)
            proto_count = obj_count - confirmed_count

            self._map.clear()
            self._proto_heap.clear()
            self._ltm_heap.clear()
            self._frame_to_objects.clear()
            self._upsert_count_total = 0

            if self.index is not None:
                self.index.clear()

        # 2026-05-31: clear disk gallery for all objects (outside the lock)
        self._gallery.clear_all()

        logger.info(f"[WM] Cleared {obj_count} objects ({confirmed_count} confirmed, {proto_count} proto)")

        return {
            "objects_cleared": obj_count,
            "confirmed_cleared": confirmed_count,
            "proto_cleared": proto_count,
        }

    # ---------- rehydration ----------

    def rehydrate_from_faiss(self, faiss_client: Any) -> Dict[str, int]:
        """Inject persisted objects from a FaissClient into WM as confirmed.

        2026-05-31: ALSO loads the on-disk persistent gallery for each
        rehydrated OID, restoring image_crops and emb_gallery. This closes
        the cross-restart matching gap that caused new OIDs to spawn for
        re-observed physical objects (see handoff_2026-05-30-addendum-part-2.md).
        """
        counts = {
            "loaded": 0,
            "skipped_no_emb": 0,
            "skipped_bad_xyz": 0,
            "skipped_dim_mismatch": 0,
            "skipped_dup": 0,
            "gallery_restored_oids": 0,
            "gallery_restored_crops": 0,
            "gallery_restored_embs": 0,
        }

        embeddings = getattr(faiss_client, "_embeddings", None) or {}
        metadata = getattr(faiss_client, "_metadata", None) or {}
        if not metadata:
            logger.info("[WM] rehydrate: FAISS has no persisted objects (cold start)")
            return counts

        expected_dim = getattr(faiss_client, "dim", None)
        if expected_dim is None:
            for v in embeddings.values():
                expected_dim = int(np.asarray(v).shape[-1])
                break
        if expected_dim is None:
            logger.warning(
                "[WM] rehydrate: cannot determine embedding dim "
                "(no faiss_client.dim, no embeddings); aborting"
            )
            return counts
        expected_dim = int(expected_dim)

        now_m = _now_mono()
        now_w = _now_wall_utc()
        cov_init = np.array([0.04, 0.04, 0.08], dtype=np.float32)

        new_objects: List[ObjectState] = []

        for oid, meta in metadata.items():
            oid = str(oid)

            if oid in self._map:
                counts["skipped_dup"] += 1
                continue

            emb = embeddings.get(oid)
            if emb is None:
                counts["skipped_no_emb"] += 1
                continue
            emb = np.asarray(emb, dtype=np.float32).reshape(-1)
            if emb.shape[0] != expected_dim:
                logger.warning(
                    f"[WM] rehydrate: skip oid={oid[:8]} dim {emb.shape[0]} "
                    f"!= expected {expected_dim}"
                )
                counts["skipped_dim_mismatch"] += 1
                continue

            xyz_raw = meta.get("xyz")
            try:
                xyz = np.asarray(xyz_raw, dtype=np.float32).reshape(-1)
                if xyz.shape[0] != 3:
                    raise ValueError(f"xyz shape {xyz.shape}")
            except Exception as e:
                logger.warning(f"[WM] rehydrate: skip oid={oid[:8]} bad xyz: {e}")
                counts["skipped_bad_xyz"] += 1
                continue

            label_topk = list(meta.get("label_topk", []) or [])
            label_scores_list = list(meta.get("label_scores", []) or [])
            label_hits_list = list(meta.get("label_hits", []) or [])
            label_scores: Dict[str, float] = {}
            label_hits: Dict[str, int] = {}
            for i, name in enumerate(label_topk):
                if i < len(label_scores_list):
                    label_scores[str(name)] = float(label_scores_list[i])
                if i < len(label_hits_list):
                    label_hits[str(name)] = int(label_hits_list[i])

            hits_default = int(max(self.promote_hits, 1))

            o = ObjectState(
                id=oid,
                xyz_world=xyz.astype(np.float32),
                cov_world=cov_init.copy(),
                emb_mean=emb.astype(np.float32),
                emb_gallery=np.zeros((0, expected_dim), dtype=np.float16),
                view_bins={0: emb.astype(np.float32)},
                label_scores=label_scores,
                label_hits=label_hits,
                label_primary=meta.get("label_primary"),
                stability=float(meta.get("stability", 0.5)),
                hits=hits_default,
                confirmed=True,
                created_mono=now_m,
                created_wall_utc=float(meta.get("created_at", now_w)),
                last_seen_mono=now_m,
                last_seen_wall_utc=float(meta.get("last_seen_wall_utc", now_w)),
                last_seen_px=None,
                last_upsert_wall_utc=now_w,
                last_upsert_mono=now_m,
                last_upsert_emb=emb.astype(np.float32).copy(),
                last_upsert_xyz=xyz.astype(np.float32).copy(),
                image_crops=[],
                last_update_frame_id=None,
                _dim=expected_dim,
                label_user=meta.get("label_user"),
                movability_class=meta.get("movability_class"),
                pose_state_at_observation=str(
                    meta.get("pose_state_at_observation", "on_floor")
                ),
            )

            # 2026-05-31: load persisted gallery from disk.  This is the
            # actual fix for cross-restart matching -- rehydrated objects
            # get their full appearance history back instead of being
            # reduced to an emb_mean-only matcher.
            disk_crops, disk_embs = self._gallery.load(oid)
            gallery_restored_here = False
            if disk_crops:
                o.image_crops = disk_crops
                counts["gallery_restored_crops"] += len(disk_crops)
                gallery_restored_here = True
            if disk_embs is not None and disk_embs.ndim == 2 and disk_embs.shape[0] > 0:
                if disk_embs.shape[-1] == expected_dim:
                    o.emb_gallery = disk_embs.astype(np.float16, copy=False)
                    counts["gallery_restored_embs"] += int(disk_embs.shape[0])
                    gallery_restored_here = True
                else:
                    logger.warning(
                        f"[WM] rehydrate: disk gallery dim mismatch for "
                        f"oid={oid[:8]}: got {disk_embs.shape[-1]} "
                        f"expected {expected_dim}; ignoring disk gallery"
                    )
            if gallery_restored_here:
                counts["gallery_restored_oids"] += 1

            # 2026-05-29: reference snapshot (named-moment ground truth).
            # The disk gallery above is the stronger signal; reference_emb
            # is only used as a single-entry fallback when the disk gallery
            # is empty (e.g. object was named but never re-observed under
            # the new persistent-gallery code).
            ref_path = meta.get("reference_image_path")
            o.reference_image_path = ref_path
            ref_emb_raw = meta.get("reference_emb")
            if ref_emb_raw is not None:
                try:
                    ref_emb_arr = np.asarray(ref_emb_raw, dtype=np.float32).reshape(-1)
                    if ref_emb_arr.shape[0] == expected_dim:
                        o.reference_emb = ref_emb_arr
                        if o.emb_gallery.shape[0] == 0:
                            o.emb_gallery = ref_emb_arr.astype(np.float16).reshape(1, -1)
                    else:
                        logger.warning(
                            f"[WM] rehydrate: reference_emb dim mismatch for "
                            f"oid={oid[:8]}: got {ref_emb_arr.shape[0]} "
                            f"expected {expected_dim}; skipping"
                        )
                except Exception as _e:
                    logger.warning(
                        f"[WM] rehydrate: bad reference_emb for {oid[:8]}: {_e}"
                    )
            new_objects.append(o)

        with self._lock:
            for o in new_objects:
                self._map[o.id] = o
                heapq.heappush(self._ltm_heap, (_now_mono(), o.id))
                counts["loaded"] += 1

        if self.index is not None:
            for o in new_objects:
                self.index.insert(o.id, o.xyz_world, wm_lookup=self.lookup_min)

        logger.info(
            f"[WM] rehydrate: loaded {counts['loaded']} objects from FAISS "
            f"(skipped no_emb={counts['skipped_no_emb']} "
            f"bad_xyz={counts['skipped_bad_xyz']} "
            f"dim={counts['skipped_dim_mismatch']} "
            f"dup={counts['skipped_dup']}) | "
            f"gallery: {counts['gallery_restored_oids']} OIDs restored "
            f"({counts['gallery_restored_crops']} crops, "
            f"{counts['gallery_restored_embs']} embs from disk)"
        )
        return counts

    # ---------- reference snapshot (named-moment ground truth) ----------

    def set_object_reference(
        self,
        oid: str,
        *,
        image_path: Optional[str],
        embedding: Optional[np.ndarray],
    ) -> Optional["ObjectState"]:
        """Thread-safe update of reference snapshot fields on an ObjectState."""
        with self._lock:
            o = self._map.get(oid)
            if o is None:
                return None
            o.reference_image_path = (
                str(image_path) if image_path is not None else None
            )
            if embedding is not None:
                arr = np.asarray(embedding, dtype=np.float32).reshape(-1)
                if o._dim and arr.shape[0] != o._dim:
                    raise ValueError(
                        f"reference embedding dim {arr.shape[0]} != "
                        f"object dim {o._dim}"
                    )
                n = float(np.linalg.norm(arr) + 1e-12)
                o.reference_emb = (arr / n).astype(np.float32)
            else:
                o.reference_emb = None
            if o.confirmed:
                heapq.heappush(self._ltm_heap, (_now_mono(), oid))
            return o

    # 2026-06-02: synchronous flush of PATCH-style mutations.  Bypasses
    # the collect_ready_for_upsert change-detection gate so label_user
    # and movability_class changes can be persisted to FAISS
    # immediately, matching the architectural pattern used by
    # /objects/merge (vectors.upsert_batch via build_faiss_record_for_merge).
    # See handoff_2026-06-01-evening-addendum.md, Bug 1.
    def force_flush_now(self, oid: str) -> Optional[Dict[str, Any]]:
        """Build a FAISS upsert payload for `oid` and update last_upsert_*.

        Returns the payload (caller passes it to vectors.upsert_batch),
        or None if the OID is unknown / unconfirmed / has no emb_mean.
        Payload shape matches collect_ready_for_upsert's regular loop
        exactly so the FAISS sidecar stays consistent.
        """
        m_now = _now_mono()
        wall_now = _now_wall_utc()
        with self._lock:
            o = self._map.get(oid)
            if o is None or not o.confirmed or o.emb_mean is None:
                return None
            label_topk = sorted(
                o.label_scores.items(), key=lambda kv: kv[1], reverse=True
            )[:5]
            payload = {
                "object_id": o.id,
                "emb": o.emb_mean.astype(np.float32),
                "xyz": o.xyz_world.astype(np.float32),
                "label_primary": o.label_primary,
                "label_user": o.label_user,
                "display_label": o.label_user or o.label_primary,
                "movability_class": o.movability_class,
                "pose_state_at_observation": o.pose_state_at_observation,
                "reference_image_path": o.reference_image_path,
                "reference_emb": (
                    o.reference_emb.astype(np.float32).tolist()
                    if o.reference_emb is not None else None
                ),
                "label_confidence": (
                    o.label_scores.get(o.label_primary, 0.0)
                    if o.label_primary else 0.0
                ),
                "label_topk": [k for k, _ in label_topk],
                "label_scores": [float(v) for _, v in label_topk],
                "label_hits":   [int(o.label_hits.get(k, 0)) for k, _ in label_topk],
                "stability": float(o.stability),
                "last_seen_wall_utc": o.last_seen_wall_utc,
                "created_at": o.created_wall_utc,
                "created_mono": o.created_mono,
                "updated_at": wall_now,
            }
            o.last_upsert_wall_utc = wall_now
            o.last_upsert_mono = m_now
            o.last_upsert_emb = o.emb_mean.copy()
            o.last_upsert_xyz = o.xyz_world.copy()
            self._upsert_count_total += 1
            return payload

    # ---------- removal ----------

    def remove_object(self, oid: str) -> bool:
        """Remove an object from WM entirely (including disk gallery)."""
        last_xyz = None
        with self._lock:
            o = self._map.get(oid)
            if o is None:
                return False
            fid = getattr(o, "last_update_frame_id", None)
            if fid is not None:
                fset = self._frame_to_objects.get(fid)
                if fset is not None:
                    fset.discard(oid)
                    if not fset:
                        del self._frame_to_objects[fid]
            if getattr(o, "xyz_world", None) is not None:
                last_xyz = o.xyz_world.copy()
            del self._map[oid]
        if self.index is not None:
            try:
                self.index.remove(oid, last_xyz)
            except Exception:
                logger.exception("remove_object: index.remove failed for %s", oid)
        # 2026-05-31: clean disk gallery
        self._gallery.remove(oid)
        logger.info("[WM] removed oid=%s", oid)
        return True
