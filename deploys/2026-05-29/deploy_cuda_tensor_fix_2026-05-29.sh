#!/bin/bash
# RTSM CUDA-tensor fix — 2026-05-29
#
# Third bug surfaced today: clip_adapter.encode_image() returns a torch
# tensor on cuda:0 (same device as the CLIP model), and our encoder calls
# np.asarray() on it directly. np.asarray on a CUDA tensor implicitly calls
# .numpy(), which fails with:
#   "can't convert cuda:0 device type tensor to numpy.
#    Use Tensor.cpu() to copy the tensor to host memory first."
#
# Fix: detect torch.Tensor and move to CPU + detach before np.asarray.
# Falls through silently if torch isn't importable.
#
# Idempotent.

set -euo pipefail

if [ ! -f rtsm/api/server.py ]; then
    echo "ERROR: run from rtsm repo root (rtsm/api/server.py not found)" >&2
    exit 1
fi
TS=$(date +%Y%m%d-%H%M%S)
SRV_PY="rtsm/api/server.py"

echo "== rtsm CUDA-tensor encode fix ($(date -Is)) =="

if grep -q "emb_raw.detach().cpu()" "$SRV_PY"; then
    echo "  already patched, skipping"
else
    cp "$SRV_PY" "$SRV_PY.bak.$TS"
    echo "  backed up to $SRV_PY.bak.$TS"

    python3 <<'PYEOF'
import pathlib, sys
p = pathlib.Path("rtsm/api/server.py")
src = p.read_text()

# Anchor: the encode_image dispatch + np.asarray line. Replace with a
# tensor-aware version.
anchor = '''        if hasattr(clip_adapter, "encode_image"):
            emb_raw = clip_adapter.encode_image(img_in)
        elif hasattr(clip_adapter, "embed_image"):
            emb_raw = clip_adapter.embed_image(img_in)
        else:
            attrs = [m for m in dir(clip_adapter)
                     if callable(getattr(clip_adapter, m, None))
                     and not m.startswith("_")]
            raise AttributeError(
                f"clip_adapter has no encode_image or embed_image method. "
                f"Available callables: {attrs}"
            )
        arr = np.asarray(emb_raw, dtype=np.float32).reshape(-1)'''

replacement = '''        if hasattr(clip_adapter, "encode_image"):
            emb_raw = clip_adapter.encode_image(img_in)
        elif hasattr(clip_adapter, "embed_image"):
            emb_raw = clip_adapter.embed_image(img_in)
        else:
            attrs = [m for m in dir(clip_adapter)
                     if callable(getattr(clip_adapter, m, None))
                     and not m.startswith("_")]
            raise AttributeError(
                f"clip_adapter has no encode_image or embed_image method. "
                f"Available callables: {attrs}"
            )
        # 2026-05-29: clip_adapter returns a torch tensor on cuda:0. Move
        # to CPU + detach before np.asarray (which implicitly calls .numpy()).
        try:
            import torch as _torch
            if isinstance(emb_raw, _torch.Tensor):
                emb_raw = emb_raw.detach().cpu().numpy()
        except ImportError:
            pass
        arr = np.asarray(emb_raw, dtype=np.float32).reshape(-1)'''

if anchor not in src:
    sys.exit("ERROR: encode dispatch + np.asarray anchor not found")
src = src.replace(anchor, replacement, 1)
p.write_text(src)
print("  ok: CUDA tensor now moved to CPU before np.asarray")
PYEOF
fi

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
echo "Then re-run the bulk repro from Albert (the same one):"
echo "  curl -s -X POST 'http://192.168.0.53:8002/objects/reference_bulk' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d @/tmp/bulk_test.json | jq '.results[0]'"
echo "Expect: {\"oid\": \"...\", \"status\": \"ok\", ...}"
echo ""
echo "Then verify the file landed on disk (from Execution):"
echo "  ls -la /mnt/rtsm-data/refs/"
