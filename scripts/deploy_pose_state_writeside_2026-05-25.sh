#!/bin/bash
# Deploy pose_state write-side fix — 2026-05-25
#
# Adds "pose_state_at_observation": o.pose_state_at_observation to both
# upsert-payload constructions in WorkingMemory.collect_ready_for_upsert():
#   - force-flush path (force_all=True, used in replay mode)
#   - normal-flush path (heap-drain, used in live ingest)
#
# Without this, the May-22 two-tier memory tag is set on ObjectState in
# memory but stripped before being written to the FAISS sidecar. Confirmed
# May 25 via inspection of index.flatip.meta.json: all 35 entries showed
# pose_state=MISSING.
#
# Idempotent. Pre-flight backup taken.

set -euo pipefail

if [ ! -f rtsm/stores/working_memory.py ]; then
    echo "ERROR: run from repo root" >&2
    exit 1
fi
TS=$(date +%Y%m%d-%H%M%S)
WM="rtsm/stores/working_memory.py"

echo "== pose_state write-side fix ($(date -Is)) =="

# Check if already applied (uniquely identifies our addition)
if grep -q '"pose_state_at_observation": o.pose_state_at_observation,' "$WM"; then
    n=$(grep -c '"pose_state_at_observation": o.pose_state_at_observation,' "$WM")
    if [ "$n" -ge 2 ]; then
        echo "  already patched ($n occurrences); skipping"
        exit 0
    else
        echo "WARNING: partial patch detected ($n occurrence; expected 2). Aborting." >&2
        echo "         Inspect rtsm/stores/working_memory.py manually before retry." >&2
        exit 1
    fi
fi

cp "$WM" "$WM.bak.$TS"
echo "  backup: $WM.bak.$TS"

# Insert the field after "movability_class" in BOTH payload dicts.
# Uses Python because the two occurrences have different indentation
# (24 spaces in the force-flush path, 20 in the normal path).
python3 <<'PYEOF'
import pathlib
p = pathlib.Path("rtsm/stores/working_memory.py")
src = p.read_text()

# Two distinct anchors — same content, different indentation. We match each
# uniquely by including the next line in the anchor (label_confidence).
patches = [
    # Force-flush path (24-space indent)
    (
        '                        "movability_class": o.movability_class,\n'
        '                        "label_confidence":',
        '                        "movability_class": o.movability_class,\n'
        '                        "pose_state_at_observation": o.pose_state_at_observation,\n'
        '                        "label_confidence":'
    ),
    # Normal-flush path (20-space indent)
    (
        '                    "movability_class": o.movability_class,\n'
        '                    "label_confidence":',
        '                    "movability_class": o.movability_class,\n'
        '                    "pose_state_at_observation": o.pose_state_at_observation,\n'
        '                    "label_confidence":'
    ),
]

new_src = src
for old, new in patches:
    if old not in new_src:
        raise SystemExit(
            f"ERROR: anchor not found:\n{old!r}\n"
            f"Has collect_ready_for_upsert been refactored?"
        )
    new_src = new_src.replace(old, new, 1)

if new_src == src:
    raise SystemExit("ERROR: no changes made")

# Verify both insertions happened
n = new_src.count('"pose_state_at_observation": o.pose_state_at_observation,')
if n != 2:
    raise SystemExit(f"ERROR: expected 2 insertions, got {n}")

p.write_text(new_src)
print(f"  ok: inserted in {n} payload dicts")
PYEOF

python3 -c "import ast; ast.parse(open('$WM').read()); print('  syntax-ok')"
echo "== done =="
echo ""
echo "Existing FAISS sidecar entries will not get the field retroactively."
echo "Restart RTSM and let new upserts repopulate, or clear the index:"
echo "  rm /mnt/rtsm-data/model_store/faiss/index.flatip*"
echo "  docker compose -f docker/docker-compose.yml restart rtsm-dev"
