#!/bin/bash
# Deploy: rtsm-dev healthcheck + rtsm-ingest depends_on service_healthy
# 2026-06-04
#
# What this changes in docker/docker-compose.yml:
#   1. Adds a healthcheck to the `rtsm-dev` service. The check pings
#      /stats via python3+urllib (no curl/wget dependency). start_period
#      90s covers SigLIP load; 30 retries x 10s gives ~5 min grace after
#      start_period before the container is marked unhealthy.
#   2. Rewrites rtsm-ingest's depends_on from the short list form
#      (`- rtsm-dev`) to the long form with `condition: service_healthy`.
#      Compose will hold rtsm-ingest in "Created" state until rtsm-dev's
#      healthcheck passes, eliminating the POST-to-port-8002-not-bound race.
#
# Idempotent (re-running detects existing patch and exits cleanly).
# Backs up to docker-compose.yml.bak.<timestamp> before editing.
# Validates YAML syntax after editing; rolls back on parse failure.
#
# Run on the Execution Jetson.

set -euo pipefail

COMPOSE="${HOME}/rtsm/docker/docker-compose.yml"
if [ ! -f "$COMPOSE" ]; then
    echo "ERROR: $COMPOSE not found." >&2
    exit 1
fi

# Idempotency: both markers must be present to consider it patched.
if grep -q '^[[:space:]]*healthcheck:' "$COMPOSE" \
   && grep -q 'condition: service_healthy' "$COMPOSE"; then
    echo "Already patched (healthcheck + service_healthy both present)."
    echo "No changes made."
    exit 0
fi

TS=$(date +%Y%m%d-%H%M%S)
BACKUP="${COMPOSE}.bak.${TS}"
cp "$COMPOSE" "$BACKUP"
echo "Backed up: $BACKUP"

python3 <<'PYEOF'
import pathlib, sys
p = pathlib.Path.home() / "rtsm/docker/docker-compose.yml"
src = p.read_text()

# ----- Change 1: insert healthcheck under rtsm-dev -----
# Anchor: the `command:` line for rtsm-dev (unique in this file).
anchor1 = 'command: ["/workspace/rtsm/scripts/entrypoint.sh"]'
if anchor1 not in src:
    sys.exit(f"ERROR: anchor 1 not found: {anchor1!r}\n"
             f"docker-compose.yml may have drifted. Inspect manually.")

# 4-space indent matches other rtsm-dev service-level keys.
# Using "CMD" form (not CMD-SHELL) — each argv element is its own list item,
# so we don't have to escape any shell metacharacters.
healthcheck_block = '''command: ["/workspace/rtsm/scripts/entrypoint.sh"]
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request as u; u.urlopen('http://localhost:8002/stats', timeout=2)"]
      interval: 10s
      timeout: 5s
      retries: 30
      start_period: 90s'''

src = src.replace(anchor1, healthcheck_block, 1)

# ----- Change 2: rewrite depends_on to long form with condition -----
anchor2 = '''depends_on:
      - rtsm-dev'''
if anchor2 not in src:
    sys.exit(f"ERROR: anchor 2 not found.\n"
             f"Expected the literal block:\n{anchor2}\n"
             f"docker-compose.yml may have drifted. Inspect manually.")

new_depends = '''depends_on:
      rtsm-dev:
        condition: service_healthy'''
src = src.replace(anchor2, new_depends, 1)

p.write_text(src)
print("text edits applied")
PYEOF

# ----- Validate YAML parses, roll back on failure -----
echo ""
echo "=== YAML sanity check ==="
if python3 -c "import yaml,sys; yaml.safe_load(open('$COMPOSE'))" 2>/dev/null; then
    echo "  YAML parse: OK"
else
    # PyYAML may not be installed; fall back to docker compose config.
    if docker compose -f "$COMPOSE" config >/dev/null 2>&1; then
        echo "  docker compose config: OK"
    else
        echo "  ERROR: YAML invalid AND docker compose config failed."
        echo "  Rolling back to $BACKUP"
        cp "$BACKUP" "$COMPOSE"
        exit 1
    fi
fi

# ----- Show what changed -----
echo ""
echo "=== Diff vs backup ==="
diff -u "$BACKUP" "$COMPOSE" || true

echo ""
echo "=== Apply with: ==="
echo "  cd ~/rtsm/docker && docker compose up -d"
echo ""
echo "=== Observe the gated startup: ==="
echo "  # rtsm-dev should pass through: Created → starting (health: starting) → Up (healthy)"
echo "  # rtsm-ingest stays in 'Created' until rtsm-dev is healthy, then starts"
echo "  watch -n 1 'docker ps --filter name=rtsm- --format \"table {{.Names}}\\t{{.Status}}\"'"
echo ""
echo "=== Rollback if needed: ==="
echo "  cp $BACKUP $COMPOSE && cd ~/rtsm/docker && docker compose up -d"
