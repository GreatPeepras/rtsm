#!/usr/bin/env bash
# backpressure-run.sh — one rate sweep at a single --post-hz value.
#
# Usage:
#   ./backpressure-run.sh 6.0    # ~uncapped (matches camera rate)
#   ./backpressure-run.sh 3.0
#   ./backpressure-run.sh 1.5
#
# What it does:
#   1. Restarts rtsm-dev (clean queue, empty WM)
#   2. Starts stats-poller.py in background
#   3. Starts subscriber.py with --instrument and --post-hz $1
#   4. Prints "WALK ALBERT NOW" and waits for Ctrl-C
#   5. On Ctrl-C: stops both processes cleanly, prints CSV paths
#
# Assumes:
#   - You're on the Execution Jetson
#   - Camera container on Albert is already running and publishing
#   - rtsm-dev container is named "rtsm-dev"
#   - rtsm-ingest container (where subscriber.py runs) is "rtsm-ingest"
#     OR subscriber.py is run from a venv on the host — adjust below.

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "usage: $0 <post-hz>" >&2
    exit 1
fi

POST_HZ="$1"
TS="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
RUN_DIR="$HOME/rtsm/notes/backpressure-2026-05-18/run-${POST_HZ}Hz-${TS}"
mkdir -p "$RUN_DIR"

SUB_CSV="$RUN_DIR/subscriber.csv"
STATS_CSV="$RUN_DIR/stats.csv"
META="$RUN_DIR/meta.txt"

echo "=== backpressure run ==="
echo "post-hz:    $POST_HZ"
echo "run dir:    $RUN_DIR"
echo

# Record metadata
{
    echo "post_hz: $POST_HZ"
    echo "ts_utc: $TS"
    echo "host: $(hostname)"
    echo "user: $(whoami)"
    echo "git_rev: $(cd $HOME/rtsm && git rev-parse --short HEAD 2>/dev/null || echo unknown)"
    echo "git_branch: $(cd $HOME/rtsm && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
} > "$META"

echo "[1/4] restarting rtsm-dev for clean queue + empty WM..."
docker restart rtsm-dev >/dev/null
echo "      polling /stats until ready (up to 60s)..."
:

# Confirm /stats responds before continuing
ready=0
for i in $(seq 1 30); do
    if curl -sf http://localhost:8002/stats >/dev/null; then
        echo "      rtsm-dev /stats responding (after ${i} attempts, ~$((i*2))s)."
        ready=1
        break
    fi
    echo "      /stats not ready (attempt $i/30)..."
    sleep 2
done
if [ "$ready" -ne 1 ]; then
    echo "ERROR: rtsm-dev did not respond on /stats within 60s. Aborting." >&2
    echo "Check 'docker logs rtsm-dev' and try again." >&2
    exit 1
fi

echo "[2/4] starting stats-poller (-> $STATS_CSV)..."
python3 "$HOME/rtsm/scripts/stats-poller.py" \
    --url http://localhost:8002/stats \
    --out "$STATS_CSV" \
    --interval 1.0 &
POLLER_PID=$!

echo "[3/4] starting subscriber (--post-hz $POST_HZ, --instrument $SUB_CSV)..."
echo
echo "      >>> WALK ALBERT THROUGH THE APARTMENT NOW <<<"
echo "      >>> Press Ctrl-C when done.                <<<"
echo

# >>>>> ADJUST THIS LINE BASED ON HOW YOU NORMALLY RUN subscriber.py <<<<<
# If subscriber runs inside a container, exec into it. If from host venv,
# activate it. Adapt to whatever ~/rtsm/scripts/run-subscriber.sh does today.
#
# Placeholder showing the *flags* you need; replace the prefix:
#
#   docker exec rtsm-ingest python3 /workspace/ingest/src/subscriber.py ...
#   OR
#   source ~/rtsm/ingest/venv/bin/activate && python3 ~/rtsm/ingest/src/subscriber.py ...
#
# Required flags:
#   --post-to http://localhost:8002/ingest/keyframe
#   --world-frame map
#   --post-hz $POST_HZ
#   --instrument $SUB_CSV
#
# Keep whatever other flags your normal run-subscriber.sh uses.

# Launch subscriber in a docker container. --init ensures PID 1 is
# tini, which forwards SIGINT to subscriber.py so its close() runs
# and the CSV is flushed cleanly. --name lets cleanup() target the
# container if SUB_PID kill misses.
SUB_NAME="rtsm-bp-sub-$$"

docker run --rm --init \
    --name "$SUB_NAME" \
    --network host \
    --ipc host \
    -e PYTHONUNBUFFERED=1 \
    -v /home/peep/rtsm/ingest/src:/workspace/rtsm-ingest:ro \
    -v "$RUN_DIR":/run_dir \
    --entrypoint bash \
    rtsm-ingest:skeleton \
    -c "source /opt/ros/humble/setup.bash && cd /workspace/rtsm-ingest && \
        python3 -u subscriber.py \
            --post-to http://localhost:8002/ingest/keyframe \
            --world-frame map \
            --post-hz $POST_HZ \
            --instrument /run_dir/subscriber.csv" \
    > "$RUN_DIR/subscriber.log" 2>&1 &
SUB_PID=$!

# Replace the cleanup trap now that we have a real SUB_PID and need
# to also stop the docker container by name (host-side kill may not
# reach into the container quickly enough).
cleanup() {
    echo
    echo "[4/4] stopping subscriber + poller..."
    # Try graceful container stop first (sends SIGTERM, then SIGKILL).
    if docker inspect "$SUB_NAME" >/dev/null 2>&1; then
        docker stop --time 5 "$SUB_NAME" >/dev/null 2>&1 || true
    fi
    # Reap host-side wrapper.
    if kill -0 "$SUB_PID" 2>/dev/null; then
        kill -INT "$SUB_PID" 2>/dev/null || true
        wait "$SUB_PID" 2>/dev/null || true
    fi
    if kill -0 "$POLLER_PID" 2>/dev/null; then
        kill -INT "$POLLER_PID" 2>/dev/null || true
        wait "$POLLER_PID" 2>/dev/null || true
    fi
    echo
    echo "=== run complete ==="
    echo "subscriber CSV: $SUB_CSV"
    echo "subscriber log: $RUN_DIR/subscriber.log"
    echo "stats CSV:      $STATS_CSV"
    echo "meta:           $META"
    echo
    echo "subscriber rows: $(wc -l < "$SUB_CSV" 2>/dev/null || echo "?")"
    echo "stats rows:      $(wc -l < "$STATS_CSV" 2>/dev/null || echo "?")"
    echo
    echo "Tail of subscriber log:"
    tail -3 "$RUN_DIR/subscriber.log" 2>/dev/null || true
    exit 0
}
trap cleanup INT TERM

# Wait on the subscriber process. If it exits on its own (e.g. crash),
# cleanup() still runs via the trap on script exit.
wait "$SUB_PID"
