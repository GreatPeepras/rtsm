from __future__ import annotations

import asyncio
import time
import threading
from datetime import datetime, timezone  # 2026-05-26 Gate 3: ISO last_seen_at
from typing import Any, Callable, Optional, Dict, List
from dataclasses import dataclass

import base64
import binascii

import cv2
from pydantic import BaseModel, Field, field_validator  # PATCH 20260507: ingest stub
import numpy as np
from fastapi import FastAPI, Response, HTTPException, WebSocket, WebSocketDisconnect, Body
from prometheus_client import Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from pydantic import BaseModel, Field

@dataclass
class ResetComponents:
    """Components that can be reset without restarting RTSM."""
    sweep_cache: Any = None
    frame_window: Any = None
    vis_server: Any = None  # VisualizationServer with registry


# PATCH 20260507: /ingest/keyframe wire-contract models (Gate 2.d)
class PoseQuat(BaseModel):
    tx: float
    ty: float
    tz: float
    qx: float
    qy: float
    qz: float
    qw: float


class KeyframePayload(BaseModel):
    rgb_jpeg: str
    depth_png: str
    K: List[float] = Field(..., min_length=9, max_length=9)
    pose: PoseQuat
    timestamp_ros: float
    frame_id: Optional[str] = "camera_color_optical_frame"
    sequence: Optional[int] = None

    @field_validator("K")
    @classmethod
    def _k_shape(cls, v: List[float]) -> List[float]:
        if len(v) != 9:
            raise ValueError("K must be 9 floats (row-major 3x3)")
        return v


# ---- Module-scoped Pydantic models (must be at module scope so
# `from __future__ import annotations` forward-refs resolve via
# get_type_hints(); closure-scoped classes break FastAPI/Pydantic v2). ----
class ObjectPatch(BaseModel):
    """Body schema for PATCH /objects/{oid}.

    All fields optional. Field omission means "leave unchanged".
    Field set to null means "clear" (revert to default).
    Empty string for label_user is rejected (use null to clear).
    """
    label_user: Optional[str] = None
    movability_class: Optional[str] = None

    model_config = {"extra": "forbid"}

class PoseStateRequest(BaseModel):
    #Body schema for POST /pose_state.
    state: str = Field(
        ...,
        description=(
            "One of: 'on_floor', 'lifted', 'unknown', 'confirmed_elevated'. "
            "Invalid values are clamped to 'unknown' (safe default)."
        ),
    )


class MergeObjectsRequest(BaseModel):
    """Body schema for POST /objects/merge.

    winner_oid and loser_oid both required. winner_oid keeps its id, xyz,
    and canonical position; loser_oid is dissolved into the winner.
    """
    winner_oid: str = Field(..., min_length=1)
    loser_oid: str = Field(..., min_length=1)
    dry_run: bool = False

    model_config = {"extra": "forbid"}


class SuggestMergesRequest(BaseModel):
    """Body schema for POST /objects/suggest_merges.

    Conservative gate (defaults cos>=0.95, dist<=1.0m) surfaces high-
    confidence Mode B duplicate candidates. Caller reviews snapshots
    via /objects/{oid}/snapshots and POSTs /objects/merge for each pair
    they confirm.
    """
    cos_threshold: float = Field(0.95, ge=0.0, le=1.0)
    dist_threshold_m: float = Field(1.0, gt=0.0)
    require_same_label: bool = False
    limit: int = Field(50, ge=1, le=500)
    include_unconfirmed: bool = False

    model_config = {"extra": "forbid"}


# 2026-05-29: reference-snapshot endpoint schemas.
class ReferenceImagePayload(BaseModel):
    """Body schema for POST /objects/{oid}/reference.

    Single base64-encoded JPEG. RTSM decodes, CLIP-embeds, writes the file
    to disk, and updates the object's reference fields. INGEST mode only
    (CLIP loaded + WM writable).
    """
    jpeg_b64: str = Field(..., description="Base64-encoded JPEG bytes.")

    model_config = {"extra": "forbid"}


class ReferenceBulkItem(BaseModel):
    """One entry in a bulk reference upload."""
    oid: str
    jpeg_b64: str


class ReferenceBulkPayload(BaseModel):
    """Body schema for POST /objects/reference_bulk.

    Albert's boot-time backfill: walk local memory.json, push every
    linked snapshot in one request. Per-item failures are reported in
    the response without aborting the batch.
    """
    items: List[ReferenceBulkItem] = Field(..., min_length=1, max_length=200)

    model_config = {"extra": "forbid"}




