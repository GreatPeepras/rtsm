#!/bin/bash
# Deploy reference-snapshot integration — 2026-05-29
#
# Wires Albert's named-moment snapshots into RTSM as a persistent
# per-object reference image + embedding. Unlocks:
#   - rehydrate seeding: named objects come back from FAISS with appearance
#     evidence (emb_gallery seeded from reference_emb), not just emb_mean.
#   - layered recall: "Where is Quackers?" -> RTSM /objects/by_label_user
#   - boot-time backfill: Albert pushes his local snapshots during warmup.
#   - Phase C unlock: visual find / re-id will read reference_emb later.
#
# Five patches to rtsm/stores/working_memory.py:
#   1. ObjectState: add reference_image_path + reference_emb fields.
#   2. collect_ready_for_upsert force-flush: include both fields in payload.
#   3. collect_ready_for_upsert normal path: same.
#   4. rehydrate_from_faiss: read both fields from sidecar, seed emb_gallery
#      from reference_emb so rehydrated named objects have appearance
#      evidence immediately (closes the "rehydrated = emb_mean-only matcher"
#      gap noted in handoff_2026-05-25.md lesson #5).
#   5. Append set_object_reference() helper method (thread-safe writer).
#
# Two patches to rtsm/api/server.py:
#   6. Add Pydantic models (ReferenceImagePayload, ReferenceBulk*).
#   7. Add endpoints:
#        POST /objects/{oid}/reference         — single snapshot upload
#        POST /objects/reference_bulk          — Albert boot-time backfill
#        GET  /objects/by_label_user           — recall path lookup
#
# Idempotent: re-running is a no-op once all patches are present.
# Pre-flight: takes timestamped backups before editing.
# Sanity: ast.parse both files at the end.

set -euo pipefail

if [ ! -f rtsm/stores/working_memory.py ] || [ ! -f rtsm/api/server.py ]; then
    echo "ERROR: run this from the rtsm repo root." >&2
    echo "  Expected: rtsm/stores/working_memory.py and rtsm/api/server.py" >&2
    exit 1
fi
TS=$(date +%Y%m%d-%H%M%S)

echo "== rtsm reference-snapshot deploy ($(date -Is)) =="

WM_PY="rtsm/stores/working_memory.py"
SRV_PY="rtsm/api/server.py"

# ---------------------------------------------------------------------------
# Patches 1-4: working_memory.py edits (ObjectState + payload x2 + rehydrate)
# ---------------------------------------------------------------------------
if grep -q "reference_image_path: Optional\[str\] = None" "$WM_PY"; then
    echo "[1-4/7] working_memory.py: already patched, skipping field/payload/rehydrate edits"
else
    cp "$WM_PY" "$WM_PY.bak.$TS"
    echo "[1-4/7] working_memory.py: backed up to $WM_PY.bak.$TS"

    python3 <<'PYEOF'
import pathlib, sys
p = pathlib.Path("rtsm/stores/working_memory.py")
src = p.read_text()

# ---- Patch 1: ObjectState dataclass — add two fields after pose_state_at_observation ----
anchor_1 = (
    "    movability_class: Optional[str] = None\n"
    "    pose_state_at_observation: str = \"on_floor\"\n"
)
addition_1 = (
    "\n"
    "    # --- 2026-05-29: reference snapshot (named-moment ground truth) ---\n"
    "    # Path on disk to the canonical JPEG (\"the moment you said this is\n"
    "    # Quackers\"). None until set via POST /objects/{oid}/reference.\n"
    "    # The file lives outside the sidecar at /mnt/rtsm-data/refs/<oid>.jpg\n"
    "    # by default. Persisted as a string in the FAISS sidecar.\n"
    "    reference_image_path: Optional[str] = None\n"
    "\n"
    "    # CLIP embedding of the reference snapshot. L2-normalized float32,\n"
    "    # same dim as emb_mean. Persisted through the FAISS sidecar (as a\n"
    "    # JSON list, coerced back to ndarray on rehydrate). On rehydrate,\n"
    "    # used to seed emb_gallery so named objects have appearance evidence\n"
    "    # at cold-start (no waiting for re-observation).\n"
    "    reference_emb: Optional[Emb] = None\n"
)
if anchor_1 not in src:
    sys.exit("ERROR [1/7]: ObjectState anchor not found (pose_state_at_observation line)")
