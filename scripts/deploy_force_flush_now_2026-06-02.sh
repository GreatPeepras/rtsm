#!/usr/bin/env bash
# Bug 1 fix from handoff_2026-06-01-evening-addendum.md:
# label_user / movability_class PATCHes don't survive restart because the
# collect_ready_for_upsert change-detection gate doesn't see those fields
# as a "change". This adds WorkingMemory.force_flush_now(oid) which
# synchronously builds the same payload collect_ready_for_upsert builds
# and updates last_upsert_* atomically. PATCH handler then calls it and
# pushes the payload to vectors.upsert_batch directly -- same architectural
# pattern the merge endpoint uses (and the DELETE-fix we just deployed).
set -euo pipefail
cd "$(dirname "$0")"

WM="rtsm/stores/working_memory.py"
SV="rtsm/api/server.py"
[ -f "$WM" ] || { echo "FATAL: $WM not found"; exit 1; }
[ -f "$SV" ] || { echo "FATAL: $SV not found"; exit 1; }

python3 - "$WM" "$SV" <<'PYEOF'
import sys, pathlib

WM_PATH, SV_PATH = sys.argv[1], sys.argv[2]

# ---------- 1. working_memory.py: add force_flush_now ----------
wm = pathlib.Path(WM_PATH)
src = wm.read_text()

WM_NEEDLE_PRESENT = "def force_flush_now" in src
if WM_NEEDLE_PRESENT:
    print("SKIP: force_flush_now already present in working_memory.py")
else:
    # Anchor: end of set_object_reference + the removal-section comment.
    anchor = (
        "            if o.confirmed:\n"
        "                heapq.heappush(self._ltm_heap, (_now_mono(), oid))\n"
        "            return o\n"
        "\n"
        "    # ---------- removal ----------\n"
    )
    if src.count(anchor) != 1:
        print(f"FATAL: working_memory.py anchor not unique (found {src.count(anchor)})")
        sys.exit(1)

    insertion = (
        "            if o.confirmed:\n"
        "                heapq.heappush(self._ltm_heap, (_now_mono(), oid))\n"
        "            return o\n"
        "\n"
        "    # 2026-06-02: synchronous flush of PATCH-style mutations.  Bypasses\n"
        "    # the collect_ready_for_upsert change-detection gate so label_user\n"
        "    # and movability_class changes can be persisted to FAISS\n"
        "    # immediately, matching the architectural pattern used by\n"
        "    # /objects/merge (vectors.upsert_batch via build_faiss_record_for_merge).\n"
        "    # See handoff_2026-06-01-evening-addendum.md, Bug 1.\n"
        "    def force_flush_now(self, oid: str) -> Optional[Dict[str, Any]]:\n"
        "        \"\"\"Build a FAISS upsert payload for `oid` and update last_upsert_*.\n"
        "\n"
        "        Returns the payload (caller passes it to vectors.upsert_batch),\n"
        "        or None if the OID is unknown / unconfirmed / has no emb_mean.\n"
        "        Payload shape matches collect_ready_for_upsert's regular loop\n"
        "        exactly so the FAISS sidecar stays consistent.\n"
        "        \"\"\"\n"
        "        m_now = _now_mono()\n"
        "        wall_now = _now_wall_utc()\n"
        "        with self._lock:\n"
        "            o = self._map.get(oid)\n"
        "            if o is None or not o.confirmed or o.emb_mean is None:\n"
        "                return None\n"
        "            label_topk = sorted(\n"
        "                o.label_scores.items(), key=lambda kv: kv[1], reverse=True\n"
        "            )[:5]\n"
        "            payload = {\n"
        "                \"object_id\": o.id,\n"
        "                \"emb\": o.emb_mean.astype(np.float32),\n"
        "                \"xyz\": o.xyz_world.astype(np.float32),\n"
        "                \"label_primary\": o.label_primary,\n"
        "                \"label_user\": o.label_user,\n"
        "                \"display_label\": o.label_user or o.label_primary,\n"
        "                \"movability_class\": o.movability_class,\n"
        "                \"pose_state_at_observation\": o.pose_state_at_observation,\n"
        "                \"reference_image_path\": o.reference_image_path,\n"
        "                \"reference_emb\": (\n"
        "                    o.reference_emb.astype(np.float32).tolist()\n"
        "                    if o.reference_emb is not None else None\n"
        "                ),\n"
        "                \"label_confidence\": (\n"
        "                    o.label_scores.get(o.label_primary, 0.0)\n"
        "                    if o.label_primary else 0.0\n"
        "                ),\n"
        "                \"label_topk\": [k for k, _ in label_topk],\n"
        "                \"label_scores\": [float(v) for _, v in label_topk],\n"
        "                \"label_hits\":   [int(o.label_hits.get(k, 0)) for k, _ in label_topk],\n"
        "                \"stability\": float(o.stability),\n"
        "                \"last_seen_wall_utc\": o.last_seen_wall_utc,\n"
        "                \"created_at\": o.created_wall_utc,\n"
        "                \"created_mono\": o.created_mono,\n"
        "                \"updated_at\": wall_now,\n"
        "            }\n"
        "            o.last_upsert_wall_utc = wall_now\n"
        "            o.last_upsert_mono = m_now\n"
        "            o.last_upsert_emb = o.emb_mean.copy()\n"
        "            o.last_upsert_xyz = o.xyz_world.copy()\n"
        "            self._upsert_count_total += 1\n"
        "            return payload\n"
        "\n"
        "    # ---------- removal ----------\n"
    )
    wm.write_text(src.replace(anchor, insertion, 1))
    print("OK: inserted force_flush_now into working_memory.py")

