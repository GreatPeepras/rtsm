#!/bin/bash
set -euo pipefail
cd /workspace/rtsm
LOG=/tmp/rtsm.log
echo "=== entrypoint: $(date -Is) RTSM_MODE=${RTSM_MODE:-serve} ===" | tee -a "$LOG"
case "${RTSM_MODE:-serve}" in
  serve)  exec rtsm --serve > >(tee -a "$LOG") 2>&1 ;;
  replay) exec rtsm --replay recordings/demo_clip > >(tee -a "$LOG") 2>&1 ;;
  live)   exec rtsm > >(tee -a "$LOG") 2>&1 ;;
  *)      echo "unknown RTSM_MODE=${RTSM_MODE}" | tee -a "$LOG"; exit 1 ;;
esac