src = src.replace(anchor_1, anchor_1 + addition_1, 1)
print("  ok [1/7]: ObjectState gained reference_image_path + reference_emb")

# ---- Patch 2: force-flush payload (24-sp indent) ----
anchor_2 = (
    "                        \"movability_class\": o.movability_class,\n"
    "                        \"pose_state_at_observation\": o.pose_state_at_observation,\n"
)
addition_2 = (
    "                        # 2026-05-29: reference snapshot (named-moment GT)\n"
    "                        \"reference_image_path\": o.reference_image_path,\n"
    "                        \"reference_emb\": (\n"
    "                            o.reference_emb.astype(np.float32).tolist()\n"
    "                            if o.reference_emb is not None else None\n"
    "                        ),\n"
)
if anchor_2 not in src:
    sys.exit("ERROR [2/7]: force-flush payload anchor not found")
src = src.replace(anchor_2, anchor_2 + addition_2, 1)
print("  ok [2/7]: force-flush payload includes reference fields")

# ---- Patch 3: normal-path payload (20-sp indent) ----
anchor_3 = (
    "                    \"movability_class\": o.movability_class,\n"
    "                    \"pose_state_at_observation\": o.pose_state_at_observation,\n"
)
addition_3 = (
    "                    # 2026-05-29: reference snapshot (named-moment GT)\n"
    "                    \"reference_image_path\": o.reference_image_path,\n"
    "                    \"reference_emb\": (\n"
    "                        o.reference_emb.astype(np.float32).tolist()\n"
    "                        if o.reference_emb is not None else None\n"
    "                    ),\n"
)
if anchor_3 not in src:
    sys.exit("ERROR [3/7]: normal-path payload anchor not found")
src = src.replace(anchor_3, anchor_3 + addition_3, 1)
print("  ok [3/7]: normal-path payload includes reference fields")

# ---- Patch 4: rehydrate — read reference fields and seed emb_gallery ----
# Anchor on the unique 'new_objects.append(o)' line (count must be 1).
anchor_4 = "            new_objects.append(o)\n"
addition_4 = (
    "            # 2026-05-29: reference snapshot (named-moment ground truth).\n"
    "            # Reads from sidecar; seeds emb_gallery so association has\n"
    "            # appearance evidence on rehydrate (no waiting for re-observation).\n"
    "            # Solves the \"rehydrated = emb_mean-only matcher\" gap noted in\n"
    "            # handoff_2026-05-25.md lesson #5 — for named objects, anyway.\n"
    "            ref_path = meta.get(\"reference_image_path\")\n"
    "            o.reference_image_path = ref_path\n"
    "            ref_emb_raw = meta.get(\"reference_emb\")\n"
    "            if ref_emb_raw is not None:\n"
    "                try:\n"
    "                    ref_emb_arr = np.asarray(ref_emb_raw, dtype=np.float32).reshape(-1)\n"
    "                    if ref_emb_arr.shape[0] == expected_dim:\n"
    "                        o.reference_emb = ref_emb_arr\n"
    "                        # Seed gallery: rehydrated object DID have appearance\n"
    "                        # at naming-time, even if we have no view_bins record.\n"
    "                        o.emb_gallery = ref_emb_arr.astype(np.float16).reshape(1, -1)\n"
    "                    else:\n"
    "                        logger.warning(\n"
    "                            f\"[WM] rehydrate: reference_emb dim mismatch for \"\n"
    "                            f\"oid={oid[:8]}: got {ref_emb_arr.shape[0]} \"\n"
    "                            f\"expected {expected_dim}; skipping\"\n"
    "                        )\n"
    "                except Exception as _e:\n"
    "                    logger.warning(\n"
    "                        f\"[WM] rehydrate: bad reference_emb for {oid[:8]}: {_e}\"\n"
    "                    )\n"
)
n_anchor_4 = src.count(anchor_4)
if n_anchor_4 != 1:
    sys.exit(f"ERROR [4/7]: new_objects.append(o) anchor count={n_anchor_4}, expected 1")
