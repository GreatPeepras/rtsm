# Reference snapshot integration — 2026-05-29 deliverables

## Server-side (shipped this charging window)

### Files

| File | Purpose |
|---|---|
| `deploy_reference_image_2026-05-29.sh` | 7-patch idempotent deploy (working_memory.py + server.py) |
| `test_reference_image.py` | 14 tests covering fields, helper, payloads, rehydrate, e2e |

### What lands

**`rtsm/stores/working_memory.py`**
1. `ObjectState` gains `reference_image_path: Optional[str]` and `reference_emb: Optional[Emb]` (both default `None`).
2. `collect_ready_for_upsert()` includes both fields in the force-flush and normal-path payloads.
3. `rehydrate_from_faiss()` reads both fields back from the sidecar, and **seeds `emb_gallery` with the reference embedding** — closing the rehydrated = `emb_mean`-only matcher gap noted in `handoff_2026-05-25.md` lesson #5 (for named objects).
4. New helper `set_object_reference(oid, *, image_path, embedding)` — thread-safe writer that L2-normalizes defensively and force-pushes the oid onto the LTM upsert heap so changes persist quickly.

**`rtsm/api/server.py`**
5. Pydantic models: `ReferenceImagePayload`, `ReferenceBulkItem`, `ReferenceBulkPayload`.
6. `POST /objects/{oid}/reference` — single snapshot upload (base64 JPEG → CLIP-embed → disk → WM).
7. `POST /objects/reference_bulk` — Albert's boot-time backfill; per-item errors don't abort the batch.
8. `GET /objects/by_label_user?name=<name>` — drives layered recall on the Albert side.

### Apply / verify

```bash
cd ~/rtsm
chmod +x deploy_reference_image_2026-05-29.sh
./deploy_reference_image_2026-05-29.sh
docker restart rtsm-dev
docker exec -w /workspace/rtsm rtsm-dev python3 test_reference_image.py
```

Expect: 14/14 pass, no regressions in `test_rehydrate.py` / `test_end_to_end_persistence.py`.

### Smoke checks after restart

```bash
# CLIP adapter wired up (encode_image found)? Sanity-check the endpoint:
docker exec rtsm-dev curl -s http://localhost:8002/healthz

# No object named anything yet → 404 (proves the endpoint is registered):
docker exec rtsm-dev curl -s http://localhost:8002/objects/by_label_user?name=Quackers | jq

# After Albert does a name_object live, the same call should return the object.
```

### Storage layout

JPEGs land at `/mnt/rtsm-data/refs/<oid>.jpg` (override with `RTSM_REFS_DIR` env).
At 50–100 named objects, expect a few MB total. Sidecar `meta.json` grows by ~3 KB per object (the 768-float embedding as JSON).

### Open assumption (verify on first apply)

The endpoint calls `clip_adapter.encode_image(rgb_uint8)`. The helper falls back to `embed_image` and otherwise lists available methods in the 503 — so if the real adapter uses a different name we'll see it instantly. Adjust the `_encode_reference_image` helper in `server.py` accordingly. The rest of the patches don't depend on this.

---

## Bench-batch (Albert side) — apply when at the bench

Three changes to the `largemodel` package. All depend on the server-side endpoints above being live and RTSM in ingest mode. Order matters within the bench session because Phase A (`name_object` prompt + voice test) is already queued from the roadmap.

### B1. Extend `name_object()` to upload the reference snapshot

After the existing `PATCH /objects/{oid}` succeeds in `action_service.py`'s `name_object()`, also POST the latest snapshot to RTSM and persist the linkage in `memory.json`. Shape:

```python
# After successful PATCH that returned 200 with the oid:
def _post_reference_snapshot(self, oid: str, image_path: str) -> bool:
    """Upload the snapshot Albert just used for naming as the canonical
    reference. Best-effort: RTSM unreachable or in serve mode = log + move on.
    """
    try:
        with open(image_path, "rb") as f:
            jpeg_b64 = base64.b64encode(f.read()).decode("ascii")
        resp = requests.post(
            f"{self.RTSM_BASE}/objects/{oid}/reference",
            json={"jpeg_b64": jpeg_b64},
            timeout=5.0,
        )
        if resp.ok:
            self.get_logger().info(
                f"[name_object] reference snapshot uploaded for {oid[:8]}"
            )
            return True
        self.get_logger().warning(
            f"[name_object] reference upload failed: HTTP {resp.status_code} "
            f"({resp.text[:120]})"
        )
    except Exception as e:
        self.get_logger().warning(f"[name_object] reference upload error: {e}")
    return False

# Then in name_object():
#   - after PATCH succeeds, capture the most recent image from seewhat()
#   - call _post_reference_snapshot(oid, image_path)
#   - either way, store rtsm_oid in memory.json so future recall can find it
```

The `memory.json` linkage: when `name_object()` succeeds AND `remember()` ran on the same utterance (augment mode), patch the matching memory entry to add `"rtsm_oid": <oid>` so the layered recall path (B2) and boot backfill (B3) can use it.

**Note:** which snapshot? After `seewhat()` runs, the latest image is in `self.image_save_path` (per the action_service.py snippets). That's the right one — it's the frame Albert was looking at when the user said "this is Quackers."

### B2. Layered `recall(query)`

Today: `recall(query)` searches local `memory.json` by tags, returns local descriptions. The Decision Brain prompts inject the result into context.

