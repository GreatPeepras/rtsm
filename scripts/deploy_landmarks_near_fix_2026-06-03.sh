#!/bin/bash
# Follow-up: /landmarks/near fix — iter_objects instead of proximity index
# 2026-06-03 (same-day follow-up to deploy_landmarks_near_2026-06-03.sh)
#
# Problem: the original /landmarks/near used working_memory.index.nearby_ids()
# which is the same mechanism /search/spatial uses. With the rings cap at 20
# and an origin-centered radius_m=100 query, it returned only 7 of 9 known
# static landmarks. Diagnostic: querying /landmarks/near centered on the
# missing objects (drawer, heater) found them fine — the bug is specific to
# far-from-object centers and is in how the proximity index iterates cell
# rings, not in the endpoint logic.
#
# The proximity index is optimized for tight "what's near me right now"
# queries fired many times per second during ingest. /landmarks/near is
# called at goto time and at landmark verification (~few Hz max). WM has
# ~160 objects; full scan is trivially cheap.
#
# Fix: swap the index call for working_memory.iter_objects() and let the
# existing radius + movability filter do the work. Bonus: the endpoint
# now works in serve-mode (frozen WM, no proximity index) as well.
#
# Idempotent. Backs up before editing. AST-parses afterwards.

set -euo pipefail

RTSM_REPO="${RTSM_REPO:-${HOME}/rtsm}"
SERVER="${SERVER:-${RTSM_REPO}/rtsm/api/server.py}"

if [ ! -f "$SERVER" ]; then
    echo "ERROR: $SERVER not found." >&2
    exit 1
fi

TS=$(date +%Y%m%d-%H%M%S)

echo "== /landmarks/near fix — iter_objects scan ($(date -Is)) =="
echo "   target: $SERVER"

cp "$SERVER" "$SERVER.bak.$TS"
echo "[backup] $SERVER.bak.$TS"

python3 - "$SERVER" << 'PYEOF'
import pathlib, sys, ast
p = pathlib.Path(sys.argv[1])
src = p.read_text()
orig = src

# The exact block to replace — the index-based lookup section of
# /landmarks/near. Anchored to the function so we don't accidentally
# touch /search/spatial (which has very similar wording).
OLD_BLOCK = '''        if working_memory.index is None:
            raise HTTPException(
                status_code=503,
                detail="Spatial search not available (no proximity index)",
            )

        center = np.array([x, y, z], dtype=np.float32)
        grid = working_memory.index.grid
        # Landmark radius may be larger than /search/spatial — bump the
        # rings cap accordingly. Still bounded to keep cost predictable.
        rings = min(20, max(1, int(np.ceil(radius_m / grid.cell_m))))

        oids = working_memory.index.nearby_ids(center, rings=rings)

        all_results: List[Dict[str, Any]] = []
        for oid in oids:
            obj = working_memory.get(oid)
            if obj is None:
                continue

            # Hard invariant: positive allow-list match only. Objects with
            # movability_class = None, "" (empty), or any other value not
            # in the canonical set are excluded. No fuzzy matching.
            mov = getattr(obj, "movability_class", None)
            if mov not in allowed:
                continue

            dist = float(np.linalg.norm(obj.xyz_world - center))
            if dist > radius_m:
                continue'''

NEW_BLOCK = '''        center = np.array([x, y, z], dtype=np.float32)

        # 2026-06-03: full WM scan instead of proximity-index lookup.
        # The proximity index is optimized for tight "what's near me"
        # queries fired per-ingest; its rings-based cell iteration drops
        # some cells for far-from-object centers with large radii (e.g.
        # whole-apartment queries centered on origin). Landmark queries
        # are infrequent and the candidate set is tiny (~dozens of
        # static/permanent objects in a typical home), so iter_objects()
        # is fast enough and correct in all cases. Also makes the
        # endpoint work in serve-mode (frozen WM, no proximity index).

        all_results: List[Dict[str, Any]] = []
        for obj in working_memory.iter_objects():
            # Hard invariant: positive allow-list match only. Objects with
            # movability_class = None, "" (empty), or any other value not
            # in the canonical set are excluded. No fuzzy matching.
            mov = getattr(obj, "movability_class", None)
            if mov not in allowed:
                continue

            xyz = getattr(obj, "xyz_world", None)
            if xyz is None:
                continue

            dist = float(np.linalg.norm(xyz - center))
            if dist > radius_m:
                continue

            oid = getattr(obj, "id", None)
            if oid is None:
                continue'''

if OLD_BLOCK not in src:
    # Idempotency: maybe we already applied this. Check.
    if "2026-06-03: full WM scan instead of proximity-index lookup" in src:
        print("[server.py] fix already applied — skipping")
        sys.exit(0)
    print("ERROR: anchor block not found. Has /landmarks/near been edited?",
          file=sys.stderr)
    print("       Run: grep -n 'rings = min(20' " + str(p), file=sys.stderr)
    sys.exit(1)

if src.count(OLD_BLOCK) != 1:
    print(f"ERROR: anchor block not unique ({src.count(OLD_BLOCK)} matches)",
          file=sys.stderr)
    sys.exit(1)

src = src.replace(OLD_BLOCK, NEW_BLOCK, 1)
print("[server.py] swapped proximity-index lookup for iter_objects scan")

# The append site has a `for oid in oids:` loop tail that referred to
# `oid` directly; we now bind `oid` from getattr(obj, "id", None) above
# so the append-block (which uses `oid` and `obj` as locals) is fine.
# The xyz reference inside append goes through obj.xyz_world.tolist();
# leave as-is.

# AST validation
try:
    ast.parse(src)
except SyntaxError as e:
    print(f"ERROR: AST parse failed after patch: {e}", file=sys.stderr)
    sys.exit(2)

p.write_text(src)
print(f"[server.py] wrote {p}")
PYEOF

echo ""
echo "== Patch applied. Next steps =="
echo ""
echo "  1. Restart RTSM container:"
echo "       cd ~/rtsm/docker && docker compose restart rtsm-dev"
echo ""
echo "  2. Should now see all 9 static landmarks:"
echo "       curl -s 'http://localhost:8002/landmarks/near?x=0&y=0&z=0&radius_m=100' \\"
echo "         | jq '{total, results: [.results[] | {display_label, distance_m}]}'"
echo "     Expected: 9 landmarks (couch, drawer, desk, Hamlet display,"
echo "     windowsill, Kallax shelf, vertical shelf, right speaker, heater)."
echo ""
echo "  3. Hard invariant still holds:"
echo "       curl -s 'http://localhost:8002/landmarks/near?x=0&y=0&z=0&radius_m=100' \\"
echo "         | jq '.results | map(.movability_class) | unique'"
echo "     Expected: [\"static\"]."
echo ""
