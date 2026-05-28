#!/bin/bash
# Deploy Camera Rename — Execution side, 2026-05-26
#
# Updates ingest/src/subscriber.py so RTSM ingest subscribes to the
# renamed realsense topics. Albert's docker launch is being changed in
# parallel to publish under camera_name:=realsense; the resulting topic
# prefix becomes /camera/realsense/... (namespace stays "camera", node
# name changes from "camera" to "realsense").
#
# Three constant flips at the top of subscriber.py:
#   COLOR_TOPIC, DEPTH_TOPIC, COLOR_INFO_TOPIC
#
# Idempotent. Backs up before editing.
#
# This patch alone is not sufficient — Albert's docker launch must also
# be updated to use camera_name:=realsense AND the base-to-camera static
# transform must be updated from "camera_link" to "realsense_link".
# Coordinate the deploy so both sides flip together (see ROLLOUT below).

set -euo pipefail

SUBSCRIBER_PY="${SUBSCRIBER_PY:-/home/peep/rtsm/ingest/src/subscriber.py}"

if [ ! -f "$SUBSCRIBER_PY" ]; then
    echo "ERROR: $SUBSCRIBER_PY not found." >&2
    echo "  Set SUBSCRIBER_PY=... and re-run if your repo lives elsewhere." >&2
    exit 1
fi

TS=$(date +%Y%m%d-%H%M%S)

echo "== camera rename — Execution side ($(date -Is)) =="
echo "   target: $SUBSCRIBER_PY"

cp "$SUBSCRIBER_PY" "$SUBSCRIBER_PY.bak.$TS"
echo "[backup] $SUBSCRIBER_PY.bak.$TS"

python3 <<PYEOF
import pathlib, sys
p = pathlib.Path("$SUBSCRIBER_PY")
src = p.read_text()
orig = src

edits = [
    (
        'COLOR_TOPIC = "/camera/camera/color/image_raw/compressed"',
        'COLOR_TOPIC = "/camera/realsense/color/image_raw/compressed"',
        "COLOR_TOPIC",
    ),
    (
        'DEPTH_TOPIC = "/camera/camera/aligned_depth_to_color/image_raw/compressedDepth"',
        'DEPTH_TOPIC = "/camera/realsense/aligned_depth_to_color/image_raw/compressedDepth"',
        "DEPTH_TOPIC",
    ),
    (
        'COLOR_INFO_TOPIC = "/camera/camera/color/camera_info"',
        'COLOR_INFO_TOPIC = "/camera/realsense/color/camera_info"',
        "COLOR_INFO_TOPIC",
    ),
]

for i, (old, new, label) in enumerate(edits, 1):
    if new in src and old not in src:
        print(f"[{i}/3] {label}: already renamed")
        continue
    if src.count(old) != 1:
        sys.exit(f"[{i}/3] FAIL: anchor for {label} not unique ({src.count(old)} matches)")
    src = src.replace(old, new, 1)
    print(f"[{i}/3] {label}: renamed")

# Optional bonus: update the descriptive comments at the top of the file
# so future readers see the correct topic names. Doesn't change behaviour.
comment_edits = [
    (
        "  - color: /camera/camera/color/image_raw/compressed",
        "  - color: /camera/realsense/color/image_raw/compressed",
    ),
    (
        "  - depth: /camera/camera/aligned_depth_to_color/image_raw/compressedDepth",
        "  - depth: /camera/realsense/aligned_depth_to_color/image_raw/compressedDepth",
    ),
]
for old, new in comment_edits:
    if new in src:
        continue
    if src.count(old) == 1:
        src = src.replace(old, new, 1)
print("[bonus] docstring topic refs updated")

if src == orig:
    print("(no changes written — already fully patched)")
else:
    p.write_text(src)
    print(f"wrote {p}")

import ast
ast.parse(p.read_text())
print("syntax OK")
PYEOF

echo
echo "== done =="
echo
echo "Verify the edit:"
echo "  grep -n 'COLOR_TOPIC\|DEPTH_TOPIC\|COLOR_INFO_TOPIC' $SUBSCRIBER_PY"
echo
echo "When you launch subscriber.py, also update --camera-frame:"
echo "  python3 subscriber.py ... --camera-frame realsense_color_optical_frame ..."
echo "  (The old default was camera_color_optical_frame; after the rename"
echo "   the realsense's optical frame name changes to realsense_*.)"
echo
echo "If you prefer to bake the new default into the code, find the argparse"
echo "  add_argument call for '--camera-frame' (around line ~750 or so) and"
echo "  change default='camera_color_optical_frame' to 'realsense_color_optical_frame'."
echo
echo "== ROLLOUT — run on both Jetsons in this order: =="
echo "  1. (Execution) Stop the ingest subscriber if running"
echo "  2. (Albert)    Stop the realsense docker:  docker stop albert_rs_camera"
echo "  3. (Albert)    Apply the Albert-side patch (camera_name + static TF)"
echo "  4. (Execution) Apply this patch  ← you are here"
echo "  5. (Albert)    Restart realsense docker"
echo "  6. (Execution) Restart ingest subscriber (with --camera-frame realsense_color_optical_frame)"
echo "  7. Verify: 'ros2 topic hz /camera/realsense/color/image_raw/compressed' shows ~6 Hz"
echo "  8. Verify: subscriber.py logs show synced frame pairs arriving"
