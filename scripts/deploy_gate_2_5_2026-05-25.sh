#!/bin/bash
# Deploy Gate 2.5: embedding-based re-id — 2026-05-25
#
# Adds an embedding-similarity match step before proto spawn in
# Associator.update_with_candidates(). When spatial matching has failed,
# search all confirmed WM objects (filtered to same label_primary) for
# an emb_mean cosine match above tau (default 0.92). If found, the
# incoming observation updates that object's identity rather than
# spawning a new proto.
#
# Use cases:
#   - An object moved beyond the proximity ring (couch dragged 2m).
#   - A rehydrated object whose stored xyz is stale from a prior session
#     but whose appearance is still distinctive.
#
# Configurable via rtsm.yaml:
#   assoc:
#     gate_2_5_enabled: true        (default: true)
#     gate_2_5_tau: 0.92            (default: 0.92)
#     gate_2_5_same_label_only: true (default: true)
#
# Idempotent. Pre-flight backup.

set -euo pipefail

if [ ! -f rtsm/core/association.py ]; then
    echo "ERROR: run from repo root" >&2
    exit 1
fi
TS=$(date +%Y%m%d-%H%M%S)
ASSOC="rtsm/core/association.py"

echo "== Gate 2.5 deploy ($(date -Is)) =="

if grep -q "_gate_2_5_match" "$ASSOC"; then
    echo "  already patched; skipping"
    exit 0
fi

cp "$ASSOC" "$ASSOC.bak.$TS"
echo "  backup: $ASSOC.bak.$TS"

python3 <<'PYEOF'
import pathlib
p = pathlib.Path("rtsm/core/association.py")
src = p.read_text()

# Insert _gate_2_5_match method right after class Associator's __init__
method = '''class Associator:
    def __init__(self, cfg: Dict[str, Any]) -> None:
        self.cfg = cfg

    # ------------------------------------------------------------------
    # Gate 2.5: embedding-based re-id (2026-05-25)
    # ------------------------------------------------------------------
    # Fires when spatial matching has failed for a candidate. Searches all
    # confirmed WM objects (by default restricted to same label_primary)
    # for an emb_mean cosine match exceeding tau. If found, the incoming
    # observation is treated as a re-observation of that object rather
    # than a new proto.
    #
    # Use case: an object that moved beyond the proximity-index ring, or
    # a rehydrated object whose stored xyz is stale, can still be matched
    # back to its existing identity via appearance.
    #
    # Cost: O(N_confirmed) cosines per spatial-match failure. At ~hundreds
    # of confirmed objects with 768-dim embeddings, sub-millisecond.
    # ------------------------------------------------------------------
    def _gate_2_5_match(
        self,
        incoming_emb: np.ndarray,
        incoming_label: Optional[str],
        wm: Any,
    ) -> Optional[Tuple[str, float]]:
        """Search WM for an emb_mean cosine match above tau.

        Args:
            incoming_emb: candidate's visual embedding, must be L2-normalized
            incoming_label: candidate's top label
            wm: WorkingMemory-like (must support iter_objects())

        Returns:
            (matched_oid, cos_sim) if a confirmed object matches, else None.
        """
        assoc_cfg = self.cfg.get('assoc', {})
        if not bool(assoc_cfg.get('gate_2_5_enabled', True)):
            return None
        tau = float(assoc_cfg.get('gate_2_5_tau', 0.92))
        same_label_only = bool(assoc_cfg.get('gate_2_5_same_label_only', True))

        # Same-label filter requires both sides to have a label. The
        # prototype's empirical analysis showed cross-label maximum
        # similarity is typically well below tau=0.92 for SigLIP/CLIP
        # embeddings, but the filter is a robust safety net.
        if same_label_only and (incoming_label is None or incoming_label == '?'):
            return None

        best_oid: Optional[str] = None
        best_sim: float = -1.0

        for o in wm.iter_objects():
            if not getattr(o, 'confirmed', False):
                continue
            if o.emb_mean is None:
                continue
            if same_label_only:
                # display_label = label_user or label_primary; honor user pins.
                existing_label = (
                    getattr(o, 'label_user', None) or getattr(o, 'label_primary', None)
                )
                if existing_label is None or existing_label != incoming_label:
                    continue
            sim = float(np.dot(incoming_emb, o.emb_mean.astype(np.float32)))
            if sim > best_sim:
                best_sim = sim
                best_oid = o.id

        if best_oid is not None and best_sim >= tau:
            return (best_oid, best_sim)
        return None

'''

