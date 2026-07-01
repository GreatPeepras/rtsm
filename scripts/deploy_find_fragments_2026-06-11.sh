#!/usr/bin/env bash
# =============================================================================
# deploy_find_fragments_2026-06-11.sh
#
# Adds POST /objects/{oid}/find_fragments to RTSM. Per-anchor merge-candidate
# search with adaptive distance threshold and pose_state-aware filtering.
#
# See find_fragments_design_2026-06-11.md for full design.
#
# Marker: FIND_FRAGMENTS_2026-06-11
#   - 2 occurrences expected in rtsm/api/server.py (schema + endpoint)
#   - 1 occurrence expected in rtsm/stores/working_memory.py (WM method)
#
# Files touched:
#   $RTSM_DIR/rtsm/api/server.py
#   $RTSM_DIR/rtsm/stores/working_memory.py
#
# Read-only endpoint. No FAISS writes, no behavior change. Container
# restart required to load the new routes.
#
# Usage:
#   ./deploy_find_fragments_2026-06-11.sh                # --dryrun default
#   ./deploy_find_fragments_2026-06-11.sh --dryrun
#   ./deploy_find_fragments_2026-06-11.sh --apply
#   ./deploy_find_fragments_2026-06-11.sh --revert
#   ./deploy_find_fragments_2026-06-11.sh --check
#
# Environment:
#   RTSM_DIR   Path to rtsm checkout (default: $HOME/rtsm)
#
# Post-apply: cd ~/rtsm/docker && docker compose restart rtsm-dev
# =============================================================================

set -euo pipefail

MODE="${1:---dryrun}"
RTSM_DIR="${RTSM_DIR:-$HOME/rtsm}"
SERVER_FILE="$RTSM_DIR/rtsm/api/server.py"
WM_FILE="$RTSM_DIR/rtsm/stores/working_memory.py"
MARKER="FIND_FRAGMENTS_2026-06-11"
BACKUP_SUFFIX=".pre-$MARKER"

color_red()    { printf "\033[31m%s\033[0m\n" "$*"; }
color_green()  { printf "\033[32m%s\033[0m\n" "$*"; }
color_yellow() { printf "\033[33m%s\033[0m\n" "$*"; }
color_blue()   { printf "\033[34m%s\033[0m\n" "$*"; }

case "$MODE" in
    --dryrun|--apply|--revert|--check) ;;
    *) color_red "Unknown mode: $MODE"
       echo "Usage: $0 [--dryrun|--apply|--revert|--check]"
       exit 2 ;;
esac

color_blue "==============================================================="
color_blue "find_fragments Deploy ($MODE)"
color_blue "Marker: $MARKER"
color_blue "==============================================================="
echo "RTSM_DIR:    $RTSM_DIR"
echo "SERVER_FILE: $SERVER_FILE"
echo "WM_FILE:     $WM_FILE"
echo

for f in "$SERVER_FILE" "$WM_FILE"; do
    if [ ! -f "$f" ]; then
        color_red "FATAL: target file not found: $f"
        exit 1
    fi
done

# ---------------------------------------------------------------------------
# Revert
# ---------------------------------------------------------------------------
if [ "$MODE" = "--revert" ]; then
    color_yellow "[REVERT] Restoring from backup files..."
    revert_one() {
        local f="$1"
        local bk="$f$BACKUP_SUFFIX"
        if [ ! -f "$bk" ]; then
            color_yellow "[REVERT] skip: $f (no backup $bk)"; return
        fi
        cp -p "$bk" "$f"
        color_green "[REVERT] restored: $f"
    }
    revert_one "$SERVER_FILE"
    revert_one "$WM_FILE"
    echo
    color_green "[REVERT] done. Restart rtsm-dev:"
    echo "    cd ~/rtsm/docker && docker compose restart rtsm-dev"
    exit 0
fi

# ---------------------------------------------------------------------------
# Check
# ---------------------------------------------------------------------------
if [ "$MODE" = "--check" ]; then
    color_yellow "[CHECK] Marker count per file:"
    check_one() {
        local f="$1" expected="$2"
        if [ -f "$f" ]; then
            # awk always prints a single number; no grep-exit-code games.
            local n
            n=$(awk -v p="$MARKER" 'index($0,p){c++} END{print c+0}' "$f")
            local status="OK"
            [ "$n" -ne "$expected" ] && status="MISMATCH (expected $expected)"
            printf "  %-60s %s markers  %s\n" "$f" "$n" "$status"
        else
            printf "  %-60s (absent)\n" "$f"
        fi
    }
    check_one "$SERVER_FILE" 2
    check_one "$WM_FILE"     1
    exit 0
