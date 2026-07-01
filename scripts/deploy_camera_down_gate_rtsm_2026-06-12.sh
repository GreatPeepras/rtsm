#!/usr/bin/env bash
# =============================================================================
# deploy_camera_down_gate_rtsm_2026-06-12.sh
#
# RTSM-side (.53) half of the camera-down safety gate.
#
# WHAT IT DOES
#   Adds an optional `max_stale_s: Optional[int] = None` query parameter to
#   GET /search/semantic. When set, results whose observation freshness
#   (now - last_seen_mono) exceeds max_stale_s — OR whose freshness can't be
#   determined (faiss_meta-only / source=="none", which carry no monotonic
#   timestamp) — are dropped. Default None == current behavior, so every
#   existing caller (recall path, UI, audits) is unaffected.
#
# WHY
#   Server-side enforcement so the freshness gate can't be bypassed by a
#   caller that forgets to pass it. Albert's name_object passes
#   max_stale_s=10 matching its local mtime gate. See the Albert-side
#   script header for the 2026-06-11 mis-anchored-OID root cause.
#
# SEMANTICS NOTE (intentional)
#   last_seen_mono is process-monotonic. After an RTSM restart, monotonic
#   clock resets; objects loaded from FAISS have last_seen_mono == 0.0 and
#   are therefore treated as "freshness unknown" -> dropped when max_stale_s
#   is set. That is the SAFE direction for name_object: right after a restart
#   Albert has not freshly observed anything, so refusing to name is correct.
#   Once Albert observes the object again, last_seen_mono updates and naming
#   works. This matches the gate's intent (don't label things you aren't
#   currently looking at) and degrades safe.
#
# MARKER
#   CAMERA_DOWN_GATE_2026-06-12   (greppable; idempotency anchor)
#
# MODES
#   --dryrun / --apply / --revert / --check   (see Albert-side script)
#
# TARGET
#   ~/rtsm/rtsm/api/server.py   (on Execution .53)
#
# AFTER APPLY
#   Restart rtsm-dev:
#     cd ~/rtsm/docker && docker compose restart rtsm-dev
#   (server.py is bind-mounted into the container; restart re-imports it.)
# =============================================================================
set -u

MARKER="CAMERA_DOWN_GATE_2026-06-12"
TARGET="${RTSM_SERVER_PATH:-$HOME/rtsm/rtsm/api/server.py}"
MODE="--dryrun"

for arg in "$@"; do
    case "$arg" in
        --dryrun|--apply|--revert|--check) MODE="$arg" ;;
        -h|--help) sed -n '2,48p' "$0"; exit 0 ;;
        *) echo "Unknown arg: $arg" >&2; exit 2 ;;
    esac
done

if [[ ! -f "$TARGET" ]]; then
    echo "FATAL: target not found: $TARGET" >&2
    echo "Set RTSM_SERVER_PATH if it lives elsewhere." >&2
    exit 1
fi

PYBIN="$(command -v python3 || true)"
if [[ -z "$PYBIN" ]]; then
    echo "FATAL: python3 not found on PATH." >&2
    exit 1
fi

if [[ "$MODE" == "--check" ]]; then
    n="$(grep -c "$MARKER" "$TARGET" || true)"
    echo "Target : $TARGET"
    echo "Marker : $MARKER"
    echo "Count  : $n"
    [[ "$n" -ge 1 ]] && echo "State  : APPLIED" || echo "State  : NOT APPLIED"
    exit 0
fi

if [[ "$MODE" == "--revert" ]]; then
    latest_bak="$(ls -1t "${TARGET}.bak."* 2>/dev/null | head -n1 || true)"
    if [[ -z "$latest_bak" ]]; then
        echo "No ${TARGET}.bak.* backups found; nothing to revert." >&2
        exit 1
    fi
    echo "Reverting $TARGET  <-  $latest_bak"
    cp -p "$latest_bak" "$TARGET"
    echo "Done. Restart rtsm-dev for the revert to take effect:"
    echo "  cd ~/rtsm/docker && docker compose restart rtsm-dev"
    exit 0
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
NEWFILE="$WORK/server.new.py"