src = src.replace(anchor_4, addition_4 + anchor_4, 1)
print("  ok [4/7]: rehydrate reads reference fields + seeds emb_gallery")

p.write_text(src)
PYEOF
fi

# ---------------------------------------------------------------------------
# Patch 5: Append set_object_reference() helper method to WorkingMemory
# ---------------------------------------------------------------------------
if grep -q "def set_object_reference" "$WM_PY"; then
    echo "[5/7] working_memory.py set_object_reference: already present, skipping"
else
    # Backup only if patches 1-4 didn't already make one this minute
    if [ ! -f "$WM_PY.bak.$TS" ]; then
        cp "$WM_PY" "$WM_PY.bak.$TS"
        echo "[5/7] working_memory.py: backed up to $WM_PY.bak.$TS"
    fi

    cat >> "$WM_PY" <<'PYEOF'

    # ---------- reference snapshot (named-moment ground truth) ----------

    def set_object_reference(
        self,
        oid: str,
        *,
        image_path: Optional[str],
        embedding: Optional[np.ndarray],
    ) -> Optional["ObjectState"]:
        """Thread-safe update of reference snapshot fields on an ObjectState.

        Args:
            oid: target object id.
            image_path: filesystem path to the JPEG (callers handle the
                actual file write). None = clear the field.
            embedding: CLIP embedding of the reference image, expected to be
                a float32 vector of shape (D,). L2-normalized defensively
                here. None = clear the field.

        Side effects:
            If the object is confirmed, pushes oid onto the LTM upsert heap
            so the new reference fields persist through the FAISS sidecar
            quickly (without waiting for the next regular upsert window).

        Returns the updated ObjectState, or None if oid not found.
        Raises ValueError on dim mismatch with the object's existing _dim.
        """
        with self._lock:
            o = self._map.get(oid)
            if o is None:
                return None
            o.reference_image_path = (
                str(image_path) if image_path is not None else None
            )
            if embedding is not None:
                arr = np.asarray(embedding, dtype=np.float32).reshape(-1)
                if o._dim and arr.shape[0] != o._dim:
                    raise ValueError(
                        f"reference embedding dim {arr.shape[0]} != "
                        f"object dim {o._dim}"
                    )
                # L2-normalize defensively (CLIP outputs typically are,
                # but the upload path is unauditable from here).
                n = float(np.linalg.norm(arr) + 1e-12)
                o.reference_emb = (arr / n).astype(np.float32)
            else:
                o.reference_emb = None
            # Force a fresh LTM upsert so the new reference fields make it
            # to the sidecar without waiting for the regular cadence.
            if o.confirmed:
                heapq.heappush(self._ltm_heap, (_now_mono(), oid))
            return o
PYEOF
    echo "  ok [5/7]: appended set_object_reference helper method"
fi

# ---------------------------------------------------------------------------
# Patches 6-7: server.py edits (Pydantic models + endpoints)
# ---------------------------------------------------------------------------
if grep -q "class ReferenceImagePayload" "$SRV_PY"; then
    echo "[6-7/7] server.py: already patched, skipping"
else
    cp "$SRV_PY" "$SRV_PY.bak.$TS"
    echo "[6-7/7] server.py: backed up to $SRV_PY.bak.$TS"

    python3 <<'PYEOF'