# ---------- 2. server.py: wire force_flush_now into PATCH handler ----------
sv = pathlib.Path(SV_PATH)
src = sv.read_text()

SV_NEEDLE_PRESENT = "force_flush_now(oid)" in src
if SV_NEEDLE_PRESENT:
    print("SKIP: PATCH handler already calls force_flush_now")
else:
    anchor = (
        "        if o is None:\n"
        "            raise HTTPException(status_code=404, detail=f\"Object {oid} not found\")\n"
        "        return _obj_detail(o)\n"
    )
    if src.count(anchor) != 1:
        print(f"FATAL: server.py PATCH anchor not unique (found {src.count(anchor)})")
        sys.exit(1)

    insertion = (
        "        if o is None:\n"
        "            raise HTTPException(status_code=404, detail=f\"Object {oid} not found\")\n"
        "\n"
        "        # 2026-06-02: synchronously flush PATCH changes to FAISS.\n"
        "        # Without this, label_user / movability_class mutations get\n"
        "        # held by the collect_ready_for_upsert change-detection gate\n"
        "        # and can be lost across restart. See\n"
        "        # handoff_2026-06-01-evening-addendum.md Bug 1.\n"
        "        if vectors is not None and hasattr(working_memory, \"force_flush_now\"):\n"
        "            try:\n"
        "                payload = working_memory.force_flush_now(oid)\n"
        "                if payload is not None:\n"
        "                    vectors.upsert_batch([payload])\n"
        "            except Exception as e:\n"
        "                import logging as _logging\n"
        "                _logging.getLogger(__name__).warning(\n"
        "                    f\"PATCH /objects/{oid}: force_flush_now failed: {e}\"\n"
        "                )\n"
        "\n"
        "        return _obj_detail(o)\n"
    )
    sv.write_text(src.replace(anchor, insertion, 1))
    print("OK: wired force_flush_now into server.py PATCH handler")
PYEOF

# AST validation
python3 -m py_compile "$WM" 2>/dev/null && echo "OK: $WM compiles" \
  || echo "WARN: $WM py_compile reported errors (check stderr; .pyc write may have failed harmlessly)"
python3 -m py_compile "$SV" 2>/dev/null && echo "OK: $SV compiles" \
  || echo "WARN: $SV py_compile reported errors (check stderr; .pyc write may have failed harmlessly)"

echo "Done. Now: docker restart rtsm-dev"
