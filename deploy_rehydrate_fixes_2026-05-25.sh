#!/bin/bash
# Deploy rehydrate fixes — 2026-05-25 (rev 2)
#
# Two related fixes to rehydrate_from_faiss(), both surfaced during the
# pose_state write-side verification:
#
#   1. Seed view_bins with emb_mean in bin 0 (was empty {}). Rehydrated
#      objects were stuck in the LTM diversity gate
#      (ltm_min_view_bins=2 default) because view_bins length 0 < 2 fails
#      the gate; the object got re-scheduled forever but never upserted.
#
#   2. Push rehydrated OIDs into _ltm_heap so they're eligible for the
#      upsert path at all. Without this, collect_ready_for_upsert (which
#      drains _ltm_heap) never even considers rehydrated objects.
#
# Net effect: rehydrated objects can now re-upsert, which means any
# write-side fields added after their original persistence will reach
# disk for those OIDs (e.g. pose_state_at_observation after today's
# write-side fix).
#
# Idempotent. Pre-flight backup.

set -euo pipefail

if [ ! -f rtsm/stores/working_memory.py ]; then
    echo "ERROR: run from repo root" >&2
    exit 1
fi
TS=$(date +%Y%m%d-%H%M%S)
WM="rtsm/stores/working_memory.py"

echo "== rehydrate fixes ($(date -Is)) =="

# Idempotency check: both fixes use unique strings
HAS_VIEWBIN_SEED=$(grep -c "view_bins={0: emb.astype" "$WM" || true)
HAS_HEAP_PUSH=$(grep -c "schedule for LTM upsert eligibility" "$WM" || true)
if [ "$HAS_VIEWBIN_SEED" -ge 1 ] && [ "$HAS_HEAP_PUSH" -ge 1 ]; then
    echo "  already patched; skipping"
    exit 0
fi

cp "$WM" "$WM.bak.$TS"
echo "  backup: $WM.bak.$TS"

python3 <<'PYEOF'
import pathlib
p = pathlib.Path("rtsm/stores/working_memory.py")
src = p.read_text()

# Fix 1: replace empty view_bins={} with seeded view_bins={0: emb_mean}
# Anchor: the specific construction inside rehydrate_from_faiss
fix1_old = (
    "                emb_gallery=np.zeros((0, expected_dim), dtype=np.float16),\n"
    "                view_bins={},\n"
)
fix1_new = (
    "                emb_gallery=np.zeros((0, expected_dim), dtype=np.float16),\n"
    "                # 2026-05-25: seed one view_bin from emb_mean so rehydrated\n"
    "                # objects can pass downstream diversity gates (notably\n"
    "                # ltm_min_view_bins in collect_ready_for_upsert). Without\n"
    "                # this, rehydrated objects with view_bins={} are stuck in a\n"
    "                # re-scheduling loop and never get re-upserted, which means\n"
    "                # they never receive write-side fields added after their\n"
    "                # original persistence (e.g. pose_state_at_observation).\n"
    "                # Bin id 0 is an arbitrary slot; we have no record of the\n"
    "                # original viewpoint. The emb is the same as emb_mean, which\n"
    "                # is consistent with \"what association would see today.\"\n"
    "                view_bins={0: emb.astype(np.float32)},\n"
)
if fix1_old not in src:
    raise SystemExit("ERROR: fix1 anchor not found. Has rehydrate_from_faiss been refactored?")
src2 = src.replace(fix1_old, fix1_new, 1)

# Fix 2: push to _ltm_heap inside the rehydrate insert loop
# Anchor: the lines around _map[o.id] = o
fix2_old = (
    "        # Single-shot lock acquisition for the actual insert.\n"
    "        with self._lock:\n"
    "            for o in new_objects:\n"
    "                self._map[o.id] = o\n"
    "                counts[\"loaded\"] += 1\n"
)
fix2_new = (
    "        # Single-shot lock acquisition for the actual insert.\n"
    "        with self._lock:\n"
    "            for o in new_objects:\n"
    "                self._map[o.id] = o\n"
    "                # 2026-05-25: schedule for LTM upsert eligibility. Without\n"
    "                # this, rehydrated objects are never considered for re-upsert\n"
    "                # (collect_ready_for_upsert only drains _ltm_heap). Any\n"
    "                # write-side fields added after the object's original\n"
    "                # persistence (e.g. pose_state_at_observation) would never\n"
    "                # reach disk for that OID. Change-detection still gates the\n"
    "                # actual write — unchanged objects skip — but the force-\n"
    "                # period check eventually re-upserts them with current\n"
    "                # payload format.\n"
    "                heapq.heappush(self._ltm_heap, (_now_mono(), o.id))\n"
    "                counts[\"loaded\"] += 1\n"
)
if fix2_old not in src2:
    raise SystemExit("ERROR: fix2 anchor not found. Has rehydrate_from_faiss been refactored?")
src3 = src2.replace(fix2_old, fix2_new, 1)

if src3 == src:
    raise SystemExit("ERROR: no changes made")

p.write_text(src3)
print("  ok: both fixes applied")
PYEOF

python3 -c "import ast; ast.parse(open('$WM').read()); print('  syntax-ok')"
echo "== done =="
echo ""
echo "To clear stale FAISS state and let rehydrate work cleanly:"
echo "  docker stop rtsm-dev"
echo "  sudo rm -f /mnt/rtsm-data/model_store/faiss/index.flatip*"
echo "  docker compose -f docker/docker-compose.yml start rtsm-dev"
