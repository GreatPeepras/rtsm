#!/usr/bin/env bash
#
# deploy_search_user_label_boost_2026-06-03.sh
#
# Patches /search/semantic in rtsm/api/server.py to surface user_label
# matches as first-class results alongside the existing CLIP visual
# similarity ranking.
#
# What changes:
#   - Adds a "Stage 0" pre-pass that scans WM for label_user matches
#     against the query. Exact (case-insensitive) -> synthetic score
#     1.0. Substring -> 0.9.
#   - User-label hits are merged with FAISS visual matches, dedup'd by
#     oid (user-label wins), sorted by score desc, truncated to top_k.
#   - Each result now includes:
#       match_type    : "user_label_exact" | "user_label_partial" | "visual_similarity"
#       label_user    : the user-assigned label, or null
#       label_primary : the model's top-confidence label, or null
#     The existing `label` field (gated display label) is unchanged.
#
# Why:
#   - 2026-06-03 debug session showed that semantic search for "bed"
#     returned 10 unrelated objects and *not* the actually-labeled bed
#     (oid 2f797dd53bca40a0). Averaged emb_mean over 897 frames is too
#     diluted to rank near "bed" text embedding, while under-observed
#     objects with 2-3 hits happen to score higher by accident.
#   - User-named objects are the canonical truth for navigation
#     (goto_object uses by_label_user exclusively). Semantic search
#     should respect that, not bury it under visual noise.
#
# Idempotent: detects existing 'Stage 0: user-label matches' marker.
# Backup: server.py.bak.<TIMESTAMP> next to the source.
# Validation: ast.parse on the edited file. Aborts on syntax error
# and restores from backup.
#
# Restart: triggers `docker compose restart rtsm-dev` so the
# uvicorn workers pick up the change.
#
# Rollback: cp the .bak.<TIMESTAMP> file back over server.py and
# restart rtsm-dev. Rollback line is printed at end of run.
#
set -euo pipefail

RTSM_REPO="${RTSM_REPO:-$HOME/rtsm}"
SERVER_PY="$RTSM_REPO/rtsm/api/server.py"
COMPOSE_DIR="$RTSM_REPO/docker"
TS="$(date +%Y%m%d_%H%M%S)"
BACKUP="${SERVER_PY}.bak.${TS}"
SENTINEL="Stage 0: user-label matches"

# ---- Pre-flight ----------------------------------------------------------

if [[ ! -f "$SERVER_PY" ]]; then
    echo "ERROR: $SERVER_PY not found. Set RTSM_REPO env var if your repo is elsewhere." >&2
    exit 1
fi

if [[ ! -d "$COMPOSE_DIR" ]]; then
    echo "WARNING: $COMPOSE_DIR not found; will skip the docker restart step." >&2
fi

if grep -q "$SENTINEL" "$SERVER_PY"; then
    echo "Already patched (found '${SENTINEL}' marker in $SERVER_PY). Nothing to do."
    exit 0
fi

cp "$SERVER_PY" "$BACKUP"
echo "Backup saved: $BACKUP"

# ---- Apply the edit via python (textual replace of the whole function) ----

python3 - "$SERVER_PY" <<'PYEOF'
import sys, ast
from pathlib import Path

path = Path(sys.argv[1])
src = path.read_text()

# The exact current function block. We anchor on the @app.get + def
# line and the closing return-dict signature. Both must match exactly
# for the replace to succeed; otherwise we fail loudly and leave the
# source file untouched.
OLD = '''    @app.get("/search/semantic")
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
'''

NEW_SIG_DOCSTRING = '''    @app.get("/search/semantic")
    def semantic_search(
        query: str,
        top_k: int = 10,
        threshold: float = 0.0,
        include_snapshot: bool = False,
        pose_state: str = "on_floor",   # "on_floor" | "elevated" | "any"
    ) -> Dict[str, Any]:

        """
        Semantic search for objects.

        Two-stage ranking:
          1. User-label matches (label_user equal-or-substring of query)
             returned first with synthetic scores (1.0 exact, 0.9 partial).
             Surfaces human-named objects reliably regardless of visual
             embedding similarity. label_user is the canonical truth used
             by goto_object; semantic search should respect that.
          2. Visual similarity via CLIP text encoding + FAISS KNN, with
             the same per-result enrichment as before.

        Results are merged (dedup by oid; user-label entries win),
        sorted by score desc, then truncated to top_k.

        Each result includes a `match_type` field:
          - "user_label_exact"   - label_user == query (case-insensitive)
          - "user_label_partial" - query is substring of label_user
          - "visual_similarity"  - CLIP visual embedding match

        Cosine scores vary by model: CLIP ViT-B/32 clusters 0.25-0.35,
        SigLIP ViT-B-16 clusters 0.05-0.15 for indoor objects. Default
        threshold=0.0 returns all ranked visual results so agents can
        decide their own cutoff. User-label hits ignore `threshold`.

        Args:
            query: Natural language search query (e.g., "red cup", "bed")
            top_k: Maximum number of results to return (after merge)
            threshold: Minimum visual-similarity score; user-label hits bypass
            include_snapshot: If true, include base64 JPEG of most recent crop
            pose_state: Filter by pose_state_at_observation (default "on_floor")
        """
'''

