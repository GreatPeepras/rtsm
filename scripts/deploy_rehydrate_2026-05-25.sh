#!/bin/bash
# Deploy FAISS persistence / WM rehydration changes — 2026-05-25 (rev 2)
#
# Three changes:
#   1. Insert rehydrate_from_faiss() call into rtsm/run.py
#   2. Append rehydrate_from_faiss() method to rtsm/stores/working_memory.py
#   3. Fix maybe_promote() to schedule LTM upsert on promotion — this was
#      the actual root cause of "FAISS persistence not wired in live ingest":
#      confirmed objects never entered _ltm_heap, so collect_ready_for_upsert
#      always returned empty and FAISS was never written.
#
# Idempotent: re-running is a no-op once all three changes are present.
# Pre-flight: takes backups (.bak.YYYYMMDD-HHMMSS) before editing.

set -euo pipefail

# Resolve repo root: expect to be run from repo root.
if [ ! -f rtsm/run.py ]; then
    echo "ERROR: rtsm/run.py not found in current dir." >&2
    echo "Run from your repo root, e.g.:  cd ~/rtsm && bash deploy_rehydrate_2026-05-25.sh" >&2
    exit 1
fi
TS=$(date +%Y%m%d-%H%M%S)

echo "== rtsm FAISS persistence deploy ($(date -Is)) =="

# ---------------------------------------------------------------------------
# Change 1: rtsm/run.py
# ---------------------------------------------------------------------------
RUN_PY="rtsm/run.py"
if grep -q "wm.rehydrate_from_faiss(vectors)" "$RUN_PY"; then
    echo "[1/2] run.py: already patched, skipping"
else
    cp "$RUN_PY" "$RUN_PY.bak.$TS"
    echo "[1/2] run.py: backed up to $RUN_PY.bak.$TS"

    # Insert the rehydration call after the Faiss-initialized log line.
    # This anchor exists once in run.py and is unique to the live-ingest branch.
    python3 <<'PYEOF'
import re, pathlib
p = pathlib.Path("rtsm/run.py")
src = p.read_text()
anchor = 'logger.info(f"Faiss vectors successfully initialized")'
insert = '''
            # 2026-05-25: rehydrate WM from persisted FAISS state so that
            # association can match new observations against objects from
            # previous sessions. Without this, every restart spawns fresh
            # OIDs for known objects. Wrapped defensively — a corrupt
            # sidecar must not block live-mode startup.
            try:
                wm.rehydrate_from_faiss(vectors)
            except Exception as e:
                logger.warning(
                    f"[run] WM rehydration from FAISS failed (continuing "
                    f"with empty WM): {e}"
                )'''
if anchor not in src:
    raise SystemExit(f"ERROR: anchor not found in {p}: {anchor!r}")
# Find the anchor and append insert AFTER its full line
lines = src.split("\n")
out = []
done = False
for line in lines:
    out.append(line)
    if not done and anchor in line:
        out.extend(insert.split("\n"))
        done = True
p.write_text("\n".join(out))
print(f"  ok: inserted rehydrate call after anchor")
PYEOF
fi

# ---------------------------------------------------------------------------
# Change 2: rtsm/stores/working_memory.py
# ---------------------------------------------------------------------------
WM_PY="rtsm/stores/working_memory.py"
if grep -q "def rehydrate_from_faiss" "$WM_PY"; then
    echo "[2/2] working_memory.py: already patched, skipping"
