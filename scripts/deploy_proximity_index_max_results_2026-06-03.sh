#!/bin/bash
# Fix: ProximityIndex.nearby_ids silently drops least-recently-touched OIDs
# 2026-06-03 (follow-up to deploy_landmarks_near_fix_2026-06-03.sh)
#
# Root cause:
#   nearby_ids() clamps its return to self.neighbors_max (default 128)
#   based on _touch recency. _touch is bumped on insert, update, AND on
#   every successful nearby_ids hit. With ~160 OIDs in WM and a wide
#   query (rings=20 from origin covers the whole apartment), the gather
#   set is >128 and the clamp drops the 32 OIDs that haven't been
#   re-observed recently. Rehydrated objects in low-traffic zones of the
#   apartment (e.g. drawer at (-1.37,-1.27), heater at (-1.22,-1.81))
#   get touched once at rehydrate, never re-touched, and silently
#   disappear from spatial query results.
#
#   This was diagnosed via /landmarks/near returning 7/9 known static
#   landmarks. /search/spatial centered on each missing landmark
#   returned it (small ring count, gather set << 128, clamp didn't
#   trigger). /landmarks/near now uses iter_objects() and bypasses this
#   path entirely; this fix is for /search/spatial and future callers
#   that need exhaustive spatial queries.
#
# Fix:
#   Add a per-query `max_results` parameter:
#     None (default) -> use self.neighbors_max (HISTORICAL BEHAVIOR)
#     0              -> disable the cap entirely
#     N > 0          -> explicit override
#
# Risk:
#   Backward compatible. Ingest path callers don't pass max_results,
#   so they get the same neighbors_max=128 behavior they always had.
#   This is strictly additive.
#
# Idempotent. Backs up before editing. AST-parses afterwards.

set -euo pipefail

RTSM_REPO="${RTSM_REPO:-${HOME}/rtsm}"
PI_FILE="${PI_FILE:-${RTSM_REPO}/rtsm/stores/proximity_index.py}"

if [ ! -f "$PI_FILE" ]; then
    echo "ERROR: $PI_FILE not found." >&2
    exit 1
fi

TS=$(date +%Y%m%d-%H%M%S)

echo "== ProximityIndex.nearby_ids max_results fix ($(date -Is)) =="
echo "   target: $PI_FILE"

cp "$PI_FILE" "$PI_FILE.bak.$TS"
echo "[backup] $PI_FILE.bak.$TS"

python3 - "$PI_FILE" << 'PYEOF'
import pathlib, sys, ast
p = pathlib.Path(sys.argv[1])
src = p.read_text()
orig = src

# ----------------------------------------------------------------------
# Edit 1: extend nearby_ids() signature with max_results kwarg
# ----------------------------------------------------------------------
OLD_SIG = '''    def nearby_ids(
        self,
        xyz_world: np.ndarray,
        rings: int = 1,
        *,
        prune_with: Optional[Callable[[str], bool]] = None,
    ) -> List[str]:
        """
        Get object IDs in the ±rings neighborhood of xyz_world's cell.
        - prune_with(oid) should return True if the ID is still live in WM.
          Stale IDs are lazily removed from the index.
        - The returned list is clamped to neighbors_max by recency (most-recent first).
        """'''

NEW_SIG = '''    def nearby_ids(
        self,
        xyz_world: np.ndarray,
        rings: int = 1,
        *,
        prune_with: Optional[Callable[[str], bool]] = None,
        max_results: Optional[int] = None,
    ) -> List[str]:
        """
        Get object IDs in the ±rings neighborhood of xyz_world's cell.
        - prune_with(oid) should return True if the ID is still live in WM.
          Stale IDs are lazily removed from the index.
        - max_results: per-query cap on returned ids.
            None (default) -> use self.neighbors_max (historical behavior;
                              suitable for ingest-time association queries
                              that don't want huge candidate sets).
            0              -> disable the cap entirely; return all hits.
                              Use for exhaustive spatial queries (whole-
                              apartment landmark/object listings) where
                              recency-based eviction would silently drop
                              the least-recently-observed objects.
            N > 0          -> explicit cap override.
        """'''