New behavior: if a local match has `rtsm_oid` or a `name` that matches an RTSM `label_user`, also query RTSM and layer in location:

```python
def recall(self, query: str, *args):
    query = query.strip("'\"").lower()
    # 1. Local hit (unchanged)
    local_match = self._local_search(query)
    
    # 2. RTSM hit — by name
    rtsm_match = None
    try:
        resp = requests.get(
            f"{self.RTSM_BASE}/objects/by_label_user",
            params={"name": query},
            timeout=2.0,
        )
        if resp.status_code == 200:
            rtsm_match = resp.json().get("primary")
        # 404 is fine; rtsm_match stays None
    except Exception:
        pass  # network/RTSM down → graceful: local only
    
    # 3. Compose the recall response based on (local_hit, rtsm_hit):
    # both → "Quackers is near the couch."
    # local only → "I remember Quackers, but I can't find him. Can you show me?"
    # rtsm only → use RTSM data; cache it locally on the fly
    # neither → standard NO_MEMORY_FOUND path
    return self._compose_recall_context(local_match, rtsm_match)
```

The "compose" step interpolates RTSM's `xyz_world` and `last_seen_wall_utc` into the context block. Decision Brain prompt already handles natural-language responses from the layered context (`Special Memory Response Mode`).

**Staleness threshold:** if RTSM's `last_seen_wall_utc` is more than ~6 hours old, treat as "stale" and bias toward the "but I haven't seen him lately" phrasing. Otherwise direct location.

### B3. Boot-time reference backfill

New file `~/largemodel/largemodel/boot_backfill_references.py` (or a method on the existing largemodel node). Runs once after ROS startup, in a background thread so it doesn't block AMCL/model-load convergence:

```python
def backfill_references_to_rtsm():
    """Push linked snapshots from memory.json to RTSM's bulk endpoint.
    
    Idempotent: RTSM overwrites the existing reference on duplicate POST.
    Retries every 30s for 5 minutes if RTSM unreachable, then gives up.
    """
    entries = _load_memory_json()
    linked = [
        e for e in entries
        if e.get("type") == "visual"
        and e.get("rtsm_oid")
        and e.get("image_path")
        and os.path.exists(e["image_path"])
    ]
    if not linked:
        log.info("[backfill] no linked memory entries; nothing to push")
        return
    
    # Build batch payload (max 200 items per call; chunk if needed)
    items = []
    for e in linked:
        try:
            with open(e["image_path"], "rb") as f:
                items.append({
                    "oid": e["rtsm_oid"],
                    "jpeg_b64": base64.b64encode(f.read()).decode("ascii"),
                })
        except Exception as ex:
            log.warning(f"[backfill] skipped {e.get('name')}: {ex}")
    
    if not items:
        return
    
    # Retry loop: 30s × 10 = 5 min max
    for attempt in range(10):
        try:
            resp = requests.post(
                f"{RTSM_BASE}/objects/reference_bulk",
                json={"items": items},
                timeout=30.0,
            )
            if resp.ok:
                summary = resp.json()
                log.info(
                    f"[backfill] pushed {summary['ok']}/{summary['total']} "
                    f"references to RTSM"
                )
                return
        except Exception as ex:
            log.info(f"[backfill] RTSM not ready (attempt {attempt+1}/10): {ex}")
        time.sleep(30.0)
    log.warning("[backfill] gave up after 5 minutes; references not backfilled")
```

Wired via the largemodel node's `__init__` (background thread spawn after node is up).

### Live test plan (at the bench)

1. Apply server-side patches, restart RTSM, run `test_reference_image.py` → 14/14.
2. Apply Phase A prompts (the original 2026-05-28 deploy) + the B1 extension. Sync prompts to Dify. Restart largemodel.
3. Voice: *"Albert, this duck is called Quackers."*
   - Expect: `seewhat()` → `remember()` → `name_object()` → reference upload.
   - Verify: `curl :8002/objects/by_label_user?name=Quackers` returns the object with `has_reference_image: true` and a path under `/mnt/rtsm-data/refs/`.
   - Verify: file actually on disk: `ssh peep@execution ls -la /mnt/rtsm-data/refs/`.
4. Restart RTSM container (`docker restart rtsm-dev`).
5. Re-query `/objects/by_label_user?name=Quackers` → still works (persistence + rehydrate verified).
6. Optional: scan RTSM logs for the new "seeded gallery from reference_emb" path on rehydrate.
7. With B2 in place: voice *"Where is Quackers?"* → expect *"He's near [location]"* (RTSM hit) or *"I remember Quackers but can't find him"* (RTSM evicted/missing) based on what RTSM says.
8. Restart Albert, watch journalctl for the B3 backfill kicking in during boot.

### Definition of done (matches the roadmap's Phase A line)

> Voice → name → searchable + navigable + survives restart.

Plus the layered-recall and boot-backfill polish from this addendum.

---

## What this unlocks (for future sessions)

- **Phase C visual find (`find_object(name)`):** all the infrastructure is in place; the endpoint just needs to take the stored `reference_emb` and run NN search against live WM.
- **Re-identification on movable objects:** `reference_emb` is the anchor a moved object can be matched against when the position-based association fails.
- **Multimodal recall responses on Albert's screen:** `/mnt/rtsm-data/refs/<oid>.jpg` is reachable via `GET /objects/{oid}` (we could add a `?include_reference=true` param later) for screen display.

These all sit on the foundation shipping today.
