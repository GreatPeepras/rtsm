#!/bin/bash
# Deploy hybrid emb_mean update — Gate 2.5 EWMA tail — 2026-05-27
#
# Background
# ----------
# Gate 2.5 (commit 9606244, 2026-05-25) shipped the cosine-similarity
# re-id half of the original design — when spatial matching fails, look
# for an appearance match above tau=0.92 against confirmed WM objects.
#
# The original Gate 2.5 spec had a second half: EWMA emb_mean update
# at alpha=0.05. That never landed; instead, working_memory.py line
# 516 has carried this since the early days:
#
#     emb_mean = _l2norm(o.emb_mean * o.hits + e)   # running mean
#
# This is an unweighted running mean. At hits=100 a new observation
# contributes ~1%; at hits=200, ~0.5%. The canonical emb ossifies.
# That's bad for Gate 2.5 specifically: when an object that's been
# observed hundreds of times physically moves and gets re-id'd at the
# new location under different lighting, the canonical appearance has
# no room to track. The cosine eventually drops below tau and we
# spawn a duplicate proto.
#
# What this patch does
# --------------------
# Hybrid: running mean while hits < threshold (fast convergence on new
# protos), then EWMA at alpha after. Defaults: threshold=20, alpha=0.05.
#
# Threshold=20 was chosen so the running-mean phase covers roughly the
# "early proto + just-promoted" window where canonical appearance is
# still being established. After that, EWMA prevents ossification.
#
# Alpha=0.05 is the original Gate 2.5 spec value. Half-update in ~14
# observations — slow enough to be stable, fast enough to track real
# drift.
#
# Both knobs are configurable in rtsm.yaml under object:
#   emb_mean_hits_threshold: 20
#   emb_mean_ewma_alpha:     0.05
#
# Files modified
# --------------
# rtsm/stores/working_memory.py
#   - __init__ reads two new obj_cfg knobs (defaults preserve back-compat
#     if rtsm.yaml is older)
#   - update_object replaces the single running-mean line with the
#     hybrid branch
# rtsm/cfg/rtsm.yaml
#   - adds the two knobs under object: with explanatory comments
#
# Idempotent. Pre-flight backups. AST-validated.

set -euo pipefail

if [ ! -f rtsm/stores/working_memory.py ] || [ ! -f rtsm/cfg/rtsm.yaml ]; then
    echo "ERROR: run from repo root (need rtsm/stores/working_memory.py and rtsm/cfg/rtsm.yaml)" >&2
    exit 1
fi

TS=$(date +%Y%m%d-%H%M%S)
WM="rtsm/stores/working_memory.py"
CFG="rtsm/cfg/rtsm.yaml"

echo "== emb_mean hybrid deploy ($(date -Is)) =="

# ----------------------------------------------------------------------
# Pre-flight idempotency check.
# ----------------------------------------------------------------------
WM_NEEDS_PATCH=1
if grep -q "emb_mean_hits_threshold" "$WM"; then
    echo "  $WM already patched; skipping"
    WM_NEEDS_PATCH=0
fi

CFG_NEEDS_PATCH=1
if grep -q "emb_mean_hits_threshold" "$CFG"; then
    echo "  $CFG already patched; skipping"
    CFG_NEEDS_PATCH=0
fi

if [ "$WM_NEEDS_PATCH" -eq 0 ] && [ "$CFG_NEEDS_PATCH" -eq 0 ]; then
    echo "  nothing to do."
    exit 0
fi

# ----------------------------------------------------------------------
# Backups.
# ----------------------------------------------------------------------
if [ "$WM_NEEDS_PATCH" -eq 1 ]; then
    cp "$WM" "$WM.bak.$TS"
    echo "  backup: $WM.bak.$TS"
fi
if [ "$CFG_NEEDS_PATCH" -eq 1 ]; then
    cp "$CFG" "$CFG.bak.$TS"
    echo "  backup: $CFG.bak.$TS"
fi

# ----------------------------------------------------------------------
# Patch working_memory.py
# ----------------------------------------------------------------------
if [ "$WM_NEEDS_PATCH" -eq 1 ]; then
python3 <<'PYEOF'
import pathlib, sys
p = pathlib.Path("rtsm/stores/working_memory.py")
src = p.read_text()
orig = src