"$PYBIN" - "$TARGET" "$NEWFILE" "$MARKER" <<'PYEOF'
import sys, io
src_path, out_path, marker = sys.argv[1], sys.argv[2], sys.argv[3]
with io.open(src_path, "r", encoding="utf-8") as f:
    src = f.read()

if marker in src:
    with io.open(out_path, "w", encoding="utf-8") as f:
        f.write(src)
    print("ALREADY_APPLIED")
    sys.exit(0)

# --- ANCHOR 1: add max_stale_s to the function signature. ---
ANCHOR_1 = (
'        include_snapshot: bool = False,\n'
'        pose_state: str = "on_floor",   # "on_floor" | "elevated" | "any"\n'
'    ) -> Dict[str, Any]:\n'
)
REPL_1 = (
'        include_snapshot: bool = False,\n'
'        pose_state: str = "on_floor",   # "on_floor" | "elevated" | "any"\n'
'        max_stale_s: Optional[int] = None,  # CAMERA_DOWN_GATE_2026-06-12\n'
'    ) -> Dict[str, Any]:\n'
)
if ANCHOR_1 not in src:
    print("FAIL_ANCHOR_1", file=sys.stderr); sys.exit(11)
if src.count(ANCHOR_1) != 1:
    print(f"FAIL_ANCHOR_1_NONUNIQUE count={src.count(ANCHOR_1)}", file=sys.stderr); sys.exit(12)
src = src.replace(ANCHOR_1, REPL_1, 1)

# --- ANCHOR 2: insert freshness filter just before the pose_state filter. ---
# The pose_state filter block begins with this exact comment + guard.
ANCHOR_2 = (
'            # For source=="none": filter them out unless pose_state=="any".\n'
'            if pose_state != "any":\n'
)
REPL_2 = (
'            # For source=="none": filter them out unless pose_state=="any".\n'
'\n'
'            # CAMERA_DOWN_GATE_2026-06-12: optional observation-freshness\n'
'            # filter. When max_stale_s is provided, drop matches whose\n'
'            # last_seen_mono is older than that, OR whose freshness is\n'
'            # unknown (faiss_meta-only / source=="none" carry no monotonic\n'
'            # timestamp; after a restart even WM objects start at 0.0).\n'
'            # Dropping unknown-freshness is the SAFE direction: name_object\n'
'            # should refuse rather than label something not freshly seen.\n'
'            # Default None == no filtering (every other caller unaffected).\n'
'            if max_stale_s is not None:\n'
'                if obj is not None:\n'
'                    _ls_mono = float(getattr(obj, "last_seen_mono", 0.0) or 0.0)\n'
'                    _age = (time.monotonic() - _ls_mono) if _ls_mono > 0 else None\n'
'                else:\n'
'                    _age = None  # faiss_meta-only / none: no monotonic time\n'
'                if _age is None or _age > max_stale_s:\n'
'                    continue\n'
'\n'
'            # For source=="none": filter them out unless pose_state=="any".\n'
'            if pose_state != "any":\n'
)
if ANCHOR_2 not in src:
    print("FAIL_ANCHOR_2", file=sys.stderr); sys.exit(13)
if src.count(ANCHOR_2) != 1:
    print(f"FAIL_ANCHOR_2_NONUNIQUE count={src.count(ANCHOR_2)}", file=sys.stderr); sys.exit(14)
src = src.replace(ANCHOR_2, REPL_2, 1)

# --- Safety: ensure `Optional` and `time` are importable in this module. ---
# Both are near-universally already imported in server.py; verify and flag
# rather than silently inject (keeps the patch surface honest).
warn = []
if "Optional" not in src:
    warn.append("Optional")
