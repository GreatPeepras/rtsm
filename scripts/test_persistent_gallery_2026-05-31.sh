#!/usr/bin/env bash
# test_persistent_gallery_2026-05-31.sh
#
# Verify the persistent gallery deploy on live RTSM.
#
# Run sequence:
#   1. Capture pre-state (object count, sample of OIDs + positions)
#   2. Inspect /stats for gallery telemetry
#   3. Check that crops_root has dirs for confirmed objects
#   4. CRITICAL test: simulate the failure mode that motivated the change
#      -- observe an existing object after restart and verify it BINDS to
#      the existing OID rather than spawning a new one.
#
# Usage:
#   bash test_persistent_gallery_2026-05-31.sh
#
# Env overrides:
#   RTSM_URL  (default http://localhost:8002)
#   CROPS_ROOT (default /mnt/rtsm-data/rtsm-workdir/crops)

set -uo pipefail

RTSM_URL="${RTSM_URL:-http://localhost:8002}"
CROPS_ROOT="${CROPS_ROOT:-/mnt/rtsm-data/rtsm-workdir/crops}"

pass() { echo "  PASS: $*"; }
fail() { echo "  FAIL: $*"; FAILED=1; }
info() { echo "  INFO: $*"; }
hr() { echo; echo "============================================================"; echo "$*"; echo "============================================================"; }

FAILED=0

hr "1. RTSM /stats: gallery telemetry"

STATS="$(curl -fsS "$RTSM_URL/stats")" || { fail "/stats unreachable at $RTSM_URL"; exit 1; }
echo "$STATS" | jq '{objects, confirmed, upserts_total, gallery_enabled, gallery_on_disk_oids, gallery_root}'

GALLERY_ENABLED="$(echo "$STATS" | jq -r '.gallery_enabled // false')"
GALLERY_OIDS="$(echo "$STATS" | jq -r '.gallery_on_disk_oids // 0')"
GALLERY_ROOT="$(echo "$STATS" | jq -r '.gallery_root // ""')"
CONFIRMED="$(echo "$STATS" | jq -r '.confirmed // 0')"

if [[ "$GALLERY_ENABLED" == "true" ]]; then
    pass "gallery_enabled=true"
else
    fail "gallery_enabled is not true; deploy may have failed or persist_galleries: false in cfg"
    exit 1
fi

if [[ -n "$GALLERY_ROOT" && "$GALLERY_ROOT" != "null" ]]; then
    pass "gallery_root reported: $GALLERY_ROOT"
else
    fail "gallery_root missing in /stats response"
fi

hr "2. Disk inspection: $CROPS_ROOT"

if [[ ! -d "$CROPS_ROOT" ]]; then
    fail "$CROPS_ROOT does not exist"
else
    DIRS_ON_DISK=$(find "$CROPS_ROOT" -maxdepth 1 -mindepth 1 -type d | wc -l)
    info "directories on disk: $DIRS_ON_DISK"
    info "gallery_on_disk_oids reported by /stats: $GALLERY_OIDS"
    if [[ "$DIRS_ON_DISK" -eq "$GALLERY_OIDS" ]]; then
        pass "/stats matches disk ($DIRS_ON_DISK == $GALLERY_OIDS)"
    else
        fail "/stats mismatch (/stats says $GALLERY_OIDS, disk has $DIRS_ON_DISK)"
    fi
    du -sh "$CROPS_ROOT" 2>/dev/null | awk '{print "  total size: " $1}'
fi

hr "3. Sample object: check disk gallery contents for one confirmed OID"

# Pick the first confirmed object that has a directory on disk
SAMPLE_OID="$(find "$CROPS_ROOT" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | head -1 | xargs -I{} basename {})"
if [[ -z "$SAMPLE_OID" ]]; then
    info "no on-disk OIDs yet (fresh deploy + no observations yet). Skipping section 3."
    info "Run a recording burst and re-run this script."
