#!/usr/bin/env bash
# Fix the merge endpoint: rename `faiss_client` -> `vectors` to match the
# actual parameter name in create_app(...).
#
# This was the cause of the FAISS sync NameError on 2026-06-01.
#
# Safety: refuses to run if `faiss_client` appears anywhere other than the
# three lines added by deploy_merge_objects_2026-06-01.sh. Backs up before
# editing. Validates syntax after.
#
# Usage:
#   bash patch_merge_faiss_client_to_vectors_2026-06-01.sh
set -euo pipefail

SERVER_PATH="${SERVER_PATH:-$HOME/rtsm/rtsm/api/server.py}"
TS=$(date -u +%Y-%m-%dT%H-%M-%SZ)

if [[ ! -f "$SERVER_PATH" ]]; then
    echo "[patch] ERROR: server.py not found at $SERVER_PATH" >&2
    exit 1
fi

# Count current `faiss_client` occurrences. We expect exactly 3 (lines
# 745, 749, 752 in the file as left by deploy_merge_objects_2026-06-01.sh).
COUNT=$(grep -c 'faiss_client' "$SERVER_PATH" || true)
if [[ "$COUNT" -ne 3 ]]; then
    echo "[patch] ERROR: expected exactly 3 'faiss_client' occurrences, found $COUNT" >&2
    echo "[patch] Locations:" >&2
    grep -n 'faiss_client' "$SERVER_PATH" >&2 || true
    echo "[patch] Aborting -- patch would over-rewrite. Inspect manually." >&2
    exit 1
fi

# Backup before any change.
cp -a "$SERVER_PATH" "$SERVER_PATH.bak.$TS"
echo "[patch] Backup: $SERVER_PATH.bak.$TS"

# Confirm those 3 occurrences are inside the merge endpoint context
# (i.e. they appear adjacent to delete/upsert_batch calls). Defensive.
CONTEXT=$(grep -B 1 -A 1 'faiss_client' "$SERVER_PATH" | grep -cE 'delete|upsert_batch' || true)
if [[ "$CONTEXT" -lt 2 ]]; then
    echo "[patch] WARNING: faiss_client references don't look like the merge endpoint" >&2
    echo "[patch] Backup is at $SERVER_PATH.bak.$TS; aborting." >&2
    exit 1
fi

# Do the rename. -i in place, /g for all 3 lines.
sed -i 's/\bfaiss_client\b/vectors/g' "$SERVER_PATH"

# Verify: 0 `faiss_client` left in the file.
LEFT=$(grep -c 'faiss_client' "$SERVER_PATH" || true)
if [[ "$LEFT" -ne 0 ]]; then
    echo "[patch] ERROR: $LEFT 'faiss_client' references still present after rename" >&2
    echo "[patch] Restoring from backup..."
    cp -a "$SERVER_PATH.bak.$TS" "$SERVER_PATH"
    exit 1
fi

# Syntax check.
if ! python3 -c "import ast; ast.parse(open('$SERVER_PATH').read())" 2>/dev/null; then
    echo "[patch] ERROR: server.py no longer parses after rename" >&2
    echo "[patch] Restoring from backup..." >&2
    cp -a "$SERVER_PATH.bak.$TS" "$SERVER_PATH"
    exit 1
fi

echo "[patch] OK: 3 references renamed, syntax clean"
echo
echo "[patch] Verification -- merge endpoint now references 'vectors':"
grep -n -B 1 -A 2 'vectors.delete\|vectors.upsert_batch\|if vectors is not None' "$SERVER_PATH" | head -20
echo
echo "[patch] Next steps:"
echo "  1) Restart the container so the patched endpoint is live:"
echo "       cd ~/rtsm/docker && docker compose restart rtsm-dev"
echo "       sleep 5 && docker logs --tail 20 rtsm-dev | grep -E 'rehydrate|listening|error'"
echo
echo "  2) The restart will revert the WM-side merge of 504b78fe/82aebeff"
echo "     (loser will resurrect from FAISS). Confirm:"
echo "       curl -s http://localhost:8002/stats | jq '{objects, confirmed}'"
echo "       # Expected: 234 / 234 (back to pre-merge count)"
echo
echo "  3) Re-do the merge -- this time the FAISS sync should succeed:"
echo "       WINNER=504b78fe0f1e4e1a"
echo "       LOSER=82aebeff6bb04b28"
echo "       curl -s -X POST http://localhost:8002/objects/merge \\"
echo "         -H 'Content-Type: application/json' \\"
echo "         -d \"{\\\"winner_oid\\\":\\\"\$WINNER\\\",\\\"loser_oid\\\":\\\"\$LOSER\\\"}\" \\"
echo "         | jq '{stats, audit_log_path, faiss_sync_warning: (.faiss_sync_warning // \"none\")}'"
echo "       # Expected: faiss_sync_warning: \"none\""
echo
echo "  4) Verify FAISS is consistent (sidecar count down to 233):"
echo "       curl -s http://localhost:8002/stats | jq '{objects, confirmed, gallery_on_disk_oids}'"
echo "       # All three should now be 233"
echo
echo "[patch] Rollback if needed:"
echo "       mv $SERVER_PATH.bak.$TS $SERVER_PATH"
echo "       cd ~/rtsm/docker && docker compose restart rtsm-dev"
