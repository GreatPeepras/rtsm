#!/bin/bash
# Diagnose rtsm-ingest autostart failure — 2026-06-04.
#
# Run on the EXECUTION Jetson (192.168.0.53), from anywhere.
# Captures everything we need to decide between the three hypotheses:
#   1. Image ENTRYPOINT eats the command (container stays Up, subscriber never runs)
#   2. Startup race vs rtsm-dev (subscriber POSTs before port 8002 is up)
#   3. DDS discovery race / cyclonedds.xml problem
#
# This script does NOT modify anything. Safe to run multiple times.
#
# Output is one big paste — copy the whole thing back.

set +e   # don't bail on individual probe failures
echo "================================================================"
echo "rtsm-ingest diagnostic — $(date -Is)"
echo "host: $(hostname)  uid: $(id -un)"
echo "================================================================"

echo ""
echo "---------------- 1. CONTAINER STATE ----------------"
docker ps --filter name=rtsm- --format \
    'table {{.Names}}\t{{.Status}}\t{{.RunningFor}}\t{{.Image}}'

echo ""
echo "---------------- 2. rtsm-ingest INSPECT (entrypoint/cmd/state) ----------------"
docker inspect rtsm-ingest 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)[0]
except Exception as e:
    print(f'inspect failed: {e}'); sys.exit(0)
print('State.Status      :', d['State'].get('Status'))
print('State.Running     :', d['State'].get('Running'))
print('State.Restarting  :', d['State'].get('Restarting'))
print('State.RestartCount:', d.get('RestartCount'))
print('State.ExitCode    :', d['State'].get('ExitCode'))
print('State.Error       :', d['State'].get('Error'))
print('State.StartedAt   :', d['State'].get('StartedAt'))
print('State.FinishedAt  :', d['State'].get('FinishedAt'))
print('Config.Entrypoint :', d['Config'].get('Entrypoint'))
print('Config.Cmd        :', d['Config'].get('Cmd'))
print('Path              :', d.get('Path'))
print('Args              :', d.get('Args'))
" 2>/dev/null

echo ""
echo "---------------- 3. IMAGE ENTRYPOINT / CMD ----------------"
docker image inspect rtsm-ingest:skeleton 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)[0]
except Exception as e:
    print(f'image inspect failed: {e}'); sys.exit(0)
cfg = d.get('Config', {})
print('Image.Entrypoint:', cfg.get('Entrypoint'))
print('Image.Cmd       :', cfg.get('Cmd'))
print('Image.WorkingDir:', cfg.get('WorkingDir'))
print('Image.User      :', cfg.get('User'))
" 2>/dev/null

echo ""
echo "---------------- 4. PROCESSES INSIDE rtsm-ingest ----------------"
docker exec rtsm-ingest ps auxf 2>&1 | head -60
echo ""
echo "(PID 1 cmdline:)"
docker exec rtsm-ingest sh -c 'cat /proc/1/cmdline | tr "\0" " "; echo' 2>&1
echo ""
echo "(Python processes anywhere in the container:)"
docker exec rtsm-ingest sh -c 'pgrep -af python || echo NONE' 2>&1

echo ""
echo "---------------- 5. LAST 50 LINES OF rtsm-ingest LOGS ----------------"
docker logs --tail 50 rtsm-ingest 2>&1

echo ""
echo "---------------- 6. rtsm-dev READINESS ----------------"
curl -sf -m 3 http://localhost:8002/stats >/dev/null && echo "rtsm-dev /stats: OK" || echo "rtsm-dev /stats: UNREACHABLE"
curl -sf -m 3 http://localhost:8002/health >/dev/null && echo "rtsm-dev /health: OK" || echo "rtsm-dev /health: not present (try /stats)"

echo ""
echo "---------------- 7. CYCLONEDDS CONFIG SANITY ----------------"
echo "host file: /home/peep/cyclonedds.xml"
if [ -f /home/peep/cyclonedds.xml ]; then
    echo "  exists, size=$(stat -c%s /home/peep/cyclonedds.xml) bytes"
    echo "  --- content (first 40 lines) ---"
    head -40 /home/peep/cyclonedds.xml
else
    echo "  MISSING — this is likely the bug"
fi
echo ""
echo "as mounted inside rtsm-ingest (/cyclonedds.xml):"
docker exec rtsm-ingest sh -c '
    if [ -f /cyclonedds.xml ]; then
        echo "  exists, size=$(stat -c%s /cyclonedds.xml) bytes"
    else
        echo "  MISSING inside container"
    fi
' 2>&1

echo ""
echo "---------------- 8. ROS DISCOVERY FROM INSIDE INGEST CONTAINER ----------------"
echo "(does subscriber actually see Albert's camera topics?)"
docker exec rtsm-ingest sh -c '
    source /opt/ros/humble/setup.bash 2>/dev/null
    timeout 5 ros2 topic list 2>&1 | head -30
' 2>&1

echo ""
echo "---------------- 9. COMPARE WITH MANUAL run-subscriber.sh STATE ----------------"
docker ps --filter name=rtsm-ingest-sub --format \
    'table {{.Names}}\t{{.Status}}\t{{.RunningFor}}'
if docker ps -q --filter name=rtsm-ingest-sub | grep -q .; then
    echo "(manual subscriber IS running — what's it doing differently?)"
    docker exec rtsm-ingest-sub ps auxf 2>&1 | head -20
else
    echo "(no manual subscriber currently running)"
fi

echo ""
echo "---------------- 10. HOST NETWORK SANITY ----------------"
echo "ping Albert (192.168.0.51):"
ping -c1 -W2 192.168.0.51 2>&1 | grep -E 'bytes from|loss'
echo "ROS UDP ports listening on host:"
ss -tulnp 2>/dev/null | awk 'NR==1 || /:7400|:7401|:7410|:7411|:8002/' | head -20

echo ""
echo "================================================================"
echo "END diagnostic — $(date -Is)"
echo "================================================================"
