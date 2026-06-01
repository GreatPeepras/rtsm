#!/usr/bin/env bash
# Deploy POST /objects/merge: insert merge_objects into working_memory.py
# and the endpoint into server.py.
#
# Idempotent (refuses to patch a file that already contains the new code).
# Takes timestamped backups. Validates syntax of modified files before
# committing the change.
#
# Usage:
#   bash deploy_merge_objects_2026-06-01.sh
#
# Expects these files to be present beside the script:
#   merge_objects_method.py       (paste source for WorkingMemory)
#   objects_merge_endpoint.py     (paste source for server.py)
#
# Override defaults via env vars:
#   WM_PATH       = path to working_memory.py
#   SERVER_PATH   = path to server.py
#   METHOD_SRC    = path to merge_objects_method.py
#   ENDPOINT_SRC  = path to objects_merge_endpoint.py
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WM_PATH="${WM_PATH:-$HOME/rtsm/rtsm/stores/working_memory.py}"
SERVER_PATH="${SERVER_PATH:-$HOME/rtsm/rtsm/api/server.py}"
METHOD_SRC="${METHOD_SRC:-$SCRIPT_DIR/merge_objects_method.py}"
ENDPOINT_SRC="${ENDPOINT_SRC:-$SCRIPT_DIR/objects_merge_endpoint.py}"

TS=$(date -u +%Y-%m-%dT%H-%M-%SZ)

echo "[deploy] WM_PATH       = $WM_PATH"
echo "[deploy] SERVER_PATH   = $SERVER_PATH"
echo "[deploy] METHOD_SRC    = $METHOD_SRC"
echo "[deploy] ENDPOINT_SRC  = $ENDPOINT_SRC"
echo "[deploy] timestamp     = $TS"
echo

for f in "$WM_PATH" "$SERVER_PATH" "$METHOD_SRC" "$ENDPOINT_SRC"; do
    if [[ ! -f "$f" ]]; then
        echo "[deploy] ERROR: required file not found: $f" >&2
        exit 1
    fi
done

# Backups
cp -a "$WM_PATH" "$WM_PATH.bak.$TS"
cp -a "$SERVER_PATH" "$SERVER_PATH.bak.$TS"
echo "[deploy] Backups: $WM_PATH.bak.$TS"
echo "[deploy]          $SERVER_PATH.bak.$TS"
echo

# All real work in Python (string surgery on .py files is safer there).
python3 - "$WM_PATH" "$SERVER_PATH" "$METHOD_SRC" "$ENDPOINT_SRC" <<'PYEOF'
import ast
import sys
import re

wm_path, server_path, method_src_path, endpoint_src_path = sys.argv[1:5]


