#!/usr/bin/env bash
# deploy_movability_default_2026-05-30.sh
#
# Coarse-default movability_class='movable' on proto spawn (RTSM Phase B item 1).
#
# Background: per movability_assignment_design.md (accepted 2026-05-28),
# every unlabeled object should get a moderate-TTL movability class at
# creation so eviction has something concrete to act on. 'movable' is the
# proposed default (~3-day TTL). static/permanent are LANDMARK-eligible
# and MUST NOT be auto-assigned -- they are reserved for manual PATCH.
#
# Changes (idempotent):
#   working_memory.py:
#     1. Add _AUTO_DEFAULT_MOVABILITY_OK class constant.
#     2. Read cfg.object.default_movability with validation in __init__.
#     3. Pass movability_class=self.default_movability into create_object's
#        ObjectState constructor.
#   rtsm.yaml:
#     4. Add default_movability: movable under the object: block.
#
# Existing objects (sidecar has movability_class=None) are NOT migrated.
# They fall through the eviction code's existing None -> semi_static
# fallback. A backfill tool for existing objects is a separate task.
#
# Usage:
#   cd ~/rtsm
#   bash deploy_movability_default_2026-05-30.sh
#
# Rollback: backup files are written next to the originals with a
# timestamp suffix. To revert:
#   cp rtsm/stores/working_memory.py.bak.<ts> rtsm/stores/working_memory.py
#   cp rtsm/cfg/rtsm.yaml.bak.<ts> rtsm/cfg/rtsm.yaml
#
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(pwd)}"
WM_PATH="$REPO_ROOT/rtsm/stores/working_memory.py"
CFG_PATH="$REPO_ROOT/rtsm/cfg/rtsm.yaml"
TS="$(date +%Y%m%d-%H%M%S)"

[ -f "$WM_PATH" ]  || { echo "FAIL: not found: $WM_PATH"  >&2; exit 1; }
[ -f "$CFG_PATH" ] || { echo "FAIL: not found: $CFG_PATH" >&2; exit 1; }

cp "$WM_PATH"  "$WM_PATH.bak.$TS"
cp "$CFG_PATH" "$CFG_PATH.bak.$TS"
echo "[+] backups: $WM_PATH.bak.$TS and $CFG_PATH.bak.$TS"

python3 - <<PYEOF
import sys
from pathlib import Path

WM  = Path("$WM_PATH")
CFG = Path("$CFG_PATH")

wm_src  = WM.read_text()
cfg_src = CFG.read_text()

# -------------------------------------------------------------------- #
# Edit 1: add _AUTO_DEFAULT_MOVABILITY_OK class constant
# Anchor: the existing _VALID_MOVABILITY frozenset definition.
# -------------------------------------------------------------------- #
old1 = '''    _VALID_MOVABILITY = frozenset({
        "permanent", "static", "semi_static",
        "movable", "roaming", "ephemeral",
    })'''
new1 = '''    _VALID_MOVABILITY = frozenset({
        "permanent", "static", "semi_static",
        "movable", "roaming", "ephemeral",
    })
    # 2026-05-30: classes safe to assign AUTOMATICALLY at proto spawn.
    # Excludes static/permanent: those are landmark-eligible per
    # movability_assignment_design.md and require manual PATCH so a human
    # confirms the pose-correctness-critical assignment. None is also
    # valid (means "no default"); eviction has its own None -> semi_static
    # fallback for back-compat.
    _AUTO_DEFAULT_MOVABILITY_OK = frozenset({
        "semi_static", "movable", "roaming", "ephemeral",
    })'''

if "_AUTO_DEFAULT_MOVABILITY_OK" in wm_src:
    print("[1/4] working_memory.py: _AUTO_DEFAULT_MOVABILITY_OK already present, skipping")
elif wm_src.count(old1) == 1:
    wm_src = wm_src.replace(old1, new1, 1)
    print("[1/4] working_memory.py: added _AUTO_DEFAULT_MOVABILITY_OK")
else:
    sys.exit(f"[1/4] FAIL: _VALID_MOVABILITY anchor not unique ({wm_src.count(old1)} matches)")

# -------------------------------------------------------------------- #
# Edit 2: read cfg.object.default_movability in __init__
# Anchor: the emb_mean_ewma_alpha line followed by self._pose_state.
# -------------------------------------------------------------------- #
old2 = '''        self.emb_mean_ewma_alpha: float = float(obj_cfg.get("emb_mean_ewma_alpha", 0.05))
        self._pose_state: str = "on_floor"'''
