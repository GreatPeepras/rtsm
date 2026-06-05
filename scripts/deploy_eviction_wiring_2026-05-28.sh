#!/usr/bin/env bash
# deploy_eviction_wiring_2026-05-28.sh
#
# Wires WorkingMemory.evict_stale() into the ingest pipeline's per-frame
# maintenance tick, on its own throttled cadence. Three idempotent edits to
# rtsm/core/pipeline.py, single .bak.
#
#   1) __init__:           self._last_evict_ts = 0.0
#   2) maintenance block:  call self._maybe_evict_stale() after the LTM flush
#   3) new method:         _maybe_evict_stale() (mirrors _maybe_flush_vectors)
#
# Cadence is monotonic (when to LOOK, process-local, cfg eviction.period_s,
# default 300s). The TTL math inside evict_stale uses the WALL clock
# (last_seen_wall_utc), so the two are cleanly separated. evict_stale() is a
# no-op unless cfg["eviction"]["enabled"] is true, so wiring it in is safe
# even before you arm it. Runs in INGEST mode only (serve mode = frozen WM,
# no pipeline); the method guards with hasattr regardless.
#
# Usage:
#   ./deploy_eviction_wiring_2026-05-28.sh            # dry-run (default)
#   APPLY=1 ./deploy_eviction_wiring_2026-05-28.sh    # patch
#   PIPE_PATH=<path> APPLY=1 ./deploy_eviction_wiring_2026-05-28.sh
set -euo pipefail

PIPE_PATH="${PIPE_PATH:-rtsm/core/pipeline.py}"
APPLY="${APPLY:-0}"
[[ -f "$PIPE_PATH" ]] || { echo "FATAL: target not found: $PIPE_PATH"; exit 1; }

python3 - "$PIPE_PATH" "$APPLY" << 'PYEOF'
import sys
p, apply = sys.argv[1], sys.argv[2]
src = open(p, encoding="utf-8").read()

if "def _maybe_evict_stale" in src:
    print("SKIP: _maybe_evict_stale already present -- already deployed (idempotent).")
    sys.exit(0)

method = '''    def _maybe_evict_stale(self):
        """Throttled Tier-2 eviction sweep (movability-aware).

        Rides the same per-frame maintenance tick as _maybe_flush_vectors,
        but on its own (much longer) cadence -- eviction is day-scale.
        Cadence uses monotonic time (process-local "when to look"); the TTL
        math inside evict_stale() uses the wall clock (last_seen_wall_utc).
        evict_stale() is a no-op unless cfg["eviction"]["enabled"] is true,
        so this is safe to leave wired in before the policy is armed.
        """
        if self.working_mem is None:
            return
        evict = getattr(self.working_mem, "evict_stale", None)
        if not callable(evict):  # serve-mode frozen WM has no pipeline ops
            return
        period_s = float(self.cfg.get("eviction", {}).get("period_s", 300.0))
        now = time.monotonic()
        if (now - self._last_evict_ts) < period_s:
            return
        self._last_evict_ts = now
        try:
            res = evict()
        except Exception as e:
            logger.warning(f"eviction sweep failed: {e}")
            return
        ev = res.get("evicted") or []
        if ev:
            logger.info(
                f"[PIPE] evicted {len(ev)} stale objects "
                f"(by_class={res.get('by_class')}, dry_run={res.get('dry_run')})"
            )

'''

edits = [
    ("init counter",
     "        self._last_flush_ts = 0.0\n",
     "        self._last_flush_ts = 0.0\n        self._last_evict_ts = 0.0\n"),
    ("maintenance call",
     "        # 7) periodic flush/upsert to vector store (if configured)\n"
     "        self._maybe_flush_vectors()\n",
     "        # 7) periodic flush/upsert to vector store (if configured)\n"
     "        self._maybe_flush_vectors()\n\n"
     "        # 7b) periodic Tier-2 eviction sweep (no-op unless armed)\n"
     "        self._maybe_evict_stale()\n"),
    ("new method",
     "    # -------- teardown --------\n",
     method + "    # -------- teardown --------\n"),
]

for desc, old, new in edits:
    n = src.count(old)
    if n != 1:
        sys.exit(f"FATAL: anchor for [{desc}] occurs {n}x (need exactly 1).")
    src = src.replace(old, new, 1)

compile(src, p, "exec")
print("OK: all 3 edits applied, module compiles clean.")
if apply != "1":
    print("DRY-RUN: no file written. Re-run with APPLY=1 to patch.")
    sys.exit(0)
import time, shutil
bak = f"{p}.bak.{time.strftime('%Y%m%d-%H%M%S')}"
shutil.copy2(p, bak)
open(p, "w", encoding="utf-8").write(src)
print(f"APPLIED. Backup: {bak}")
PYEOF
