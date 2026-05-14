#!/usr/bin/env bash
# live-test.sh — fixed-duration subscriber test against rtsm-dev.
#
# Usage:
#   ./live-test.sh                       # 15s test, world-frame=map (default)
#   ./live-test.sh 30                    # 30s test
#   ./live-test.sh 15 camera_link        # 15s test, world-frame=camera_link

set -euo pipefail

DURATION="${1:-15}"
WORLD_FRAME="${2:-map}"
INGEST_URL="http://localhost:8002"

echo "=== Live test: ${DURATION}s, --world-frame ${WORLD_FRAME} ==="
echo

echo "--- BEFORE ---"
curl -sS "${INGEST_URL}/stats"
echo
echo

# Tail rtsm-dev logs into a tempfile, filtering for interesting lines.
LOG_TMP=$(mktemp /tmp/rtsm-dev-test.XXXXXX.log)
docker logs -f --tail 0 rtsm-dev 2>&1 \
    | grep --line-buffered -E "ingest/keyframe|422|400|500|Traceback|assoc-" \
    > "$LOG_TMP" &
TAIL_PID=$!

# Trap to clean up the tail no matter how we exit.
trap 'kill $TAIL_PID 2>/dev/null; wait $TAIL_PID 2>/dev/null; rm -f "$LOG_TMP"' EXIT

echo "--- SUBSCRIBER (${DURATION}s, world=${WORLD_FRAME}) ---"
timeout "$DURATION" docker run --rm \
    --network host \
    --ipc host \
    -e PYTHONUNBUFFERED=1 \
    -v /home/peep/rtsm/ingest/src:/workspace/rtsm-ingest:ro \
    --entrypoint bash \
    rtsm-ingest:skeleton \
    -c "source /opt/ros/humble/setup.bash && cd /workspace/rtsm-ingest && \
        python3 -u subscriber.py \
            --post-to ${INGEST_URL}/ingest/keyframe \
            --post-hz 6.0 \
            --world-frame ${WORLD_FRAME}" \
    || true   # timeout returns 124, don't fail the script

echo
echo "--- AFTER ---"
curl -sS "${INGEST_URL}/stats"
echo
echo

echo "--- rtsm-dev log lines during test ---"
cat "$LOG_TMP"
echo "--- end log ---"