if OLD_SIG not in src:
    if "max_results: Optional[int] = None" in src:
        print("[proximity_index.py] signature already patched — skipping")
    else:
        print("ERROR: nearby_ids signature not found verbatim. Has it been edited?",
              file=sys.stderr)
        sys.exit(1)
else:
    if src.count(OLD_SIG) != 1:
        print(f"ERROR: signature anchor not unique ({src.count(OLD_SIG)} matches)",
              file=sys.stderr)
        sys.exit(1)
    src = src.replace(OLD_SIG, NEW_SIG, 1)
    print("[proximity_index.py] extended nearby_ids signature")

# ----------------------------------------------------------------------
# Edit 2: replace the unconditional neighbors_max clamp with one that
# honors the max_results kwarg
# ----------------------------------------------------------------------
OLD_CLAMP = '''            # Clamp by recency (keep most-recent touched)
            if len(ids) > self.neighbors_max:
                ids_sorted = sorted(ids, key=lambda k: self._touch.get(k, 0.0), reverse=True)
                ids = set(ids_sorted[: self.neighbors_max])'''

NEW_CLAMP = '''            # Resolve effective cap:
            #   max_results=None -> historical default (self.neighbors_max)
            #   max_results=0    -> unlimited (no clamp)
            #   max_results=N>0  -> explicit override
            if max_results is None:
                _cap = self.neighbors_max
            elif max_results == 0:
                _cap = None
            else:
                _cap = int(max_results)

            # Clamp by recency (keep most-recent touched)
            if _cap is not None and len(ids) > _cap:
                ids_sorted = sorted(ids, key=lambda k: self._touch.get(k, 0.0), reverse=True)
                ids = set(ids_sorted[:_cap])'''

if OLD_CLAMP not in src:
    if "Resolve effective cap:" in src:
        print("[proximity_index.py] clamp already patched — skipping")
    else:
        print("ERROR: clamp block not found verbatim. Has it been edited?",
              file=sys.stderr)
        sys.exit(1)
else:
    if src.count(OLD_CLAMP) != 1:
        print(f"ERROR: clamp anchor not unique ({src.count(OLD_CLAMP)} matches)",
              file=sys.stderr)
        sys.exit(1)
    src = src.replace(OLD_CLAMP, NEW_CLAMP, 1)
    print("[proximity_index.py] swapped clamp for max_results-aware version")

# AST validation
try:
    ast.parse(src)
except SyntaxError as e:
    print(f"ERROR: AST parse failed after patch: {e}", file=sys.stderr)
    sys.exit(2)

if src != orig:
    p.write_text(src)
    print(f"[proximity_index.py] wrote {p}")
else:
    print("[proximity_index.py] no changes to write")
PYEOF

echo ""
echo "== Patch applied. Next steps =="
echo ""
echo "  1. Restart RTSM container:"
echo "       cd ~/rtsm/docker && docker compose restart rtsm-dev"
echo ""
echo "  2. Unit test for the new parameter:"
echo "       cd ~/rtsm && PYTHONPATH=. python3 tests/test_nearby_ids_max_results.py"
echo "     Expected: 5 passed, 0 failed."
echo ""
echo "  3. Sanity-confirm nothing else broke:"
echo "       cd ~/rtsm && PYTHONPATH=. python3 tests/test_landmarks_near.py"
echo "     Expected: 18 passed, 0 failed (same as before — /landmarks/near"
echo "     uses iter_objects, not the proximity index)."
echo ""
echo "  4. Optional: confirm /search/spatial radius=large now returns the"
echo "     full set instead of clamped 128. Pick any wide-radius query"
echo "     centered somewhere in the apartment:"
echo "       curl -s 'http://localhost:8002/search/spatial?x=0&y=0&z=0&radius_m=20' \\"
echo "         | jq '.total'"
echo "     (Won't change *yet* because /search/spatial doesn't pass"
echo "     max_results — that's a follow-up. This deploy makes the fix"
echo "     available; calling code can opt in when ready.)"
echo ""
