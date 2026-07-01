#!/usr/bin/env bash
# deploy_wallclock_freshness_2026-06-30.sh
#
# MARKER: WALLCLOCK_FRESHNESS_2026-06-30
# Target: .53  rtsm/rtsm/api/server.py  (semantic_search freshness gate)
#
# BUG: the CAMERA_DOWN_GATE freshness filter ages off last_seen_mono vs
# time.monotonic(). The monotonic clock RESETS to a boot baseline on every
# rehydrate, so after any restart every rehydrated object reads as
# ~uptime-seconds stale. With name_object sending max_stale_s=10, the gate
# then drops the ENTIRE corpus -> /search/semantic returns [] for objects
# that are demonstrably present and in view -> name_object can never link
# anything -> no rtsm_oid ever backfills. Confirmed live: gate-off query
# returns dad/pet toy/etc; gate-on (max_stale_s=10) returns [].
#
# FIX: age the gate off last_seen_wall_utc, which persists across reboot
# (working_memory field @325, written to faiss sidecar @1100; surfaced as
# last_seen_at on both wm and faiss_meta results). Window unchanged (10s,
# "name only what's in view"); unknown-freshness still dropped (safe dir).
# After this, an object genuinely seen N real seconds ago reads as N s and
# passes; in-view naming works again post-restart.
#
# Does NOT change semantics ("name only what's in view"), only the clock the
# age is measured against. Every other caller passes max_stale_s=None and is
# unaffected.
#
# Idempotent, anchor-based, abort-on-drift, AST-validated, atomic write,
# timestamped .pre-MARKER backup. After apply:
#   cd ~/rtsm/docker && docker compose restart rtsm-dev
#
# Modes: --check (default) | --dryrun | --apply | --revert
set -euo pipefail

MARKER="WALLCLOCK_FRESHNESS_2026-06-30"
SRV="${SRV:-/home/peep/rtsm/rtsm/api/server.py}"
MODE="${1:---check}"
TS="$(date +%Y%m%d_%H%M%S)"
BK_ROOT="$HOME/.albert_deploy_backups/${TS}_${MARKER}"
say(){ printf '%s\n' "$*"; }

[[ -f "$SRV" ]] || { say "[ABORT] server.py not found at $SRV (set SRV=...)"; exit 2; }

