#!/bin/bash
# RTSM server-side hotfixes — 2026-05-29
#
# Two bugs surfaced during today's voice tests:
#
#   1. _encode_reference_image passes a numpy ndarray to clip_adapter, which
#      expects a PIL.Image and calls .convert() on it. Result:
#        HTTP 400 {"detail":"'numpy.ndarray' object has no attribute 'convert'"}
#      whenever name_object() tries to upload its reference snapshot.
#
#   2. /objects/by_label_user crashes inside _entry() with AttributeError on
#      xyz.tolist() when xyz_world is already a Python list (not ndarray).
#      FastAPI turns the AttributeError into a 500, jq parses the body as
#      null, looks like "no match found". Also defensively wrap robot_pose.
#
# Idempotent: re-running detects each patch and skips.

set -euo pipefail

if [ ! -f rtsm/api/server.py ]; then
    echo "ERROR: run from rtsm repo root (rtsm/api/server.py not found)" >&2
    exit 1
fi
TS=$(date +%Y%m%d-%H%M%S)
SRV_PY="rtsm/api/server.py"

echo "== rtsm server hotfixes ($(date -Is)) =="

# ---------------------------------------------------------------------------
# Fix 1: wrap ndarray in PIL.Image for clip_adapter
# ---------------------------------------------------------------------------
if grep -q "PIL.Image.fromarray\|_PILImage.fromarray" "$SRV_PY"; then
    echo "[1/2] PIL wrap: already patched, skipping"
else
    cp "$SRV_PY" "$SRV_PY.bak.$TS"
    echo "[1/2] backed up to $SRV_PY.bak.$TS"

    python3 <<'PYEOF'
import pathlib, sys
p = pathlib.Path("rtsm/api/server.py")
src = p.read_text()

# Anchor: the encode_image / embed_image dispatch block.
anchor = '''        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        if hasattr(clip_adapter, "encode_image"):
            emb_raw = clip_adapter.encode_image(rgb)
        elif hasattr(clip_adapter, "embed_image"):
            emb_raw = clip_adapter.embed_image(rgb)
        else:'''

replacement = '''        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        # 2026-05-29: clip_adapter.encode_image expects a PIL.Image (it
        # calls .convert() internally). Wrap the ndarray defensively;
        # fall back to ndarray only if PIL isn't importable.
        try:
            from PIL import Image as _PILImage
            img_in = _PILImage.fromarray(rgb)
        except Exception:
            img_in = rgb
        if hasattr(clip_adapter, "encode_image"):
            emb_raw = clip_adapter.encode_image(img_in)
        elif hasattr(clip_adapter, "embed_image"):
            emb_raw = clip_adapter.embed_image(img_in)
        else:'''

if anchor not in src:
    sys.exit("ERROR [1/2]: encode_image dispatch anchor not found")
src = src.replace(anchor, replacement, 1)
p.write_text(src)
print("  ok [1/2]: wrapped ndarray in PIL.Image")
PYEOF
fi

# ---------------------------------------------------------------------------
# Fix 2: defensive serialization in by_label_user _entry helper + robot_pose
# ---------------------------------------------------------------------------
if grep -q "_xyz_to_list\|2026-05-29: defensive serialization" "$SRV_PY"; then
    echo "[2/2] by_label_user serialization: already patched, skipping"
else
    if [ ! -f "$SRV_PY.bak.$TS" ]; then
        cp "$SRV_PY" "$SRV_PY.bak.$TS"
        echo "[2/2] backed up to $SRV_PY.bak.$TS"
    fi

    python3 <<'PYEOF'
import pathlib, sys
p = pathlib.Path("rtsm/api/server.py")
src = p.read_text()