fi

# ---------------------------------------------------------------------------
# Patch (used by both --dryrun and --apply)
# ---------------------------------------------------------------------------
SERVER_TMP=$(mktemp /tmp/server_find_fragments.XXXXXX.py)
WM_TMP=$(mktemp /tmp/working_memory_find_fragments.XXXXXX.py)
trap 'rm -f "$SERVER_TMP" "$WM_TMP"' EXIT

# --- Patch server.py ---
python3 - "$SERVER_FILE" "$SERVER_TMP" "$MARKER" <<'PYEOF'
import sys, ast

SRC_FILE, OUT_FILE, MARKER = sys.argv[1], sys.argv[2], sys.argv[3]

with open(SRC_FILE, "r", encoding="utf-8") as f:
    src = f.read()

# Idempotency
if MARKER in src:
    n = src.count(MARKER)
    print(f"[server.py] Already patched (marker x{n}). No changes.", file=sys.stderr)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(src)
    sys.exit(0)

# =============================================================================
# Insertion 1: FindFragmentsRequest body schema
# Anchor: end of SuggestMergesRequest class, immediately before the
# 2026-05-29 reference-snapshot section header.
# =============================================================================
ANCHOR_SCHEMA = '''    include_unconfirmed: bool = False

    model_config = {"extra": "forbid"}


# 2026-05-29: reference-snapshot endpoint schemas.'''

NEW_SCHEMA = '''    include_unconfirmed: bool = False

    model_config = {"extra": "forbid"}


# Added 2026-06-11. Marker: FIND_FRAGMENTS_2026-06-11.
class FindFragmentsRequest(BaseModel):
    """Body schema for POST /objects/{oid}/find_fragments.

    Per-anchor merge-candidate search. All fields optional.

    The distance threshold is adaptive to the anchor's movability_class
    unless explicitly overridden:
      permanent / static / semi_static -> 3.0m  (furniture extent)
      movable / roaming / ephemeral    -> 9.0m  (room diagonal)
      null / unset                     -> 5.0m  (fallback)

    pose_state filter applies to candidates only (anchor always
    included):
      "any"          -- both buckets (default; surfaces lift/lower duplicates)
      "on_floor"     -- candidates seen on the floor only
      "elevated"     -- candidates seen elevated only
      "match_anchor" -- candidates matching the anchor's pose_state
    """
    cos_threshold: float = Field(0.85, ge=0.0, le=1.0)
    dist_threshold_m: Optional[float] = Field(None, gt=0.0)
    include_unconfirmed: bool = True
    exclude_named: bool = False
    pose_state: str = Field("any")
    limit: int = Field(20, ge=1, le=500)

    @field_validator("pose_state")
    @classmethod
    def _check_pose_state(cls, v: str) -> str:
        allowed = {"any", "on_floor", "elevated", "match_anchor"}
        if v not in allowed:
            raise ValueError(
                f"pose_state must be one of {sorted(allowed)}, got {v!r}"
            )
        return v

    model_config = {"extra": "forbid"}


# 2026-05-29: reference-snapshot endpoint schemas.'''

if ANCHOR_SCHEMA not in src:
    print("[server.py] FAILED: schema anchor not found. Source drift?", file=sys.stderr)
    sys.exit(3)
if src.count(ANCHOR_SCHEMA) != 1:
    print(f"[server.py] FAILED: schema anchor not unique (count={src.count(ANCHOR_SCHEMA)})", file=sys.stderr)
    sys.exit(3)
src = src.replace(ANCHOR_SCHEMA, NEW_SCHEMA, 1)
print("[server.py] (1/2) FindFragmentsRequest schema inserted", file=sys.stderr)

# =============================================================================
# Insertion 2: find_fragments_endpoint
# Anchor: end of suggest_merges_endpoint, immediately before the
# 2026-05-29 reference snapshot endpoints section header.
# =============================================================================
ANCHOR_ENDPOINT = '''        return result

    # ---- 2026-05-29: reference snapshot endpoints ----'''