import pathlib, sys
p = pathlib.Path("rtsm/api/server.py")
src = p.read_text()

# ---- Patch 6: new Pydantic models after PoseStateRequest ----
# Anchor on the closing of PoseStateRequest's `state: str = Field(...)` block
# plus the trailing blank lines before `def create_app`.
anchor_6 = (
    "class PoseStateRequest(BaseModel):\n"
    "    #Body schema for POST /pose_state.\n"
    "    state: str = Field(\n"
    "        ...,\n"
    "        description=(\n"
    "            \"One of: 'on_floor', 'lifted', 'unknown', 'confirmed_elevated'. \"\n"
    "            \"Invalid values are clamped to 'unknown' (safe default).\"\n"
    "        ),\n"
    "    )\n"
)
addition_6 = (
    "\n"
    "\n"
    "# 2026-05-29: reference-snapshot endpoint schemas.\n"
    "class ReferenceImagePayload(BaseModel):\n"
    "    \"\"\"Body schema for POST /objects/{oid}/reference.\n"
    "\n"
    "    Single base64-encoded JPEG. RTSM decodes, CLIP-embeds, writes the file\n"
    "    to disk, and updates the object's reference fields. INGEST mode only\n"
    "    (CLIP loaded + WM writable).\n"
    "    \"\"\"\n"
    "    jpeg_b64: str = Field(..., description=\"Base64-encoded JPEG bytes.\")\n"
    "\n"
    "    model_config = {\"extra\": \"forbid\"}\n"
    "\n"
    "\n"
    "class ReferenceBulkItem(BaseModel):\n"
    "    \"\"\"One entry in a bulk reference upload.\"\"\"\n"
    "    oid: str\n"
    "    jpeg_b64: str\n"
    "\n"
    "\n"
    "class ReferenceBulkPayload(BaseModel):\n"
    "    \"\"\"Body schema for POST /objects/reference_bulk.\n"
    "\n"
    "    Albert's boot-time backfill: walk local memory.json, push every\n"
    "    linked snapshot in one request. Per-item failures are reported in\n"
    "    the response without aborting the batch.\n"
    "    \"\"\"\n"
    "    items: List[ReferenceBulkItem] = Field(..., min_length=1, max_length=200)\n"
    "\n"
    "    model_config = {\"extra\": \"forbid\"}\n"
)
if anchor_6 not in src:
    sys.exit("ERROR [6/7]: PoseStateRequest anchor not found")
src = src.replace(anchor_6, anchor_6 + addition_6, 1)
print("  ok [6/7]: server.py gained reference-snapshot Pydantic models")

