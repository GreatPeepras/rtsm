#!/usr/bin/env bash
# =============================================================================
# deploy_name_intent_rtsm_2026-06-29.sh   (PHASE 1 — RTSM side only)
#
# Wires the deferred name-intent reconciler into RTSM so name_object can label
# objects that confirm AFTER dispatch (the "giant egg" lag case). See
# name_intent_reconciler_design_2026-06-29.md.
#
# What it does (.53, plugged-in AGX — no Albert battery needed):
#   1. Drops name_intent.py next to server.py / working_memory.py.
#   2. working_memory.py:
#        a. import NameIntentRegistry, ResolvedMatch
#        b. instantiate self.name_intents in __init__
#        c. reconcile hook inside maybe_promote() right after promotion
#        d. new method register_name_intent() (runs reconcile-at-registration)
#   3. server.py: NameIntentBody model + 4 endpoints
#        POST /name_intents, GET /name_intents, GET /name_intents/resolved,
#        DELETE /name_intents/{intent_id}
#   4. AST-validates both files, atomic-writes, .pre-MARKER backups, restarts.
#
# Marker: NAME_INTENT_2026-06-29
#
# Usage:
#   ./deploy_name_intent_rtsm_2026-06-29.sh            # --dryrun (default)
#   ./deploy_name_intent_rtsm_2026-06-29.sh --apply
#   ./deploy_name_intent_rtsm_2026-06-29.sh --revert
#   ./deploy_name_intent_rtsm_2026-06-29.sh --check
#
# IMPORTANT: the anchors below were lifted from project-knowledge copies and
# MUST be grep-verified against the LIVE files. The patcher ABORTS loudly on any
# anchor miss (source drift) without writing — that is by design. If it aborts,
# paste the live region around the named anchor and tighten the OLD string.
#
# Env overrides:
#   RTSM_REPO       (default $HOME/rtsm)
#   RTSM_API_DIR    (default autodetect: dir containing server.py)
#   NAME_INTENT_IMPORT  (default 'from name_intent import NameIntentRegistry, ResolvedMatch')
#   MODULE_SRC      (default ./name_intent.py — the module to drop)
# =============================================================================

set -euo pipefail

MODE="${1:---dryrun}"
MARKER="NAME_INTENT_2026-06-29"
BACKUP_SUFFIX=".pre-$MARKER"

RTSM_REPO="${RTSM_REPO:-$HOME/rtsm}"
# Package-relative import (the codebase is a package: rtsm/api, rtsm/stores).
# working_memory.py lives in stores/; name_intent.py is dropped beside it.
# Dual try/except handles relative-package vs absolute-package loading.
MODULE_SRC="${MODULE_SRC:-$(dirname "$0")/name_intent.py}"

color_red()   { printf "\033[31m%s\033[0m\n" "$*"; }
color_green() { printf "\033[32m%s\033[0m\n" "$*"; }
color_yellow(){ printf "\033[33m%s\033[0m\n" "$*"; }
color_blue()  { printf "\033[34m%s\033[0m\n" "$*"; }

case "$MODE" in
  --dryrun|--apply|--revert|--check) ;;
  *) color_red "Unknown mode: $MODE"; echo "Usage: $0 [--dryrun|--apply|--revert|--check]"; exit 2 ;;
esac

# ---- locate the two target files (they live in DIFFERENT package dirs) ----
# working_memory.py -> rtsm/stores/ ; server.py -> rtsm/api/ (NOT visualization/).
find_one() {  # $1 = path-glob suffix; prefer explicit override in $2
  local override="$2"
  if [ -n "${override:-}" ] && [ -f "$override" ]; then echo "$override"; return 0; fi
  find "$RTSM_REPO" -path "*$1" -type f 2>/dev/null | head -1
}
WM="$(find_one "/stores/working_memory.py" "${WM_FILE:-}")"
[ -n "$WM" ] || WM="$(find_one "/working_memory.py" "${WM_FILE:-}")"
# server: insist on the api/ one, never visualization/
SERVER="$(find_one "/api/server.py" "${SERVER_FILE:-}")"