else
    cp "$WM_PY" "$WM_PY.bak.$TS"
    echo "[2/2] working_memory.py: backed up to $WM_PY.bak.$TS"

    cat >> "$WM_PY" <<'PYEOF'

    # ---------- rehydration ----------

    def rehydrate_from_faiss(self, faiss_client: Any) -> Dict[str, int]:
        """Inject persisted objects from a FaissClient into WM as confirmed.

        Called once at live-mode startup so that association can match new
        observations against objects from previous sessions. Without this,
        every restart spawns fresh OIDs for already-known objects, breaking
        cross-session continuity.

        Reads `faiss_client._embeddings` (oid -> ndarray) and
        `faiss_client._metadata` (oid -> dict). Skips objects with missing
        or malformed data; never crashes the caller.

        Returns counts: {loaded, skipped_no_emb, skipped_bad_xyz,
        skipped_dim_mismatch, skipped_dup}.

        Notes on what's NOT carried across:
        - emb_gallery: empty. Association falls back to emb_mean (verified
          in association.py:307-308). Gallery rebuilds as Albert re-observes.
        - view_bins: empty. Same fallback rationale.
        - cov_world: initialized wide ([0.04, 0.04, 0.08]) since we have
          no certainty about how stale the stored xyz is.
        - last_seen_*: set to "now" so rehydrated objects don't immediately
          look stale to downstream consumers.
        - last_upsert_*: also "now" with current emb/xyz, so change-detection
          in collect_ready_for_upsert correctly skips them until they
          actually change.
        """
        counts = {
            "loaded": 0,
            "skipped_no_emb": 0,
            "skipped_bad_xyz": 0,
            "skipped_dim_mismatch": 0,
            "skipped_dup": 0,
        }

        embeddings = getattr(faiss_client, "_embeddings", None) or {}
        metadata = getattr(faiss_client, "_metadata", None) or {}
        if not metadata:
            logger.info("[WM] rehydrate: FAISS has no persisted objects (cold start)")
            return counts

        # Determine expected embedding dimension. Prefer FaissClient's
        # configured dim if available; otherwise infer from first embedding.
        expected_dim = getattr(faiss_client, "dim", None)
        if expected_dim is None:
            for v in embeddings.values():
                expected_dim = int(np.asarray(v).shape[-1])
                break
        if expected_dim is None:
            logger.warning(
                "[WM] rehydrate: cannot determine embedding dim "
                "(no faiss_client.dim, no embeddings); aborting"
            )
            return counts
        expected_dim = int(expected_dim)

        now_m = _now_mono()
        now_w = _now_wall_utc()

        # Wider initial covariance than fresh-create (0.02/0.02/0.04) since
        # we don't know how stale this position is. EWMA on new observations
        # will tighten it as evidence accumulates.
        cov_init = np.array([0.04, 0.04, 0.08], dtype=np.float32)

        new_objects: List[ObjectState] = []

        for oid, meta in metadata.items():
            oid = str(oid)

            # Skip if already present (shouldn't happen at startup, but
            # defensive: a second rehydrate call is a no-op for existing oids).
            if oid in self._map:
                counts["skipped_dup"] += 1
                continue

            emb = embeddings.get(oid)
            if emb is None:
                counts["skipped_no_emb"] += 1
                continue
            emb = np.asarray(emb, dtype=np.float32).reshape(-1)
            if emb.shape[0] != expected_dim:
                logger.warning(
                    f"[WM] rehydrate: skip oid={oid[:8]} dim {emb.shape[0]} "
                    f"!= expected {expected_dim}"
                )
                counts["skipped_dim_mismatch"] += 1
                continue

            # xyz comes back from FaissClient.load() as either ndarray or list
            # depending on sidecar version; coerce defensively.
            xyz_raw = meta.get("xyz")
            try:
                xyz = np.asarray(xyz_raw, dtype=np.float32).reshape(-1)
                if xyz.shape[0] != 3:
                    raise ValueError(f"xyz shape {xyz.shape}")
            except Exception as e:
                logger.warning(f"[WM] rehydrate: skip oid={oid[:8]} bad xyz: {e}")
                counts["skipped_bad_xyz"] += 1
                continue

            # Reconstruct label dicts from parallel lists stored in the
            # upsert payload (see collect_ready_for_upsert).
            label_topk = list(meta.get("label_topk", []) or [])
            label_scores_list = list(meta.get("label_scores", []) or [])
            label_hits_list = list(meta.get("label_hits", []) or [])
            label_scores: Dict[str, float] = {}
            label_hits: Dict[str, int] = {}
            for i, name in enumerate(label_topk):
                if i < len(label_scores_list):
                    label_scores[str(name)] = float(label_scores_list[i])
                if i < len(label_hits_list):
                    label_hits[str(name)] = int(label_hits_list[i])

            # hits is the WM observation counter, not in the upsert payload.
            # Default to promote_hits — a confirmed object must have passed
            # that gate at least once, so this is a safe lower bound.
            hits_default = int(max(self.promote_hits, 1))

            o = ObjectState(
                id=oid,
                xyz_world=xyz.astype(np.float32),
                cov_world=cov_init.copy(),
                emb_mean=emb.astype(np.float32),
                emb_gallery=np.zeros((0, expected_dim), dtype=np.float16),
                view_bins={},
                label_scores=label_scores,
                label_hits=label_hits,
                label_primary=meta.get("label_primary"),
                stability=float(meta.get("stability", 0.5)),
                hits=hits_default,
                confirmed=True,
                created_mono=now_m,  # monotonic clock is process-local; reset
                created_wall_utc=float(meta.get("created_at", now_w)),
                last_seen_mono=now_m,
                last_seen_wall_utc=now_w,
                last_seen_px=None,
                last_upsert_wall_utc=now_w,
                last_upsert_mono=now_m,
                last_upsert_emb=emb.astype(np.float32).copy(),
                last_upsert_xyz=xyz.astype(np.float32).copy(),
                image_crops=[],
                last_update_frame_id=None,
                _dim=expected_dim,
                label_user=meta.get("label_user"),
                movability_class=meta.get("movability_class"),
                # 2026-05-25: preserve the two-tier memory tag from May-22.
                # Default "on_floor" matches frozen_wm's back-compat behavior
                # for sidecars written before the field existed. NOTE: the
                # write side (collect_ready_for_upsert) must also include
                # this field for the round-trip to fully work; verify before
                # relying on elevated objects surviving restarts.
                pose_state_at_observation=str(
                    meta.get("pose_state_at_observation", "on_floor")
                ),
            )
            new_objects.append(o)

        # Single-shot lock acquisition for the actual insert.
        with self._lock:
            for o in new_objects:
                self._map[o.id] = o
                counts["loaded"] += 1

        # Spatial index insertion is outside the WM lock (matches create_object).
        if self.index is not None:
            for o in new_objects:
                self.index.insert(o.id, o.xyz_world, wm_lookup=self.lookup_min)

        logger.info(
            f"[WM] rehydrate: loaded {counts['loaded']} objects from FAISS "
            f"(skipped no_emb={counts['skipped_no_emb']} "
            f"bad_xyz={counts['skipped_bad_xyz']} "
            f"dim={counts['skipped_dim_mismatch']} "
            f"dup={counts['skipped_dup']})"
        )
        return counts
