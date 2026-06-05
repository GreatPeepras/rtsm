#!/usr/bin/env bash
#
# deploy_arm_eviction_dryrun_2026-06-05.sh
#
# Phase B.3 -- arm Tier-2 eviction in DRY-RUN mode.
#
# Two changes (both idempotent, both reversible via .bak.<ts>):
#   1) rtsm/api/server.py  -- add /admin/evictable (GET) + /admin/evict (POST).
#   2) rtsm/cfg/rtsm.yaml  -- append eviction: block (enabled: true,
#      dry_run: true, period_s: 300).
#
# Hard invariant already enforced in WorkingMemory:
#     label_user is not None  =>  never evicted
# All ~12 currently-named OIDs are protected unconditionally.
#
# Usage:
#     ./deploy_arm_eviction_dryrun_2026-06-05.sh           # preview (default)
#     APPLY=1 ./deploy_arm_eviction_dryrun_2026-06-05.sh   # actually write
#
# After APPLY=1:
#     cd ~/rtsm/docker && docker compose restart rtsm-dev

set -euo pipefail

RTSM_ROOT="${RTSM_ROOT:-$HOME/rtsm}"
APPLY="${APPLY:-0}"

export RTSM_ROOT APPLY

python3 - <<'PYEOF'
import os
import sys
import datetime
import pathlib

RTSM_ROOT = pathlib.Path(os.environ["RTSM_ROOT"])
APPLY     = os.environ.get("APPLY", "0") == "1"
TS        = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

SERVER_PY = RTSM_ROOT / "rtsm" / "api" / "server.py"
RTSM_YAML = RTSM_ROOT / "rtsm" / "cfg" / "rtsm.yaml"

MARKER_SERVER = "# === eviction admin endpoints v1 (2026-06-05) ==="
MARKER_YAML   = "# === Phase B.3 eviction block v1 (2026-06-05) ==="
ANCHOR_SERVER = "    # ---- Detailed stats endpoint ----"

SERVER_INSERT = '''\
    # ---- Admin / eviction inspection (Phase B.3, 2026-06-05) ----
    # === eviction admin endpoints v1 (2026-06-05) ===
    @app.get("/admin/evictable")
    def admin_evictable() -> Dict[str, Any]:
        """List what WOULD evict right now (no side effects).

        Pure read. Does NOT check cfg.eviction.enabled, so it works for
        TTL tuning even when the periodic sweep is disabled. Returns
        candidate list sorted oldest-first plus a per-class histogram.
        """
        if not hasattr(working_memory, "select_evictable"):
            raise HTTPException(
                status_code=400,
                detail="select_evictable not supported (frozen mode?)",
            )
        try:
            candidates = working_memory.select_evictable()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"select failed: {e}")
        by_class: Dict[str, int] = {}
        for c in candidates:
            cls = (c.get("movability_class") or "unknown")
            by_class[cls] = by_class.get(cls, 0) + 1
        return {
            "status": "ok",
            "count": len(candidates),
            "by_class": by_class,
            "candidates": candidates,
        }

    @app.post("/admin/evict")
    def admin_evict(dry_run: bool = True) -> Dict[str, Any]:
        """Trigger one eviction sweep on demand.

        Honors cfg.eviction.enabled (if False, returns scanned=0/evicted=[]).
        The `dry_run` query-param OVERRIDES cfg.eviction.dry_run. Default
        True -- this endpoint never deletes unless explicitly called with
        ?dry_run=false. Safety net so an accidental curl doesn't evict
        the world.
        """
        if not hasattr(working_memory, "evict_stale"):
            raise HTTPException(
                status_code=400,
                detail="evict_stale not supported (frozen mode?)",
            )
        try:
            result = working_memory.evict_stale(dry_run=dry_run)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"evict failed: {e}")
        return {"status": "ok", **result}

'''

