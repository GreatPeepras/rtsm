#!/usr/bin/env bash
# deploy_persistent_gallery_2026-05-31.sh
#
# Land the disk-backed crops+emb_gallery change to working_memory.py.
# Idempotent: backs up the current file with a timestamp suffix; will
# refuse to clobber an existing backup. Run from the directory that
# also contains the new working_memory.py.
#
# Usage:
#   cd <dir containing this script + working_memory.py>
#   bash deploy_persistent_gallery_2026-05-31.sh
#
# What this changes in WorkingMemory:
#   * New _PersistentGallery helper: per-OID dir under cfg.object.crops_root
#     (default /mnt/rtsm-data/rtsm-workdir/crops) with NNNN.jpg files,
#     embs.npy (float16), and manifest.json. Atomic writes via os.replace.
#   * create_object / update_object now mirror image_crops + emb_gallery
#     to disk after each successful write/FIFO-prune.
#   * rehydrate_from_faiss now LOADS crops + emb_gallery from disk. The
#     reference_emb path is preserved as a single-entry gallery fallback
#     when no on-disk gallery exists (e.g. objects named under the old
#     code that were never re-observed after deploy).
#   * remove_object / clear / expire_timeouts / evict_stale now also
#     clean the on-disk gallery for removed OIDs.
#   * max_gallery and max_image_crops defaults bumped from 6 -> 10.
#   * stats() now reports gallery_enabled / gallery_on_disk_oids /
#     gallery_root for live introspection.
#
# What this does NOT change:
#   * association.py: untouched. Existing emb_gallery code path already
#     uses the gallery for matching; we are just making the gallery
#     non-empty after restart.
#   * FAISS sidecar format: untouched. reference_emb / reference_image_path
#     still persist there as before.
#   * Config defaults are backward compatible. Add cfg.object.crops_root
#     and cfg.object.persist_galleries: true to rtsm.yaml only if you
#     want to override the defaults.
#
# Rollback: cp <backup>.py rtsm/stores/working_memory.py && restart.

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
NEW_FILE="$SCRIPT_DIR/working_memory.py"
RTSM_ROOT="${RTSM_ROOT:-$HOME/rtsm}"
TARGET="$RTSM_ROOT/rtsm/stores/working_memory.py"
CROPS_ROOT="${CROPS_ROOT:-/mnt/rtsm-data/rtsm-workdir/crops}"
TS="$(date +%Y%m%d-%H%M%S)"

# --- preflight ---

echo "[deploy] RTSM_ROOT=$RTSM_ROOT"
echo "[deploy] TARGET=$TARGET"
echo "[deploy] NEW_FILE=$NEW_FILE"
echo "[deploy] CROPS_ROOT=$CROPS_ROOT"
echo

if [[ ! -f "$NEW_FILE" ]]; then
    echo "[deploy] ERROR: $NEW_FILE not found"
    echo "[deploy] Place working_memory.py next to this script and re-run."
    exit 1
fi

if [[ ! -f "$TARGET" ]]; then
    echo "[deploy] ERROR: target $TARGET does not exist"
    echo "[deploy] Set RTSM_ROOT if your tree lives elsewhere."
    exit 1
fi

# Syntax check the new file before touching anything
echo "[deploy] syntax check on new working_memory.py..."
python3 -c "import ast, sys
src = open('$NEW_FILE').read()
ast.parse(src)
print(f'  OK ({len(src.splitlines())} lines)')"
echo

# Quick sanity: does the new file have the gallery class?
if ! grep -q "_PersistentGallery" "$NEW_FILE"; then
    echo "[deploy] ERROR: _PersistentGallery class missing from new file. Aborting."
    exit 1
fi

# --- backup ---

BACKUP="${TARGET}.bak.${TS}"
if [[ -f "$BACKUP" ]]; then
    echo "[deploy] ERROR: backup target already exists: $BACKUP"
    exit 1
fi
cp "$TARGET" "$BACKUP"
echo "[deploy] backup: $BACKUP"

# --- swap ---

cp "$NEW_FILE" "$TARGET"
echo "[deploy] installed new working_memory.py"

# --- crops_root ---

# Owned by current user; container will need to read+write it. If you
# run RTSM under a different uid, chown after this.
mkdir -p "$CROPS_ROOT"
echo "[deploy] ensured $CROPS_ROOT exists"
ls -ld "$CROPS_ROOT"

# Show the diff scope (counts only, full diff is verbose)
echo
echo "[deploy] diff summary vs backup:"
diff -u "$BACKUP" "$TARGET" | grep -E "^(\+|\-)" | grep -v "^[\+\-]{3}" | awk '
  /^\+/ {plus++}
  /^\-/ {minus++}
  END {printf "  +%d -%d lines\n", plus+0, minus+0}'

cat <<EOF

[deploy] DONE swapping working_memory.py.

NEXT STEPS:

1. Restart RTSM so the new code is loaded. From $RTSM_ROOT:

     docker compose down
     docker compose up -d

2. Verify the gallery is enabled in the startup logs:

     docker compose logs rtsm 2>&1 | grep -E "persistent gallery|rehydrate"

   You should see:
     [WM] persistent gallery enabled at /mnt/rtsm-data/rtsm-workdir/crops
       (max_gallery=10 max_image_crops=10)
     [WM] rehydrate: loaded N objects ... | gallery: 0 OIDs restored ...

   First post-deploy restart will show 0 OIDs restored (disk is empty).
   THAT IS EXPECTED. The gallery rebuilds as observations come in.

3. Recording burst to populate the new on-disk gallery:

     # Start subscriber so observations flow
     cd $RTSM_ROOT/ingest
     ./run-subscriber.sh --post-to http://localhost:8002/ingest/keyframe \\
         --post-hz 6 --camera-frame realsense_color_optical_frame &

     # Drive Albert through a 4-6 viewpoint pass on the key objects.
     # 30-45s dwell per viewpoint is enough for the gallery to fill.

4. Inspect the on-disk state for a confirmed object:

     curl -s http://localhost:8002/stats | jq '{gallery_enabled, gallery_on_disk_oids, gallery_root}'
     ls -la $CROPS_ROOT/ | head -20
     du -sh $CROPS_ROOT

5. THE ACTUAL TEST -- does rehydrate-matching now work?

     # docker compose restart rtsm   (clean restart, no shutdown race)
     docker compose restart rtsm

     # In the logs, look for the rehydrate line:
     docker compose logs rtsm --tail=50 2>&1 | grep "rehydrate"

     # Expect: gallery: N OIDs restored (X crops, Y embs from disk)
     # where N matches the number of confirmed objects from before restart.

6. Then run the verification script:

     bash test_persistent_gallery_2026-05-31.sh

ROLLBACK if anything goes wrong:

     cp "$BACKUP" "$TARGET"
     docker compose restart rtsm

EOF
