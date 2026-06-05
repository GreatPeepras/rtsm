#!/usr/bin/env bash
# deploy_serve_mode_rename_2026-05-28.sh  [EXECUTION / RTSM serve mode]
#
# Makes PATCH /objects/{oid} work in SERVE mode (was 405). All contained in
# frozen_wm.py; server.py is UNCHANGED (its handler stops 405-ing the moment
# FrozenWorkingMemory grows update_user_fields). Three idempotent edits:
#   1) module consts: _UNSET + _VALID_MOVABILITY
#   2) READ fix: _record_to_object reads label_user/display_label/movability_class
#      back from the sidecar (previously dropped -> names invisible in serve mode)
#   3) WRITE path: update_user_fields() + _persist_user_fields() (in-memory +
#      atomic sidecar write-through; single-writer in serve mode)
#
# Usage:
#   ./deploy_serve_mode_rename_2026-05-28.sh            # dry-run
#   APPLY=1 ./deploy_serve_mode_rename_2026-05-28.sh    # patch
#   FW_PATH=<path> BLOCK=<file> APPLY=1 ./...
set -euo pipefail
FW_PATH="${FW_PATH:-rtsm/stores/frozen_wm.py}"
BLOCK="${BLOCK:-serve_rename_methods.py}"
APPLY="${APPLY:-0}"
[[ -f "$FW_PATH" ]] || { echo "FATAL: target not found: $FW_PATH"; exit 1; }
[[ -f "$BLOCK"   ]] || { echo "FATAL: method block not found: $BLOCK"; exit 1; }

python3 - "$FW_PATH" "$BLOCK" "$APPLY" << 'PYEOF'
import sys
fw, block_path, apply = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(fw, encoding="utf-8").read()
methods = open(block_path, encoding="utf-8").read()

if "def update_user_fields" in src:
    print("SKIP: update_user_fields already present -- already deployed (idempotent).")
    sys.exit(0)

# Edit 1: module consts after the logger line.
anc1 = "logger = logging.getLogger(__name__)\n"
consts = (
    "logger = logging.getLogger(__name__)\n\n"
    "# 2026-05-28: serve-mode rename support.\n"
    "_UNSET = object()\n"
    "_VALID_MOVABILITY = frozenset({\n"
    '    "permanent", "static", "semi_static",\n'
    '    "movable", "roaming", "ephemeral",\n'
    "})\n"
)
if src.count(anc1) != 1:
    sys.exit(f"FATAL: logger anchor occurs {src.count(anc1)}x")
src = src.replace(anc1, consts, 1)

# Edit 2: READ fix -- pull user fields back from the record.
anc2 = "        # extras that some endpoints read\n"
readfix = (
    '        label_user=rec.get("label_user"),\n'
    '        display_label=(rec.get("display_label")\n'
    '                       or rec.get("label_user")\n'
    '                       or rec.get("label_primary")),\n'
    '        movability_class=rec.get("movability_class"),\n'
    "        # extras that some endpoints read\n"
)
if src.count(anc2) != 1:
    sys.exit(f"FATAL: read-fix anchor occurs {src.count(anc2)}x")
src = src.replace(anc2, readfix, 1)

# Edit 3: insert the write methods before the "deliberately absent" comment.
anc3 = "    # ---- tracking/mutation API: deliberately absent ----\n"
if src.count(anc3) != 1:
    sys.exit(f"FATAL: methods anchor occurs {src.count(anc3)}x")
src = src.replace(anc3, methods.rstrip("\n") + "\n\n" + anc3, 1)

compile(src, fw, "exec")
print(f"OK: 3 edits applied, module compiles clean (+{len(methods.splitlines())} method lines).")
if apply != "1":
    print("DRY-RUN: no file written. Re-run with APPLY=1 to patch.")
    sys.exit(0)
import time, shutil
bak = f"{fw}.bak.{time.strftime('%Y%m%d-%H%M%S')}"
shutil.copy2(fw, bak)
open(fw, "w", encoding="utf-8").write(src)
print(f"APPLIED. Backup: {bak}")
PYEOF
