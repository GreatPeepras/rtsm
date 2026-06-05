#!/usr/bin/env bash
# deploy_last_seen_persist_2026-05-28.sh
#
# Persists last_seen_wall_utc through the FAISS sidecar round-trip.
# Three surgical edits to working_memory.py, idempotent, single .bak.
#
#   WRITE: add "last_seen_wall_utc": o.last_seen_wall_utc to BOTH upsert
#          payload dicts in collect_ready_for_upsert() (faiss_client is
#          pass-through, so this alone persists it to the .meta.json sidecar).
#   READ : rehydrate_from_faiss() now reads it from meta instead of stamping
#          now_w -- with legacy fallback to now_w for pre-field sidecars.
#
# WHY NOW: the Tier-2 eviction policy keys on last_seen_wall_utc. Without this,
# every restart resets last-seen to boot time, so TTL clocks never accumulate
# across reboots and eviction would never fire on a long-running deployment.
#
# Usage:
#   ./deploy_last_seen_persist_2026-05-28.sh            # dry-run (default)
#   APPLY=1 ./deploy_last_seen_persist_2026-05-28.sh    # patch
#   WM_PATH=<path> APPLY=1 ./deploy_last_seen_persist_2026-05-28.sh
set -euo pipefail

WM_PATH="${WM_PATH:-rtsm/stores/working_memory.py}"
APPLY="${APPLY:-0}"
[[ -f "$WM_PATH" ]] || { echo "FATAL: target not found: $WM_PATH"; exit 1; }

python3 - "$WM_PATH" "$APPLY" << 'PYEOF'
import sys
wm_path, apply = sys.argv[1], sys.argv[2]
src = open(wm_path, encoding="utf-8").read()

GUARD = '"last_seen_wall_utc": o.last_seen_wall_utc'
if GUARD in src:
    print("SKIP: write-side field already present -- already deployed (idempotent).")
    sys.exit(0)

edits = [
    # (description, old, new) -- each old MUST occur exactly once.
    # Block 1: force_all path (24-space indent, no updated_at).
    ("write block 1 (force_all)",
     '                        "stability": float(o.stability),\n'
     '                        "created_at": o.created_wall_utc,',
     '                        "stability": float(o.stability),\n'
     '                        "last_seen_wall_utc": o.last_seen_wall_utc,\n'
     '                        "created_at": o.created_wall_utc,'),
    # Block 2: scheduled path (20-space indent, has updated_at).
    ("write block 2 (scheduled)",
     '                    "stability": float(o.stability),\n'
     '                    "created_at": o.created_wall_utc,',
     '                    "stability": float(o.stability),\n'
     '                    "last_seen_wall_utc": o.last_seen_wall_utc,\n'
     '                    "created_at": o.created_wall_utc,'),
    # Read side: rehydrate.
    ("read (rehydrate)",
     '                last_seen_wall_utc=now_w,',
     '                last_seen_wall_utc=float(meta.get("last_seen_wall_utc", now_w)),'),
]

for desc, old, new in edits:
    n = src.count(old)
    if n != 1:
        sys.exit(f"FATAL: anchor for [{desc}] occurs {n}x (need exactly 1).")
    src = src.replace(old, new, 1)

compile(src, wm_path, "exec")
print("OK: all 3 edits applied, module compiles clean.")
if apply != "1":
    print("DRY-RUN: no file written. Re-run with APPLY=1 to patch.")
    sys.exit(0)
import time, shutil
bak = f"{wm_path}.bak.{time.strftime('%Y%m%d-%H%M%S')}"
shutil.copy2(wm_path, bak)
open(wm_path, "w", encoding="utf-8").write(src)
print(f"APPLIED. Backup: {bak}")
PYEOF
