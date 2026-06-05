#!/usr/bin/env bash
# deploy_eviction_policy_2026-05-28.sh
#
# Inserts the Tier-2 movability-aware eviction policy into WorkingMemory.
# Anchor-based, idempotent, single timestamped .bak. Dry-run by default.
#
# Adds (all DISABLED until cfg["eviction"]["enabled"]=true):
#   _DEFAULT_EVICTION_TTL_S / _EVICTION_FALLBACK_CLASS  (class consts)
#   _eviction_ttl_s(), _compute_evictable_locked(),
#   select_evictable(), evict_stale()
#
# Usage:
#   ./deploy_eviction_policy_2026-05-28.sh            # dry-run (default)
#   APPLY=1 ./deploy_eviction_policy_2026-05-28.sh    # actually patch
#   WM_PATH=/path/to/working_memory.py APPLY=1 ./...  # override target
#
# NOTE: set WM_PATH to the Execution-Jetson RTSM path before applying.
set -euo pipefail

WM_PATH="${WM_PATH:-rtsm/stores/working_memory.py}"
BLOCK="${BLOCK:-eviction_block.py}"
ANCHOR='    def iter_objects(self) -> Iterable[ObjectState]:'
GUARD='def evict_stale('
APPLY="${APPLY:-0}"

[[ -f "$WM_PATH" ]] || { echo "FATAL: target not found: $WM_PATH"; exit 1; }
[[ -f "$BLOCK"   ]] || { echo "FATAL: block not found: $BLOCK"; exit 1; }

if grep -q "$GUARD" "$WM_PATH"; then
  echo "SKIP: '$GUARD' already present in $WM_PATH -- already deployed (idempotent)."
  exit 0
fi
if ! grep -qF "$ANCHOR" "$WM_PATH"; then
  echo "FATAL: anchor not found in $WM_PATH:"; echo "  $ANCHOR"; exit 1
fi

python3 - "$WM_PATH" "$BLOCK" "$ANCHOR" "$APPLY" << 'PYEOF'
import sys
wm_path, block_path, anchor, apply = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
src = open(wm_path, encoding="utf-8").read()
block = open(block_path, encoding="utf-8").read()
if src.count(anchor) != 1:
    sys.exit(f"FATAL: anchor appears {src.count(anchor)}x (need exactly 1)")
patched = src.replace(anchor, block.rstrip("\n") + "\n\n" + anchor, 1)
# Validate the patched module compiles before writing anything.
compile(patched, wm_path, "exec")
print(f"OK: compiles clean. +{len(block.splitlines())} lines "
      f"({len(src.splitlines())} -> {len(patched.splitlines())}).")
if apply != "1":
    print("DRY-RUN: no file written. Re-run with APPLY=1 to patch.")
    sys.exit(0)
import time, shutil
bak = f"{wm_path}.bak.{time.strftime('%Y%m%d-%H%M%S')}"
shutil.copy2(wm_path, bak)
open(wm_path, "w", encoding="utf-8").write(patched)
print(f"APPLIED. Backup: {bak}")
PYEOF