if [ -z "${WM:-}" ] || [ ! -f "${WM:-/nonexistent}" ]; then
  color_red "FATAL: working_memory.py not found under $RTSM_REPO."
  color_red "Override with WM_FILE=/abs/path/working_memory.py"; exit 1
fi
if [ -z "${SERVER:-}" ] || [ ! -f "${SERVER:-/nonexistent}" ]; then
  color_red "FATAL: api/server.py not found under $RTSM_REPO (note: visualization/server.py is NOT the target)."
  color_red "Override with SERVER_FILE=/abs/path/api/server.py"; exit 1
fi

WM_DIR="$(dirname "$WM")"
MODULE_DEST="$WM_DIR/name_intent.py"          # module sits beside working_memory.py
# Default import is package-relative with an absolute fallback (multi-line block
# inserted by the patcher). Override the whole block via NAME_INTENT_IMPORT.
NAME_INTENT_IMPORT="${NAME_INTENT_IMPORT:-__DEFAULT_RELATIVE__}"

color_blue "============================================================"
color_blue "Name-Intent Reconciler — RTSM side ($MODE)"
color_blue "Marker: $MARKER"
color_blue "============================================================"
echo "WM:      $WM"
echo "SERVER:  $SERVER"
echo "MODULE:  $MODULE_DEST   (from $MODULE_SRC)"
echo

# ---- check ----
if [ "$MODE" = "--check" ]; then
  for f in "$SERVER" "$WM" "$MODULE_DEST"; do
    if [ -f "$f" ]; then
      n=$(grep -c "$MARKER" "$f" 2>/dev/null || true); n="${n:-0}"
      printf "  %-60s %s markers\n" "$f" "$n"
    else
      printf "  %-60s (absent)\n" "$f"
    fi
  done
  exit 0
fi

# ---- revert ----
if [ "$MODE" = "--revert" ]; then
  for f in "$SERVER" "$WM"; do
    bk="$f$BACKUP_SUFFIX"
    if [ -f "$bk" ]; then cp -p "$bk" "$f"; color_green "[REVERT] restored $f"; else color_yellow "[REVERT] no backup for $f"; fi
  done
  if [ -f "$MODULE_DEST" ]; then rm -f "$MODULE_DEST"; color_green "[REVERT] removed $MODULE_DEST"; fi
  color_green "[REVERT] done. Restart: cd $RTSM_REPO/docker && docker compose restart rtsm-dev"
  exit 0
fi

# ---- module presence ----
if [ ! -f "$MODULE_SRC" ]; then
  color_red "FATAL: module source not found: $MODULE_SRC (place name_intent.py beside this script)"; exit 1
fi
python3 -c "import ast,sys; ast.parse(open('$MODULE_SRC').read())" || { color_red "FATAL: $MODULE_SRC fails to parse"; exit 1; }

APPLY=0; [ "$MODE" = "--apply" ] && APPLY=1

WM_TMP=""; SRV_TMP=""
trap 'rm -f "$WM_TMP" "$SRV_TMP" 2>/dev/null || true' EXIT

# ===========================================================================
# Patch working_memory.py
# ===========================================================================
WM_TMP="$(mktemp /tmp/wm.XXXXXX.py)"
python3 - "$WM" "$WM_TMP" "$MARKER" "$NAME_INTENT_IMPORT" <<'PYEOF'
import sys
WM, OUT, MARKER, IMPORT_LINE = sys.argv[1:5]
src = open(WM, encoding="utf-8").read()
if MARKER in src:
    print(f"[WM] already patched ({MARKER}); no changes", file=sys.stderr)
    open(OUT,"w",encoding="utf-8").write(src); sys.exit(0)

def must_replace(src, old, new, label):
    if src.count(old) != 1:
        print(f"[WM] ANCHOR MISS ({label}): expected exactly 1 occurrence, found {src.count(old)}.", file=sys.stderr)
        print("---- expected anchor ----", file=sys.stderr); print(old, file=sys.stderr)
        sys.exit(3)
    return src.replace(old, new, 1)

