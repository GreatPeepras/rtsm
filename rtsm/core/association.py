"""
Associator: Match per-frame Candidates to live objects in WorkingMemory, or spawn new protos.

Design highlights
- Uses proximity index to fetch nearby IDs (bounded by rings/neighbors_max).
- Gates in order: 3D distance (and optional Z), reprojection px error, cosine similarity.
- Scores survivors and commits a 1:1 match. Otherwise, spawns a proto (with per-cell spawn cap).
- Builds a minimal Observation object to pass into WM.update_object (WM handles EMA, bins, EWMA labels, stability, etc.).

Assumptions
- Candidate.stats.centroid_cam is a (3,) np.ndarray in *camera* frame (meters).
- Candidate.stats.centroid_px is (x,y) in pixels (optional but helps reprojection gate).
- Snapshot.pose_cam_T_world is a 4x4 float32 transforming world -> camera. If you only
  have T_world_cam, pass its inverse here. We'll invert once per update call if needed.
- Snapshot.intrinsics = {fx,fy,cx,cy}.

This module deliberately does not import WM or ObjectIndex types — they are duck-typed.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
import logging
import numpy as np

logger = logging.getLogger(__name__)

# ---------- local observation envelope passed to WM.update_object ----------

@dataclass(slots=True)
class AssocUpdate:
    p_world: np.ndarray                 # (3,) float32 meters
    emb_vis: np.ndarray                 # (D,) float32, L2-normalized
    view_dir_cam: Optional[np.ndarray]  # (3,) float32, unit vector or None
    centroid_px: Optional[Tuple[float, float]]
    depth_valid: float
    quality: float
    # optional metrics for stability gain logging in WM
    cos_sim: float = 0.0
    dist_m: float = 0.0
    # optional: semantic top-k for EWMA label update in WM
    label_topk: Optional[list[tuple[str, float]]] = None
    # optional: RGB crop for gallery storage (224x224x3 uint8)
    crop: Optional[np.ndarray] = None
    # keyframe flag for EMA weighting (keyframes dominate position smoothing)
    is_keyframe: bool = False
    # frame_id for precise pose correction tracking in WM
    frame_id: Optional[str] = None

# ---------- math helpers ----------

def _ensure_l2(v: np.ndarray) -> np.ndarray:
    v = v.astype(np.float32, copy=False)
    n = float(np.linalg.norm(v) + 1e-12)
    return v / n


def _invert_h(T: np.ndarray) -> np.ndarray:
    """Invert 4x4 homogeneous transform (fast path for rigid)."""
    R = T[:3, :3]
    t = T[:3, 3]
    Tinv = np.eye(4, dtype=T.dtype)
    Tinv[:3, :3] = R.T
    Tinv[:3, 3] = -R.T @ t
    return Tinv


def _project_px(p_world: np.ndarray, T_cam_world: np.ndarray, intr: Dict[str, float]) -> Optional[Tuple[float, float]]:
    """Project world point into pixels; return None if behind camera or invalid."""
    fx, fy, cx, cy = float(intr['fx']), float(intr['fy']), float(intr['cx']), float(intr['cy'])
    pw = np.append(p_world.astype(np.float32), 1.0)
    pc = T_cam_world @ pw
    Z = float(pc[2])
    if Z <= 1e-6:
        return None
    u = fx * float(pc[0]) / Z + cx
    v = fy * float(pc[1]) / Z + cy
    return (u, v)


def _px_error(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return float(np.hypot(a[0] - b[0], a[1] - b[1]))


# ---------- main associator ----------

class Associator:
    def __init__(self, cfg: Dict[str, Any]) -> None:
        self.cfg = cfg

    def update_with_candidates(self, cands, snap, wm, index, *, per_cell_spawn_counter: Optional[Dict[Tuple[int, int, int] | Tuple[int, int], int]] = None, is_keyframe: bool = False, frame_id: Optional[str] = None) -> Dict[str, int]:
        """Process a batch of Candidates for one Snapshot.
        - cands: iterable of Candidate (duck-typed: .stats.centroid_cam, .emb_vis, .stats.centroid_px, .priority)
        - snap: Snapshot (duck-typed: .pose_cam_T_world [4x4], .intrinsics {fx,fy,cx,cy})
        - wm: WorkingMemory-like (duck-typed)
        - index: ObjectIndex-like (duck-typed)
        - per_cell_spawn_counter: optional dict to enforce per-cell spawn cap per trigger
        """
        if not cands:
            return {"matched": 0, "created": 0}

        assoc_cfg = self.cfg.get('assoc', {})
        rings = int(assoc_cfg.get('rings', 1))
        gate_dist = float(assoc_cfg.get('gate_dist_base_m', 0.20))
        gate_z = float(assoc_cfg.get('gate_z_m', 1e9))  # effectively off unless set
        gate_px = float(assoc_cfg.get('gate_reproj_px', 30.0))
        use_embeddings = bool(assoc_cfg.get('use_embeddings', True))
        cos_min = float(assoc_cfg.get('cos_min', 0.95)) if use_embeddings else -1.0
        nearest_m = int(assoc_cfg.get('nearest_m_for_cos', 12))
        spawn_cap = int(assoc_cfg.get('spawn_max_per_cell_per_trigger', 2))

        # Precompute transforms
        T_cw: Optional[np.ndarray] = getattr(snap, 'pose_cam_T_world', None)
        if T_cw is None:
            # if caller supplied world->cam missing, try 'pose_world_T_cam' or identity
            T_wc = getattr(snap, 'pose_world_T_cam', None)
            if T_wc is None:
                T_cw = np.eye(4, dtype=np.float32)
                T_wc = np.eye(4, dtype=np.float32)
            else:
                T_wc = T_wc.astype(np.float32)
                T_cw = _invert_h(T_wc)
        else:
            T_cw = T_cw.astype(np.float32)
            T_wc = _invert_h(T_cw)

        # Debug: log T_cw and T_wc translations for comparison
        if not hasattr(self, '_assoc_pose_log_count'):
            self._assoc_pose_log_count = 0
        self._assoc_pose_log_count += 1
        if self._assoc_pose_log_count % 30 == 1:
            t_cw = T_cw[:3, 3]
            t_wc = T_wc[:3, 3]
            logger.debug(f"[assoc] T_cw (from pipeline): [{t_cw[0]:.4f}, {t_cw[1]:.4f}, {t_cw[2]:.4f}]")
            logger.debug(f"[assoc] T_wc (inverted back): [{t_wc[0]:.4f}, {t_wc[1]:.4f}, {t_wc[2]:.4f}]")

        # Validate transform: rotation matrix determinant should be ~1.0
        det = np.linalg.det(T_wc[:3, :3])
        if abs(det - 1.0) > 0.01:
            logger.warning(f"[assoc] T_wc rotation determinant={det:.4f}, expected ~1.0 (may cause position offset)")

        intr = getattr(snap, 'intrinsics', None) or {}
        fx = intr.get('fx', None)
        # We only do reprojection gate if intrinsics present
        have_intr = all(k in intr for k in ('fx', 'fy', 'cx', 'cy'))

        matched_count = 0
        created_count = 0
        best_id = None
        # process high-priority first (cands assumed pre-ranked); nothing enforces order here
        for c in cands:
            # require 3D centroid; embedding is optional if use_embeddings=False
            p_cam = getattr(c.stats, 'centroid_cam', None)
            e = getattr(c, 'emb_vis', None)
            if p_cam is None or (use_embeddings and e is None):
                continue

            # PATCH 20260503: capture candidate's top label for diagnostic logs
            _cand_topk = getattr(c, 'label_topk', None)
            top_cand_label = _cand_topk[0][0] if _cand_topk else '?'

            # world point: transform p_cam (camera frame) to world frame using T_wc
            pw = (T_wc @ np.append(p_cam.astype(np.float32), 1.0))[:3]

            # Diagnostic position logging (enable via assoc.debug_positions: true)
            if bool(assoc_cfg.get('debug_positions', False)):
                depth_v = float(getattr(c.stats, 'depth_valid', 0.0))
                label_info = getattr(c, 'label_topk', [])
                top_label = label_info[0][0] if label_info else '?'
                # Log camera position (T_wc translation = camera position in world)
                cam_pos = T_wc[:3, 3]
                logger.info(
                    f"[DIAG] cam_pos=[{cam_pos[0]:.3f},{cam_pos[1]:.3f},{cam_pos[2]:.3f}] "
                    f"p_cam=[{p_cam[0]:.3f},{p_cam[1]:.3f},{p_cam[2]:.3f}] "
                    f"-> p_world=[{pw[0]:.3f},{pw[1]:.3f},{pw[2]:.3f}] "
                    f"depth_valid={depth_v:.2f} label={top_label}"
                )

            # neighbor fetch with lazy prune
            cell = index.grid.cell(pw)
            cand_ids = index.nearby_ids(pw, rings=rings, prune_with=wm.exists)
            try:
                logger.debug(
                    "assoc qry: pw=%s cell=%s rings=%d nearby=%d",
                    pw.tolist(),
                    cell,
                    rings,
                    len(cand_ids),
                )
            except Exception:
                pass
            if not cand_ids:
                # PATCH 20260503: log empty-lookup case for diagnosis
                logger.info(
                    f"[assoc-empty-lookup] pw=[{pw[0]:.2f},{pw[1]:.2f},{pw[2]:.2f}] "
                    f"cell={cell} label={top_cand_label} rings={rings}"
                )
                # Optional fallback: scan all WM objects if index returns empty
                # Only fallback when WM has few objects (early exploration phase)
                if bool(assoc_cfg.get('fallback_all_when_empty', False)):
                    try:
                        all_ids = [o.id for o in wm.iter_objects()]
                        if len(all_ids) < 20:
                            logger.debug("assoc fallback: scanning all=%d", len(all_ids))
                            cand_ids = all_ids
                        # else: don't fallback, let it create new object
                    except Exception:
                        pass
                if not cand_ids:
                    best_id = None
            else:
                # Pre-gate by 3D/Z and (optionally) px reprojection, then keep nearest_m for cosine
                survivors: List[Tuple[str, float, float]] = []  # (oid, dist, pxerr)
                px_obs = getattr(c.stats, 'centroid_px', None)
                for oid in cand_ids:
                    o = wm.get(oid)
                    if o is None:
                        continue
                    dist = float(np.linalg.norm(pw - o.xyz_world))
                    if dist > gate_dist:
                        continue
                    if abs(float(pw[2] - o.xyz_world[2])) > gate_z:
                        continue
                    px_err = 0.0
                    if have_intr and px_obs is not None:
                        uv = _project_px(o.xyz_world, T_cw, intr)
                        if uv is None:
                            continue
                        px_err = _px_error(uv, (float(px_obs[0]), float(px_obs[1])))
                        if px_err > gate_px:
                            continue

                        try:
                            logger.debug(
                                "assoc debug: oid=%s pw=%s o.xyz=%s dist=%.3f px_err=%.1f",
                                oid,
                                pw.tolist(),
                                o.xyz_world.tolist(),
                                dist,
                                px_err,
                            )
                        except Exception:
                            pass

                    survivors.append((oid, dist, px_err))

                if not survivors:
                    best_id = None
                else:
                    # take nearest M by distance before cosine
                    survivors.sort(key=lambda t: t[1])
                    survivors = survivors[:max(1, nearest_m)]

                    alpha = float(assoc_cfg.get('score', {}).get('alpha_cos', 1.0))
                    if not use_embeddings:
                        alpha = 0.0
                    beta = float(assoc_cfg.get('score', {}).get('beta_dist', 1.0))
                    gamma = float(assoc_cfg.get('score', {}).get('gamma_reproj', 0.02))
                    delta_q = float(assoc_cfg.get('score', {}).get('delta_quality', 0.1))

                    quality = float(getattr(c.stats, 'depth_valid', 1.0))  # crude proxy
                    if use_embeddings and e is not None:
                        e = _ensure_l2(e)
                    best_id = None
                    best_score = -1e9
                    best_cos = 0.0
                    best_dist = 0.0

                    for oid, dist, px_err in survivors:
                        o = wm.get(oid)
                        if o is None:
                            continue
                        if use_embeddings and e is not None:
                            # PATCH 2026-05-13 (viewbin-aware-assoc):
                            # Compare against MAX cosine over all stored view-bin
                            # embeddings; fall back to emb_mean only if view_bins
                            # is empty. emb_mean is biased toward the most-observed
                            # angle so it falsely rejects valid new views.
                            # PATCH 2026-05-13 (gallery-aware-assoc):
                            # Match against the union of (a) emb_gallery (raw,
                            # diverse observations FIFO, capped at max_gallery=6,
                            # dedup'd at gallery_dupe_cos=0.995) and (b) view_bins
                            # (smoothed per-bin EMA). Either source can win;
                            # we take max cos. Gallery preserves viewpoint
                            # diversity that view_bins averages away, fixing
                            # the cardbox-cluster spawn-race at large viewpoint
                            # changes (~90 deg rotations drop view_bins cos to
                            # ~0.6-0.7 while gallery keeps a hit at >=0.85).
                            e32 = e.astype(np.float32)
                            match_gallery = bool(assoc_cfg.get('match_against_gallery', True))
                            gallery = getattr(o, 'emb_gallery', None)
                            bins = getattr(o, 'view_bins', None) or {}
                            refs = []  # list of (source_name, cos)
                            n_gallery = 0
                            n_bins = len(bins)
                            if match_gallery and gallery is not None and gallery.shape[0] > 0:
                                # Vectorized: one BLAS matmul over (N,D) @ (D,) -> (N,)
                                gallery_cos = float(np.max(gallery.astype(np.float32) @ e32))
                                refs.append(('gallery', gallery_cos))
                                n_gallery = int(gallery.shape[0])
                            if bins:
                                bin_cos = max(
                                    float(np.dot(e32, ref_emb.astype(np.float32)))
                                    for ref_emb in bins.values()
                                )
                                refs.append(('view_bins', bin_cos))
                            if not refs and o.emb_mean is not None:
                                refs.append(('emb_mean', float(np.dot(e32, o.emb_mean.astype(np.float32)))))
                            if not refs:
                                # No reference embeddings at all — skip cos gating
                                cos = 1.0
                                ref_source = 'no_refs'
                            else:
                                ref_source, cos = max(refs, key=lambda kv: kv[1])
                            if cos < cos_min:
                                # PATCH 20260503: log cosine rejection (extended 2026-05-13 with n_gallery)
                                existing_label = getattr(o, 'label_primary', None) or '?'
                                logger.info(
                                    f"[assoc-reject-cos] oid={oid[:8]} "
                                    f"cos={cos:.4f}<{cos_min:.3f} dist={dist:.3f} "
                                    f"label_cand={top_cand_label} label_existing={existing_label} "
                                    f"ref={ref_source} n_gallery={n_gallery} n_bins={n_bins}"
                                )
                                continue
                        else:
                            cos = 1.0  # neutral when embeddings disabled
                        score = alpha * cos - beta * dist - gamma * px_err + delta_q * quality
                        if score > best_score:
                            best_score = score
                            best_id = oid
                            best_cos = cos
                            best_dist = dist

            if best_id is not None:
                # matched → update WM
                assoc_update = AssocUpdate(
                    p_world=pw.astype(np.float32),
                    emb_vis=_ensure_l2(e),
                    view_dir_cam=(p_cam.astype(np.float32) / (np.linalg.norm(p_cam) + 1e-12)),
                    centroid_px=getattr(c.stats, 'centroid_px', None),
                    depth_valid=float(getattr(c.stats, 'depth_valid', 1.0)),
                    quality=float(getattr(c.stats, 'coverage', 1.0)),
                    cos_sim=best_cos,
                    dist_m=best_dist,
                    label_topk=getattr(c, 'label_topk', None),
                    crop=getattr(c, 'crop', None),
                    is_keyframe=is_keyframe,
                    frame_id=frame_id,
                )
                wm.update_object(best_id, assoc_update)
                wm.maybe_promote(best_id)
                matched_count += 1
                continue

            # no match → consider spawn (respect per-cell spawn cap)
            cell = index.grid.cell(pw)

            # PATCH 20260503: log spawn context BEFORE cap check
            nearest_hint = "no_nearby"
            if cand_ids:
                try:
                    best_nearby_oid = None
                    best_nearby_d = float('inf')
                    for _oid in cand_ids:
                        _o = wm.get(_oid)
                        if _o is None:
                            continue
                        _d = float(np.linalg.norm(pw - _o.xyz_world))
                        if _d < best_nearby_d:
                            best_nearby_d = _d
                            best_nearby_oid = _oid
                    if best_nearby_oid is not None:
                        _on = wm.get(best_nearby_oid)
                        _on_label = (getattr(_on, 'label_primary', None) or '?') if _on else '?'
                        nearest_hint = (
                            f"nearest={best_nearby_oid[:8]} d={best_nearby_d:.3f} "
                            f"label_nearest={_on_label}"
                        )
                except Exception:
                    pass
            logger.info(
                f"[assoc-spawn] pw=[{pw[0]:.2f},{pw[1]:.2f},{pw[2]:.2f}] "
                f"cell={cell} label={top_cand_label} n_cands={len(cand_ids)} {nearest_hint}"
            )

            if per_cell_spawn_counter is not None:
                count = per_cell_spawn_counter.get(cell, 0)
                if count >= spawn_cap:
                    # PATCH 20260503: log spawn-cap reject
                    logger.info(
                        f"[assoc-reject-cap] cell={cell} count={count}/{spawn_cap} "
                        f"label={top_cand_label}"
                    )
                    continue
                per_cell_spawn_counter[cell] = count + 1

            oid = wm.create_object(
                p_world=pw.astype(np.float32),
                emb_vis=_ensure_l2(e),
                label_topk=getattr(c, 'label_topk', None),
                view_dir_cam=(p_cam.astype(np.float32) / (np.linalg.norm(p_cam) + 1e-12)),
                centroid_px=getattr(c.stats, 'centroid_px', None),
                crop=getattr(c, 'crop', None),
                frame_id=frame_id,
            )
            # No promote here; will happen after subsequent matches
            if oid is not None:
                created_count += 1

        # End for each candidate
        return {"matched": matched_count, "created": created_count}