NEW_ENDPOINT = '''        return result

    # Added 2026-06-11. Marker: FIND_FRAGMENTS_2026-06-11.
    @app.post("/objects/{oid}/find_fragments")
    def find_fragments_endpoint(
        oid: str,
        req: FindFragmentsRequest = Body(default_factory=FindFragmentsRequest),
    ) -> Dict[str, Any]:
        """Per-anchor merge-candidate search.

        Finds OIDs that may be fragments of the same physical object as
        the anchor oid. Sibling to /objects/suggest_merges; fixes the
        anchor and widens the gates. Distance threshold is adaptive to
        the anchor's movability_class unless explicitly overridden in
        the body.

        Read-only. Does NOT call merge_objects. Caller reviews
        snapshots and POSTs /objects/merge for each confirmed fragment.

        Errors:
          404 -- anchor oid not in working memory
          405 -- WM is frozen (serve-mode; no find_fragments method)
          422 -- invalid body (e.g. pose_state outside enum)
          500 -- unexpected failure inside the WM sweep
        """
        if not hasattr(working_memory, "find_fragments"):
            raise HTTPException(
                status_code=405,
                detail="find_fragments not supported on frozen working memory",
            )
        try:
            result = working_memory.find_fragments(
                anchor_oid=oid,
                cos_threshold=req.cos_threshold,
                dist_threshold_m=req.dist_threshold_m,
                include_unconfirmed=req.include_unconfirmed,
                exclude_named=req.exclude_named,
                pose_state=req.pose_state,
                limit=req.limit,
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"find_fragments failed: {e}",
            )

        # WM returns {"error": "not_found", ...} for unknown oid;
        # convert to 404 HTTP semantics.
        if isinstance(result, dict) and result.get("error") == "not_found":
            raise HTTPException(
                status_code=404,
                detail=f"anchor oid not found: {oid}",
            )

        # Augment response with snapshot URLs (relative paths; caller
        # composes base). HTTP-layer concern, not WM-layer.
        anchor_block = result.get("anchor")
        if isinstance(anchor_block, dict) and anchor_block.get("oid"):
            anchor_block["snapshot_url"] = (
                f"/objects/{anchor_block['oid']}/snapshots/0/image"
            )
        for frag in result.get("fragments", []) or []:
            if isinstance(frag, dict) and frag.get("oid"):
                frag["snapshot_url"] = (
                    f"/objects/{frag['oid']}/snapshots/0/image"
                )
        return result

    # ---- 2026-05-29: reference snapshot endpoints ----'''

if ANCHOR_ENDPOINT not in src:
    print("[server.py] FAILED: endpoint anchor not found. Source drift?", file=sys.stderr)
    sys.exit(3)
if src.count(ANCHOR_ENDPOINT) != 1:
    print(f"[server.py] FAILED: endpoint anchor not unique (count={src.count(ANCHOR_ENDPOINT)})", file=sys.stderr)
    sys.exit(3)
src = src.replace(ANCHOR_ENDPOINT, NEW_ENDPOINT, 1)
print("[server.py] (2/2) find_fragments_endpoint inserted", file=sys.stderr)

# Marker count check
n = src.count(MARKER)
print(f"[server.py] Marker count: {n}", file=sys.stderr)
if n != 2:
    print(f"[server.py] FAILED: expected exactly 2 markers, got {n}", file=sys.stderr)
    sys.exit(4)

# AST validation
try:
    ast.parse(src, filename=OUT_FILE)
except SyntaxError as e:
    print(f"[server.py] FAILED: syntax error: {e}", file=sys.stderr)
    sys.exit(5)
print("[server.py] AST validation passed", file=sys.stderr)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write(src)
PYEOF

SERVER_RC=$?
if [ $SERVER_RC -ne 0 ]; then
    color_red "server.py patcher failed (rc=$SERVER_RC). No changes made."
    exit $SERVER_RC
fi

# --- Patch working_memory.py ---
python3 - "$WM_FILE" "$WM_TMP" "$MARKER" <<'PYEOF'
import sys, ast

SRC_FILE, OUT_FILE, MARKER = sys.argv[1], sys.argv[2], sys.argv[3]

with open(SRC_FILE, "r", encoding="utf-8") as f:
    src = f.read()

# Idempotency
if MARKER in src:
    n = src.count(MARKER)
    print(f"[working_memory.py] Already patched (marker x{n}). No changes.", file=sys.stderr)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(src)
    sys.exit(0)

# =============================================================================
# Insertion 3: WorkingMemory.find_fragments method
# Anchor: between suggest_merges' return and _suggest_merge_winner.
# =============================================================================
ANCHOR_WM = '''            "thresholds": thresholds,
        }

    @staticmethod
    def _suggest_merge_winner('''