PYEOF
    echo "  ok: appended rehydrate_from_faiss method"
fi

# ---------------------------------------------------------------------------
# Change 3: rtsm/stores/working_memory.py — schedule LTM upsert on promote.
# This is the actual root cause of "FAISS persistence not wired in live
# ingest mode". maybe_promote() sets o.confirmed=True but never pushes to
# self._ltm_heap, so collect_ready_for_upsert (which drains the heap)
# never sees anything. Replay mode worked because it bypasses the heap
# with force_all=True. Live mode silently dropped every confirmed object.
# ---------------------------------------------------------------------------
if grep -q "schedule for immediate LTM upsert eligibility" "$WM_PY"; then
    echo "[3/3] working_memory.py maybe_promote: already patched, skipping"
else
    # Don't re-backup if change 2 already did
    if [ ! -f "$WM_PY.bak.$TS" ]; then
        cp "$WM_PY" "$WM_PY.bak.$TS"
        echo "[3/3] working_memory.py: backed up to $WM_PY.bak.$TS"
    fi

    python3 <<'PYEOF'
import pathlib
p = pathlib.Path("rtsm/stores/working_memory.py")
src = p.read_text()
# Anchor: the promote-log inside maybe_promote. Capture the WHOLE block
# (if all_pass: ... logger.info(...)) and append a heappush after it.
# Match is keyed on the unique log format string.
anchor = (
    '            if all_pass:\n'
    '                o.confirmed = True\n'
    '                logger.info(\n'
    '                    f"[WM] promote oid={oid} label={top_lbl} "\n'
    '                    f"conf={top_conf:.3f} hits={o.hits} stab={o.stability:.3f}"\n'
    '                )'
)
addition = (
    '\n                # 2026-05-25: schedule for immediate LTM upsert eligibility.\n'
    '                # Without this, confirmed objects never reach FAISS in live\n'
    '                # ingest mode (the upsert path drains _ltm_heap; nothing else\n'
    '                # populates it). Lost in a previous refactor; force_all=True\n'
    '                # in replay mode bypassed the heap and masked the bug.\n'
    '                heapq.heappush(self._ltm_heap, (_now_mono(), oid))'
)
if anchor not in src:
    raise SystemExit(
        "ERROR: maybe_promote anchor not found. Has the file been edited "
        "since the deploy script was written? Inspect "
        "rtsm/stores/working_memory.py maybe_promote() and add this line "
        "manually after `o.confirmed = True` plus its log call:\n"
        "  heapq.heappush(self._ltm_heap, (_now_mono(), oid))"
    )
new_src = src.replace(anchor, anchor + addition, 1)
if new_src == src:
    raise SystemExit("ERROR: anchor replace was a no-op")
p.write_text(new_src)
print("  ok: inserted heappush after promote log")
PYEOF
fi

# ---------------------------------------------------------------------------
# Sanity: verify both files parse
# ---------------------------------------------------------------------------
python3 -c "
import ast
for p in ['rtsm/run.py', 'rtsm/stores/working_memory.py']:
    ast.parse(open(p).read())
    print(f'  syntax-ok: {p}')
"

echo ""
echo "== done =="
echo "Restart RTSM to load changes:"
echo "  docker compose -f docker/docker-compose.yml restart rtsm-dev"
echo "Check logs for the rehydrate message:"
echo "  docker exec rtsm-dev tail -f /tmp/rtsm.log | grep -i rehydrat"
