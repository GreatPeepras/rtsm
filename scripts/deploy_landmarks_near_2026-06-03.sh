#!/bin/bash
# Deploy /landmarks/near Endpoint — server.py, 2026-06-03
#
# Adds GET /landmarks/near to RTSM's HTTP API. Returns landmark-eligible
# objects (movability_class IN 'static', 'permanent', optionally
# 'semi_static') within a radius of a 3D point. Used by:
#   - goto_object(name) name resolution (when label_user lookup fails or
#     for fuzzy "find a landmark nearby" planning)
#   - landmark-AMCL pose verification gate (verify-only mode first)
#
# Hard invariant enforced inside the endpoint: NEVER returns objects
# with movability_class outside the allow-list, regardless of label
# or hits. Defense-in-depth — both the proximity-index iteration AND
# the per-object check apply the filter.
#
# Per on_demand_nav_and_landmark_gate_design.md (2026-06-02).
#
# Idempotent. Backs up before editing. AST-parses afterwards.
# Also installs tests/test_landmarks_near.py if not already present.

set -euo pipefail

# Allow override via env. Defaults match the Execution Jetson layout.
RTSM_REPO="${RTSM_REPO:-${HOME}/rtsm}"
SERVER="${SERVER:-${RTSM_REPO}/rtsm/api/server.py}"
TEST_SRC_DIR="${TEST_SRC_DIR:-$(dirname "$(readlink -f "$0")")}"
TEST_DST="${TEST_DST:-${RTSM_REPO}/tests/test_landmarks_near.py}"

if [ ! -f "$SERVER" ]; then
    echo "ERROR: $SERVER not found." >&2
    echo "  Set SERVER=... or RTSM_REPO=... and re-run." >&2
    exit 1
fi

TS=$(date +%Y%m%d-%H%M%S)

echo "== /landmarks/near patch — server.py ($(date -Is)) =="
echo "   target:   $SERVER"
echo "   test out: $TEST_DST"

cp "$SERVER" "$SERVER.bak.$TS"
echo "[backup] $SERVER.bak.$TS"

# ----------------------------------------------------------------------
# Patch server.py — insert the new endpoint before the Analytics marker
# ----------------------------------------------------------------------
python3 - "$SERVER" << 'PYEOF'
import pathlib, sys, ast
p = pathlib.Path(sys.argv[1])
src = p.read_text()
orig = src

ENDPOINT_BLOCK = '''    @app.get("/landmarks/near")
    def landmarks_near(
        x: float, y: float, z: float,
        radius_m: float = 2.0,
        include_semi_static: bool = False,
        offset: int = 0,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """Landmark-eligible spatial search.

        Returns objects with movability_class IN ('static', 'permanent'),
        or optionally widened to include 'semi_static'. Hard invariant:
        this endpoint NEVER returns objects with movability_class outside
        the allow-list, regardless of label or hits. The landmark consumer
        must be able to trust the filter completely.

        Per on_demand_nav_and_landmark_gate_design.md (2026-06-02) —
        shared infrastructure for nav2 goal resolution and AMCL landmark
        gating.

        Args:
            x, y, z: Center point in world coordinates (meters)
            radius_m: Search radius in meters (default 2.0 — wider than
                /search/spatial because landmarks are sparser than the
                general observation population)
            include_semi_static: If True, widen the allow-list to include
                'semi_static' (3D printer, label printer, etc.). Default
                False — semi_statics are not landmarks by default.
            offset: Skip first N results (for pagination)
            limit: Maximum results to return (default 50, max 200)

        Returns:
            Landmarks sorted by distance ascending, with pagination.
        """
        limit = min(max(1, limit), 200)
        offset = max(0, offset)

        # Build the allow-list. ALWAYS includes 'static' + 'permanent';
        # optionally widens to 'semi_static'. NEVER includes movable /
        # roaming / ephemeral / None.
        allowed = {"static", "permanent"}
        if include_semi_static:
            allowed.add("semi_static")

        if working_memory.index is None:
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
                continue

            # Surface the fields landmark consumers actually need:
            #   - label_user for goto-by-name resolution
            #   - display_label for TTS narration
            #   - last_seen_wall_utc for staleness reasoning
            # Compute label_primary the same way _obj_summary does
            # (min_label_hits gate), so display_label is consistent
            # across this and the rest of the API.
            _scores = getattr(obj, "label_scores", {}) or {}
            _hits = getattr(obj, "label_hits", {}) or {}
            _min_hits = int(getattr(working_memory, "min_label_hits", 5))
            _gated = {k: v for k, v in _scores.items()
                      if int(_hits.get(k, 0)) >= _min_hits}
            if _gated:
                label_primary = max(_gated, key=_gated.get)
            else:
                label_primary = getattr(obj, "label_primary", None)
            label_user = getattr(obj, "label_user", None)

            all_results.append({
                "id": oid,
                "distance_m": round(dist, 4),
                "xyz_world": obj.xyz_world.tolist(),
                "confirmed": bool(getattr(obj, "confirmed", False)),
                "stability": round(float(getattr(obj, "stability", 0.0)), 3),
                "hits": int(getattr(obj, "hits", 0)),
                "label_user": label_user,
                "label_primary": label_primary,
                "display_label": label_user or label_primary,
                "movability_class": mov,
                "last_seen_wall_utc": float(
                    getattr(obj, "last_seen_wall_utc", 0.0)
                ),
            })

        all_results.sort(key=lambda r: r["distance_m"])
        total = len(all_results)
        page = all_results[offset : offset + limit]

        return {
            "center": [x, y, z],
            "radius_m": radius_m,
            "include_semi_static": include_semi_static,
            "allowed_movability": sorted(allowed),
            "robot_pose": working_memory.get_robot_pose(),
            "total": total,
            "offset": offset,
            "limit": limit,
            "count": len(page),
            "results": page,
        }

'''