# (a) import — anchor on the numpy import (verify live!). On the default
#     sentinel, insert a package-relative import with an absolute fallback,
#     since name_intent.py is dropped into the same package dir as this file
#     (rtsm/stores/). Override the whole block via NAME_INTENT_IMPORT=...
if IMPORT_LINE == "__DEFAULT_RELATIVE__":
    IMPORT_BLOCK = (
        f"# {MARKER}: deferred name-intent registry\n"
        "try:\n"
        "    from .name_intent import NameIntentRegistry, ResolvedMatch\n"
        "except ImportError:\n"
        "    from name_intent import NameIntentRegistry, ResolvedMatch\n"
    )
else:
    IMPORT_BLOCK = f"{IMPORT_LINE}  # {MARKER}\n"
A_IMPORT = "import numpy as np\n"
src = must_replace(src, A_IMPORT, A_IMPORT + IMPORT_BLOCK, "import")

# (b) __init__ registry — anchor on require_view_bins assignment
A_INIT = '        self.require_view_bins: int = int(obj_cfg.get("require_view_bins", 2))\n'
B_INIT = A_INIT + (
    f"        # {MARKER}: pending name-intent registry (deferred labeling)\n"
    "        self.name_intents = NameIntentRegistry()\n"
)
src = must_replace(src, A_INIT, B_INIT, "__init__")

# (c) maybe_promote hook — anchor on the promote log + ltm heap push (unique to
#     maybe_promote; a bare heappush also appears in collect_ready_for_upsert)
A_HOOK = (
    '                    f"conf={top_conf:.3f} hits={o.hits} stab={o.stability:.3f}"\n'
    '                )\n'
    '                heapq.heappush(self._ltm_heap, (_now_mono(), oid))\n'
)
B_HOOK = A_HOOK + (
    f"                # {MARKER}: reconcile newly-confirmed object vs pending intents\n"
    "                try:\n"
    "                    _m = self.name_intents.reconcile_object(\n"
    "                        o.id, getattr(o, 'emb_mean', None),\n"
    "                        getattr(o, 'xyz_world', None), bool(getattr(o, 'label_user', None)))\n"
    "                    if _m is not None:\n"
    "                        o.label_user = _m.label\n"
    "                        logger.info(f\"[name-intent] applied label_user={_m.label!r} \"\n"
    "                                    f\"to oid={o.id[:8]} sim={_m.sim:.3f}\")\n"
    "                except Exception as _e:\n"
    "                    logger.warning(f\"[name-intent] reconcile-on-confirm failed: {_e}\")\n"
)
src = must_replace(src, A_HOOK, B_HOOK, "maybe_promote-hook")

# (d) register_name_intent method — insert before get_robot_pose
A_METH = "    def get_robot_pose(self) -> Optional[Dict[str, Any]]:\n"
NEW_METH = (
    f"    # {MARKER}: deferred name-intent registration + reconcile-at-registration\n"
    "    def register_name_intent(self, *, label, description, memory_name,\n"
    "                             intent_emb, ttl_s=None):\n"
    "        \"\"\"Register a pending name-intent and immediately try to match it\n"
    "        against already-confirmed, unlabeled objects (covers the case where\n"
    "        the object confirmed between dispatch and this call). Returns\n"
    "        (intent_id, immediate_oid_or_None, immediate_sim_or_None).\"\"\"\n"
    "        robot_pose = self.get_robot_pose()\n"
    "        with self._lock:\n"
    "            iid = self.name_intents.register(\n"
    "                label=label, description=description, memory_name=memory_name,\n"
    "                intent_emb=intent_emb, robot_pose=robot_pose, ttl_s=ttl_s)\n"
    "            # reconcile-at-registration: scan recent confirmed unlabeled objs\n"
    "            imm_oid, imm_sim = None, None\n"
    "            for o in self._map.values():\n"
    "                if not getattr(o, 'confirmed', False):\n"
    "                    continue\n"
    "                if getattr(o, 'label_user', None):\n"
    "                    continue\n"
    "                _m = self.name_intents.reconcile_object(\n"
    "                    o.id, getattr(o, 'emb_mean', None),\n"
    "                    getattr(o, 'xyz_world', None), False)\n"
    "                if _m is not None:\n"
    "                    o.label_user = _m.label\n"
    "                    imm_oid, imm_sim = o.id, _m.sim\n"
    "                    logger.info(f\"[name-intent] immediate match intent={iid[:8]} \"\n"
    "                                f\"-> oid={o.id[:8]} sim={_m.sim:.3f}\")\n"
    "                    break\n"
    "        return iid, imm_oid, imm_sim\n"
    "\n"
)
src = must_replace(src, A_METH, NEW_METH + A_METH, "register_name_intent")