old_class = '''class Associator:
    def __init__(self, cfg: Dict[str, Any]) -> None:
        self.cfg = cfg

'''

if old_class not in src:
    raise SystemExit(
        "ERROR: Associator class anchor not found. Has it been refactored?"
    )
src2 = src.replace(old_class, method, 1)

# Insert the spawn-site call. Anchor is uniquely the spawn-context log
# block's leading comment.
spawn_anchor = '''            # no match → consider spawn (respect per-cell spawn cap)
            cell = index.grid.cell(pw)

            # PATCH 20260503: log spawn context BEFORE cap check'''

spawn_replacement = '''            # no match → consider spawn (respect per-cell spawn cap)
            cell = index.grid.cell(pw)

            # 2026-05-25: Gate 2.5 — embedding re-id of moved/lost objects.
            # Spatial matching failed. Before spawning a new proto, check if
            # this observation matches an existing confirmed object by
            # appearance alone. Use cases:
            #   - An object that physically moved beyond the proximity ring
            #     (e.g., couch dragged 2m, mug carried to another room).
            #   - A rehydrated object whose stored xyz is stale from a prior
            #     session but whose appearance is still distinctive.
            # The candidate's identity is updated rather than duplicated.
            g25_match = self._gate_2_5_match(
                incoming_emb=_ensure_l2(e),
                incoming_label=top_cand_label,
                wm=wm,
            )
            if g25_match is not None:
                matched_oid, g25_sim = g25_match
                o_match = wm.get(matched_oid)
                old_xyz = (
                    o_match.xyz_world.copy()
                    if o_match is not None and o_match.xyz_world is not None
                    else None
                )
                assoc_update = AssocUpdate(
                    p_world=pw.astype(np.float32),
                    emb_vis=_ensure_l2(e),
                    view_dir_cam=(p_cam.astype(np.float32) / (np.linalg.norm(p_cam) + 1e-12)),
                    centroid_px=getattr(c.stats, 'centroid_px', None),
                    depth_valid=float(getattr(c.stats, 'depth_valid', 1.0)),
                    quality=float(getattr(c.stats, 'coverage', 1.0)),
                    cos_sim=g25_sim,
                    dist_m=0.0,  # spatial gating was bypassed; no meaningful distance
                    label_topk=getattr(c, 'label_topk', None),
                    crop=getattr(c, 'crop', None),
                    is_keyframe=is_keyframe,
                    frame_id=frame_id,
                )
                wm.update_object(matched_oid, assoc_update)
                shift_m = (
                    float(np.linalg.norm(pw - old_xyz)) if old_xyz is not None else -1.0
                )
                logger.info(
                    f"[assoc-g25] re-id oid={matched_oid[:8]} "
                    f"label={top_cand_label} cos={g25_sim:.4f} "
                    f"xyz_shift={shift_m:.2f}m cell={cell}"
                )
                matched_count += 1
                continue

            # PATCH 20260503: log spawn context BEFORE cap check'''

if spawn_anchor not in src2:
    raise SystemExit(
        "ERROR: spawn-site anchor not found. Has the spawn block been refactored?"
    )
src3 = src2.replace(spawn_anchor, spawn_replacement, 1)

if src3 == src:
    raise SystemExit("ERROR: no changes made")

p.write_text(src3)
print("  ok: both insertions applied")
PYEOF

python3 -c "import ast; ast.parse(open('$ASSOC').read()); print('  syntax-ok')"
echo "== done =="
echo ""
echo "Restart RTSM to load the new association path:"
echo "  docker compose -f docker/docker-compose.yml restart rtsm-dev"
echo ""
echo "Optionally tune via rtsm.yaml (defaults are sensible):"
echo "  assoc:"
echo "    gate_2_5_enabled: true"
echo "    gate_2_5_tau: 0.92"
echo "    gate_2_5_same_label_only: true"
echo ""
echo "Watch for re-id events in the log:"
echo "  docker exec rtsm-dev tail -f /tmp/rtsm.log | grep assoc-g25"
