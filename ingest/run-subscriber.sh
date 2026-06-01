#!/bin/bash
# Launch the rtsm-ingest subscriber with forwarded args.
# Foreground (no -d), auto-removed (--rm), so `timeout` and Ctrl-C
# both work cleanly without leaving orphaned containers.
#
# Usage:
#   ./run-subscriber.sh --post-to http://localhost:8002/ingest/keyframe --post-hz 6
#   ./run-subscriber.sh --record --max-frames 1000
#   timeout 60 ./run-subscriber.sh --post-hz 10 --post-to http://localhost:8002/ingest/keyframe

set -e

# Stop any prior subscriber container before we start a new one.
docker rm -f rtsm-ingest-sub 2>/dev/null || true

exec docker run --rm \
  --network host \
  --ipc=host \
  -e ROS_DOMAIN_ID=30 \
  -e ROS_LOCALHOST_ONLY=0 \
  -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
  -e CYCLONEDDS_URI=file:///cyclonedds.xml \
  -v /home/peep/cyclonedds.xml:/cyclonedds.xml:ro \
  -v /home/peep/rtsm/ingest:/workspace/rtsm-ingest \
  -v /mnt/rtsm-data/rtsm-recordings:/recordings \
  --name rtsm-ingest-sub \
  rtsm-ingest:skeleton \
  python3 /workspace/rtsm-ingest/src/subscriber.py "$@"
