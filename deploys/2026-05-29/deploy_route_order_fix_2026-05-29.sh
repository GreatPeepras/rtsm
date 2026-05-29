#!/bin/bash
# RTSM route-ordering fix — 2026-05-29
#
# FastAPI matches routes in registration order. /objects/{oid} was defined
# before /objects/by_label_user, so any request to /objects/by_label_user
# was caught by the {oid} handler with oid="by_label_user" — which then
# returned {"error":"not_found","id":"by_label_user"} as HTTP 200.
#
# Every "null primary" today was this routing shadow, not a WM miss.
#
# Fix: cut the by_label_user function block out of its current location
# (after the reference endpoints) and paste it just before /objects/{oid}'s
# GET handler. This is a syntactic-level move — no functional change to
# the handler itself, just earlier registration.
#
# Done via Python because regex-aware function extraction is more robust
# than guessing the exact pre-hotfix vs post-hotfix string shape.
#
# Idempotent: detects whether the registration order is already correct.

set -euo pipefail

if [ ! -f rtsm/api/server.py ]; then
    echo "ERROR: run from rtsm repo root (rtsm/api/server.py not found)" >&2
    exit 1
fi
TS=$(date +%Y%m%d-%H%M%S)
SRV_PY="rtsm/api/server.py"

echo "== rtsm route-ordering fix ($(date -Is)) =="

python3 <<'PYEOF'
import pathlib, re, sys

p = pathlib.Path("rtsm/api/server.py")
src = p.read_text()

# Find positions of the two route decorators.
by_label_marker = '@app.get("/objects/by_label_user")'
obj_marker      = '@app.get("/objects/{oid}")'

by_label_pos = src.find(by_label_marker)
obj_pos      = src.find(obj_marker)

if by_label_pos == -1:
    sys.exit("ERROR: /objects/by_label_user route not present — was the reference deploy applied?")
if obj_pos == -1:
    sys.exit("ERROR: /objects/{oid} GET route not found")

# Idempotency check: if by_label_user is already BEFORE /objects/{oid}, nothing to do.
if by_label_pos < obj_pos:
    print("  already ordered correctly, skipping")
    sys.exit(0)

# Find the start of the by_label_user function block. The decorator string lives
# on its own line; we want to capture from the line's indented start (4 spaces).
# Walk backwards from the marker position to find the start of that line.
line_start = src.rfind("\n", 0, by_label_pos) + 1
# Validate that what's between line_start and by_label_pos is just whitespace.
indent = src[line_start:by_label_pos]
if indent.strip() != "":
    sys.exit(f"ERROR: unexpected content before decorator: {indent!r}")

# Find the end of the function block by locating the NEXT @app.* decorator
# (or end of file). The function body is everything between the decorator and
# the next route's decorator.
remainder = src[by_label_pos + len(by_label_marker):]
next_decorator = re.search(
    r'\n[ \t]*@app\.(get|post|put|patch|delete)\(',
    remainder,
)
if next_decorator is None:
    sys.exit("ERROR: could not find end of by_label_user function (no following @app.* decorator)")

# end_pos is the position where the NEXT decorator's line starts (the \n character).
# We want to include the trailing whitespace/blank lines that belong to the by_label_user
# block, so end_pos = start of the next decorator's leading whitespace line.
end_pos = by_label_pos + len(by_label_marker) + next_decorator.start() + 1  # +1 to include the \n itself

block = src[line_start:end_pos]
# Ensure block ends with exactly one blank line for clean separation.
block = block.rstrip("\n") + "\n\n"

# Build the new source: remove the block from its old location, insert before /objects/{oid}.
# Recompute obj_pos because removing the block shifts it (if it was after).
# Actually we already verified by_label_pos > obj_pos, so removing the block doesn't
# affect obj_pos. But after removal, the indices shift — recompute on the new source.
src_without_block = src[:line_start] + src[end_pos:]

# Find /objects/{oid} again in the trimmed source. Walk backwards to the start of that line.
obj_pos_new = src_without_block.find(obj_marker)
if obj_pos_new == -1:
    sys.exit("ERROR: /objects/{oid} GET route disappeared after block removal — aborting")
obj_line_start = src_without_block.rfind("\n", 0, obj_pos_new) + 1

src_final = (
    src_without_block[:obj_line_start]
    + block
    + src_without_block[obj_line_start:]
)

# Sanity: same length minus the moved block.
orig_len = len(src)
final_len = len(src_final)
# After move, length should be unchanged except for the rstrip + "\n\n" tweak.
delta = final_len - orig_len
if abs(delta) > 10:
    sys.exit(f"ERROR: unexpected length delta {delta} after move — refusing to write")

# Backup + write
bak = p.with_suffix(p.suffix + f".bak.{__import__('time').strftime('%Y%m%d-%H%M%S')}")
bak.write_text(src)
print(f"  backed up to {bak}")
p.write_text(src_final)
print(f"  ok: moved by_label_user registration above /objects/{{oid}} (delta={delta:+d} chars)")
PYEOF

python3 -c "
import ast
ast.parse(open('rtsm/api/server.py').read())
print('  syntax-ok: rtsm/api/server.py')
"

echo ""
echo "== done =="
echo "Restart RTSM:"
echo "  docker restart rtsm-dev"
echo ""
echo "Verify the route is now reached (not shadowed):"
echo "  curl -s --get 'http://localhost:8002/objects/by_label_user' \\"
echo "    --data-urlencode 'name=nonexistent' | jq"
echo "Expect: HTTP 404 with {\"detail\":\"No object with label_user='nonexistent'\"}"
echo "(Previously this returned HTTP 200 with {\"error\":\"not_found\",\"id\":\"by_label_user\"})"