import ast
ast.parse(src)   # raises on broken result
open(OUT,"w",encoding="utf-8").write(src)
print("[WM] patched OK", file=sys.stderr)
PYEOF
color_green "[WM] patch generated + AST-validated"

# ===========================================================================
# Patch server.py
# ===========================================================================
SRV_TMP="$(mktemp /tmp/srv.XXXXXX.py)"
python3 - "$SERVER" "$SRV_TMP" "$MARKER" <<'PYEOF'
import sys, ast
SERVER, OUT, MARKER = sys.argv[1:4]
src = open(SERVER, encoding="utf-8").read()
if MARKER in src:
    print(f"[SRV] already patched ({MARKER}); no changes", file=sys.stderr)
    open(OUT,"w",encoding="utf-8").write(src); sys.exit(0)

def must_replace(src, old, new, label):
    if src.count(old) != 1:
        print(f"[SRV] ANCHOR MISS ({label}): expected 1 occurrence, found {src.count(old)}.", file=sys.stderr)
        print("---- expected anchor ----", file=sys.stderr); print(old, file=sys.stderr)
        sys.exit(3)
    return src.replace(old, new, 1)

# Endpoints inserted before the /objects/{oid} route so they share the same
# enclosing scope (closure over `app`, `working_memory`, `clip_adapter`).
ANCHOR = '    @app.get("/objects/{oid}")\n'
BLOCK = (
    f"    # ===== {MARKER}: deferred name-intent endpoints =====\n"
    "    class NameIntentBody(BaseModel):\n"
    "        label: str\n"
    "        description: str = \"\"\n"
    "        memory_name: str = \"\"\n"
    "        image_b64: Optional[str] = None\n"
    "        ttl_s: Optional[float] = None\n"
    "\n"
    "    def _encode_intent_image(image_b64):\n"
    "        if not image_b64:\n"
    "            return None\n"
    "        try:\n"
    "            import io\n"
    "            import numpy as _np\n"
    "            from PIL import Image\n"
    "            raw = base64.b64decode(image_b64)\n"
    "            img = Image.open(io.BytesIO(raw)).convert(\"RGB\")\n"
    "            enc = getattr(clip_adapter, \"encode_image\", None) \\\n"
    "                  or getattr(clip_adapter, \"embed_image\", None)\n"
    "            if enc is None:\n"
    "                return None\n"
    "            v = enc(img)\n"
    "            # adapter.encode_image runs keep_on_device=True -> may return a\n"
    "            # torch tensor on GPU; move to host before numpy conversion.\n"
    "            if hasattr(v, \"detach\"):\n"
    "                v = v.detach().cpu().numpy()\n"
    "            return _np.asarray(v, dtype=_np.float32).reshape(-1)\n"
    "        except Exception as _e:\n"
    "            import logging as _l\n"
    "            _l.getLogger(\"rtsm.name_intent\").warning(f\"intent image encode failed: {_e}\")\n"
    "            return None\n"
    "\n"
    "    @app.post(\"/name_intents\")\n"
    "    def post_name_intent(body: NameIntentBody) -> Dict[str, Any]:\n"
    "        emb = _encode_intent_image(body.image_b64)\n"
    "        iid, imm_oid, imm_sim = working_memory.register_name_intent(\n"
    "            label=body.label, description=body.description,\n"
    "            memory_name=body.memory_name, intent_emb=emb, ttl_s=body.ttl_s)\n"
    "        return {\"intent_id\": iid, \"immediate_oid\": imm_oid, \"immediate_sim\": imm_sim,\n"
    "                \"had_image\": emb is not None}\n"
    "\n"
    "    @app.get(\"/name_intents\")\n"
    "    def list_name_intents() -> Dict[str, Any]:\n"
    "        return {\"intents\": working_memory.name_intents.list_live()}\n"
    "\n"
    "    @app.get(\"/name_intents/resolved\")\n"
    "    def list_resolved_name_intents() -> Dict[str, Any]:\n"
    "        return {\"resolved\": working_memory.name_intents.list_resolved_unacked()}\n"
    "\n"
    "    @app.delete(\"/name_intents/{intent_id}\")\n"
    "    def ack_name_intent(intent_id: str) -> Dict[str, Any]:\n"
    "        return {\"acked\": working_memory.name_intents.ack(intent_id)}\n"
    "\n"
)
src = must_replace(src, ANCHOR, BLOCK + ANCHOR, "name_intent-endpoints")