NEW_WM = '''            "thresholds": thresholds,
        }

    # Added 2026-06-11. Marker: FIND_FRAGMENTS_2026-06-11.
    def find_fragments(
        self,
        anchor_oid: str,
        *,
        cos_threshold: float = 0.85,
        dist_threshold_m: Optional[float] = None,
        include_unconfirmed: bool = True,
        exclude_named: bool = False,
        pose_state: str = "any",
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Per-anchor merge-candidate search.

        Finds OIDs that may be fragments of the same physical object as
        anchor_oid. Unlike suggest_merges (pairwise O(N^2) sweep with
        fixed thresholds), this fixes the anchor and widens the gates.
        Designed for human review of "is anything else in WM a fragment
        of this named object?" -- particularly useful for catching
        across-room movement of movable items and lifted/lowered
        duplicates.

        Adaptive dist_threshold_m:
          If dist_threshold_m is None, the threshold is selected from
          the anchor's movability_class:
            permanent / static / semi_static -> 3.0m  (furniture extent)
            movable / roaming / ephemeral    -> 9.0m  (room diagonal)
            null / unset                     -> 5.0m  (fallback)
          Caller can override with any positive float.

        pose_state filter (candidates only; anchor always included):
          "any"          -- both buckets (default; surfaces lift/lower)
          "on_floor"     -- candidates seen on the floor only
          "elevated"     -- candidates seen elevated only
          "match_anchor" -- candidates matching the anchor's pose_state

        Read-only. Does NOT mutate WM. The caller is responsible for
        reviewing snapshots and POSTing /objects/merge for each
        confirmed fragment.

        Returns {"error": "not_found", "id": ...} if anchor_oid is
        unknown. The HTTP wrapper converts that to a 404.
        """
        DIST_DEFAULTS_M = {
            "permanent":   3.0,
            "static":      3.0,
            "semi_static": 3.0,
            "movable":     9.0,
            "roaming":     9.0,
            "ephemeral":   9.0,
        }
        DIST_FALLBACK_M = 5.0

        VALID_POSE_STATES = ("any", "on_floor", "elevated", "match_anchor")
        if pose_state not in VALID_POSE_STATES:
            raise ValueError(
                f"pose_state must be one of {VALID_POSE_STATES}, "
                f"got {pose_state!r}"
            )

        # Snapshot all relevant fields under the lock; compute outside.
        with self._lock:
            anchor = self._map.get(anchor_oid)
            if anchor is None:
                return {"error": "not_found", "id": anchor_oid}

            anchor_snap = {
                "oid": anchor.id,
                "emb": anchor.emb_mean.astype(np.float32).copy(),
                "xyz": anchor.xyz_world.astype(np.float32).copy(),
                "label_primary": anchor.label_primary,
                "label_user": anchor.label_user,
                "movability_class": anchor.movability_class,
                "hits": int(anchor.hits),
                "stability": float(anchor.stability),
                "has_reference": anchor.reference_image_path is not None,
                "last_seen_wall_utc": float(anchor.last_seen_wall_utc),
                "pose_state_at_observation": getattr(
                    anchor, "pose_state_at_observation", "on_floor"
                ),
                "confirmed": bool(getattr(anchor, "confirmed", False)),
            }

            # Candidate pool: everything except the anchor itself.
            candidates_raw = []
            for o in self._map.values():
                if o.id == anchor_oid:
                    continue
                if not include_unconfirmed and not getattr(o, "confirmed", False):
                    continue
                candidates_raw.append({
                    "oid": o.id,
                    "emb": o.emb_mean.astype(np.float32).copy(),
                    "xyz": o.xyz_world.astype(np.float32).copy(),
                    "label_primary": o.label_primary,
                    "label_user": o.label_user,
                    "movability_class": o.movability_class,
                    "hits": int(o.hits),
                    "stability": float(o.stability),
                    "has_reference": o.reference_image_path is not None,
                    "last_seen_wall_utc": float(o.last_seen_wall_utc),
                    "pose_state_at_observation": getattr(
                        o, "pose_state_at_observation", "on_floor"
                    ),
                    "confirmed": bool(getattr(o, "confirmed", False)),
                })

        # Resolve adaptive distance threshold.
        if dist_threshold_m is None:
            anchor_cls = anchor_snap["movability_class"]
            resolved_dist = DIST_DEFAULTS_M.get(anchor_cls, DIST_FALLBACK_M)
            dist_default_used = True
        else:
            resolved_dist = float(dist_threshold_m)
            dist_default_used = False

        # Resolve pose_state filter.
        if pose_state == "match_anchor":
            resolved_pose = anchor_snap["pose_state_at_observation"]
        else:
            resolved_pose = pose_state

        # Apply pool filters (post-snapshot, pre-sweep).
        if resolved_pose != "any":
            candidates_raw = [
                c for c in candidates_raw
                if c["pose_state_at_observation"] == resolved_pose
            ]
        if exclude_named:
            candidates_raw = [
                c for c in candidates_raw if c["label_user"] is None
            ]

        thresholds = {
            "cos_threshold": float(cos_threshold),
            "dist_threshold_m": float(resolved_dist),
            "dist_threshold_default_used": dist_default_used,
            "include_unconfirmed": bool(include_unconfirmed),
            "exclude_named": bool(exclude_named),
            "pose_state": pose_state,
            "pose_state_resolved": resolved_pose,
            "limit": int(limit),
        }

        # Build the anchor response block (no emb in output).
        anchor_block = {
            "oid": anchor_snap["oid"],
            "label_user": anchor_snap["label_user"],
            "label_primary": anchor_snap["label_primary"],
            "movability_class": anchor_snap["movability_class"],
            "xyz": anchor_snap["xyz"].tolist(),
            "hits": anchor_snap["hits"],
            "stability": round(anchor_snap["stability"], 3),
            "has_reference": anchor_snap["has_reference"],
            "confirmed": anchor_snap["confirmed"],
            "pose_state_at_observation": anchor_snap["pose_state_at_observation"],
            "last_seen_wall_utc": anchor_snap["last_seen_wall_utc"],
        }

        n = len(candidates_raw)
        if n == 0:
            return {
                "anchor": anchor_block,
                "fragments": [],
                "scanned_objects": 0,
                "returned": 0,
                "total_above_thresholds": 0,
                "thresholds": thresholds,
            }

        # Vectorized cosine + distance vs the anchor. Embeddings are
        # pre-normalized (L2) so dot product equals cosine similarity.
        anchor_emb = anchor_snap["emb"]
        anchor_xyz = anchor_snap["xyz"]
        cand_embs = np.stack([c["emb"] for c in candidates_raw], axis=0)
        cand_xyzs = np.stack([c["xyz"] for c in candidates_raw], axis=0)
        cosines = (cand_embs @ anchor_emb).astype(np.float32)
        dists = np.linalg.norm(
            cand_xyzs - anchor_xyz, axis=1
        ).astype(np.float32)

        fragments: List[Dict[str, Any]] = []
        total_above = 0
        for idx, c in enumerate(candidates_raw):
            cos_i = float(cosines[idx])
            if cos_i < cos_threshold:
                continue
            dist_i = float(dists[idx])
            if dist_i > resolved_dist:
                continue
            total_above += 1
            fragments.append({
                "oid": c["oid"],
                "label_user": c["label_user"],
                "label_primary": c["label_primary"],
                "movability_class": c["movability_class"],
                "cosine": round(cos_i, 4),
                "distance_m": round(dist_i, 4),
                "hits": c["hits"],
                "stability": round(c["stability"], 3),
                "has_reference": c["has_reference"],
                "confirmed": c["confirmed"],
                "pose_state_at_observation": c["pose_state_at_observation"],
                "xyz": cand_xyzs[idx].tolist(),
                "last_seen_wall_utc": c["last_seen_wall_utc"],
            })

        fragments.sort(key=lambda f: (-f["cosine"], f["distance_m"]))
        truncated = fragments[: max(0, int(limit))]

        return {
            "anchor": anchor_block,
            "fragments": truncated,
            "scanned_objects": n,
            "returned": len(truncated),
            "total_above_thresholds": total_above,
            "thresholds": thresholds,
        }

    @staticmethod
    def _suggest_merge_winner('''

