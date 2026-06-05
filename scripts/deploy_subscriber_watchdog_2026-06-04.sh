#!/bin/bash
# Deploy: subscription-staleness watchdog for ingest/src/subscriber.py
# 2026-06-04
#
# What this adds:
#   A ROS2 timer (fires every 30s) checks `time.monotonic() - last_synced_mono`.
#   If no synced color+depth pair has arrived within --watchdog-no-frame-s
#   seconds (default 180), raise SystemExit so docker's `restart: unless-stopped`
#   recycles the container with a fresh DDS subscription.
#
# Why:
#   Covers the "Execution Jetson boots first, Albert hours later" scenario.
#   When subscriber.py starts and Albert isn't reachable yet, DDS late-join
#   discovery SHOULD bind topics later — but empirically it sometimes
#   doesn't (third recurrence of this bug). Restarting the python process
#   gives DDS a fresh start. Restart is cheap (<5s, no GPU work).
#
# Default 180s rationale:
#   - Long enough to ride out brief blips and Albert's boot sequence
#   - Short enough to recover fast: max 180s + 30s tick = ~210s worst-case
#     wait after Albert publishes before fresh subscription is established
#   - During multi-hour Albert-off: ~20 restarts/hr; cheap, just log noise
#
# Idempotent. Backs up. Validates Python syntax. Bind-mount means no
# image rebuild needed — restart the container and you're live.

set -euo pipefail

TARGET="${HOME}/rtsm/ingest/src/subscriber.py"
if [ ! -f "$TARGET" ]; then
    echo "ERROR: $TARGET not found." >&2
    exit 1
fi

# Idempotency
if grep -q 'PATCH 20260603: subscription-staleness watchdog' "$TARGET"; then
    echo "Already patched (watchdog marker present)."
    exit 0
fi

TS=$(date +%Y%m%d-%H%M%S)
BACKUP="${TARGET}.bak.${TS}"
cp "$TARGET" "$BACKUP"
echo "Backed up: $BACKUP"

python3 <<'PYEOF'
import pathlib, sys
p = pathlib.Path.home() / "rtsm/ingest/src/subscriber.py"
src = p.read_text()

# ----- Edit 1: add watchdog_no_frame_s param to __init__ -----
anchor1 = 'post_hz: float = 2.0,  # PATCH 20260518: default tuned for bursty workload, see backpressure-2026-05-18'
if anchor1 not in src:
    sys.exit(f"ERROR: anchor 1 not found.\nExpected line containing PATCH 20260518.")
add1 = (anchor1 +
        "\n        watchdog_no_frame_s: float = 180.0,  # PATCH 20260603: subscription-staleness watchdog")
src = src.replace(anchor1, add1, 1)

# ----- Edit 2: add watchdog state + timer at end of __init__ -----
anchor2 = '''self.get_logger().info(
            f"rtsm_ingest_subscriber up (compressed transport). "
            f"color={COLOR_TOPIC} depth={DEPTH_TOPIC} "
            f"slop={SYNC_SLOP_SEC*1000:.0f}ms "
            f"recording={rec_status} http={http_status} "
            f"tf={self._world_frame}->{self._camera_frame}"
        )'''
if anchor2 not in src:
    sys.exit("ERROR: anchor 2 not found (startup log line).")
add2 = anchor2 + '''

        # PATCH 20260603: subscription-staleness watchdog.
        # If no synced frame arrives within watchdog_no_frame_s of either
        # startup or the last successful sync, raise SystemExit so the
        # container's `restart: unless-stopped` recycles into a fresh
        # subscription. Covers two known modes:
        #   1. DDS late-join race when subscriber starts before publisher
        #      is reachable (Execution Jetson boots; Albert hours later).
        #   2. Subscription handle staleness across publisher reboots.
        self._last_synced_mono = self._t_start
        self._watchdog_no_frame_s = watchdog_no_frame_s
        if watchdog_no_frame_s > 0:
            self._watchdog_timer = self.create_timer(30.0, self._watchdog_check)
            self.get_logger().info(
                f"watchdog: exit if no synced frame for "
                f"{watchdog_no_frame_s:.0f}s (checked every 30s)"
            )
        else:
            self.get_logger().info(
                "watchdog: disabled (--watchdog-no-frame-s 0)"
            )'''
src = src.replace(anchor2, add2, 1)

# ----- Edit 3: heartbeat at top of _on_synced -----
anchor3 = '''def _on_synced(self, color_msg: CompressedImage, depth_msg: CompressedImage):
        try:
            rgb = self._decode_jpeg(color_msg.data)'''