# Idempotency check.
if '@app.get("/landmarks/near")' in src:
    print("[server.py] /landmarks/near already present — skipping insertion")
else:
    # Anchor: the comment that marks the start of the analytics section,
    # which immediately follows /search/spatial. Inserting before this
    # keeps the new endpoint grouped with the other spatial queries.
    anchor = "    # ---- Analytics endpoint ----"
    if anchor not in src:
        print(f"ERROR: anchor not found in {p}: {anchor!r}", file=sys.stderr)
        sys.exit(1)
    if src.count(anchor) != 1:
        print(f"ERROR: anchor not unique in {p}: {src.count(anchor)} occurrences",
              file=sys.stderr)
        sys.exit(1)
    src = src.replace(anchor, ENDPOINT_BLOCK + anchor, 1)
    print("[server.py] inserted /landmarks/near before Analytics section")

# AST validation — catch syntax errors before the deploy hits the container.
try:
    ast.parse(src)
except SyntaxError as e:
    print(f"ERROR: AST parse failed after patch: {e}", file=sys.stderr)
    sys.exit(2)

if src != orig:
    p.write_text(src)
    print(f"[server.py] wrote {p}")
else:
    print(f"[server.py] no changes to write")
PYEOF

# ----------------------------------------------------------------------
# Install test file (if not already present at the destination)
# ----------------------------------------------------------------------
TEST_SRC="${TEST_SRC_DIR}/test_landmarks_near.py"
if [ -f "$TEST_SRC" ]; then
    mkdir -p "$(dirname "$TEST_DST")"
    if [ -f "$TEST_DST" ]; then
        if cmp -s "$TEST_SRC" "$TEST_DST"; then
            echo "[tests] $TEST_DST already up to date"
        else
            cp "$TEST_DST" "$TEST_DST.bak.$TS"
            cp "$TEST_SRC" "$TEST_DST"
            echo "[tests] updated $TEST_DST (backup: $TEST_DST.bak.$TS)"
        fi
    else
        cp "$TEST_SRC" "$TEST_DST"
        echo "[tests] installed $TEST_DST"
    fi
else
    echo "[tests] WARNING: $TEST_SRC not found alongside this script; skipping"
    echo "          (you can copy tests/test_landmarks_near.py manually)"
fi

echo ""
echo "== Patch applied. Next steps =="
echo ""
echo "  1. Restart RTSM container:"
echo "       cd ~/rtsm/docker && docker compose restart rtsm-dev"
echo ""
echo "  2. Sanity check the endpoint is registered:"
echo "       curl -s http://localhost:8002/openapi.json | jq '.paths | keys[]' \\"
echo "         | grep landmarks"
echo "     Expected: \"/landmarks/near\""
echo ""
echo "  3. Smoke test against a real landmark (couch is at \$XYZ — adjust):"
echo "       curl -s 'http://localhost:8002/landmarks/near?x=0&y=0&z=0&radius_m=5' \\"
echo "         | jq '{total, count, results: [.results[] | {id, display_label, distance_m, movability_class}]}'"
echo "     Expected: 9 landmarks within reach (per 2026-06-02 evening handoff)."
echo ""
echo "  4. Run unit tests against the host repo (NOT in container):"
echo "       cd ~/rtsm && PYTHONPATH=. python3 tests/test_landmarks_near.py"
echo "     Expected: 18 passed, 0 failed."
echo ""
echo "  5. Verify the hard invariant on live data:"
echo "       curl -s 'http://localhost:8002/landmarks/near?x=0&y=0&z=0&radius_m=100' \\"
echo "         | jq '.results | map(.movability_class) | unique'"
echo "     Expected: [\"static\"] (only static landmarks classified so far)."
echo "     Adding ?include_semi_static=true should add semi_static entries."
echo ""