def create_app(
    *,
    working_memory: Any,
    clip_adapter: Optional[Any] = None,
    vectors: Optional[Any] = None,
    extra_stats_provider: Optional[Callable[[], Dict[str, Any]]] = None,
    registry: Optional[CollectorRegistry] = None,
    reset_components: Optional[ResetComponents] = None,
    seg_analytics: Optional[Any] = None,
    latency_analytics: Optional[Any] = None,
    mcp_enabled: bool = False,
    vis_server: Optional[Any] = None,
    vis_broadcaster: Optional[Any] = None,
    vis_registry: Optional[Any] = None,
    static_dir: Optional[str] = None,
    ingest_queue: Optional[Any] = None,
) -> FastAPI:
    """
    Build a FastAPI app exposing:
      - /healthz: liveness
      - /readyz: readiness (trivial true for now)
      - /stats: JSON snapshot (WorkingMemory.stats() + optional extra stats)
      - /metrics: Prometheus metrics (mounted ASGI app)
      - /ws: WebSocket for visualization (when vis_server is provided)
      - /: Static frontend (when static_dir is provided)

    When vis_server is provided, its periodic tasks (objects push, analytics)
    run on this server's event loop — no separate viz server port needed.
    """
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Start visualization periodic tasks on THIS event loop
        if vis_server is not None:
            await vis_server.start_tasks()
        yield
        if vis_server is not None:
            await vis_server.stop_tasks()

    app = FastAPI(
        title="RTSM API — Real-Time Spatio-Semantic Memory",
        version="1.0.0",
        lifespan=lifespan,
    )

    # ---------------- Prometheus metrics ----------------
    # Create a few dynamic gauges that read values from WorkingMemory on scrape.
    # Default to the global REGISTRY when a custom registry isn't provided.
    reg = registry or REGISTRY

    # PATCH 20260507: /ingest/keyframe counters (stub state)
    _ingest_counters: Dict[str, int] = {
        "frames_received": 0,
        "bytes_received": 0,
        "last_sequence": -1,
        "queue_full_drops": 0,
        "frames_queued": 0,
    }
    _ingest_queue = ingest_queue  # closure ref; None in --serve mode
    objects_gauge = Gauge(
        "rtsm_working_objects",
        "Total objects in WorkingMemory",
        registry=reg,
    )
    confirmed_gauge = Gauge(
        "rtsm_confirmed_objects",
        "Confirmed objects in WorkingMemory",
        registry=reg,
    )
    upserts_total_gauge = Gauge(
        "rtsm_upserts_total",
        "Total upserts emitted by WorkingMemory",
        registry=reg,
    )

    def _wm_stat_val(key: str) -> Callable[[], float]:
        def _f() -> float:
            try:
                st = working_memory.stats()
                v = float(st.get(key, 0.0))
                return v
            except Exception:
                return 0.0
        return _f

    objects_gauge.set_function(_wm_stat_val("objects"))
    confirmed_gauge.set_function(_wm_stat_val("confirmed"))
    upserts_total_gauge.set_function(_wm_stat_val("upserts_total"))

    # Expose metrics at /metrics directly (avoid nested /metrics/metrics when mounting)
    @app.get("/metrics")
    def metrics() -> Response:
        data = generate_latest(registry=reg)
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    # ---------------- Routes ----------------
    @app.get("/healthz")
    def healthz() -> Dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz() -> Dict[str, str]:
        # TODO: add checks for external deps (Milvus, FAISS, ZMQ subscriber)
        return {"status": "ready"}

    @app.get("/stats")
    def stats() -> Dict[str, Any]:
        base = {}
        try:
            base = dict(working_memory.stats())
        except Exception:
            base = {}
        if extra_stats_provider is not None:
            try:
                extra = extra_stats_provider() or {}
                base.update(extra)
            except Exception:
                pass
        return base

    @app.post("/pose_state")
    def set_pose_state(req: PoseStateRequest) -> Dict[str, Any]:
        
        #Update RTSM's pose-trust state. Called by Albert's pose_state_bridge
        #whenever /albert/pose_state changes.

        #States:
          #on_floor          -- AMCL pose is trusted; writes proceed normally
          #lifted            -- robot mid-air; writes BLOCKED
          #unknown           -- robot at rest but surface not yet known; BLOCKED
          #confirmed_elevated -- robot on a desk; writes proceed, tagged "elevated"
        
        try:
            result = working_memory.set_pose_state(req.state)
            return result
        except AttributeError:
            # FrozenWorkingMemory in serve mode doesn't have this method
            # (or has a no-op stub). Return a benign response so the bridge
            # doesn't log it as a failure.
            return {
                "old_state": "unsupported",
                "new_state": "unsupported",
                "note": "serve mode; pose_state not applicable",
            }

    @app.get("/pose_state")
    def get_pose_state() -> Dict[str, Any]:
        #Current pose-state, for diagnostics.
        try:
            state = working_memory.get_pose_state()
        except AttributeError:
            state = "unsupported"
        return {"state": state}

    # ---- Object debug endpoints ----
    # ------------------------------------------------------------------
    # 2026-05-26 Gate 3 helpers: shared response-enrichment utilities used
    # by /search/semantic and /search/spatial so the Albert bridge has
    # enough context to speak a useful answer ("X at [a,b,c], Nm from you,
    # last seen <ISO>"). All helpers degrade gracefully — they return None
    # rather than raising when a field is missing, so legacy WM objects
    # and rehydrated faiss_meta entries both work.
    # ------------------------------------------------------------------
    def _display_label(o: Any) -> Optional[str]:
        """Resolve the human-speakable label for an ObjectState.

        Mirrors the gated label_primary selection in _obj_summary so the
        search endpoints surface the same label /objects would. Falls
        back through:  label_user > gated argmax(label_scores) > label_primary.
        """
        try:
            label_user = getattr(o, "label_user", None)
            if label_user:
                return label_user
            _scores = getattr(o, "label_scores", {}) or {}
            _hits = getattr(o, "label_hits", {}) or {}
            _min_hits = int(getattr(working_memory, "min_label_hits", 5))
            _gated = {k: v for k, v in _scores.items()
                      if int(_hits.get(k, 0)) >= _min_hits}
            if _gated:
                return max(_gated, key=_gated.get)
            return getattr(o, "label_primary", None)
        except Exception:
            return None

    def _robot_xyz(robot_pose: Any) -> Optional[np.ndarray]:
        """Defensively extract a 3-vec from working_memory.get_robot_pose().

        That accessor's return shape is not pinned in this file, so try
        the common shapes (dict with 'xyz' or 'position'; len>=3 sequence)
        and return None on anything we can't make sense of.
        """
        if robot_pose is None:
            return None
        try:
            if isinstance(robot_pose, dict):
                xyz = robot_pose.get("xyz") or robot_pose.get("position")
                if xyz is None:
                    return None
                arr = np.asarray(xyz, dtype=np.float32)
            elif hasattr(robot_pose, "__len__") and len(robot_pose) >= 3:
                arr = np.asarray(robot_pose[:3], dtype=np.float32)
            else:
                return None
            return arr if arr.shape == (3,) else None
        except Exception:
            return None

    def _distance_from_robot(obj_xyz: Any, robot_xyz: Optional[np.ndarray]) -> Optional[float]:
        """Euclidean distance from object to robot in world frame.

        Returns None if either xyz is unusable, never raises.
        """
        if obj_xyz is None or robot_xyz is None:
            return None
        try:
            obj_arr = np.asarray(obj_xyz, dtype=np.float32)
            if obj_arr.shape != (3,):
                return None
            return round(float(np.linalg.norm(obj_arr - robot_xyz)), 3)
        except Exception:
            return None

    def _iso_from_wall_utc(t: Any) -> Optional[str]:
        """Convert a float UTC epoch to ISO-8601 with timezone, or None.

        last_seen_wall_utc is stored as a float on ObjectState; the LLM
        wants something speakable. Treat 0/None/negative as "never seen".
        """
        try:
            ts = float(t) if t is not None else 0.0
            if ts <= 0:
                return None
            return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        except Exception:
            return None

    def _obj_summary(o: Any) -> Dict[str, Any]:
        try:
            # 2026-05-11: surface user override + display label + movability + age
            label_user = getattr(o, "label_user", None)
            # PATCH 20260513: gate label_primary on hits>=min_label_hits to
            # prevent post-promotion EWMA drift from surfacing under-evidenced
            # labels in the summary. Falls back to stored label_primary if
            # the gated subset is empty (defensive; shouldn't happen for
            # confirmed objects).
            _scores = getattr(o, "label_scores", {}) or {}
            _hits   = getattr(o, "label_hits",   {}) or {}
            _min_hits = int(getattr(working_memory, "min_label_hits", 5))
            _gated = {k: v for k, v in _scores.items()
                      if int(_hits.get(k, 0)) >= _min_hits}
            if _gated:
                label_primary = max(_gated, key=_gated.get)
            else:
                label_primary = getattr(o, "label_primary", None)
            last_seen = float(getattr(o, "last_seen_mono", 0.0))
            now_mono = time.monotonic()
            return {
                "id": getattr(o, "id", None),
                "xyz_world": getattr(o, "xyz_world", None).tolist() if getattr(o, "xyz_world", None) is not None else None,
                "created_wall_utc": float(getattr(o, "created_wall_utc", 0.0)),
                "created_mono": float(getattr(o, "created_mono", 0.0)),
                "stability": float(getattr(o, "stability", 0.0)),
                "hits": int(getattr(o, "hits", 0)),
                "confirmed": bool(getattr(o, "confirmed", False)),
                "label_primary": label_primary,
                "label_user": label_user,
                "display_label": label_user or label_primary,
                "label_top_hits": int((getattr(o, "label_hits", {}) or {}).get(label_primary, 0)) if label_primary else 0,
                "movability_class": getattr(o, "movability_class", None),
                "pose_state_at_observation": getattr(o, "pose_state_at_observation", "on_floor"),
                "view_bins": len(getattr(o, "view_bins", {}) or {}),
                "last_seen_mono": last_seen,
                "last_seen_age_s": (max(0.0, now_mono - last_seen)
                                    if last_seen > 0 else None),
                "pose_state_at_observation": getattr(o, "pose_state_at_observation", "on_floor"),
            }
        except Exception:
            return {"id": getattr(o, "id", None)}

    def _obj_detail(o: Any, *, include_vectors: bool = False) -> Dict[str, Any]:
        d = _obj_summary(o)
        try:
            d.update({
                "cov_world": getattr(o, "cov_world", None).tolist() if getattr(o, "cov_world", None) is not None else None,
                "label_scores": dict(getattr(o, "label_scores", {}) or {}),
                "label_hits":   dict(getattr(o, "label_hits",   {}) or {}),
                "last_seen_wall_utc": float(getattr(o, "last_seen_wall_utc", 0.0)),
                "last_seen_px": list(getattr(o, "last_seen_px", [])) if getattr(o, "last_seen_px", None) is not None else None,
                "upsert": {
                    "last_upsert_wall_utc": float(getattr(o, "last_upsert_wall_utc", 0.0)),
                    "last_upsert_mono": float(getattr(o, "last_upsert_mono", 0.0)),
                },
                "view_bins_keys": list((getattr(o, "view_bins", {}) or {}).keys()),
            })
            if include_vectors:
                emb_mean = getattr(o, "emb_mean", None)
                d["emb_mean"] = emb_mean.tolist() if emb_mean is not None else None
                emb_gallery = getattr(o, "emb_gallery", None)
                if emb_gallery is not None:
                    try:
                        d["emb_gallery_shape"] = list(emb_gallery.shape)
                        # Avoid dumping entire gallery by default; include if requested
                        d["emb_gallery"] = emb_gallery.astype(float).tolist()
                    except Exception:
                        d["emb_gallery"] = None
        except Exception:
            pass
        return d

    @app.get("/objects")
    def list_objects(
        include_vectors: bool = False,
        include_snapshot: bool = False,
        confirmed_only: bool = False,
        pose_state: str = "on_floor",   # NEW: filter; "on_floor" | "elevated" | "any"
        offset: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """List objects in working memory with pagination.

        Args:
            include_vectors: Include CLIP embedding vectors in response
            include_snapshot: Include latest observation crop (base64 JPEG)
                for multimodal agent verification
            confirmed_only: If true, only return confirmed objects
            offset: Skip first N objects (for pagination)
            limit: Maximum objects to return (default 100, max 500)
        """
        limit = min(max(1, limit), 500)
        offset = max(0, offset)

        try:
            objs: List[Any] = working_memory.iter_objects()
        except Exception:
            objs = []

        if confirmed_only:
            objs = [o for o in objs if getattr(o, 'confirmed', False)]

        # 2026-05-22 pose-state filter: navigation queries get on_floor
        # by default. Pass ?pose_state=any to see everything.
        if pose_state != "any":
            objs = [
                o for o in objs
                if getattr(o, "pose_state_at_observation", "on_floor") == pose_state
            ]

        if pose_state != "any":
            wanted = pose_state  # "on_floor" or "elevated"
            objs = [
                o for o in objs
                if getattr(o, "pose_state_at_observation", "on_floor") == wanted
            ]

        total = len(objs)
        page = objs[offset : offset + limit]

        result_list = []
        for o in page:
            entry = _obj_detail(o, include_vectors=include_vectors) if include_vectors else _obj_summary(o)
            if include_snapshot:
                crops = getattr(o, 'image_crops', None) or []
                if crops:
                    entry["snapshot_b64"] = base64.b64encode(crops[-1]).decode('ascii')
                    entry["snapshot_count"] = len(crops)
            result_list.append(entry)
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "count": len(result_list),
            "objects": result_list,
        }

    @app.get("/objects/by_label_user")
    def get_object_by_label_user(
        name: str,
        case_insensitive: bool = True,
    ) -> Dict[str, Any]:
        """Look up an object by its user-assigned name (label_user).

        Drives Albert's layered recall: local memory hits first, then this
        endpoint for current RTSM state (location, last_seen, reference).
        Returns 404 if no object carries this label_user. If multiple
        objects share the name (rare; user normally pins one), returns the
        most recently observed one and surfaces a list of all matches.
        """
        q = name.strip()
        if not q:
            raise HTTPException(status_code=400, detail="name must be non-empty")

        matches: List[Any] = []
        try:
            for o in working_memory.iter_objects():
                lu = getattr(o, "label_user", None)
                if lu is None:
                    continue
                if case_insensitive:
                    if lu.lower() == q.lower():
                        matches.append(o)
                else:
                    if lu == q:
                        matches.append(o)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"WM iteration failed: {e}")

        if not matches:
            raise HTTPException(
                status_code=404,
                detail=f"No object with label_user={name!r}",
            )

        # Most-recent first by last_seen_wall_utc.
        matches.sort(
            key=lambda o: float(getattr(o, "last_seen_wall_utc", 0.0) or 0.0),
            reverse=True,
        )
        primary = matches[0]

        # 2026-05-29: defensive serialization. xyz_world may be a
        # Python list OR a numpy ndarray depending on how the object got
        # into WM (ingest path vs faiss-rehydrate). Convert both safely.
        def _xyz_to_list(xyz: Any) -> Optional[List[float]]:
            if xyz is None:
                return None
            if hasattr(xyz, "tolist"):
                try:
                    return [float(v) for v in xyz.tolist()]
                except Exception:
                    pass
            try:
                return [float(v) for v in xyz]
            except Exception:
                return None

        def _entry(o: Any) -> Dict[str, Any]:
            ref_path = getattr(o, "reference_image_path", None)
            return {
                "id": getattr(o, "id", None),
                "label_user": getattr(o, "label_user", None),
                "label_primary": getattr(o, "label_primary", None),
                "xyz_world": _xyz_to_list(getattr(o, "xyz_world", None)),
                "movability_class": getattr(o, "movability_class", None),
                "pose_state_at_observation": getattr(
                    o, "pose_state_at_observation", "on_floor"
                ),
                "confirmed": bool(getattr(o, "confirmed", False)),
                "last_seen_wall_utc": float(
                    getattr(o, "last_seen_wall_utc", 0.0) or 0.0
                ),
                "reference_image_path": ref_path,
                "has_reference_image": bool(ref_path),
            }

        # robot_pose may also surface non-serializable types; degrade to None
        # so the endpoint never 500s just because of pose-shape weirdness.
        try:
            robot_pose = working_memory.get_robot_pose()
        except Exception:
            robot_pose = None

        return {
            "name": name,
            "match_count": len(matches),
            "primary": _entry(primary),
            "all_matches": [_entry(o) for o in matches],
            "robot_pose": robot_pose,
        }

    # ---- Snapshot gallery endpoints ----

    @app.get("/objects/{oid}")
    def get_object(oid: str, include_vectors: bool = False) -> Dict[str, Any]:
        try:
            o = working_memory.get(oid)
        except Exception:
            o = None
        if o is None:
            return {"error": "not_found", "id": oid}
        return _obj_detail(o, include_vectors=include_vectors)

    # ---- 2026-05-11 PR: user override + lifecycle hooks ----

    @app.patch("/objects/{oid}")
    def patch_object(oid: str, patch: ObjectPatch = Body(...)) -> Dict[str, Any]:
        """Update user-controllable fields on a WM object.

        Distinguishes:
          - field omitted from body  -> leave unchanged
          - field set to null        -> clear (revert to default)
          - label_user empty string  -> 400 (use null to clear)
          - movability_class invalid -> 400

        Returns the updated object detail. Returns 405 on frozen WM
        (serve-mode), 404 on unknown oid.
        """
        # Frozen WM (serve-mode) is read-only.
        if not hasattr(working_memory, "update_user_fields"):
            raise HTTPException(
                status_code=405,
                detail="PATCH not supported on frozen working memory (serve-mode)",
            )

        provided = patch.model_fields_set
        kwargs: Dict[str, Any] = {}
        if "label_user" in provided:
            kwargs["label_user"] = patch.label_user
        if "movability_class" in provided:
            kwargs["movability_class"] = patch.movability_class

        if not kwargs:
            # Idempotent no-op: client sent {} or only unrelated fields.
            o = working_memory.get(oid)
            if o is None:
                raise HTTPException(status_code=404, detail=f"Object {oid} not found")
            return _obj_detail(o)

        try:
            o = working_memory.update_user_fields(oid, **kwargs)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if o is None:
            raise HTTPException(status_code=404, detail=f"Object {oid} not found")

        # 2026-05-29: force-flush PATCH'd label_user/movability to FAISS.
        # update_user_fields modifies WM only; without this push the change
        # waits for natural re-observation, and a restart in that window
        # loses the user's label. Re-asserting reference state via
        # set_object_reference triggers the same lock-protected heap push
        # that pinning a reference image already does.
        if (getattr(o, "confirmed", False)
                and hasattr(working_memory, "set_object_reference")):
            try:
                working_memory.set_object_reference(
                    oid,
                    image_path=getattr(o, "reference_image_path", None),
                    embedding=getattr(o, "reference_emb", None),
                )
            except Exception as e:
                logger.warning(
                    f"PATCH force-flush for {oid} failed: {e}"
                )

        return _obj_detail(o)

    @app.post("/objects/merge")
    def merge_objects_endpoint(
        req: MergeObjectsRequest = Body(...),
    ) -> Dict[str, Any]:
        """Consolidate two confirmed OIDs into one.

        Use cases:
          - Mode B duplicates: same physical object split across two OIDs
            because of CLIP label drift or position drift.
          - Manual cleanup during ground-truth annotation pass.

        Semantics:
          - winner_oid keeps its id, xyz_world, cov_world.
          - Galleries (emb_gallery + image_crops) are unioned with the
            same dedup + FIFO gates that update_object uses.
          - view_bins are unioned; collisions averaged.
          - label_scores: per-key hits-weighted average.
          - label_hits: per-key sum.
          - label_user / movability_class / reference_image_path:
            winner's if set, else loser's (human pins survive).
          - hits summed; stability = max; created_* = older; last_seen_* =
            most recent.

        Side effects:
          - WM mutated atomically under lock.
          - Persistent gallery on disk: winner's directory rewritten,
            loser's removed.
          - FAISS sidecar updated: loser deleted, winner upserted.
          - Audit log JSON written under cfg.object.merge_log_dir.

        Errors:
          400 - winner_oid == loser_oid, dim mismatch, validation
          404 - either oid not found
          405 - WM is frozen (serve-mode)
        """
        # Frozen WM (serve-mode) is read-only.
        if not hasattr(working_memory, "merge_objects"):
            raise HTTPException(
                status_code=405,
                detail="merge not supported on frozen working memory (serve-mode)",
            )

        winner_oid = req.winner_oid.strip()
        loser_oid = req.loser_oid.strip()

        try:
            result = working_memory.merge_objects(
                winner_oid, loser_oid, dry_run=req.dry_run,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Method returns {"error": "not_found", ...} for unknown oids,
        # instead of raising. Translate to 404.
        if result.get("error") == "not_found":
            raise HTTPException(
                status_code=404,
                detail=f"Object {result.get('missing_oid')} not found",
            )

        # On dry-run we skip the FAISS sync (no state change).
        if req.dry_run:
            return result

        # Sync to FAISS: delete loser, upsert winner with merged state.
        # Best-effort with logging -- if this fails, the in-memory state
        # is still correct and the next normal upsert cycle will reconcile.
        # The audit log captures intent so manual recovery is possible.
        try:
            if vectors is not None:
                # Delete loser first. The current FaissClient.delete()
                # leaves the index empty after the call but the next
                # upsert_batch fully rebuilds, so this ordering is safe.
                vectors.delete([loser_oid])
                record = working_memory.build_faiss_record_for_merge(winner_oid)
                if record is not None:
                    vectors.upsert_batch([record])
        except Exception:
            import traceback
            traceback.print_exc()
            # Don't fail the response -- WM is the source of truth, and
            # the merge has already succeeded there. Surface a warning in
            # the result instead.
            result["faiss_sync_warning"] = (
                "FAISS sync raised; check logs. WM state is correct; "
                "next observation or restart will reconcile."
            )

        # Re-fetch and return the merged winner's full detail.
        winner = working_memory.get(winner_oid)
        if winner is not None:
            result["winner"] = _obj_detail(winner)
        return result

    @app.post("/objects/suggest_merges")
    def suggest_merges_endpoint(
        req: SuggestMergesRequest = Body(...),
    ) -> Dict[str, Any]:
        """Surface high-confidence Mode B duplicate candidates for review.

        Read-only. Does NOT call merge_objects -- the caller reviews each
        candidate (e.g., via /objects/{oid}/snapshots) and explicitly POSTs
        /objects/merge to consolidate.

        Defaults (cos>=0.95, dist<=1.0m) match the conservative gate
        documented in handoff_2026-06-01-addendum.md. Tighter or looser
        thresholds are accepted for exploration.

        Errors:
          405 -- WM is frozen (serve-mode)
          500 -- unexpected failure inside the WM sweep
        """
        if not hasattr(working_memory, "suggest_merges"):
            raise HTTPException(
                status_code=405,
                detail="suggest_merges not supported on frozen working memory",
            )
        try:
            result = working_memory.suggest_merges(
                cos_threshold=req.cos_threshold,
                dist_threshold_m=req.dist_threshold_m,
                require_same_label=req.require_same_label,
                limit=req.limit,
                include_unconfirmed=req.include_unconfirmed,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"suggest_merges failed: {e}",
            )
        return result

    # ---- 2026-05-29: reference snapshot endpoints ----
    # Reference snapshots are the named-moment ground truth for each object:
    # one JPEG + one CLIP embedding, persisted through the FAISS sidecar.
    # Distinct from image_crops (rolling observation gallery, WM-only).

    def _encode_reference_image(jpeg_bytes: bytes) -> "np.ndarray":
        """Decode JPEG + CLIP-embed. Returns L2-normalized fp32 of shape (D,).

        Defensive about clip_adapter's method name: tries encode_image first
        (OpenCLIP convention; matches the encode_text pair already used by
        /search/semantic), falls back to embed_image. Fails loudly if neither
        is available so the deploy/test cycle catches it immediately.
        """
        img_buf = np.frombuffer(jpeg_bytes, dtype=np.uint8)
        bgr = cv2.imdecode(img_buf, cv2.IMREAD_COLOR)
        if bgr is None:
            raise ValueError("cv2.imdecode returned None for JPEG bytes")
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        # 2026-05-29: clip_adapter.encode_image expects a PIL.Image (it
        # calls .convert() internally). Wrap the ndarray defensively;
        # fall back to ndarray only if PIL isn't importable.
        try:
            from PIL import Image as _PILImage
            img_in = _PILImage.fromarray(rgb)
        except Exception:
            img_in = rgb
        if hasattr(clip_adapter, "encode_image"):
            emb_raw = clip_adapter.encode_image(img_in)
        elif hasattr(clip_adapter, "embed_image"):
            emb_raw = clip_adapter.embed_image(img_in)
        else:
            attrs = [m for m in dir(clip_adapter)
                     if callable(getattr(clip_adapter, m, None))
                     and not m.startswith("_")]
            raise AttributeError(
                f"clip_adapter has no encode_image or embed_image method. "
                f"Available callables: {attrs}"
            )
        # 2026-05-29: clip_adapter returns a torch tensor on cuda:0. Move
        # to CPU + detach before np.asarray (which implicitly calls .numpy()).
        try:
            import torch as _torch
            if isinstance(emb_raw, _torch.Tensor):
                emb_raw = emb_raw.detach().cpu().numpy()
        except ImportError:
            pass
        arr = np.asarray(emb_raw, dtype=np.float32).reshape(-1)
        n = float(np.linalg.norm(arr) + 1e-12)
        return (arr / n).astype(np.float32)

    @app.post("/objects/{oid}/reference")
    def set_object_reference(
        oid: str,
        payload: ReferenceImagePayload = Body(...),
    ) -> Dict[str, Any]:
        """Upload the canonical reference snapshot for an object.

        Stores JPEG bytes at /mnt/rtsm-data/refs/<oid>.jpg, CLIP-embeds, and
        updates reference_image_path + reference_emb on the WM object. The
        new fields persist through the next sidecar flush (the helper pushes
        an immediate LTM upsert for the oid).

        Errors:
            400 — malformed base64 or unreadable JPEG
            404 — unknown oid
            405 — frozen WM (serve mode)
            503 — CLIP adapter not available
            500 — CLIP encode failed or filesystem write failed
        """
        import os
        from pathlib import Path

        if not hasattr(working_memory, "set_object_reference"):
            raise HTTPException(
                status_code=405,
                detail="reference upload not supported on frozen WM (serve mode)",
            )
        if clip_adapter is None:
            raise HTTPException(
                status_code=503,
                detail="CLIP adapter not available; cannot embed reference",
            )

        obj = working_memory.get(oid)
        if obj is None:
            raise HTTPException(status_code=404, detail=f"Object {oid} not found")

        # Decode base64 -> JPEG bytes
        try:
            jpeg_bytes = base64.b64decode(payload.jpeg_b64, validate=True)
        except (binascii.Error, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"base64 decode failed: {e}")
        if not jpeg_bytes:
            raise HTTPException(status_code=400, detail="empty JPEG bytes")

        # CLIP-embed (also validates that cv2 can decode the JPEG)
        try:
            emb = _encode_reference_image(jpeg_bytes)
        except (ValueError, AttributeError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"CLIP encode failed: {e}")

        # Persist JPEG to disk. The refs dir lives alongside FAISS so it
        # rolls with the same data volume.
        refs_dir = Path(os.environ.get(
            "RTSM_REFS_DIR", "/workspace/workdir/refs"
        ))
        try:
            refs_dir.mkdir(parents=True, exist_ok=True)
            out_path = refs_dir / f"{oid}.jpg"
            out_path.write_bytes(jpeg_bytes)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"file write failed: {e}")

        # Update WM (also schedules immediate LTM upsert for the oid).
        try:
            working_memory.set_object_reference(
                oid, image_path=str(out_path), embedding=emb,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return {
            "id": oid,
            "reference_image_path": str(out_path),
            "reference_emb_dim": int(emb.shape[0]),
            "size_bytes": len(jpeg_bytes),
        }

    @app.post("/objects/reference_bulk")
    def set_object_reference_bulk(
        payload: ReferenceBulkPayload = Body(...),
    ) -> Dict[str, Any]:
        """Bulk reference upload, intended for Albert's boot-time backfill.

        Processes each item independently — per-item errors are recorded in
        the response without aborting the batch. Returns a summary plus
        per-item status.
        """
        import os
        from pathlib import Path

        if not hasattr(working_memory, "set_object_reference"):
            raise HTTPException(
                status_code=405,
                detail="reference upload not supported on frozen WM (serve mode)",
            )
        if clip_adapter is None:
            raise HTTPException(
                status_code=503,
                detail="CLIP adapter not available; cannot embed references",
            )

        refs_dir = Path(os.environ.get(
            "RTSM_REFS_DIR", "/workspace/workdir/refs"
        ))
        try:
            refs_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"refs dir setup failed: {e}")

        results: List[Dict[str, Any]] = []
        ok_count = 0
        for item in payload.items:
            entry: Dict[str, Any] = {"oid": item.oid}
            obj = working_memory.get(item.oid)
            if obj is None:
                entry["status"] = "not_found"
                results.append(entry)
                continue
            try:
                jpeg_bytes = base64.b64decode(item.jpeg_b64, validate=True)
                if not jpeg_bytes:
                    raise ValueError("empty JPEG bytes")
                emb = _encode_reference_image(jpeg_bytes)
                out_path = refs_dir / f"{item.oid}.jpg"
                out_path.write_bytes(jpeg_bytes)
                working_memory.set_object_reference(
                    item.oid, image_path=str(out_path), embedding=emb,
                )
                entry["status"] = "ok"
                entry["reference_image_path"] = str(out_path)
                entry["size_bytes"] = len(jpeg_bytes)
                ok_count += 1
            except Exception as e:
                entry["status"] = "error"
                entry["detail"] = str(e)
            results.append(entry)

        return {
            "total": len(payload.items),
            "ok": ok_count,
            "failed": len(payload.items) - ok_count,
            "results": results,
        }

    @app.get("/objects/{oid}/snapshots")
    def get_object_snapshots(oid: str, index: Optional[int] = None) -> Dict[str, Any]:
        """
        Get image crop gallery for an object.

        Args:
            oid: Object ID
            index: Optional specific index (0 = most recent, -1 = oldest)

        Returns:
            List of base64-encoded JPEG images (most recent first)
        """
        try:
            o = working_memory.get(oid)
        except Exception:
            o = None
        if o is None:
            raise HTTPException(status_code=404, detail=f"Object {oid} not found")

        crops = getattr(o, 'image_crops', []) or []
        if not crops:
            # 2026-05-30: fall back to the persisted reference snapshot if
            # set. Named objects (via name_object) get a canonical JPEG that
            # survives restart even when image_crops is empty (which it
            # always is post-rehydrate, since crops aren't persisted to
            # FAISS).
            ref_path = getattr(o, "reference_image_path", None)
            if ref_path and os.path.isfile(ref_path):
                try:
                    with open(ref_path, "rb") as _f:
                        _ref_bytes = _f.read()
                    _ref_b64 = base64.b64encode(_ref_bytes).decode("ascii")
                    _ref_uri = f"data:image/jpeg;base64,{_ref_b64}"
                    if index is not None and index != 0:
                        raise HTTPException(
                            status_code=404,
                            detail=(
                                f"Snapshot index {index} out of range "
                                f"(only the reference snapshot is available)"
                            ),
                        )
                    if index == 0:
                        return {
                            "id": oid,
                            "index": 0,
                            "total": 1,
                            "snapshot": _ref_uri,
                            "source": "reference",
                        }
                    return {
                        "id": oid,
                        "count": 1,
                        "snapshots": [{
                            "index": 0,
                            "data": _ref_uri,
                            "size_bytes": len(_ref_bytes),
                            "source": "reference",
                        }],
                    }
                except (OSError, IOError) as _e:
                    logger.warning(
                        "[snapshots] failed to read reference for %s: %s",
                        oid, _e,
                    )
            return {"id": oid, "count": 0, "snapshots": []}

        # Reverse order so index 0 is most recent
        crops_reversed = list(reversed(crops))

        if index is not None:
            if index < 0 or index >= len(crops_reversed):
                raise HTTPException(status_code=404, detail=f"Snapshot index {index} out of range (have {len(crops_reversed)})")
            jpeg_bytes = crops_reversed[index]
            b64 = base64.b64encode(jpeg_bytes).decode('ascii')
            return {
                "id": oid,
                "index": index,
                "total": len(crops_reversed),
                "snapshot": f"data:image/jpeg;base64,{b64}",
            }

        # Return all snapshots
        snapshots = []
        for i, jpeg_bytes in enumerate(crops_reversed):
            b64 = base64.b64encode(jpeg_bytes).decode('ascii')
            snapshots.append({
                "index": i,
                "data": f"data:image/jpeg;base64,{b64}",
                "size_bytes": len(jpeg_bytes),
            })

        return {
            "id": oid,
            "count": len(snapshots),
            "snapshots": snapshots,
        }

    @app.get("/objects/{oid}/snapshots/{index}/image")
    def get_object_snapshot_image(oid: str, index: int) -> Response:
        """Get raw JPEG image for a specific snapshot."""
        try:
            o = working_memory.get(oid)
        except Exception:
            o = None
        if o is None:
            raise HTTPException(status_code=404, detail=f"Object {oid} not found")

        crops = getattr(o, 'image_crops', []) or []
        if not crops:
            raise HTTPException(status_code=404, detail=f"Object {oid} has no snapshots")

        crops_reversed = list(reversed(crops))
        if index < 0 or index >= len(crops_reversed):
            raise HTTPException(status_code=404, detail=f"Snapshot index {index} out of range")

        return Response(content=crops_reversed[index], media_type="image/jpeg")

    # ---- Object debug endpoint ----
    # 2026-05-30: cleanup endpoints. Mirror the design doc's intent
    # that named objects are user-managed and pollution should be
    # explicitly removable.
    @app.delete("/objects/{oid}/reference")
    def delete_object_reference(oid: str) -> Dict[str, Any]:
        """Clear the reference snapshot fields on a WM object and delete
        the on-disk JPEG.

        Triggers an LTM heap push so the FAISS sidecar loses the reference
        fields on the next upsert cycle (asynchronous; restart inside
        flush_period_s can lose this -- mirrors the 5/29 PATCH timing
        caveat).
        """
        if not hasattr(working_memory, "set_object_reference"):
            raise HTTPException(
                status_code=405,
                detail="reference not supported on frozen working memory",
            )
        o = working_memory.get(oid)
        if o is None:
            raise HTTPException(status_code=404, detail=f"Object {oid} not found")
        old_path = getattr(o, "reference_image_path", None)
        try:
            working_memory.set_object_reference(oid, image_path=None, embedding=None)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        file_deleted = False
        if old_path and os.path.isfile(old_path):
            try:
                os.remove(old_path)
                file_deleted = True
            except OSError as e:
                logger.warning(
                    "[delete_reference] failed to remove %s: %s", old_path, e
                )
        return {
            "id": oid,
            "cleared": True,
            "old_reference_image_path": old_path,
            "file_deleted": file_deleted,
        }

    @app.delete("/objects/{oid}")
    def delete_object(oid: str) -> Dict[str, Any]:
        """Remove an object from WM entirely.

        Also deletes the reference JPEG if present, and attempts to remove
        from the FAISS sidecar if the configured vectors client exposes a
        remove() method. Without sidecar removal, the object will rehydrate
        on next restart.
        """
        if not hasattr(working_memory, "remove_object"):
            raise HTTPException(
                status_code=405,
                detail="DELETE not supported on frozen working memory",
            )
        o = working_memory.get(oid)
        if o is None:
            raise HTTPException(status_code=404, detail=f"Object {oid} not found")
        ref_path = getattr(o, "reference_image_path", None)
        file_deleted = False
        if ref_path and os.path.isfile(ref_path):
            try:
                os.remove(ref_path)
                file_deleted = True
            except OSError as e:
                logger.warning(
                    "[delete_object] failed to remove reference %s: %s", ref_path, e
                )
        faiss_removed = False
        if vectors is not None and hasattr(vectors, "remove"):
            try:
                vectors.remove(oid)
                faiss_removed = True
            except Exception as e:
                logger.warning(
                    "[delete_object] vectors.remove failed for %s: %s", oid, e
                )
        removed = working_memory.remove_object(oid)
        if not removed:
            raise HTTPException(
                status_code=500,
                detail=f"Object {oid} disappeared from WM during delete",
            )
        return {
            "id": oid,
            "removed": True,
            "reference_file_deleted": file_deleted,
            "faiss_sidecar_removed": faiss_removed,
        }

    @app.get("/objects/{oid}/debug")
    def get_object_debug(oid: str) -> Dict[str, Any]:
        """Get detailed diagnostic information for an object."""
        try:
            o = working_memory.get(oid)
        except Exception:
            o = None
        if o is None:
            return {"error": "not_found", "id": oid}

        xyz = getattr(o, "xyz_world", None)
        cov = getattr(o, "cov_world", None)

        return {
            "id": oid,
            "position": {
                "xyz_world": xyz.tolist() if xyz is not None else None,
                "cov_world": cov.tolist() if cov is not None else None,
                "cov_diag_cm": [float(np.sqrt(c) * 100) for c in cov] if cov is not None else None,
            },
            "tracking": {
                "hits": int(getattr(o, "hits", 0)),
                "stability": float(getattr(o, "stability", 0.0)),
                "confirmed": bool(getattr(o, "confirmed", False)),
                "last_seen_px": list(getattr(o, "last_seen_px", [])) if getattr(o, "last_seen_px", None) else None,
            },
            "labels": {
                "primary": getattr(o, "label_primary", None),
                "scores": dict(getattr(o, "label_scores", {}) or {}),
                "hits":   dict(getattr(o, "label_hits",   {}) or {}),
            },
            "view_diversity": {
                "bins_filled": len(getattr(o, "view_bins", {}) or {}),
                "bin_ids": list((getattr(o, "view_bins", {}) or {}).keys()),
            },
            "gallery": {
                "image_crops_count": len(getattr(o, "image_crops", []) or []),
                "emb_gallery_shape": list(getattr(o, "emb_gallery", np.array([])).shape) if getattr(o, "emb_gallery", None) is not None else None,
            },
            "timestamps": {
                "created_wall_utc": float(getattr(o, "created_wall_utc", 0.0)),
                "last_seen_wall_utc": float(getattr(o, "last_seen_wall_utc", 0.0)),
                "age_s": time.time() - float(getattr(o, "created_wall_utc", time.time())),
            },
        }

    # ---- Reset endpoint ----
    @app.post("/reset")
    def reset() -> Dict[str, Any]:
        """
        Reset RTSM runtime state while keeping models loaded.

        Clears:
        - WorkingMemory (all objects, proto/confirmed)
        - ProximityIndex (spatial grid, via WM.clear())
        - SweepCache (sweep timestamps, camera snapshots)
        - FrameWindow (buffered RGB-D frames)
        - VisualizationServer registry (keyframes/point clouds)

        Does NOT clear:
        - FastSAM / CLIP models (expensive to reload)
        - FAISS LTM vectors (preserves long-term memory)
        - Configuration
        """
        result: Dict[str, Any] = {
            "status": "ok",
            "reset_time_utc": time.time(),
            "cleared": {},
        }

        # Clear WorkingMemory (also clears attached ProximityIndex)
        try:
            wm_result = working_memory.clear()
            result["cleared"]["working_memory"] = wm_result
        except Exception as e:
            result["cleared"]["working_memory"] = {"error": str(e)}

        # Clear SweepCache
        if reset_components and reset_components.sweep_cache:
            try:
                sc_result = reset_components.sweep_cache.clear()
                result["cleared"]["sweep_cache"] = sc_result
            except Exception as e:
                result["cleared"]["sweep_cache"] = {"error": str(e)}

        # Clear FrameWindow
        if reset_components and reset_components.frame_window:
            try:
                fw_result = reset_components.frame_window.clear()
                result["cleared"]["frame_window"] = fw_result
            except Exception as e:
                result["cleared"]["frame_window"] = {"error": str(e)}

        # Clear VisualizationServer (registry + TSDF + broadcast clear to clients)
        if reset_components and reset_components.vis_server:
            try:
                vis = reset_components.vis_server
                vis_result = {}
                if hasattr(vis, 'registry') and vis.registry:
                    kf_cleared = vis.registry.clear()
                    vis_result["keyframes_cleared"] = kf_cleared
                if hasattr(vis, 'tsdf') and vis.tsdf is not None:
                    vis.tsdf.reset()
                    vis_result["tsdf_reset"] = True
                # Broadcast clear to all connected web clients
                if hasattr(vis, 'broadcaster') and vis._running:
                    vis.broadcaster.schedule(
                        vis.broadcaster._broadcast_json({"type": "clear"})
                    )
                    vis_result["clients_notified"] = True
                result["cleared"]["visualization"] = vis_result
            except Exception as e:
                result["cleared"]["visualization"] = {"error": str(e)}

        # Clear analytics buffers
        if seg_analytics:
            try:
                seg_analytics.clear()
                result["cleared"]["seg_analytics"] = True
            except Exception as e:
                result["cleared"]["seg_analytics"] = {"error": str(e)}
        if latency_analytics:
            try:
                latency_analytics.clear()
                result["cleared"]["latency_analytics"] = True
            except Exception as e:
                result["cleared"]["latency_analytics"] = {"error": str(e)}

        return result

    # PATCH III 20260501: hot-reload FrozenWorkingMemory from its on-disk sidecar.
    # Serve-mode only (requires working_memory to be a FrozenWorkingMemory).
    @app.post("/reload")
    def reload_frozen() -> Dict[str, Any]:
        """Reload FrozenWorkingMemory from the FAISS meta sidecar without restarting.

        Returns 200 with a summary on success, 400 if the current working_memory
        does not support reload (live pipeline mode), 404 if the sidecar is missing,
        500 for parse/other errors. On failure, existing state is preserved.
        """
        if not hasattr(working_memory, "reload"):
            raise HTTPException(
                status_code=400,
                detail="reload not supported (working_memory has no reload method)",
            )
        try:
            summary = working_memory.reload()
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=f"sidecar missing: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"reload failed: {e}")
        return {"status": "ok", **summary}

    # ---- Detailed stats endpoint ----
    @app.get("/stats/detailed")
    def stats_detailed() -> Dict[str, Any]:
        """
        Get detailed stats from all RTSM components.
        """
        result: Dict[str, Any] = {}

        # WorkingMemory stats
        try:
            result["working_memory"] = dict(working_memory.stats())
        except Exception:
            result["working_memory"] = {}

        # SweepCache stats
        if reset_components and reset_components.sweep_cache:
            try:
                result["sweep_cache"] = reset_components.sweep_cache.stats()
            except Exception:
                result["sweep_cache"] = {}

        # FrameWindow stats
        if reset_components and reset_components.frame_window:
            try:
                result["frame_window"] = reset_components.frame_window.stats()
            except Exception:
                result["frame_window"] = {}

        # VisualizationServer stats
        if reset_components and reset_components.vis_server:
            try:
                vis = reset_components.vis_server
                if hasattr(vis, 'registry') and vis.registry:
                    result["visualization"] = vis.registry.stats()
            except Exception:
                result["visualization"] = {}

        # Extra stats provider
        if extra_stats_provider:
            try:
                result["extra"] = extra_stats_provider()
            except Exception:
                pass

        return result

    # ---- Semantic search endpoint ----
    @app.get("/search/semantic")
    def semantic_search(
        query: str,
        top_k: int = 10,
        threshold: float = 0.0,
        include_snapshot: bool = False,
        pose_state: str = "on_floor",   # NEW: "on_floor" | "elevated" | "any"
    ) -> Dict[str, Any]:

        """
        Semantic search for objects using CLIP text encoding + FAISS KNN.

        Cosine scores vary by model: CLIP ViT-B/32 clusters 0.25-0.35,
        SigLIP ViT-B-16 clusters 0.05-0.15 for indoor objects. The ranking
        is meaningful (top results are most relevant) even though absolute
        scores are low. Default threshold=0.0 returns all ranked results
        so agents can decide their own cutoff.

        For visual verification, set include_snapshot=true to get the most
        recent observation crop (base64 JPEG) for each result. This enables
        multimodal LLM planners to visually verify objects without relying
        on CLIP classification.

        Args:
            query: Natural language search query (e.g., "red cup", "chair")
            top_k: Maximum number of results to return
            threshold: Minimum cosine similarity threshold (default 0.0 = return all ranked)
            include_snapshot: If true, include base64 JPEG of most recent crop
        """
        if not clip_adapter or not vectors:
            raise HTTPException(status_code=503, detail="Semantic search not available (CLIP or vectors not configured)")

        # 1. Encode query text with CLIP
        # For OpenAI CLIP models, wrap short queries in caption format
        # ("a photo of a dog") since CLIP was trained on image-caption pairs.
        # SigLIP models work better with raw queries (trained differently).
        clip_query = query
        if hasattr(clip_adapter, '_prompt_wrap') and clip_adapter._prompt_wrap and len(query.split()) <= 3:
            clip_query = f"a photo of a {query}"
        try:
            query_emb = clip_adapter.encode_text(clip_query)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to encode query: {e}")

        # 2. KNN search via FAISS
        try:
            matches = vectors.search(query_emb, top_k=top_k)  # [(oid, score), ...]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Vector search failed: {e}")

        # 3. Filter by threshold and enrich with WM metadata, falling back
        #    to the FAISS-side metadata sidecar when WM has no entry for the
        #    oid (e.g. a fresh process that only loaded FAISS from disk).
        # 2026-05-26 Gate 3: compute robot_pose / robot_xyz once and reuse
        # for distance_from_robot on every result. None-safe; if robot pose
        # isn't published the per-result distance just becomes None and the
        # Albert bridge degrades to "distance unknown".
        robot_pose = working_memory.get_robot_pose()
        robot_xyz = _robot_xyz(robot_pose)
        results = []
        for oid, score in matches:
            if score < threshold:
                continue
            obj = working_memory.get(oid)
            if obj is not None:
                source = "wm"
                confirmed_v = obj.confirmed
                stability_v = round(float(obj.stability), 3)
                xyz = obj.xyz_world
                xyz_v = xyz.tolist() if xyz is not None else None
            else:
                meta = None
                get_meta = getattr(vectors, "get_metadata", None)
                if callable(get_meta):
                    try:
                        meta = get_meta(oid)
                    except Exception:
                        meta = None
                if meta is not None:
                    source = "faiss_meta"
                    confirmed_v = True  # only confirmed objects ever reach FAISS
                    stability_v = round(float(meta.get("stability", 0.0) or 0.0), 3)
                    mxyz = meta.get("xyz")
                    if mxyz is None:
                        xyz_v = None
                    elif hasattr(mxyz, "tolist"):
                        xyz_v = mxyz.tolist()
                    else:
                        xyz_v = list(mxyz)
                else:
                    source = "none"
                    confirmed_v = True
                    stability_v = 0.0
                    xyz_v = None

            # 2026-05-22 pose-state filter: navigation queries get on_floor
            # by default. Pass ?pose_state=any to see everything (debug/UI),
            # or ?pose_state=elevated to see only desk-observed objects.
            #
            # For WM objects: read the field directly (default "on_floor"
            # for any object created pre-patch).
            # For faiss_meta-only objects: they predate this field; treat
            # them as on_floor (historically they were only persisted from
            # floor observations).
            # For source=="none": filter them out unless pose_state=="any".
            if pose_state != "any":
                if obj is not None:
                    tag = getattr(obj, "pose_state_at_observation", "on_floor")
                elif source == "faiss_meta":
                    tag = "on_floor"
                else:
                    # No metadata available; safer to skip unless explicitly
                    # asked for "any". Caller can override with ?pose_state=any.
                    continue
                if tag != pose_state:
                    continue

            # Compute tag for response (reuse the logic from filter; obj/source
            # were already resolved above).
            if obj is not None:
                tag_for_response = getattr(obj, "pose_state_at_observation", "on_floor")
            elif source == "faiss_meta":
                tag_for_response = "on_floor"
            else:
                tag_for_response = "unknown"

            # 2026-05-26 Gate 3: resolve label + last_seen for the Albert
            # bridge. WM path uses live attributes (with gated label
            # selection matching _obj_summary). faiss_meta path reads the
            # sidecar — if the sidecar payload predates Gate 3 these come
            # back None, which the bridge degrades gracefully on.
            if obj is not None:
                label_v = _display_label(obj)
                last_seen_v = _iso_from_wall_utc(
                    getattr(obj, "last_seen_wall_utc", 0.0)
                )
            elif source == "faiss_meta" and meta is not None:
                label_v = (meta.get("label")
                           or meta.get("label_user")
                           or meta.get("label_primary"))
                last_seen_v = _iso_from_wall_utc(meta.get("last_seen_wall_utc"))
            else:
                label_v = None
                last_seen_v = None

            entry: Dict[str, Any] = {
                "id": oid,
                "score": round(float(score), 4),
                "confirmed": confirmed_v,
                "stability": stability_v,
                "xyz_world": xyz_v,
                "source": source,
                "pose_state_at_observation": tag_for_response,
                # 2026-05-26 Gate 3 additions:
                "label": label_v,
                "last_seen_at": last_seen_v,
                "distance_from_robot": _distance_from_robot(xyz_v, robot_xyz),
            }


            # Include most recent snapshot for multimodal agent verification.
            # Snapshots live only in WM (not persisted to FAISS), so they are
            # unavailable via the faiss_meta path; this is intentional.
            if include_snapshot and obj:
                crops = getattr(obj, 'image_crops', None) or []
                if crops:
                    # Most recent crop is last in list
                    entry["snapshot_b64"] = base64.b64encode(crops[-1]).decode('ascii')
                    entry["snapshot_count"] = len(crops)

            results.append(entry)

        return {
            "query": query,
            "robot_pose": robot_pose,
            "results": results,
        }

    # ---- Spatial search endpoint ----
    @app.get("/search/spatial")
    def spatial_search(
        x: float, y: float, z: float,
        radius_m: float = 1.0,
        offset: int = 0,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Spatial search for objects within a radius of a 3D point.

        Args:
            x, y, z: Center point in world coordinates (meters)
            radius_m: Search radius in meters (default 1.0)
            offset: Skip first N results (for pagination)
            limit: Maximum results to return (default 50, max 200)

        Returns:
            List of nearby objects sorted by distance, with pagination
        """
        limit = min(max(1, limit), 200)
        offset = max(0, offset)

        if working_memory.index is None:
            raise HTTPException(status_code=503, detail="Spatial search not available (no proximity index)")

        center = np.array([x, y, z], dtype=np.float32)
        grid = working_memory.index.grid
        rings = min(10, max(1, int(np.ceil(radius_m / grid.cell_m))))

        oids = working_memory.index.nearby_ids(center, rings=rings)

        # 2026-05-26 Gate 3: compute robot_pose / robot_xyz once and reuse
        # for distance_from_robot. None-safe.
        robot_pose = working_memory.get_robot_pose()
        robot_xyz = _robot_xyz(robot_pose)

        all_results = []
        for oid in oids:
            obj = working_memory.get(oid)
            if obj is None:
                continue
            dist = float(np.linalg.norm(obj.xyz_world - center))
            if dist > radius_m:
                continue
            xyz_v = obj.xyz_world.tolist()
            all_results.append({
                "id": oid,
                "distance_m": round(dist, 4),
                "xyz_world": xyz_v,
                "confirmed": bool(getattr(obj, "confirmed", False)),
                "stability": round(float(getattr(obj, "stability", 0.0)), 3),
                # 2026-05-26 Gate 3 additions:
                "label": _display_label(obj),
                "last_seen_at": _iso_from_wall_utc(
                    getattr(obj, "last_seen_wall_utc", 0.0)
                ),
                "distance_from_robot": _distance_from_robot(xyz_v, robot_xyz),
                "pose_state_at_observation": getattr(
                    obj, "pose_state_at_observation", "on_floor"
                ),
            })

        all_results.sort(key=lambda r: r["distance_m"])
        total = len(all_results)
        page = all_results[offset : offset + limit]

        return {
            "center": [x, y, z],
            "radius_m": radius_m,
            "robot_pose": robot_pose,
            "total": total,
            "offset": offset,
            "limit": limit,
            "count": len(page),
            "results": page,
        }

    # ---- Analytics endpoint ----
    @app.get("/stats/analytics")
    def stats_analytics() -> Dict[str, Any]:
        """Get runtime analytics (segmentation breakdown + latency/throughput)."""
        if not seg_analytics and not latency_analytics:
            raise HTTPException(status_code=503, detail="Analytics not enabled")
        result: Dict[str, Any] = {}
        if latency_analytics:
            result["latency"] = {
                "aggregate": latency_analytics.aggregate(),
                "hourly": latency_analytics.hourly_history(),
            }
        if seg_analytics:
            result["segmentation"] = {
                "aggregate": seg_analytics.aggregate(),
                "hourly": seg_analytics.hourly_history(),
            }
        return result

    # ---- Embedded MCP server (optional) ----
    if mcp_enabled:
        try:
            from rtsm.io.mcp_embedded import create_mcp_app
            mcp_mount = create_mcp_app(
                working_memory=working_memory,
                clip_adapter=clip_adapter,
                vectors=vectors,
            )
            app.mount("/mcp", mcp_mount)
        except ImportError:
            import logging as _logging
            _logging.getLogger(__name__).warning(
                "MCP enabled in config but 'mcp' package not installed. "
                "Install with: pip install \"rtsm[mcp]\""
            )

    # ---- Visualization WebSocket (optional, for single-port demo) ----
    if vis_broadcaster is not None and vis_registry is not None:

        @app.websocket("/ws")
        async def viz_websocket(websocket: WebSocket):
            await websocket.accept()
            await vis_broadcaster.connect(websocket)
            synced = await vis_broadcaster.sync_new_client(websocket, vis_registry)
            # Sync latest TSDF mesh to new client
            if vis_server is not None and hasattr(vis_server, 'tsdf') and vis_server.tsdf is not None:
                latest = vis_server.tsdf.get_latest_mesh()
                if latest is not None:
                    import numpy as _np
                    positions, colors = latest
                    identity = _np.eye(4, dtype=_np.float32)
                    data = vis_broadcaster._pack_mesh_create(
                        "tsdf_fused", positions, colors, identity
                    )
                    await vis_broadcaster._try_send_bytes(websocket, data)
                    synced += 1
            import logging as _log
            _log.getLogger(__name__).info(f"[api/ws] Client connected, synced {synced} keyframes")
            try:
                while True:
                    data = await websocket.receive_text()
                    # Handle client commands (clear, stats)
                    try:
                        import json as _json
                        msg = _json.loads(data)
                        cmd = msg.get("cmd")
                        if cmd == "clear":
                            vis_registry.clear()
                            await vis_broadcaster._broadcast_json({"type": "clear"})
                    except Exception:
                        pass
            except WebSocketDisconnect:
                pass
            finally:
                await vis_broadcaster.disconnect(websocket)

    # ---- /ingest/keyframe (Gate 2.f.1 -- decode-only) ----
    # PATCH 20260507  (Gate 2.d):   stub that validated wire contract and counted bytes.
    # PATCH 20260507b (Gate 2.f.1): decode + validate; no pipeline dispatch yet.
    # Gate 2.f.2 will construct FramePacket and push to IngestQueue.
    def _decode_keyframe_payload(payload: KeyframePayload) -> Dict[str, Any]:
        """Decode a KeyframePayload into numpy arrays + validated metadata.

        Pure function; never raises. Pydantic has already validated schema
        before we are called. Decode errors become structured
        {mode: "decode-failed", ...} responses.
        """
        t0 = time.perf_counter()

        # Stage 1: base64 decode (validate=True so garbage fails loudly).
        try:
            rgb_jpeg_bytes = base64.b64decode(payload.rgb_jpeg, validate=True)
            depth_png_bytes = base64.b64decode(payload.depth_png, validate=True)
        except (binascii.Error, ValueError) as e:
            return {
                "mode": "decode-failed",
                "error": "base64_decode_failed",
                "stage": "base64",
                "detail": str(e),
                "timings": {"base64_ms": (time.perf_counter() - t0) * 1000.0},
            }
        t1 = time.perf_counter()

        # Stage 2: cv2 image decode.
        try:
            rgb_buf = np.frombuffer(rgb_jpeg_bytes, dtype=np.uint8)
            rgb = cv2.imdecode(rgb_buf, cv2.IMREAD_COLOR)   # BGR HxWx3 uint8
            if rgb is None:
                raise ValueError("cv2.imdecode returned None for rgb_jpeg")
            depth_buf = np.frombuffer(depth_png_bytes, dtype=np.uint8)
            depth_raw = cv2.imdecode(depth_buf, cv2.IMREAD_UNCHANGED)  # HxW uint16 (mm)
            if depth_raw is None:
                raise ValueError("cv2.imdecode returned None for depth_png")
        except Exception as e:
            return {
                "mode": "decode-failed",
                "error": "cv2_decode_failed",
                "stage": "cv2",
                "detail": str(e),
                "timings": {
                    "base64_ms": (t1 - t0) * 1000.0,
                    "cv2_ms": (time.perf_counter() - t1) * 1000.0,
                },
            }
        t2 = time.perf_counter()

        # Stage 3: validation (non-fatal: collect warnings, still decode-only).
        warnings_list: List[str] = []
        if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.dtype != np.uint8:
            warnings_list.append(
                f"rgb shape/dtype: got {list(rgb.shape)} {rgb.dtype}, expected HxWx3 uint8"
            )
        if depth_raw.ndim != 2 or depth_raw.dtype != np.uint16:
            warnings_list.append(
                f"depth shape/dtype: got {list(depth_raw.shape)} {depth_raw.dtype}, expected HxW uint16"
            )
        if rgb.ndim == 3 and depth_raw.ndim == 2 and rgb.shape[:2] != depth_raw.shape:
            warnings_list.append(
                f"rgb/depth shape mismatch: rgb {list(rgb.shape[:2])} vs depth {list(depth_raw.shape)}"
            )

        K = payload.K
        fx, fy, cx, cy = K[0], K[4], K[2], K[5]
        H = int(rgb.shape[0]) if rgb.ndim == 3 else 0
        W = int(rgb.shape[1]) if rgb.ndim == 3 else 0
        if not (fx > 0 and fy > 0):
            warnings_list.append(f"K: fx={fx} fy={fy} must be positive")
        if W > 0 and not (0.0 <= cx <= W):
            warnings_list.append(f"K: cx={cx} out of [0, {W}]")
        if H > 0 and not (0.0 <= cy <= H):
            warnings_list.append(f"K: cy={cy} out of [0, {H}]")

        p = payload.pose
        qnorm = (p.qx * p.qx + p.qy * p.qy + p.qz * p.qz + p.qw * p.qw) ** 0.5
        if abs(qnorm - 1.0) > 0.01:
            warnings_list.append(f"pose quaternion not unit: norm={qnorm:.4f}")

        if depth_raw.ndim == 2 and depth_raw.size > 0:
            valid = int(np.count_nonzero(depth_raw))
            depth_valid_pct = 100.0 * valid / depth_raw.size
        else:
            depth_valid_pct = 0.0

        t3 = time.perf_counter()

        return {
            "mode": "decode-only",
            "rgb_shape": list(rgb.shape),
            "depth_shape": list(depth_raw.shape),
            "depth_valid_pct": round(depth_valid_pct, 2),
            "timings": {
                "base64_ms": round((t1 - t0) * 1000.0, 3),
                "cv2_ms": round((t2 - t1) * 1000.0, 3),
                "validate_ms": round((t3 - t2) * 1000.0, 3),
                "total_ms": round((t3 - t0) * 1000.0, 3),
            },
            "validation_warnings": warnings_list,
            "_arrays": {"rgb": rgb, "depth_raw": depth_raw},
        }

    @app.post("/ingest/keyframe")
    def ingest_keyframe(payload: KeyframePayload) -> Dict[str, Any]:
        """Accept a keyframe: decode, build FramePacket, push to ingest queue.

        Gate 2.f.2: builds FramePacket from decoded arrays and enqueues it for
        the pipeline consumer. Returns 503 if the queue is full (backpressure).
        If no ingest_queue is bound (e.g. --serve mode), falls back to the
        2.f.1 decode-only behavior.
        """
        import logging as _log
        import queue as _queue
        from rtsm.core.datamodel import (
            FramePacket, TimeBundle, PoseStamped, PinholeIntrinsics,
        )

        rgb_bytes = len(payload.rgb_jpeg)
        depth_bytes = len(payload.depth_png)
        total_bytes = rgb_bytes + depth_bytes

        # Transport counters increment regardless of decode / dispatch outcome.
        _ingest_counters["frames_received"] += 1
        _ingest_counters["bytes_received"] += total_bytes
        if payload.sequence is not None:
            _ingest_counters["last_sequence"] = int(payload.sequence)

        decoded = _decode_keyframe_payload(payload)

        # Decode failure: return early in the same shape as 2.f.1.
        if decoded.get("mode") != "decode-only":
            _log.getLogger(__name__).warning(
                "[ingest] decode-failed seq=%s stage=%s",
                payload.sequence, decoded.get("stage"),
            )
            return {
                "status": "decode_failed",
                "observations_added": 0,
                "objects_updated": 0,
                "sequence": payload.sequence,
                **decoded,
            }

        # Extract arrays; build FramePacket.
        arrays = decoded.pop("_arrays")
        rgb = arrays["rgb"]
        depth_raw = arrays["depth_raw"]
        # depth_raw is uint16 mm (D435i convention, 0 = invalid).
        depth_m = depth_raw.astype(np.float32) / 1000.0
        depth_m[depth_raw == 0] = np.nan

        H, W = int(rgb.shape[0]), int(rgb.shape[1])
        K = payload.K
        intr = PinholeIntrinsics(
            width=W, height=H,
            fx=K[0], fy=K[4], cx=K[2], cy=K[5],
        )
        pq = payload.pose
        t_sensor_ns = int(payload.timestamp_ros * 1e9)
        tb = TimeBundle(
            t_mono_s=time.monotonic(),
            t_wall_utc_s=time.time(),
            t_sensor_ns=t_sensor_ns,
            seq=payload.sequence,
        )
        pose = PoseStamped(
            stamp_ns=t_sensor_ns,
            frame_id=payload.frame_id,
            t_wc=np.array([pq.tx, pq.ty, pq.tz], dtype=np.float32),
            q_wc_xyzw=np.array([pq.qx, pq.qy, pq.qz, pq.qw], dtype=np.float32),
        )
        pkt = FramePacket(
            time=tb, rgb=rgb, depth_m=depth_m,
            pose=pose, intr=intr,
            is_keyframe=True,
        )

        # If no queue is bound (e.g. --serve mode), behave as 2.f.1.
        if _ingest_queue is None:
            _log.getLogger(__name__).info(
                "[ingest] rx seq=%s ts=%.3f no queue bound; decode-only",
                payload.sequence, payload.timestamp_ros,
            )
            return {
                "status": "accepted",
                "observations_added": 0,
                "objects_updated": 0,
                "sequence": payload.sequence,
                **decoded,
                "notes": "no ingest_queue bound; decode-only (likely --serve mode)",
            }

        # Queue put (non-blocking). Full -> 503.
        t_q0 = time.perf_counter()
        try:
            _ingest_queue.put(pkt, block=False)
        except _queue.Full:
            _ingest_counters["queue_full_drops"] += 1
            _log.getLogger(__name__).warning(
                "[ingest] queue full; drop seq=%s", payload.sequence,
            )
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "queue_full",
                    "sequence": payload.sequence,
                    "queue_full_drops": _ingest_counters["queue_full_drops"],
                },
            )
        queue_put_ms = round((time.perf_counter() - t_q0) * 1000.0, 3)
        _ingest_counters["frames_queued"] += 1

        decoded["timings"]["queue_put_ms"] = queue_put_ms
        _log.getLogger(__name__).info(
            "[ingest] queued seq=%s ts=%.3f rgb=%dB depth=%dB total_ms=%s",
            payload.sequence, payload.timestamp_ros,
            rgb_bytes, depth_bytes,
            decoded.get("timings", {}).get("total_ms"),
        )

        return {
            "status": "queued",
            "observations_added": 0,
            "objects_updated": 0,
            "sequence": payload.sequence,
            **decoded,
        }

    @app.get("/stats/ingest")
    def stats_ingest() -> Dict[str, Any]:
        """Ingest counters (not reset by /reset -- transport-layer accounting)."""
        out = dict(_ingest_counters)
        if _ingest_queue is not None:
            out["queue_depth"] = int(_ingest_queue.qsize())
            out["queue_maxsize"] = int(getattr(_ingest_queue, "maxsize", 0))
            out["mode"] = "queued"
        else:
            out["mode"] = "decode-only"
        return out
    # ---- end PATCH 20260507 / 20260507b ----

    # ---- Static frontend (mount LAST so API routes take priority) ----
    if static_dir:
        import os
        if os.path.isdir(static_dir):
            from fastapi.staticfiles import StaticFiles
            app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")

    return app


def start_server(app: FastAPI, host: str = "0.0.0.0", port: int = 8000) -> threading.Thread:
    """Start a uvicorn server in a background daemon thread.

    Blocks until the server is listening and the lifespan startup has
    completed (so vis_server.start_tasks() has run before we return).
    """
    import uvicorn

    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    # Avoid uvicorn installing signal handlers in a child thread
    server.install_signal_handlers = lambda: None  # type: ignore[attr-defined]

    ready = threading.Event()
    _orig_startup = server.startup

    async def _startup_then_signal(*a, **kw):
        result = await _orig_startup(*a, **kw)
        ready.set()
        return result

    server.startup = _startup_then_signal  # type: ignore[attr-defined]

    def _run() -> None:
        server.run()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    ready.wait(timeout=30)  # block until lifespan completes
    return t