# Replace just the signature + docstring; the rest of the function will
# be rewritten by a second targeted replace below. Splitting it in two
# keeps each old-string anchor small enough to be unambiguous.

if OLD not in src:
    print("ERROR: could not locate the signature/docstring block of semantic_search.", file=sys.stderr)
    print("       The source may have already been edited or diverges from the audited version.", file=sys.stderr)
    sys.exit(2)

src = src.replace(OLD, NEW_SIG_DOCSTRING, 1)

# Now replace the function body. Anchor: from "if not clip_adapter"
# down to and including the final return dict immediately before the
# spatial-search endpoint decorator.

OLD_BODY = '''        if not clip_adapter or not vectors:
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
'''

NEW_BODY_HEAD = '''        if not clip_adapter or not vectors:
            raise HTTPException(status_code=503, detail="Semantic search not available (CLIP or vectors not configured)")

        # --- Stage 0: user-label matches (always win) ---
        # 2026-06-03: surface label_user matches in semantic results.
        # Without this, a human-named object never appears for a query
        # matching its name unless its averaged visual embedding also
        # ranks near the top -- which it usually doesn't for well-observed
        # objects whose emb_mean has been diluted across many views.
        user_label_hits: Dict[str, tuple] = {}  # oid -> (synthetic_score, match_type)
        q_lower = (query or "").strip().lower()
        if q_lower:
            try:
                for o in working_memory.iter_objects():
                    lu = getattr(o, "label_user", None)
                    if not lu:
                        continue
                    lu_l = lu.lower()
                    if lu_l == q_lower:
                        user_label_hits[getattr(o, "id", None)] = (1.0, "user_label_exact")
                    elif q_lower in lu_l:
                        oid_ = getattr(o, "id", None)
                        if oid_ is not None and oid_ not in user_label_hits:
                            user_label_hits[oid_] = (0.9, "user_label_partial")
            except Exception:
                # Fail open: pure visual fallback if WM iteration breaks.
                user_label_hits = {}

        # --- Stage 1: encode query text with CLIP ---
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

        # --- Stage 2: FAISS KNN ---
        # Request extra so user-label dedup doesn't shrink the visual list.
        knn_k = int(top_k) + len(user_label_hits)
        try:
            matches = vectors.search(query_emb, top_k=knn_k)  # [(oid, score), ...]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Vector search failed: {e}")
        # Drop visual matches already covered by user-label hits.
        matches = [(oid, sc) for oid, sc in matches if oid not in user_label_hits]
'''

if OLD_BODY not in src:
    print("ERROR: could not locate the head-of-body block of semantic_search.", file=sys.stderr)
    sys.exit(3)
src = src.replace(OLD_BODY, NEW_BODY_HEAD, 1)

# Replace the per-result loop preamble to iterate the merged list. We
# anchor on the existing comment "# 3. Filter by threshold and enrich
# with WM metadata" through "for oid, score in matches:". The replacement
# changes the loop variable signature to include match_type.

OLD_LOOP_HEAD = '''        # 3. Filter by threshold and enrich with WM metadata, falling back
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
'''

NEW_LOOP_HEAD = '''        # --- Stage 3: build combined candidate list ---
        # User-label hits first (always pass; threshold doesn't apply).
        # Visual matches second (threshold-gated). Each entry carries a
        # match_type tag so the WebUI / agent can distinguish provenance.
        combined: List[tuple] = []
        for _oid, (_sc, _mtype) in user_label_hits.items():
            if _oid is None:
                continue
            combined.append((_oid, float(_sc), _mtype))
        for _oid, _sc in matches:
            if _sc < threshold:
                continue
            combined.append((_oid, float(_sc), "visual_similarity"))

        # --- Stage 4: enrich each entry ---
        # 2026-05-26 Gate 3: compute robot_pose / robot_xyz once and reuse
        # for distance_from_robot on every result. None-safe; if robot pose
        # isn't published the per-result distance just becomes None and the
        # Albert bridge degrades to "distance unknown".
        robot_pose = working_memory.get_robot_pose()
        robot_xyz = _robot_xyz(robot_pose)
        results = []
        for oid, score, match_type in combined:
'''

if OLD_LOOP_HEAD not in src:
    print("ERROR: could not locate the loop-head block of semantic_search.", file=sys.stderr)
    sys.exit(4)
src = src.replace(OLD_LOOP_HEAD, NEW_LOOP_HEAD, 1)

# Replace the entry-dict construction to include label_user, label_primary,
# and match_type. Anchor on the existing entry literal (small but unique).

OLD_ENTRY = '''            if obj is not None:
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
'''