# `time` is used elsewhere in server.py (_obj_summary uses time.monotonic()),
# so it should already be imported. Verify defensively.
import re as _re
if not _re.search(r'(^|\n)\s*import time(\s|$)', src) and "time.monotonic" not in src.replace("time.monotonic()", "", 0):
    # crude check; time.monotonic already used in _obj_summary so this should pass
    pass

with io.open(out_path, "w", encoding="utf-8") as f:
    f.write(src)
if warn:
    print("PATCHED_WITH_WARN:" + ",".join(warn))
else:
    print("PATCHED")
PYEOF

PYRC=$?
if [[ $PYRC -ne 0 ]]; then
    echo "FATAL: patch builder failed (rc=$PYRC). No changes made." >&2
    case $PYRC in
        11|12) echo "  -> ANCHOR 1 (function signature) not found/unique. Source drifted." >&2 ;;
        13|14) echo "  -> ANCHOR 2 (pose_state filter comment) not found/unique. Source drifted." >&2 ;;
    esac
    exit $PYRC
fi

SENTINEL="$("$PYBIN" - "$TARGET" "$MARKER" <<'PYEOF2'
import sys, io
src_path, marker = sys.argv[1], sys.argv[2]
with io.open(src_path, "r", encoding="utf-8") as f:
    src = f.read()
print("ALREADY_APPLIED" if marker in src else "NEEDS_PATCH")
PYEOF2
)"

if [[ "$SENTINEL" == "ALREADY_APPLIED" ]]; then
    echo "Marker already present in $TARGET — nothing to do (idempotent)."
    exit 0
fi

if grep -q "^Optional" "$NEWFILE" 2>/dev/null; then :; fi
if ! grep -qE "(from typing import .*Optional|import typing)" "$NEWFILE"; then
    echo "WARNING: could not confirm 'Optional' is imported in server.py." >&2
    echo "         The signature uses Optional[int]. Verify the import exists" >&2
    echo "         (it is used elsewhere in server.py, e.g. ObjectPatch), or" >&2
    echo "         the module will fail to import on restart." >&2
fi

if ! "$PYBIN" -c "import ast,sys; ast.parse(open(sys.argv[1],encoding='utf-8').read())" "$NEWFILE"; then
    echo "FATAL: AST validation FAILED on patched candidate. Not writing." >&2
    exit 20
fi
echo "AST validation: OK"

if [[ "$MODE" == "--dryrun" ]]; then
    echo "===== DRYRUN DIFF ($TARGET) ====="
    if command -v diff >/dev/null 2>&1; then
        diff -u "$TARGET" "$NEWFILE" || true
    else
        grep -n "$MARKER" "$NEWFILE" || true
    fi
    echo "===== END DRYRUN (no changes written) ====="
    echo
    echo "To apply:  $0 --apply"
    exit 0
fi

if [[ "$MODE" == "--apply" ]]; then
    STAMP="$(date +%Y%m%d-%H%M%S)"
    BAK="${TARGET}.bak.${STAMP}"
    cp -p "$TARGET" "$BAK"
    cp -p "$NEWFILE" "$TARGET"
    echo "Applied. Backup: $BAK"
    echo
    grep -n "$MARKER" "$TARGET" | sed 's/^/  /'
    echo
    echo "NEXT (Execution): restart rtsm-dev so the change goes live:"
    echo "  cd ~/rtsm/docker && docker compose restart rtsm-dev"
    echo
    echo "Smoke test (after restart):"
    echo "  # 1. Default (no filter) still returns matches:"
    echo "  curl -s 'http://localhost:8002/search/semantic?query=desk&top_k=1&pose_state=any' | jq '.results | length'"
    echo "  # 2. Absurdly strict freshness should return 0 (nothing seen <1s ago):"
    echo "  curl -s 'http://localhost:8002/search/semantic?query=desk&top_k=5&pose_state=any&max_stale_s=1' | jq '.results | length'"
    exit 0
fi