YAML_APPEND = '''
# === Phase B.3 eviction block v1 (2026-06-05) ===
# Tier-2 time-based eviction (movability-aware). Hard invariant in WM:
#     label_user is not None  =>  never evicted
# All named OIDs (~12 at arming time) are protected unconditionally.
# Dry-run on: evict_stale computes and logs candidates without deleting.
eviction:
  enabled: true
  dry_run: true
  period_s: 300            # sweep cadence (monotonic); day-scale TTLs, so generous
  ttl_s: {}                # per-class overrides (seconds); empty => use defaults
                           #   permanent:   null  (never)
                           #   static:      90d
                           #   semi_static: 14d   (default fallback)
                           #   movable:      3d
                           #   roaming:      1d
                           #   ephemeral:   12h
'''

# -------------------------------------------------------------- preflight
errs = []
if not SERVER_PY.is_file(): errs.append(f"missing: {SERVER_PY}")
if not RTSM_YAML.is_file(): errs.append(f"missing: {RTSM_YAML}")
if errs:
    for e in errs: print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)

print(f"==> RTSM root:  {RTSM_ROOT}")
print(f"==> server.py:  {SERVER_PY}")
print(f"==> rtsm.yaml:  {RTSM_YAML}")
print(f"==> mode:       {'APPLY' if APPLY else 'PREVIEW'}")
print()

# -------------------------------------------------------------- server.py
src = SERVER_PY.read_text(encoding="utf-8")
if MARKER_SERVER in src:
    print("[server.py] marker present; skipping insert")
elif ANCHOR_SERVER not in src:
    print(f"ERROR: anchor not found in server.py: {ANCHOR_SERVER!r}", file=sys.stderr)
    print("       file layout may have changed; refusing to guess.", file=sys.stderr)
    sys.exit(2)
else:
    if APPLY:
        bak = SERVER_PY.with_suffix(SERVER_PY.suffix + f".bak.{TS}")
        bak.write_bytes(SERVER_PY.read_bytes())
        new = src.replace(ANCHOR_SERVER, SERVER_INSERT + ANCHOR_SERVER, 1)
        SERVER_PY.write_text(new, encoding="utf-8")
        print(f"[server.py] patched (backup: {bak.name})")
    else:
        n = len(SERVER_INSERT.splitlines())
        print(f"[server.py] PREVIEW -- would insert {n} lines before anchor:")
        print(f"             {ANCHOR_SERVER!r}")

# -------------------------------------------------------------- rtsm.yaml
yml = RTSM_YAML.read_text(encoding="utf-8")
has_eviction_key = any(l.startswith("eviction:") for l in yml.splitlines())
if has_eviction_key or MARKER_YAML in yml:
    print("[rtsm.yaml] eviction block already present; skipping append")
else:
    if APPLY:
        bak = RTSM_YAML.with_suffix(RTSM_YAML.suffix + f".bak.{TS}")
        bak.write_bytes(RTSM_YAML.read_bytes())
        tail = "" if yml.endswith("\n") else "\n"
        RTSM_YAML.write_text(yml + tail + YAML_APPEND, encoding="utf-8")
        print(f"[rtsm.yaml] eviction block appended (backup: {bak.name})")
    else:
        n = len(YAML_APPEND.strip().splitlines())
        print(f"[rtsm.yaml] PREVIEW -- would append {n} lines:")
        for line in YAML_APPEND.strip().splitlines():
            print(f"             {line}")

print()
if APPLY:
    print("==> APPLY complete. Next steps:")
    print("      cd ~/rtsm/docker && docker compose restart rtsm-dev")
    print("      # wait ~5s for healthcheck")
    print("      curl -s http://localhost:8002/admin/evictable | jq '{count, by_class}'")
    print("      curl -s -X POST 'http://localhost:8002/admin/evict?dry_run=true' | jq")
    print("      docker exec rtsm-dev tail -f /tmp/rtsm.log | grep -i evict")
else:
    print("==> PREVIEW only. Re-run with APPLY=1 to write.")
PYEOF