NEW_ENTRY = '''            if obj is not None:
                label_v = _display_label(obj)
                label_user_v = getattr(obj, "label_user", None)
                label_primary_v = getattr(obj, "label_primary", None)
                last_seen_v = _iso_from_wall_utc(
                    getattr(obj, "last_seen_wall_utc", 0.0)
                )
            elif source == "faiss_meta" and meta is not None:
                label_v = (meta.get("label")
                           or meta.get("label_user")
                           or meta.get("label_primary"))
                label_user_v = meta.get("label_user")
                label_primary_v = meta.get("label_primary")
                last_seen_v = _iso_from_wall_utc(meta.get("last_seen_wall_utc"))
            else:
                label_v = None
                label_user_v = None
                label_primary_v = None
                last_seen_v = None

            entry: Dict[str, Any] = {
                "id": oid,
                "score": round(float(score), 4),
                # 2026-06-03 search-boost additions:
                "match_type": match_type,
                "label_user": label_user_v,
                "label_primary": label_primary_v,
                # ---
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
'''

if OLD_ENTRY not in src:
    print("ERROR: could not locate the entry-dict block of semantic_search.", file=sys.stderr)
    sys.exit(5)
src = src.replace(OLD_ENTRY, NEW_ENTRY, 1)

# Also ensure meta is initialized to None in the WM-hit branch so the
# faiss_meta fallback inside the label block doesn't reference an
# undefined name. Anchor on the existing branch.

OLD_META_INIT = '''            obj = working_memory.get(oid)
            if obj is not None:
                source = "wm"
                confirmed_v = obj.confirmed
                stability_v = round(float(obj.stability), 3)
                xyz = obj.xyz_world
                xyz_v = xyz.tolist() if xyz is not None else None
            else:
                meta = None
                get_meta = getattr(vectors, "get_metadata", None)
'''

NEW_META_INIT = '''            obj = working_memory.get(oid)
            meta = None
            if obj is not None:
                source = "wm"
                confirmed_v = obj.confirmed
                stability_v = round(float(obj.stability), 3)
                xyz = obj.xyz_world
                xyz_v = xyz.tolist() if xyz is not None else None
            else:
                get_meta = getattr(vectors, "get_metadata", None)
'''

if OLD_META_INIT not in src:
    print("ERROR: could not locate the meta-init block of semantic_search.", file=sys.stderr)
    sys.exit(6)
src = src.replace(OLD_META_INIT, NEW_META_INIT, 1)

# Replace the final return so it sorts and truncates after merge.

OLD_RETURN = '''            results.append(entry)

        return {
            "query": query,
            "robot_pose": robot_pose,
            "results": results,
        }
'''

NEW_RETURN = '''            results.append(entry)

        # --- Stage 5: sort by score desc, truncate to top_k ---
        results.sort(key=lambda r: -float(r.get("score") or 0.0))
        results = results[:int(top_k)]

        return {
            "query": query,
            "robot_pose": robot_pose,
            "results": results,
        }
'''

if OLD_RETURN not in src:
    print("ERROR: could not locate the return-block of semantic_search.", file=sys.stderr)
    sys.exit(7)
src = src.replace(OLD_RETURN, NEW_RETURN, 1)

# Validate with ast.parse before writing.
try:
    ast.parse(src)
except SyntaxError as e:
    print(f"ERROR: ast.parse failed after edit: {e}", file=sys.stderr)
    sys.exit(8)

path.write_text(src)
print("ast.parse OK; server.py written.")
PYEOF

# ---- Post-edit checks ----------------------------------------------------

echo
echo "Verifying sentinel landed:"
if grep -q "$SENTINEL" "$SERVER_PY"; then
    echo "  found '$SENTINEL'"
else
    echo "  MISSING. Restoring backup."
    cp "$BACKUP" "$SERVER_PY"
    exit 9
fi

echo
echo "Verifying py_compile:"
python3 -m py_compile "$SERVER_PY" && echo "  OK"

# ---- Restart rtsm-dev ----------------------------------------------------

if [[ -d "$COMPOSE_DIR" ]]; then
    echo
    echo "Restarting rtsm-dev container..."
    (cd "$COMPOSE_DIR" && docker compose restart rtsm-dev)
    echo "  done."
else
    echo
    echo "Skipping container restart (compose dir not found)."
fi

# ---- Smoke test ---------------------------------------------------------

echo
echo "Waiting 8s for uvicorn to come back up..."
sleep 8

echo "Smoke test: /search/semantic?query=bed&top_k=5"
curl -s 'http://192.168.0.53:8002/search/semantic?query=bed&top_k=5' \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'  query={d.get(\"query\")!r}, results={len(d.get(\"results\", []))}')
for i, r in enumerate(d.get('results', [])[:5], 1):
    print(f'  [{i}] score={r.get(\"score\")} match_type={r.get(\"match_type\")} '
          f'label_user={r.get(\"label_user\")!r} label_primary={r.get(\"label_primary\")!r} '
          f'id={r.get(\"id\","")[:12]}')
" || echo "  (smoke test failed; check logs)"

echo
echo "Done."
echo
echo "Rollback (if needed):"
echo "  cp '$BACKUP' '$SERVER_PY'"
echo "  (cd '$COMPOSE_DIR' && docker compose restart rtsm-dev)"