# Anchor: the _entry() helper inside get_object_by_label_user. Replace the
# whole function body and the return-with-robot_pose so we cover both bugs.
anchor = '''        def _entry(o: Any) -> Dict[str, Any]:
            xyz = getattr(o, "xyz_world", None)
            ref_path = getattr(o, "reference_image_path", None)
            return {
                "id": getattr(o, "id", None),
                "label_user": getattr(o, "label_user", None),
                "label_primary": getattr(o, "label_primary", None),
                "xyz_world": xyz.tolist() if xyz is not None else None,
                "movability_class": getattr(o, "movability_class", None),
                "pose_state_at_observation": getattr(
                    o, "pose_state_at_observation", "on_floor"
                ),
                "confirmed": bool(getattr(o, "confirmed", False)),
                "last_seen_wall_utc": float(
                    getattr(o, "last_seen_wall_utc", 0.0) or 0.0
                ),
                "reference_image_path": ref_path,
                "has_reference_image": bool(ref_path),
            }

        return {
            "name": name,
            "match_count": len(matches),
            "primary": _entry(primary),
            "all_matches": [_entry(o) for o in matches],
            "robot_pose": working_memory.get_robot_pose(),
        }'''

replacement = '''        # 2026-05-29: defensive serialization. xyz_world may be a
        # Python list OR a numpy ndarray depending on how the object got
        # into WM (ingest path vs faiss-rehydrate). Convert both safely.
        def _xyz_to_list(xyz: Any) -> Optional[List[float]]:
            if xyz is None:
                return None
            if hasattr(xyz, "tolist"):
                try:
                    return [float(v) for v in xyz.tolist()]
                except Exception:
                    pass
            try:
                return [float(v) for v in xyz]
            except Exception:
                return None

        def _entry(o: Any) -> Dict[str, Any]:
            ref_path = getattr(o, "reference_image_path", None)
            return {
                "id": getattr(o, "id", None),
                "label_user": getattr(o, "label_user", None),
                "label_primary": getattr(o, "label_primary", None),
                "xyz_world": _xyz_to_list(getattr(o, "xyz_world", None)),
                "movability_class": getattr(o, "movability_class", None),
                "pose_state_at_observation": getattr(
                    o, "pose_state_at_observation", "on_floor"
                ),
                "confirmed": bool(getattr(o, "confirmed", False)),
                "last_seen_wall_utc": float(
                    getattr(o, "last_seen_wall_utc", 0.0) or 0.0
                ),
                "reference_image_path": ref_path,
                "has_reference_image": bool(ref_path),
            }

        # robot_pose may also surface non-serializable types; degrade to None
        # so the endpoint never 500s just because of pose-shape weirdness.
        try:
            robot_pose = working_memory.get_robot_pose()
        except Exception:
            robot_pose = None

        return {
            "name": name,
            "match_count": len(matches),
            "primary": _entry(primary),
            "all_matches": [_entry(o) for o in matches],
            "robot_pose": robot_pose,
        }'''

if anchor not in src:
    sys.exit("ERROR [2/2]: by_label_user _entry anchor not found")
src = src.replace(anchor, replacement, 1)
p.write_text(src)
print("  ok [2/2]: by_label_user _entry hardened against xyz/pose shape")
PYEOF
fi

# ---------------------------------------------------------------------------
# Sanity
# ---------------------------------------------------------------------------
python3 -c "
import ast
ast.parse(open('rtsm/api/server.py').read())
print('  syntax-ok: rtsm/api/server.py')
"

echo ""
echo "== done =="
echo "Restart RTSM:"
echo "  docker restart rtsm-dev"
echo ""
echo "Then retry from Execution:"
echo "  curl -s --get 'http://localhost:8002/objects/by_label_user' \\"
echo "    --data-urlencode 'name=gloves' | jq .primary"
echo "  # expect: {id: '7543b81b...', label_user: 'gloves', ...}"
echo ""
echo "And after the next voice test that names an object, expect:"
echo "  ls -la /mnt/rtsm-data/refs/"
echo "  # expect: <oid>.jpg present"
