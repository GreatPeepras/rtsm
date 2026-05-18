#!/usr/bin/env bash
# run-subscriber.sh — long-running subscriber with disk logging and recording.
#
# Logs go to ./logs/subscriber-YYYY-MM-DDTHH-MM-SSZ.log
# Recordings go to ./recordings/<run_id>/ (the subscriber picks the timestamp)
#
# Exits cleanly on SIGTERM/SIGINT (will fix the rclpy traceback in a separate patch).

set -euo pipefail

LOG_DIR="/home/peep/rtsm/ingest/logs"
REC_DIR="/home/peep/rtsm/ingest/recordings"
mkdir -p "$LOG_DIR" "$REC_DIR"

LOG_FILE="$LOG_DIR/subscriber-$(date -u +%Y-%m-%dT%H-%M-%SZ).log"
echo "Logging to: $LOG_FILE"

# --rm + --name lets you `docker logs rtsm-subscriber` from another terminal,
# but it goes away when you stop it.
exec docker run --rm \
    --name rtsm-subscriber \
    --network host \
    --ipc host \
    -e PYTHONUNBUFFERED=1 \
    -v /home/peep/rtsm/ingest/src:/workspace/rtsm-ingest:ro \
    -v "$REC_DIR":/recordings \
    --entrypoint bash \
    rtsm-ingest:skeleton \
    -c "source /opt/ros/humble/setup.bash && cd /workspace/rtsm-ingest && \
        python3 -u subscriber.py \
            --post-to http://localhost:8002/ingest/keyframe \
            --post-hz 2.0 \
            --record \
            --record-root /recordings" \
    2>&1 | tee "$LOG_FILE"