def die(msg):
    print(f"[deploy] ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def read(p):
    with open(p, "r") as fp:
        return fp.read()


def write(p, content):
    with open(p, "w") as fp:
        fp.write(content)


def validate_syntax(path, content):
    try:
        ast.parse(content)
    except SyntaxError as e:
        die(f"syntax error in modified {path}: {e}")


# ============================================================
# 1) working_memory.py: insert the merge_objects methods
# ============================================================

method_src = read(method_src_path)

# Strip the leading header comment block. The first method begins at
# `    # 2026-06-01: Mode B duplicate consolidation.`
START_MARKER = "    # 2026-06-01: Mode B duplicate consolidation."
idx = method_src.find(START_MARKER)
if idx < 0:
    die(f"start marker not found in {method_src_path}")
methods_code = method_src[idx:]
# Trim trailing whitespace and ensure two blank lines after.
methods_code = methods_code.rstrip() + "\n\n"

wm_src = read(wm_path)

# Idempotency: if merge_objects is already present, skip.
if "def merge_objects(" in wm_src:
    print(f"[wm] merge_objects already present in {wm_path}; skipping insert")
else:
    # Insertion point: immediately before `def iter_objects` (a public
    # WM method that's stable across recent versions).
    target_re = re.compile(
        r"^( {4})def iter_objects\(self\) -> Iterable\[ObjectState\]:",
        re.MULTILINE,
    )
    m = target_re.search(wm_src)
    if not m:
        die("could not locate `def iter_objects(self)` in working_memory.py")
    insert_at = m.start()
    new_src = wm_src[:insert_at] + methods_code + wm_src[insert_at:]
    validate_syntax(wm_path, new_src)
    write(wm_path, new_src)
    print(f"[wm] Inserted merge_objects methods at line "
          f"{wm_src[:insert_at].count(chr(10)) + 1}")

# Re-read to confirm and report.
wm_src_after = read(wm_path)
if "def merge_objects(" not in wm_src_after:
    die("merge_objects still missing from working_memory.py after insert")
print(f"[wm] OK: merge_objects present "
      f"(file is now {wm_src_after.count(chr(10))} lines)")


# ============================================================
# 2) server.py: insert MergeObjectsRequest + the endpoint
# ============================================================

endpoint_src = read(endpoint_src_path)

# Extract the two chunks from objects_merge_endpoint.py.
# Chunk A: the body model (class MergeObjectsRequest)
# Chunk B: the endpoint (    @app.post("/objects/merge"))
A_START = "class MergeObjectsRequest(BaseModel):"
A_END_MARKER = "# ----- (B)"
B_START = "    @app.post(\"/objects/merge\")"

a_idx = endpoint_src.find(A_START)
ab_idx = endpoint_src.find(A_END_MARKER)
b_idx = endpoint_src.find(B_START)
if a_idx < 0 or ab_idx < 0 or b_idx < 0:
    die("could not parse chunks A/B from endpoint source; markers missing")

chunk_a = endpoint_src[a_idx:ab_idx].rstrip() + "\n\n"
# Chunk B is everything from the @app.post line to end-of-file.
chunk_b = endpoint_src[b_idx:].rstrip() + "\n"

server_src = read(server_path)

# Idempotency: if either piece is already present, skip that piece.
if "class MergeObjectsRequest" in server_src:
    print(f"[server] MergeObjectsRequest already present; skipping model insert")
else:
    # Insertion point for the body model: immediately after the
    # PoseStateRequest class definition. Find its end by walking the AST.
    tree = ast.parse(server_src)
    pose_state_end = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "PoseStateRequest":
            pose_state_end = node.end_lineno  # 1-based, inclusive
            break
    if pose_state_end is None:
        die("could not locate class PoseStateRequest in server.py")
    lines = server_src.splitlines(keepends=True)
    # Find the next non-blank line after pose_state_end and insert before it.
    insert_line = pose_state_end  # 0-based index = line number after last line of class
    # advance past trailing blank lines
    while insert_line < len(lines) and lines[insert_line].strip() == "":
        insert_line += 1
    new_lines = (
        lines[:insert_line]
        + [chunk_a + "\n"]
        + lines[insert_line:]
    )
    new_src = "".join(new_lines)
    validate_syntax(server_path, new_src)
    write(server_path, new_src)
    server_src = new_src  # for next stage
    print(f"[server] Inserted MergeObjectsRequest after class PoseStateRequest "
          f"(line {pose_state_end})")

if '@app.post("/objects/merge")' in server_src:
    print(f"[server] /objects/merge endpoint already present; skipping endpoint insert")
else:
    # Insertion point for the endpoint: immediately after the
    # patch_object function. Find via AST.
    tree = ast.parse(server_src)
    patch_object_end = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "patch_object":
            patch_object_end = node.end_lineno
            break
    if patch_object_end is None:
        die("could not locate function patch_object in server.py")
    lines = server_src.splitlines(keepends=True)
    insert_line = patch_object_end
    while insert_line < len(lines) and lines[insert_line].strip() == "":
        insert_line += 1
    new_lines = (
        lines[:insert_line]
        + [chunk_b + "\n"]
        + lines[insert_line:]
    )
    new_src = "".join(new_lines)
    validate_syntax(server_path, new_src)
    write(server_path, new_src)
    print(f"[server] Inserted /objects/merge endpoint after patch_object "
          f"(function ends line {patch_object_end})")

# Final verification.
server_src_after = read(server_path)
if "class MergeObjectsRequest" not in server_src_after:
    die("MergeObjectsRequest missing from server.py after insert")
if '@app.post("/objects/merge")' not in server_src_after:
    die("/objects/merge endpoint missing from server.py after insert")
print(f"[server] OK: both pieces present "
      f"(file is now {server_src_after.count(chr(10))} lines)")
PYEOF

echo
echo "[deploy] === Verification ==="
python3 -c "
import ast
for p in ['$WM_PATH', '$SERVER_PATH']:
    with open(p) as f:
        ast.parse(f.read())
    print(f'[deploy] {p}: parses cleanly')
"

echo
echo "[deploy] Done. Next steps:"
echo "  1) Run tests:"
echo "     docker exec rtsm-dev bash -c \\"
echo "       'cd /workspace/rtsm && PYTHONPATH=. python3 tests/test_merge_objects.py'"
echo "  2) Restart container so the new endpoint becomes live:"
echo "     cd ~/rtsm/docker && docker compose restart rtsm-dev"
echo "  3) Dry-run smoke test against the live API."
echo
echo "[deploy] Rollback if needed:"
echo "     mv $WM_PATH.bak.$TS $WM_PATH"
echo "     mv $SERVER_PATH.bak.$TS $SERVER_PATH"
echo "     cd ~/rtsm/docker && docker compose restart rtsm-dev"