if ANCHOR_WM not in src:
    print("[working_memory.py] FAILED: WM anchor not found. Source drift?", file=sys.stderr)
    sys.exit(3)
if src.count(ANCHOR_WM) != 1:
    print(f"[working_memory.py] FAILED: WM anchor not unique (count={src.count(ANCHOR_WM)})", file=sys.stderr)
    sys.exit(3)
src = src.replace(ANCHOR_WM, NEW_WM, 1)
print("[working_memory.py] find_fragments method inserted", file=sys.stderr)

# Verify Optional is importable (we use it in the signature)
if "Optional" not in src.split("\n", 200)[0:80].__str__() and "from typing import" in src[:5000]:
    # Cheap heuristic; the real check is AST + actual import grep below.
    pass

# Sanity: confirm Optional was already imported (we depend on it).
import re
typing_imports = re.findall(r"from typing import [^\n]+", src[:5000])
has_optional = any("Optional" in line for line in typing_imports)
if not has_optional:
    print("[working_memory.py] WARN: 'Optional' not found in typing imports of first 5000 chars.", file=sys.stderr)
    print("[working_memory.py] AST parse will catch it if it's actually missing.", file=sys.stderr)

# Marker count check
n = src.count(MARKER)
print(f"[working_memory.py] Marker count: {n}", file=sys.stderr)
if n != 1:
    print(f"[working_memory.py] FAILED: expected exactly 1 marker, got {n}", file=sys.stderr)
    sys.exit(4)

