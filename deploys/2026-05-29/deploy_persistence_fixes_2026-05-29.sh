#!/bin/bash
# RTSM persistence fixes — 2026-05-29
#
# Two follow-on fixes after today's voice-test marathon:
#
#   1. RTSM_REFS_DIR default points at /mnt/rtsm-data/refs, which is NOT
#      bind-mounted into the rtsm-dev container — files end up only in the
#      container's overlay filesystem and vanish on `docker rm`. Move the
#      default to /workspace/workdir/refs, which IS bind-mounted (it's the
#      same physical disk where FAISS lives), so reference images persist
#      across container recreations and are visible on the host at
#      /mnt/rtsm-data/rtsm-workdir/refs/.
#
#   2. update_user_fields (the PATCH endpoint's target) modifies WM in-place
#      but does NOT push to _ltm_heap, so PATCH'd label_user / movability
#      changes wait indefinitely for the object to be re-observed before
#      they hit FAISS. Any restart in the window loses the user's label.
#      Force-flush by re-invoking set_object_reference() with current values
#      after the PATCH succeeds — its lock-protected heap push is exactly
#      the side effect we need.
#
# Idempotent.

set -euo pipefail

if [ ! -f rtsm/api/server.py ]; then
    echo "ERROR: run from rtsm repo root (rtsm/api/server.py not found)" >&2
    exit 1
fi
TS=$(date +%Y%m%d-%H%M%S)
SRV_PY="rtsm/api/server.py"

echo "== rtsm persistence fixes ($(date -Is)) =="

# ---------------------------------------------------------------------------
# Fix 1: change RTSM_REFS_DIR default to a bind-mounted path
# ---------------------------------------------------------------------------
if grep -q '"/workspace/workdir/refs"' "$SRV_PY"; then
    echo "[1/2] refs-dir default: already patched, skipping"
else
    cp "$SRV_PY" "$SRV_PY.bak.$TS"
    echo "[1/2] backed up to $SRV_PY.bak.$TS"

    # The string appears twice (single-item endpoint + bulk endpoint), both
    # identical. A single str.replace with count=2 would handle both, but
    # for clarity we do it in a loop in Python.
    python3 <<'PYEOF'
import pathlib, sys
p = pathlib.Path("rtsm/api/server.py")
src = p.read_text()
old = '"RTSM_REFS_DIR", "/mnt/rtsm-data/refs"'
new = '"RTSM_REFS_DIR", "/workspace/workdir/refs"'
n = src.count(old)
if n == 0:
    sys.exit("ERROR [1/2]: RTSM_REFS_DIR default anchor not found")
if n != 2:
    sys.exit(f"ERROR [1/2]: expected 2 occurrences, found {n}")
src = src.replace(old, new)
p.write_text(src)
print(f"  ok [1/2]: refs-dir default changed in {n} place(s)")
print("           inside container: /workspace/workdir/refs")
print("           on host:          /mnt/rtsm-data/rtsm-workdir/refs")
PYEOF
fi

# ---------------------------------------------------------------------------
# Fix 2: force-flush PATCH'd user fields to FAISS
# ---------------------------------------------------------------------------
if grep -q "2026-05-29: force-flush PATCH" "$SRV_PY"; then
    echo "[2/2] PATCH force-flush: already patched, skipping"
else
    if [ ! -f "$SRV_PY.bak.$TS" ]; then
        cp "$SRV_PY" "$SRV_PY.bak.$TS"
        echo "[2/2] backed up to $SRV_PY.bak.$TS"
    fi

    python3 <<'PYEOF'
import pathlib, sys
p = pathlib.Path("rtsm/api/server.py")
src = p.read_text()

# Anchor: the PATCH success branch.
anchor = '''        try:
            o = working_memory.update_user_fields(oid, **kwargs)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if o is None:
            raise HTTPException(status_code=404, detail=f"Object {oid} not found")
        return _obj_detail(o)'''

replacement = '''        try:
            o = working_memory.update_user_fields(oid, **kwargs)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if o is None:
            raise HTTPException(status_code=404, detail=f"Object {oid} not found")

        # 2026-05-29: force-flush PATCH'd label_user/movability to FAISS.
        # update_user_fields modifies WM only; without this push the change
        # waits for natural re-observation, and a restart in that window
        # loses the user's label. Re-asserting reference state via
        # set_object_reference triggers the same lock-protected heap push
        # that pinning a reference image already does.
        if (getattr(o, "confirmed", False)
                and hasattr(working_memory, "set_object_reference")):
            try:
                working_memory.set_object_reference(
                    oid,
                    image_path=getattr(o, "reference_image_path", None),
                    embedding=getattr(o, "reference_emb", None),
                )
            except Exception as e:
                logger.warning(
                    f"PATCH force-flush for {oid} failed: {e}"
                )

        return _obj_detail(o)'''

if anchor not in src:
    sys.exit("ERROR [2/2]: PATCH success-path anchor not found")
src = src.replace(anchor, replacement, 1)
p.write_text(src)
print("  ok [2/2]: PATCH endpoint force-flushes user fields to FAISS")
PYEOF
fi

python3 -c "
import ast
ast.parse(open('rtsm/api/server.py').read())
print('  syntax-ok: rtsm/api/server.py')
"

echo ""
echo "== done =="
echo ""
echo "Apply:"
echo "  docker restart rtsm-dev"
echo ""
echo "After restart, on the next voice-naming test:"
echo "  - The PATCH that pins label_user will immediately trigger an LTM upsert."
echo "  - The reference JPEG lands at /workspace/workdir/refs/<oid>.jpg inside"
echo "    the container, visible from the host at:"
echo "      /mnt/rtsm-data/rtsm-workdir/refs/<oid>.jpg"
echo ""
echo "To migrate the existing gloves JPEG out of the container overlay (so"
echo "you don't have to re-name them after this restart):"
echo "  docker cp rtsm-dev:/mnt/rtsm-data/refs/7543b81b2084438f.jpg \\"
echo "    /mnt/rtsm-data/rtsm-workdir/refs/"
echo "  # then on Albert, re-PATCH the gloves label_user so it sticks:"
echo "  #   curl -X PATCH http://192.168.0.53:8002/objects/7543b81b2084438f \\"
echo "  #     -H 'Content-Type: application/json' -d '{\"label_user\":\"gloves\"}'"
