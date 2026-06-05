#!/usr/bin/env bash
# Bug 2 fix from handoff_2026-06-01-evening-addendum.md
set -euo pipefail
cd "$(dirname "$0")"
TARGET="rtsm/api/server.py"
[ -f "$TARGET" ] || { echo "FATAL: $TARGET not found"; exit 1; }

# Uniqueness check on both tokens
for needle in 'hasattr(vectors, "remove")' 'vectors.remove(oid)'; do
  n=$(grep -c -F "$needle" "$TARGET" || true)
  if [ "$n" != "1" ]; then
    echo "FATAL: expected exactly 1 occurrence of '$needle', found $n"
    exit 1
  fi
done

python3 - "$TARGET" <<'INNER'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
src = p.read_text()
src = src.replace('hasattr(vectors, "remove")', 'hasattr(vectors, "delete")', 1)
src = src.replace('vectors.remove(oid)',         'vectors.delete([oid])',    1)
p.write_text(src)
print("OK: applied 2 token replacements")
INNER

python3 -m py_compile "$TARGET" && echo "OK: $TARGET compiles"
echo "Done. Now: docker restart rtsm-dev"