if anchor3 not in src:
    sys.exit("ERROR: anchor 3 not found (_on_synced opening).")
add3 = '''def _on_synced(self, color_msg: CompressedImage, depth_msg: CompressedImage):
        self._last_synced_mono = time.monotonic()  # PATCH 20260603: watchdog heartbeat
        try:
            rgb = self._decode_jpeg(color_msg.data)'''
src = src.replace(anchor3, add3, 1)

# ----- Edit 4: insert _watchdog_check method before _on_camera_info -----
anchor4 = '    def _on_camera_info(self, msg: CameraInfo):'
if anchor4 not in src:
    sys.exit("ERROR: anchor 4 not found (_on_camera_info).")
add4 = '''    def _watchdog_check(self):
        # PATCH 20260603: exit if no synced frame for too long.
        silent_s = time.monotonic() - self._last_synced_mono
        if silent_s > self._watchdog_no_frame_s:
            self.get_logger().warning(
                f"watchdog: no synced frame for {silent_s:.0f}s "
                f"(threshold={self._watchdog_no_frame_s:.0f}s). "
                f"Exiting; container restart policy will recycle with "
                f"a fresh subscription."
            )
            raise SystemExit(1)

    def _on_camera_info(self, msg: CameraInfo):'''
src = src.replace(anchor4, add4, 1)

# ----- Edit 5: add CLI arg in main() -----
anchor5 = '    args = parser.parse_args()'
if anchor5 not in src:
    sys.exit("ERROR: anchor 5 not found (parser.parse_args()).")
add5 = '''    # PATCH 20260603: subscription-staleness watchdog.
    parser.add_argument(
        "--watchdog-no-frame-s", type=float, default=180.0,
        help="Exit (so container can restart) if no synced frame arrives "
             "for this many seconds. 0 disables. Default: 180.",
    )
    args = parser.parse_args()'''
src = src.replace(anchor5, add5, 1)

# ----- Edit 6: pass arg to constructor in main() -----
anchor6 = '''        post_hz=args.post_hz,
    )'''
if anchor6 not in src:
    sys.exit("ERROR: anchor 6 not found (constructor call).")
add6 = '''        post_hz=args.post_hz,
        watchdog_no_frame_s=args.watchdog_no_frame_s,  # PATCH 20260603
    )'''
src = src.replace(anchor6, add6, 1)

# Sanity: count patch markers — must equal 6 if all edits applied.
n = src.count('PATCH 20260603')
if n != 6:
    sys.exit(f"ERROR: expected 6 PATCH 20260603 markers after edits, found {n}")

p.write_text(src)
print(f"applied {n} patch markers across 6 edits")
PYEOF

# ----- Validate Python syntax -----
echo ""
echo "=== Python syntax check ==="
if python3 -m py_compile "$TARGET"; then
    echo "  py_compile: OK"
else
    echo "  ERROR: syntax invalid. Rolling back to $BACKUP"
    cp "$BACKUP" "$TARGET"
    exit 1
fi

# ----- Show diff summary -----
echo ""
echo "=== Diff vs backup (summary) ==="
diff -u "$BACKUP" "$TARGET" | head -120 || true
echo "  ... (truncated; full diff: diff -u $BACKUP $TARGET)"

echo ""
echo "=== Apply: ==="
echo "  cd ~/rtsm/docker && docker compose restart rtsm-ingest"
echo ""
echo "=== Verify watchdog is armed: ==="
echo "  docker logs --tail 30 rtsm-ingest 2>&1 | grep watchdog"
echo "  # Expected: 'watchdog: exit if no synced frame for 180s (checked every 30s)'"
echo ""
echo "=== Verify cycling (with Albert off): ==="
echo "  docker ps --filter name=rtsm-ingest --format 'table {{.Names}}\\t{{.Status}}'"
echo "  # After ~3.5 min: should see Status 'Up <small number> seconds' "
echo "  # — that's the restart kicking in. Repeat: should restart every ~3.5 min."
echo "  # docker logs --tail 5 rtsm-ingest should show the watchdog exit message."
echo ""
echo "=== Override threshold (e.g. for testing): ==="
echo "  # Edit docker/docker-compose.yml, add to rtsm-ingest.command:"
echo "  #   - --watchdog-no-frame-s=30"
echo "  # Then: docker compose up -d"
echo ""
echo "=== Rollback: ==="
echo "  cp $BACKUP $TARGET && docker compose restart rtsm-ingest"