# Ensure Optional is imported (it is used in the model). Best-effort check only.
if "Optional" not in src.split("\n", 40)[0:40].__str__() and "from typing import" not in src:
    print("[SRV] WARN: could not confirm 'Optional' import; verify typing imports.", file=sys.stderr)

ast.parse(src)
open(OUT,"w",encoding="utf-8").write(src)
print("[SRV] patched OK", file=sys.stderr)
PYEOF
color_green "[SRV] patch generated + AST-validated"

# ---- diff preview ----
echo; color_blue "---- working_memory.py diff ----"; diff -u "$WM" "$WM_TMP" || true
echo; color_blue "---- server.py diff ----"; diff -u "$SERVER" "$SRV_TMP" || true

if [ "$APPLY" -ne 1 ]; then
  echo; color_yellow "[DRYRUN] no files written. Re-run with --apply to commit."
  color_yellow "[DRYRUN] reminder: verify anchors against LIVE files first."
  exit 0
fi

# ---- apply: backup (never clobber a prior pre-marker backup) + atomic write ----
[ -f "$WM$BACKUP_SUFFIX" ]     || cp -p "$WM" "$WM$BACKUP_SUFFIX"
[ -f "$SERVER$BACKUP_SUFFIX" ] || cp -p "$SERVER" "$SERVER$BACKUP_SUFFIX"
mv "$WM_TMP" "$WM.new"; mv "$SRV_TMP" "$SERVER.new"; WM_TMP=""; SRV_TMP=""
python3 -c "import ast; ast.parse(open('$WM.new').read()); ast.parse(open('$SERVER.new').read())"
mv -f "$WM.new" "$WM"; mv -f "$SERVER.new" "$SERVER"
cp -p "$MODULE_SRC" "$MODULE_DEST"
color_green "[APPLY] wrote working_memory.py, server.py, name_intent.py"

# ---- restart rtsm-dev ----
if [ -d "$RTSM_REPO/docker" ]; then
  ( cd "$RTSM_REPO/docker" && docker compose restart rtsm-dev ) && color_green "[APPLY] rtsm-dev restarted"
else
  color_yellow "[APPLY] $RTSM_REPO/docker not found — restart rtsm-dev manually"
fi

echo; color_green "[APPLY] done. Smoke test:"
cat <<'SMOKE'
  # 1) list (should be empty)
  curl -s localhost:8002/name_intents | jq .
  # 2) register an intent for a KNOWN confirmed object using its current crop:
  OID=eeda1f599e6149d0
  IMG=$(curl -s "localhost:8002/objects/$OID/snapshots/0/image" | base64 -w0)
  curl -s -X POST localhost:8002/name_intents -H 'Content-Type: application/json' \
    -d "{\"label\":\"test egg\",\"description\":\"large white egg\",\"memory_name\":\"large white egg\",\"image_b64\":\"$IMG\"}" | jq .
  # expect immediate_oid == $OID (reconcile-at-registration via image match)
  # 3) resolved list, then ack:
  curl -s localhost:8002/name_intents/resolved | jq .
SMOKE