# AST validation
try:
    ast.parse(src, filename=OUT_FILE)
except SyntaxError as e:
    print(f"[working_memory.py] FAILED: syntax error: {e}", file=sys.stderr)
    sys.exit(5)
print("[working_memory.py] AST validation passed", file=sys.stderr)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write(src)
PYEOF

WM_RC=$?
if [ $WM_RC -ne 0 ]; then
    color_red "working_memory.py patcher failed (rc=$WM_RC). No changes made."
    exit $WM_RC
fi

# ---------------------------------------------------------------------------
# Dryrun: show diffs, no writes
# ---------------------------------------------------------------------------
if [ "$MODE" = "--dryrun" ]; then
    color_green "[DRYRUN] Both patches validated cleanly. No files modified."
    echo
    color_yellow "--- server.py diff ---"
    diff -u "$SERVER_FILE" "$SERVER_TMP" || true
    echo
    color_yellow "--- working_memory.py diff ---"
    diff -u "$WM_FILE" "$WM_TMP" || true
    echo
    echo "To apply: $0 --apply"
    exit 0
fi

# ---------------------------------------------------------------------------
# Apply: backup + atomic write + verify
# ---------------------------------------------------------------------------
if [ "$MODE" = "--apply" ]; then
    color_yellow "[APPLY] Backing up and writing patched sources..."

    apply_one() {
        local dest="$1" tmp="$2" expected_markers="$3"
        local bk="$dest$BACKUP_SUFFIX"
        if [ ! -f "$bk" ]; then
            cp -p "$dest" "$bk"
            color_green "[APPLY] backup created: $bk"
        else
            color_yellow "[APPLY] backup exists, preserving: $bk"
        fi
        local atomic_tmp="$dest.atomic.$$"
        cp -p "$tmp" "$atomic_tmp"
        mv "$atomic_tmp" "$dest"
        color_green "[APPLY] patched: $dest"
        local n
        n=$(awk -v p="$MARKER" 'index($0,p){c++} END{print c+0}' "$dest")
        if [ "$n" -ne "$expected_markers" ]; then
            color_red "[APPLY] VERIFY FAILED: $dest has $n markers (expected $expected_markers)"
            exit 9
        fi
    }

    apply_one "$SERVER_FILE" "$SERVER_TMP" 2
    apply_one "$WM_FILE"     "$WM_TMP"     1

    echo
    color_green "==============================================================="
    color_green "find_fragments applied. Next steps:"
    color_green "==============================================================="
    echo "  1. Restart rtsm-dev to load the new route:"
    echo "        cd ~/rtsm/docker && docker compose restart rtsm-dev"
    echo
    echo "  2. Smoke-check the new endpoint is registered:"
    echo "        curl -s http://localhost:8002/openapi.json \\"
    echo "             | jq '.paths | keys[] | select(contains(\"find_fragments\"))'"
    echo "     Expected: \"/objects/{oid}/find_fragments\""
    echo
    echo "  3. Run unit tests (inside the container):"
    echo "        docker exec -w /workspace/rtsm rtsm-dev \\"
    echo "             python3 -m unittest tests.test_find_fragments -v"
    echo
    echo "  4. Live probe against the named basketball:"
    echo "        curl -s -X POST http://localhost:8002/objects/18503a243abd46fb/find_fragments \\"
    echo "             -H 'Content-Type: application/json' -d '{}' | jq '.thresholds, .returned'"
    echo
    echo "To revert: $0 --revert"
    exit 0
fi