build_python_patcher() {
cat <<'PYEOF'
import sys, ast, re, os, tempfile
path, marker, mode = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(path, encoding="utf-8").read()
if marker in src:
    print(f"[skip] marker present -> {path}"); sys.exit(0)

# Anchor: the exact monotonic gate block. The _ls_mono line is the unique
# fingerprint; we consume the whole `if max_stale_s is not None:` block
# through its `continue`. Indent-tolerant.
pat = re.compile(
    r'(?P<ind>[ \t]+)if max_stale_s is not None:[ \t]*\n'
    r'(?P=ind)[ \t]+if obj is not None:[ \t]*\n'
    r'(?P=ind)[ \t]+_ls_mono = float\(getattr\(obj, "last_seen_mono", 0\.0\) or 0\.0\)[ \t]*\n'
    r'(?P=ind)[ \t]+_age = \(time\.monotonic\(\) - _ls_mono\) if _ls_mono > 0 else None[ \t]*\n'
    r'(?P=ind)[ \t]+else:[ \t]*\n'
    r'(?P=ind)[ \t]+_age = None[^\n]*\n'
    r'(?P=ind)[ \t]+if _age is None or _age > max_stale_s:[ \t]*\n'
    r'(?P=ind)[ \t]+continue[ \t]*\n'
)
ms = list(pat.finditer(src))
if len(ms) == 0:
    print(f"[ABORT] monotonic gate block not found (drift?) -> {path}"); sys.exit(3)
if len(ms) > 1:
    print(f"[ABORT] gate block not unique ({len(ms)}x) -> {path}"); sys.exit(3)
m = ms[0]
ind = m.group("ind")

repl = (
f'{ind}# {marker}: age off wall-clock, not monotonic. last_seen_mono resets\n'
f'{ind}# to a boot baseline on rehydrate, so the old gate dropped every\n'
f'{ind}# rehydrated object as ~uptime stale and nuked the whole corpus when\n'
f'{ind}# max_stale_s was set. last_seen_wall_utc persists across reboot.\n'
f'{ind}# Window + "name only what is in view" semantics unchanged; unknown\n'
f'{ind}# freshness still dropped (safe direction for name_object).\n'
f'{ind}if max_stale_s is not None:\n'
f'{ind}    _now_wall = time.time()\n'
f'{ind}    _age = None\n'
f'{ind}    if obj is not None:\n'
f'{ind}        _lw = float(getattr(obj, "last_seen_wall_utc", 0.0) or 0.0)\n'
f'{ind}        if _lw > 0:\n'
f'{ind}            _age = _now_wall - _lw\n'
f'{ind}    elif source == "faiss_meta" and meta is not None:\n'
f'{ind}        _lw = meta.get("last_seen_wall_utc")\n'
f'{ind}        if _lw:\n'
f'{ind}            _age = _now_wall - float(_lw)\n'
f'{ind}    if _age is None or _age > max_stale_s:\n'
f'{ind}        continue\n'
)

new = src[:m.start()] + repl + src[m.end():]
try:
    ast.parse(new)
except SyntaxError as e:
    print(f"[ABORT] patched source fails AST -> {path}: {e}"); sys.exit(4)

if mode == "dryrun":
    print(f"[dryrun] would patch gate at lines "
          f"{src[:m.start()].count(chr(10))+1}..{src[:m.end()].count(chr(10))+1} -> {path}")
    sys.exit(0)

d = os.path.dirname(path)
fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_wallclock_", suffix=".py")
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(new)
    os.replace(tmp, path)
finally:
    if os.path.exists(tmp): os.unlink(tmp)
print(f"[APPLYED] {marker} -> {path}")
PYEOF
}

PYPATCH="$(mktemp /tmp/wallclock_patch_XXXX.py)"
build_python_patcher > "$PYPATCH"
trap 'rm -f "$PYPATCH"' EXIT

case "$MODE" in
  --check)
    say "== $MARKER : check =="
    if grep -q "$MARKER" "$SRV"; then say "[present] $SRV"
    elif grep -q '_ls_mono = float(getattr(obj, "last_seen_mono"' "$SRV"; then
      say "[pending] monotonic gate present, marker absent -> $SRV"
    else say "[??] neither marker nor monotonic anchor -> $SRV (drift?)"; fi
    ;;
  --dryrun)
    say "== $MARKER : dryrun =="
    python3 "$PYPATCH" "$SRV" "$MARKER" dryrun
    say "(no files written)"
    ;;
  --apply)
    say "== $MARKER : apply =="
    mkdir -p "$BK_ROOT"
    cp -p "$SRV" "$BK_ROOT/server.py.pre-$MARKER"
    ln -sfn "$BK_ROOT" "$HOME/.albert_deploy_backups/latest_${MARKER}"
    say "[backup] -> $BK_ROOT/server.py.pre-$MARKER"
    python3 "$PYPATCH" "$SRV" "$MARKER" apply
    say ""
    say "Restart the dev container to load it:"
    say "  cd ~/rtsm/docker && docker compose restart rtsm-dev"
    say ""
    say "Verify (should now return dad/objects in view, NOT []):"
    say "  curl -s 'http://localhost:8002/search/semantic?query=dad&top_k=5&pose_state=any&max_stale_s=10' | jq '.results | length'"
    ;;
  --revert)
    say "== $MARKER : revert =="
    LATEST="$HOME/.albert_deploy_backups/latest_${MARKER}"
    bk="$LATEST/server.py.pre-$MARKER"
    [[ -f "$bk" ]] || { say "[ABORT] no backup at $bk"; exit 2; }
    cp -p "$bk" "$SRV"
    say "[revert] $SRV <- $bk"
    say "Restart: cd ~/rtsm/docker && docker compose restart rtsm-dev"
    ;;
  *) say "usage: $0 [--check|--dryrun|--apply|--revert]"; exit 1 ;;
esac