new2 = '''        self.emb_mean_ewma_alpha: float = float(obj_cfg.get("emb_mean_ewma_alpha", 0.05))

        # 2026-05-30: coarse-default movability_class on proto spawn.
        # Per movability_assignment_design.md (accepted 2026-05-28):
        #  - Default 'movable' (~3-day TTL) gives eviction something to act on.
        #  - None is allowed for back-compat (eviction falls back to semi_static).
        #  - static/permanent are landmark-eligible and MUST NOT be auto-assigned;
        #    they require manual PATCH. Bad values warn and fall back to 'movable'.
        _raw_default_mov = obj_cfg.get("default_movability", "movable")
        if _raw_default_mov is None:
            self.default_movability: Optional[str] = None
        elif _raw_default_mov in self._AUTO_DEFAULT_MOVABILITY_OK:
            self.default_movability = str(_raw_default_mov)
        else:
            logger.warning(
                "[WM] object.default_movability=%r is not auto-assignable "
                "(must be one of %s, or null). static/permanent are "
                "landmark-eligible and require manual PATCH. Falling back to "
                "'movable'. See movability_assignment_design.md.",
                _raw_default_mov, sorted(self._AUTO_DEFAULT_MOVABILITY_OK),
            )
            self.default_movability = "movable"

        self._pose_state: str = "on_floor"'''

if "default_movability" in wm_src and "self.default_movability" in wm_src:
    print("[2/4] working_memory.py: default_movability config-read already present, skipping")
elif wm_src.count(old2) == 1:
    wm_src = wm_src.replace(old2, new2, 1)
    print("[2/4] working_memory.py: added default_movability config-read")
else:
    sys.exit(f"[2/4] FAIL: __init__ anchor not unique ({wm_src.count(old2)} matches)")

# -------------------------------------------------------------------- #
# Edit 3: pass movability_class into ObjectState() in create_object()
# Anchor: pose_state_at_observation line followed by the closing paren.
# -------------------------------------------------------------------- #
old3 = '''            pose_state_at_observation=self._current_observation_tag,
        )
        with self._lock:'''
new3 = '''            pose_state_at_observation=self._current_observation_tag,
            # 2026-05-30: coarse default; see __init__ for validation.
            movability_class=self.default_movability,
        )
        with self._lock:'''

if "movability_class=self.default_movability" in wm_src:
    print("[3/4] working_memory.py: create_object already passes movability_class, skipping")
elif wm_src.count(old3) == 1:
    wm_src = wm_src.replace(old3, new3, 1)
    print("[3/4] working_memory.py: create_object now defaults movability_class")
else:
    sys.exit(f"[3/4] FAIL: create_object anchor not unique ({wm_src.count(old3)} matches)")

WM.write_text(wm_src)

# -------------------------------------------------------------------- #
# Edit 4: rtsm.yaml -- add default_movability under object:
# Anchor: the last line of the object: block (emb_mean_ewma_alpha entry).
# -------------------------------------------------------------------- #
old4 = '''  emb_mean_ewma_alpha: 0.05          # weight on new obs once threshold reached'''
new4 = '''  emb_mean_ewma_alpha: 0.05          # weight on new obs once threshold reached
  # 2026-05-30: coarse default movability_class for every new proto.
  # Auto-assignable values: semi_static, movable, roaming, ephemeral, or null.
  # static/permanent are landmark-eligible and require manual PATCH per
  # movability_assignment_design.md. Bad values fall back to 'movable'.
  default_movability: movable'''

if "default_movability:" in cfg_src:
    print("[4/4] rtsm.yaml: default_movability already present, skipping")
elif cfg_src.count(old4) == 1:
    cfg_src = cfg_src.replace(old4, new4, 1)
    CFG.write_text(cfg_src)
    print("[4/4] rtsm.yaml: added default_movability: movable")
else:
    sys.exit(f"[4/4] FAIL: rtsm.yaml object: anchor not unique ({cfg_src.count(old4)} matches)")

print()
print("Applied. Restart RTSM to take effect:")
print("  docker compose -f ~/rtsm/docker/docker-compose.yml restart rtsm-dev")
print()
print("Verify with the unit test:")
print("  cd ~/rtsm && PYTHONPATH=. python3 tests/test_movability_default.py")
print()
print("Or with a quick smoke test (after restart):")
print("  curl -s http://localhost:8002/objects?limit=5 | jq '.objects[] | {id, movability_class}'")
print("  (Existing objects will still show null until they re-create or you backfill.)")
PYEOF