# ------------------------------------------------------------------
# Edit 1: add the two config knobs in __init__, right after the
# existing max_gallery / gallery_dupe_cos pair (which are the other
# obj_cfg embedding-side knobs — keeps related config together).
# ------------------------------------------------------------------
old1 = (
    '        self.max_gallery: int = int(obj_cfg.get("max_gallery", 6))\n'
    '        self.gallery_dupe_cos: float = float(obj_cfg.get("gallery_dupe_cos", 0.995))\n'
)
new1 = (
    '        self.max_gallery: int = int(obj_cfg.get("max_gallery", 6))\n'
    '        self.gallery_dupe_cos: float = float(obj_cfg.get("gallery_dupe_cos", 0.995))\n'
    '        # 2026-05-27: Gate 2.5 EWMA tail on emb_mean. Running mean for\n'
    '        # the first N=emb_mean_hits_threshold observations (fast\n'
    '        # convergence on new protos), then EWMA at alpha to prevent\n'
    '        # canonical-embedding ossification on long-lived objects.\n'
    '        # See update_object() below.\n'
    '        self.emb_mean_hits_threshold: int = int(obj_cfg.get("emb_mean_hits_threshold", 20))\n'
    '        self.emb_mean_ewma_alpha: float = float(obj_cfg.get("emb_mean_ewma_alpha", 0.05))\n'
)
n1 = src.count(old1)
if n1 != 1:
    sys.exit(f"[1/2] FAIL: max_gallery anchor not unique ({n1} matches)")
src = src.replace(old1, new1, 1)
print("[1/2] config knobs: added emb_mean_hits_threshold + emb_mean_ewma_alpha")

# ------------------------------------------------------------------
# Edit 2: replace the running-mean line with the hybrid branch.
# Anchor is the full line including the trailing comment, which is
# distinctive enough to be unique.
# ------------------------------------------------------------------
old2 = '        emb_mean = _l2norm(o.emb_mean * o.hits + e)  # simple running mean in L2 space (approx)\n'
new2 = (
    '        # 2026-05-27: hybrid emb_mean update. Running mean while the\n'
    '        # object is young (fast convergence), then EWMA at alpha once\n'
    '        # established (anti-ossification). The EWMA half is the\n'
    '        # second part of the original Gate 2.5 design — the first\n'
    '        # part, cosine re-id at tau=0.92, shipped 2026-05-25.\n'
    '        if o.hits < self.emb_mean_hits_threshold:\n'
    '            emb_mean = _l2norm(o.emb_mean * o.hits + e)\n'
    '        else:\n'
    '            alpha = self.emb_mean_ewma_alpha\n'
    '            emb_mean = _l2norm((1.0 - alpha) * o.emb_mean + alpha * e)\n'
)
n2 = src.count(old2)
if n2 != 1:
    sys.exit(f"[2/2] FAIL: running-mean anchor not unique ({n2} matches)")
src = src.replace(old2, new2, 1)
print("[2/2] update_object: replaced running mean with hybrid branch")

if src == orig:
    sys.exit("FAIL: no changes were made")

p.write_text(src)
PYEOF

python3 -c "import ast; ast.parse(open('rtsm/stores/working_memory.py').read()); print('  syntax-ok: working_memory.py')"
fi

# ----------------------------------------------------------------------
# Patch rtsm.yaml
# ----------------------------------------------------------------------
if [ "$CFG_NEEDS_PATCH" -eq 1 ]; then
python3 <<'PYEOF'
import pathlib, sys
p = pathlib.Path("rtsm/cfg/rtsm.yaml")
src = p.read_text()
orig = src

# Anchor on the last line of the existing object: block (miss_decay).
# Insert the new knobs right after it, keeping the section grouped.
old1 = "  miss_decay: 0.5\n"
new1 = (
    "  miss_decay: 0.5\n"
    "  # 2026-05-27: Gate 2.5 EWMA tail for emb_mean. Running mean for the\n"
    "  # first N observations (fast convergence on a new proto), then EWMA\n"
    "  # at alpha once established (prevents canonical-embedding\n"
    "  # ossification on long-lived objects, which Gate 2.5 re-id depends\n"
    "  # on). Defaults match the original Gate 2.5 spec.\n"
    "  emb_mean_hits_threshold: 20        # switch to EWMA after this many hits\n"
    "  emb_mean_ewma_alpha: 0.05          # weight on new obs once threshold reached\n"
)
n = src.count(old1)
if n != 1:
    sys.exit(f"FAIL: miss_decay anchor not unique in rtsm.yaml ({n} matches)")
src = src.replace(old1, new1, 1)
if src == orig:
    sys.exit("FAIL: no changes were made to rtsm.yaml")
p.write_text(src)
print("  yaml: added emb_mean_hits_threshold + emb_mean_ewma_alpha to object:")
PYEOF
fi

echo "== done =="
echo ""
echo "Restart RTSM to pick up the new config + behavior:"
echo "  docker compose -f docker/docker-compose.yml restart rtsm-dev"
echo ""
echo "To tune (defaults are sensible):"
echo "  object:"
echo "    emb_mean_hits_threshold: 20    # higher = longer running-mean phase"
echo "    emb_mean_ewma_alpha: 0.05      # higher = faster drift tracking"
echo ""
echo "To verify in a running container:"
echo "  docker exec rtsm-dev python3 -c \"\\"
echo "import yaml; cfg = yaml.safe_load(open('rtsm/cfg/rtsm.yaml'));\\"
echo "obj = cfg.get('object', {});\\"
echo "print('threshold=', obj.get('emb_mean_hits_threshold'));\\"
echo "print('alpha=',     obj.get('emb_mean_ewma_alpha'))\""
