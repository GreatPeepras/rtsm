#!/usr/bin/env bash
# deploy_suggest_merges_2026-06-02.sh
#
# Adds POST /objects/suggest_merges to RTSM:
#   - WorkingMemory.suggest_merges()   : read-only sweep over confirmed
#                                        objects for high-cosine + co-located
#                                        pairs; surfaces Mode B duplicate
#                                        candidates for human review.
#   - SuggestMergesRequest body model  : conservative defaults
#                                        (cos>=0.95, dist<=1.0m)
#   - POST /objects/suggest_merges     : thin wrapper around the WM method
#
# Read-only: does NOT call merge_objects. Caller reviews each candidate
# via /objects/{oid}/snapshots and explicitly POSTs /objects/merge to
# consolidate.
#
# Idempotent. Safe to re-run; will skip insertions already present.
# Validates syntax (ast.parse + py_compile) of both modified files
# before committing changes. Backs up first.

set -euo pipefail

RTSM_ROOT="${RTSM_ROOT:-$HOME/rtsm}"
WM_PATH="$RTSM_ROOT/rtsm/stores/working_memory.py"
SRV_PATH="$RTSM_ROOT/rtsm/api/server.py"

TS="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
WM_BAK="${WM_PATH}.bak.${TS}"
SRV_BAK="${SRV_PATH}.bak.${TS}"

echo "[deploy] rtsm root: $RTSM_ROOT"
echo "[deploy] timestamp: $TS"

[[ -f "$WM_PATH" ]]  || { echo "ERROR: $WM_PATH not found"; exit 1; }
[[ -f "$SRV_PATH" ]] || { echo "ERROR: $SRV_PATH not found"; exit 1; }

cp "$WM_PATH"  "$WM_BAK"
cp "$SRV_PATH" "$SRV_BAK"
echo "[deploy] backups:"
echo "  $WM_BAK"
echo "  $SRV_BAK"

export WM_PATH SRV_PATH

python3 - <<'PYEOF'
import ast
import os
import sys

WM_PATH  = os.environ["WM_PATH"]
SRV_PATH = os.environ["SRV_PATH"]

# ---------------------------------------------------------------------------
# 1. WorkingMemory.suggest_merges (+ helper _suggest_merge_winner)
# ---------------------------------------------------------------------------

WM_METHOD = '''
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
'''

# Insertion point: right before `def iter_objects` in WorkingMemory.
WM_ANCHOR = "    def iter_objects(self) -> Iterable[ObjectState]:"

with open(WM_PATH, "r") as f:
    wm_src = f.read()

if "def suggest_merges(" in wm_src:
    print("[deploy] WM: suggest_merges already present, skipping")
else:
    cnt = wm_src.count(WM_ANCHOR)
    if cnt != 1:
        print(f"ERROR: WM anchor 'def iter_objects' found {cnt} times "
              f"(expected 1); aborting")
        sys.exit(2)
    wm_new = wm_src.replace(
        WM_ANCHOR,
        WM_METHOD.lstrip("\n") + "\n" + WM_ANCHOR,
        1,
    )
    try:
        ast.parse(wm_new)
    except SyntaxError as e:
        print(f"ERROR: WM patched source has SyntaxError: {e}")
        sys.exit(2)
    with open(WM_PATH, "w") as f:
        f.write(wm_new)
    print("[deploy] WM: inserted suggest_merges method")

# ---------------------------------------------------------------------------
# 2. server.py: SuggestMergesRequest body model
# ---------------------------------------------------------------------------

SERVER_MODEL = '''
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


'''

SRV_MODEL_ANCHOR = "# 2026-05-29: reference-snapshot endpoint schemas."

with open(SRV_PATH, "r") as f:
    srv_src = f.read()

if "class SuggestMergesRequest(BaseModel)" in srv_src:
    print("[deploy] server: SuggestMergesRequest already present, skipping")
else:
    cnt = srv_src.count(SRV_MODEL_ANCHOR)
    if cnt != 1:
        print(f"ERROR: server model anchor found {cnt} times "
              f"(expected 1); aborting")
        sys.exit(2)
    srv_src = srv_src.replace(
        SRV_MODEL_ANCHOR,
        SERVER_MODEL.lstrip("\n") + SRV_MODEL_ANCHOR,
        1,
    )
    print("[deploy] server: inserted SuggestMergesRequest model")

# ---------------------------------------------------------------------------
# 3. server.py: /objects/suggest_merges endpoint
# ---------------------------------------------------------------------------

SERVER_ENDPOINT = '''
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

'''

SRV_ENDPOINT_ANCHOR = "    # ---- 2026-05-29: reference snapshot endpoints ----"

if "def suggest_merges_endpoint(" in srv_src:
    print("[deploy] server: suggest_merges_endpoint already present, skipping")
else:
    cnt = srv_src.count(SRV_ENDPOINT_ANCHOR)
    if cnt != 1:
        print(f"ERROR: server endpoint anchor found {cnt} times "
              f"(expected 1); aborting")
        sys.exit(2)
    srv_src = srv_src.replace(
        SRV_ENDPOINT_ANCHOR,
        SERVER_ENDPOINT.lstrip("\n") + SRV_ENDPOINT_ANCHOR,
        1,
    )
    print("[deploy] server: inserted suggest_merges_endpoint")

# Validate server.py syntax before committing.
try:
    ast.parse(srv_src)
except SyntaxError as e:
    print(f"ERROR: server patched source has SyntaxError: {e}")
    sys.exit(2)

with open(SRV_PATH, "w") as f:
    f.write(srv_src)

print("[deploy] all patches applied + ast-validated")
PYEOF

# Belt-and-braces: full byte-compile pass on both files.
python3 -m py_compile "$WM_PATH"  && echo "[deploy] py_compile OK: working_memory.py"
python3 -m py_compile "$SRV_PATH" && echo "[deploy] py_compile OK: server.py"

cat <<'POSTAMBLE'

[deploy] done.

Next steps:

  1. Restart the rtsm-dev container to pick up changes:

       cd ~/rtsm/docker && docker compose restart rtsm-dev

  2. Sanity check the endpoint:

       curl -s -X POST http://localhost:8002/objects/suggest_merges \
            -H 'Content-Type: application/json' \
            -d '{"cos_threshold": 0.95, "dist_threshold_m": 1.0, "limit": 10}' \
            | jq '{returned, total_pairs_above_thresholds, scanned_objects,
                   thresholds, top: .candidates[0]}'

     Expected: scanned_objects = 230 (current corpus), some number of
     candidates returned. With these thresholds you should see the
     remaining tight Mode B clusters (chairs, etc).

  3. Try same-label-only for a tighter pass:

       curl -s -X POST http://localhost:8002/objects/suggest_merges \
            -H 'Content-Type: application/json' \
            -d '{"cos_threshold": 0.92, "dist_threshold_m": 1.5,
                 "require_same_label": true, "limit": 20}' \
            | jq '.candidates[] | {a_oid, b_oid, suggested_winner_oid,
                                    cosine, distance_m, a_display_label}'

  4. For each candidate that looks right after eyeballing
     /objects/{oid}/snapshots, merge with the existing endpoint:

       curl -s -X POST http://localhost:8002/objects/merge \
            -H 'Content-Type: application/json' \
            -d '{"winner_oid": "<WINNER>", "loser_oid": "<LOSER>"}'

  5. Run the unit tests:

       docker exec -it rtsm-dev pytest tests/test_suggest_merges.py -v

To roll back, restore from the .bak files written above.

POSTAMBLE