# ---- Patch 7: endpoints inserted before the snapshot-gallery section ----
# Anchor: the `# ---- Snapshot gallery endpoints ----` comment block start.
anchor_7 = "    # ---- Snapshot gallery endpoints ----\n"
addition_7 = '''    # ---- 2026-05-29: reference snapshot endpoints ----
    # Reference snapshots are the named-moment ground truth for each object:
    # one JPEG + one CLIP embedding, persisted through the FAISS sidecar.
    # Distinct from image_crops (rolling observation gallery, WM-only).

    def _encode_reference_image(jpeg_bytes: bytes) -> "np.ndarray":
        """Decode JPEG + CLIP-embed. Returns L2-normalized fp32 of shape (D,).

        Defensive about clip_adapter's method name: tries encode_image first
        (OpenCLIP convention; matches the encode_text pair already used by
        /search/semantic), falls back to embed_image. Fails loudly if neither
        is available so the deploy/test cycle catches it immediately.
        """
        img_buf = np.frombuffer(jpeg_bytes, dtype=np.uint8)
        bgr = cv2.imdecode(img_buf, cv2.IMREAD_COLOR)
        if bgr is None:
            raise ValueError("cv2.imdecode returned None for JPEG bytes")
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        if hasattr(clip_adapter, "encode_image"):
            emb_raw = clip_adapter.encode_image(rgb)
        elif hasattr(clip_adapter, "embed_image"):
            emb_raw = clip_adapter.embed_image(rgb)
        else:
            attrs = [m for m in dir(clip_adapter)
                     if callable(getattr(clip_adapter, m, None))
                     and not m.startswith("_")]
            raise AttributeError(
                f"clip_adapter has no encode_image or embed_image method. "
                f"Available callables: {attrs}"
            )
        arr = np.asarray(emb_raw, dtype=np.float32).reshape(-1)
        n = float(np.linalg.norm(arr) + 1e-12)
        return (arr / n).astype(np.float32)

    @app.post("/objects/{oid}/reference")
    def set_object_reference(
        oid: str,
        payload: ReferenceImagePayload = Body(...),
    ) -> Dict[str, Any]:
        """Upload the canonical reference snapshot for an object.

        Stores JPEG bytes at /mnt/rtsm-data/refs/<oid>.jpg, CLIP-embeds, and
        updates reference_image_path + reference_emb on the WM object. The
        new fields persist through the next sidecar flush (the helper pushes
        an immediate LTM upsert for the oid).

        Errors:
            400 — malformed base64 or unreadable JPEG
            404 — unknown oid
            405 — frozen WM (serve mode)
            503 — CLIP adapter not available
            500 — CLIP encode failed or filesystem write failed
        """
        import os
        from pathlib import Path

        if not hasattr(working_memory, "set_object_reference"):
            raise HTTPException(
                status_code=405,
                detail="reference upload not supported on frozen WM (serve mode)",
            )
        if clip_adapter is None:
            raise HTTPException(
                status_code=503,
                detail="CLIP adapter not available; cannot embed reference",
            )

        obj = working_memory.get(oid)
        if obj is None:
            raise HTTPException(status_code=404, detail=f"Object {oid} not found")

        # Decode base64 -> JPEG bytes
        try:
            jpeg_bytes = base64.b64decode(payload.jpeg_b64, validate=True)
        except (binascii.Error, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"base64 decode failed: {e}")
        if not jpeg_bytes:
            raise HTTPException(status_code=400, detail="empty JPEG bytes")

        # CLIP-embed (also validates that cv2 can decode the JPEG)
        try:
            emb = _encode_reference_image(jpeg_bytes)
        except (ValueError, AttributeError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"CLIP encode failed: {e}")

        # Persist JPEG to disk. The refs dir lives alongside FAISS so it
        # rolls with the same data volume.
        refs_dir = Path(os.environ.get(
            "RTSM_REFS_DIR", "/mnt/rtsm-data/refs"
        ))
        try:
            refs_dir.mkdir(parents=True, exist_ok=True)
            out_path = refs_dir / f"{oid}.jpg"
            out_path.write_bytes(jpeg_bytes)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"file write failed: {e}")

        # Update WM (also schedules immediate LTM upsert for the oid).
        try:
            working_memory.set_object_reference(
                oid, image_path=str(out_path), embedding=emb,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return {
            "id": oid,
            "reference_image_path": str(out_path),
            "reference_emb_dim": int(emb.shape[0]),
            "size_bytes": len(jpeg_bytes),
        }

    @app.post("/objects/reference_bulk")
    def set_object_reference_bulk(
        payload: ReferenceBulkPayload = Body(...),
    ) -> Dict[str, Any]:
        """Bulk reference upload, intended for Albert's boot-time backfill.

        Processes each item independently — per-item errors are recorded in
        the response without aborting the batch. Returns a summary plus
        per-item status.
        """
        import os
        from pathlib import Path

        if not hasattr(working_memory, "set_object_reference"):
            raise HTTPException(
                status_code=405,
                detail="reference upload not supported on frozen WM (serve mode)",
            )
        if clip_adapter is None:
            raise HTTPException(
                status_code=503,
                detail="CLIP adapter not available; cannot embed references",
            )

        refs_dir = Path(os.environ.get(
            "RTSM_REFS_DIR", "/mnt/rtsm-data/refs"
        ))
        try:
            refs_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"refs dir setup failed: {e}")

        results: List[Dict[str, Any]] = []
        ok_count = 0
        for item in payload.items:
            entry: Dict[str, Any] = {"oid": item.oid}
            obj = working_memory.get(item.oid)
            if obj is None:
                entry["status"] = "not_found"
                results.append(entry)
                continue
            try:
                jpeg_bytes = base64.b64decode(item.jpeg_b64, validate=True)
                if not jpeg_bytes:
                    raise ValueError("empty JPEG bytes")
                emb = _encode_reference_image(jpeg_bytes)
                out_path = refs_dir / f"{item.oid}.jpg"
                out_path.write_bytes(jpeg_bytes)
                working_memory.set_object_reference(
                    item.oid, image_path=str(out_path), embedding=emb,
                )
                entry["status"] = "ok"
                entry["reference_image_path"] = str(out_path)
                entry["size_bytes"] = len(jpeg_bytes)
                ok_count += 1
            except Exception as e:
                entry["status"] = "error"
                entry["detail"] = str(e)
            results.append(entry)

        return {
            "total": len(payload.items),
            "ok": ok_count,
            "failed": len(payload.items) - ok_count,
            "results": results,
        }

    @app.get("/objects/by_label_user")
    def get_object_by_label_user(
        name: str,
        case_insensitive: bool = True,
    ) -> Dict[str, Any]:
        """Look up an object by its user-assigned name (label_user).

        Drives Albert's layered recall: local memory hits first, then this
        endpoint for current RTSM state (location, last_seen, reference).
        Returns 404 if no object carries this label_user. If multiple
        objects share the name (rare; user normally pins one), returns the
        most recently observed one and surfaces a list of all matches.
        """
        q = name.strip()
        if not q:
            raise HTTPException(status_code=400, detail="name must be non-empty")

        matches: List[Any] = []
        try:
            for o in working_memory.iter_objects():
                lu = getattr(o, "label_user", None)
                if lu is None:
                    continue
                if case_insensitive:
                    if lu.lower() == q.lower():
                        matches.append(o)
                else:
                    if lu == q:
                        matches.append(o)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"WM iteration failed: {e}")

        if not matches:
            raise HTTPException(
                status_code=404,
                detail=f"No object with label_user={name!r}",
            )

        # Most-recent first by last_seen_wall_utc.
        matches.sort(
            key=lambda o: float(getattr(o, "last_seen_wall_utc", 0.0) or 0.0),
            reverse=True,
        )
        primary = matches[0]

        def _entry(o: Any) -> Dict[str, Any]:
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
        }

'''
if anchor_7 not in src:
    sys.exit("ERROR [7/7]: snapshot-gallery section anchor not found")
src = src.replace(anchor_7, addition_7 + anchor_7, 1)
print("  ok [7/7]: server.py gained 3 reference-snapshot endpoints")

p.write_text(src)
PYEOF
fi

# ---------------------------------------------------------------------------
# Sanity: both files parse
# ---------------------------------------------------------------------------
python3 -c "
import ast
for path in ['rtsm/stores/working_memory.py', 'rtsm/api/server.py']:
    ast.parse(open(path).read())
    print(f'  syntax-ok: {path}')
"

echo ""
echo "== done =="
echo ""
echo "Restart RTSM to load changes:"
echo "  docker restart rtsm-dev"
echo ""
echo "Run the test suite (inside the container):"
echo "  docker exec -w /workspace/rtsm rtsm-dev python3 test_reference_image.py"
echo ""
echo "Smoke-test the endpoint (after restart, RTSM in ingest mode):"
echo "  # Encode any JPEG and POST it against a real oid; tests cover the rest."
