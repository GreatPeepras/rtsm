#!/usr/bin/env bash
# Part 2 of Bug 1 fix (handoff_2026-06-01-evening-addendum.md):
# Replace the broken 2026-05-29 set_object_reference heap-push with a
# direct force_flush_now -> vectors.upsert_batch pair in the PATCH handler.
# WM-side force_flush_now was added by deploy_force_flush_now_2026-06-02.sh;
# this script only touches server.py.
set -euo pipefail
cd "$(dirname "$0")"

SV="rtsm/api/server.py"
[ -f "$SV" ] || { echo "FATAL: $SV not found"; exit 1; }

python3 - "$SV" <<'PYEOF'
import sys, pathlib
sv = pathlib.Path(sys.argv[1])
src = sv.read_text()

if "force_flush_now(oid)" in src:
    print("SKIP: PATCH handler already calls force_flush_now")
    sys.exit(0)

anchor = (
'        # 2026-05-29: force-flush PATCH\'d label_user/movability to FAISS.\n'
'        # update_user_fields modifies WM only; without this push the change\n'
'        # waits for natural re-observation, and a restart in that window\n'
'        # loses the user\'s label. Re-asserting reference state via\n'
'        # set_object_reference triggers the same lock-protected heap push\n'
'        # that pinning a reference image already does.\n'
'        if (getattr(o, "confirmed", False)\n'
'                and hasattr(working_memory, "set_object_reference")):\n'
'            try:\n'
'                working_memory.set_object_reference(\n'
'                    oid,\n'
'                    image_path=getattr(o, "reference_image_path", None),\n'
'                    embedding=getattr(o, "reference_emb", None),\n'
'                )\n'
'            except Exception as e:\n'
'                logger.warning(\n'
'                    f"PATCH force-flush for {oid} failed: {e}"\n'
'                )\n'
)

if src.count(anchor) != 1:
    print(f"FATAL: anchor not unique (found {src.count(anchor)})")
    sys.exit(1)

replacement = (
'        # 2026-06-02: synchronous flush of PATCH\'d label_user/movability\n'
'        # to FAISS. Supersedes the 2026-05-29 set_object_reference heap-\n'
'        # push, which the change-detection gate in collect_ready_for_upsert\n'
'        # silently dropped when neither emb nor xyz had moved (handoff_\n'
'        # 2026-06-01-evening-addendum.md, Bug 1). force_flush_now builds\n'
'        # the same payload collect_ready_for_upsert would build and writes\n'
'        # it via vectors.upsert_batch directly -- same pattern as\n'
'        # /objects/merge.\n'
'        if (getattr(o, "confirmed", False)\n'
'                and vectors is not None\n'
'                and hasattr(working_memory, "force_flush_now")):\n'
'            try:\n'
'                payload = working_memory.force_flush_now(oid)\n'
'                if payload is not None:\n'
'                    vectors.upsert_batch([payload])\n'
'            except Exception as e:\n'
'                logger.warning(\n'
'                    f"PATCH force-flush for {oid} failed: {e}"\n'
'                )\n'
)

sv.write_text(src.replace(anchor, replacement, 1))
print("OK: swapped set_object_reference -> force_flush_now in PATCH handler")
PYEOF

python3 -m py_compile "$SV" 2>/dev/null && echo "OK: $SV compiles" \
  || echo "WARN: $SV py_compile reported errors (check stderr; .pyc write may have failed harmlessly)"

echo "Done. Now: docker restart rtsm-dev"