else
    info "sampling oid=$SAMPLE_OID"
    SAMPLE_DIR="$CROPS_ROOT/$SAMPLE_OID"
    JPEG_COUNT=$(find "$SAMPLE_DIR" -maxdepth 1 -name "*.jpg" 2>/dev/null | wc -l)
    HAS_EMBS=0
    [[ -f "$SAMPLE_DIR/embs.npy" ]] && HAS_EMBS=1
    HAS_MANIFEST=0
    [[ -f "$SAMPLE_DIR/manifest.json" ]] && HAS_MANIFEST=1
    info "  jpegs: $JPEG_COUNT (cap is 10)"
    info "  embs.npy: $([ $HAS_EMBS -eq 1 ] && echo present || echo MISSING)"
    info "  manifest.json: $([ $HAS_MANIFEST -eq 1 ] && echo present || echo MISSING)"
    if [[ $JPEG_COUNT -gt 0 && $HAS_EMBS -eq 1 && $HAS_MANIFEST -eq 1 ]]; then
        pass "sample object has full gallery on disk"
    else
        fail "sample object missing parts of the gallery"
    fi

    # Check embs.npy dimensions roughly match
    if [[ $HAS_EMBS -eq 1 ]]; then
        EMBS_SHAPE=$(python3 -c "
import numpy as np
a = np.load('$SAMPLE_DIR/embs.npy')
print(f'{a.shape} {a.dtype}')
" 2>/dev/null || echo "load_failed")
        info "  embs.npy shape: $EMBS_SHAPE"
        if [[ "$EMBS_SHAPE" == "load_failed" ]]; then
            fail "embs.npy fails to load via numpy"
        fi
    fi

    # Cross-check: does RTSM /objects/<oid>/snapshots/0 return a crop?
    SNAP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$RTSM_URL/objects/$SAMPLE_OID/snapshots?index=0")
    if [[ "$SNAP_STATUS" == "200" ]]; then
        pass "RTSM /objects/<oid>/snapshots returns 200 for sample"
    else
        info "RTSM /objects/<oid>/snapshots returned $SNAP_STATUS (200 expected if WM has the crop)"
    fi
fi

hr "4. Rehydrate-matching test (the actual failure mode this is fixing)"

cat <<EOF
This is the test that yesterday revealed the broken pipeline. After a restart,
do new observations of existing physical objects BIND to the rehydrated OIDs,
or do they spawn NEW OIDs at the same positions?

Manual sequence (cannot fully automate without driving Albert):

  a) Capture pre-test snapshot:
     curl -s "$RTSM_URL/objects?limit=200" | \\
       jq '.objects | map({oid: .id, label: .display_label, xyz: .xyz_world}) | sort_by(.oid)' \\
       > /tmp/objects_before.json
     wc -l /tmp/objects_before.json

  b) Start subscriber and drive Albert past 2-3 KNOWN rehydrated objects.
     Dwell 15-30s on each.

  c) Stop subscriber, capture post-test snapshot:
     curl -s "$RTSM_URL/objects?limit=200" | \\
       jq '.objects | map({oid: .id, label: .display_label, xyz: .xyz_world}) | sort_by(.oid)' \\
       > /tmp/objects_after.json
     wc -l /tmp/objects_after.json

  d) Diff the OID sets:
     comm -23 <(jq -r '.[].oid' /tmp/objects_before.json | sort) \\
              <(jq -r '.[].oid' /tmp/objects_after.json | sort)
     # OIDs only in BEFORE (expected: 0 -- nothing was deleted)

     comm -13 <(jq -r '.[].oid' /tmp/objects_before.json | sort) \\
              <(jq -r '.[].oid' /tmp/objects_after.json | sort)
     # OIDs only in AFTER (NEW OIDs created during observation)

  EXPECTED OUTCOME:
    * 0 NEW OIDs at positions where rehydrated OIDs already exist.
    * Rehydrated OIDs should have growing snapshot_counts (gallery
      getting topped up with fresh observations).

  IF YOU STILL SEE NEW OIDS at existing positions, the gallery is
  present but association.py is not using it strongly enough. That
  would be a separate matching-threshold tuning issue, not a
  persistence problem. Report back with /tmp/objects_*.json contents.

EOF

hr "Summary"

if [[ $FAILED -eq 0 ]]; then
    echo "All automated checks passed."
    echo "Now do the manual rehydrate-matching test in section 4 to confirm"
    echo "the architectural fix is working end-to-end."
else
    echo "Some checks FAILED. See output above."
    exit 1
fi
