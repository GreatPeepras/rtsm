# Design — `POST /objects/{oid}/find_fragments` (2026-06-11)

Per-anchor merge-candidate search. Sibling to `POST /objects/suggest_merges`;
fixes the anchor and widens the gates to surface fragmentation around a
specific named object.

## Motivation

`suggest_merges` is an O(N²) pairwise sweep with conservative thresholds
(`cos >= 0.95`, `dist <= 1.0m`) tuned for whole-corpus passes. Two known
failure modes:

1. **Systematic under-detection for furniture-scale objects.** A 3m couch
   can have two legitimate OIDs at opposite ends from centroid drift; the
   1m gate misses them. Documented in `userMemories` and in the 6/2
   handoff long-tail backlog.
2. **No way to ask "what else looks like THIS named thing?"** When Albert
   re-names a basketball that moved across the room, the new OID is up
   to ~9m from the old one; no chance of being surfaced by a global
   sweep. The original `label_user` is silently lost (it stays on the
   old OID; the new sighting gets the new name on a new OID).

`find_fragments` is the targeted complement: anchor-aware defaults,
distance threshold adaptive to the anchor's `movability_class`, and a
`pose_state` filter that surfaces lift/lower duplicates by default.

## API

`POST /objects/{oid}/find_fragments`

Body schema `FindFragmentsRequest` — all fields optional:

| Field | Type | Default | Notes |
|---|---|---|---|
| `cos_threshold` | float `[0, 1]` | `0.85` | Lower than suggest_merges (anchor-asymmetric search) |
| `dist_threshold_m` | float `> 0` or null | `null` → adaptive | See table below |
| `include_unconfirmed` | bool | `true` | Protos are exactly what we want |
| `exclude_named` | bool | `false` | Surface named-named conflicts |
| `pose_state` | enum | `"any"` | `"any"` / `"on_floor"` / `"elevated"` / `"match_anchor"` |
| `limit` | int `[1, 500]` | `20` | |

Adaptive `dist_threshold_m` (used only when caller passes `null`):

| Anchor `movability_class` | Default | Rationale |
|---|---|---|
| `permanent`, `static`, `semi_static` | `3.0m` | Covers couch/desk extent + centroid drift |
| `movable`, `roaming`, `ephemeral` | `9.0m` | Full room diagonal `√(3.5² + 8²) ≈ 8.7m` |
| `null` / unset | `5.0m` | Middle-of-the-road fallback |

`pose_state="match_anchor"` resolves to the anchor's own
`pose_state_at_observation` before filtering.

### Response

```jsonc
{
  "anchor": {
    "oid": "18503a243abd46fb",
    "label_user": "basketball",
    "label_primary": "ball",
    "movability_class": "movable",
    "xyz": [-0.49, 1.64, 0.89],
    "hits": 12,
    "stability": 0.85,
    "has_reference": true,
    "confirmed": true,
    "pose_state_at_observation": "on_floor",
    "last_seen_wall_utc": 1718000000.0,
    "snapshot_url": "/objects/18503a243abd46fb/snapshots/0/image"
  },
  "fragments": [
    {
      "oid": "...",
      "label_user": null,
      "label_primary": "ball",
      "movability_class": "movable",
      "cosine": 0.91,
      "distance_m": 2.4,
      "hits": 3,
      "stability": 0.6,
      "has_reference": false,
      "confirmed": true,
      "pose_state_at_observation": "elevated",
      "xyz": [...],
      "last_seen_wall_utc": ...,
      "snapshot_url": "/objects/.../snapshots/0/image"
    }
  ],
  "scanned_objects": 230,
  "returned": 1,
  "total_above_thresholds": 1,
  "thresholds": {
    "cos_threshold": 0.85,
    "dist_threshold_m": 9.0,
    "dist_threshold_default_used": true,
    "include_unconfirmed": true,
    "exclude_named": false,
    "pose_state": "any",
    "pose_state_resolved": "any",
    "limit": 20
  }
}
```

`fragments` sorted by cosine descending, then distance ascending.

### Errors

| Code | Meaning |
|---|---|
| `404` | `anchor oid not found` |
| `405` | WM frozen (serve-mode) — no `find_fragments` method |
| `422` | invalid body (e.g. `pose_state` outside enum) |
| `500` | unexpected failure inside WM sweep |

## Implementation

### `WorkingMemory.find_fragments(anchor_oid, *, ...)` in `rtsm/stores/working_memory.py`

Insertion point: between `suggest_merges` and `_suggest_merge_winner`.
Anchor: `    @staticmethod\n    def _suggest_merge_winner(` (unique).

Algorithm:
1. **Snapshot under lock**: anchor first (resolve adaptive defaults from
   `anchor.movability_class`), then pool of candidates (everything except
   the anchor itself, optionally filtered by `confirmed` / `pose_state` /
   `exclude_named`). All fields copied to local dicts so the lock can be
   released for compute.
2. **Resolve adaptive `dist_threshold_m`** from anchor's class if caller
   passed `None`.
3. **Resolve `pose_state="match_anchor"`** to the anchor's own value.
4. **Apply pool filters** (pose_state, exclude_named).
5. **Vectorized sweep**: `cand_embs @ anchor_emb` for cosines (embs are
   pre-normalized), `np.linalg.norm(cand_xyzs - anchor_xyz, axis=1)` for
   distances. O(N), not O(N²).
6. **Filter, build response, sort, truncate.**

### `FindFragmentsRequest` body schema in `rtsm/api/server.py`

Insertion point: immediately before `# 2026-05-29: reference-snapshot
endpoint schemas.` (just after the `SuggestMergesRequest` class).
Anchor includes the closing `model_config` line of `SuggestMergesRequest`
plus blank lines plus the section comment, ensuring uniqueness.

Uses a `field_validator` on `pose_state` to enforce the enum (FastAPI
returns 422 with a clear message on invalid input).

### `POST /objects/{oid}/find_fragments` endpoint in `rtsm/api/server.py`

Insertion point: immediately before `    # ---- 2026-05-29: reference
snapshot endpoints ----` (just after `suggest_merges_endpoint`).

Thin wrapper:
- 405 if `working_memory` lacks `find_fragments` (frozen WM).
- Calls WM method.
- 422 on `ValueError` (validator messages).
- 500 on anything else.
- WM returns `{"error": "not_found", ...}` for unknown anchor → convert
  to 404.
- Augment response with `snapshot_url` strings (`/objects/{oid}/snapshots/0/image`).

## Marker

`FIND_FRAGMENTS_2026-06-11` appears 3 times after apply:
1. In `FindFragmentsRequest` docstring/comment (server.py)
2. In the endpoint function docstring/comment (server.py)
3. In the WM method docstring/comment (working_memory.py)

Idempotency check: deploy skips with "already applied" if any marker
already present in target file.

## Tests

`tests/test_find_fragments.py` — unit tests against the WM method
(skips the HTTP layer; mocks `ObjectState` shape via `types.SimpleNamespace`
since the real `ObjectState` requires CLIP/FAISS init):

1. **Anchor not found** → `{"error": "not_found"}`.
2. **Empty pool** (only the anchor exists) → empty `fragments` list.
3. **Single near-duplicate proto** → returned with expected cosine/distance.
4. **`exclude_named=true`** filters out OIDs with `label_user`.
5. **`include_unconfirmed=false`** filters out unconfirmed OIDs.
6. **Adaptive distance default**: `movable` anchor uses 9m, `static`
   uses 3m, `null` falls back to 5m.
7. **Explicit `dist_threshold_m` override** wins over adaptive default.
8. **`pose_state="match_anchor"`** filters to anchor's pose_state.
9. **`pose_state="any"`** surfaces both buckets (lift/lower duplicates).
10. **`limit`** truncates after sort (highest cosine kept).
11. **Cosine ordering**: results sorted descending by cosine, then
    ascending by distance.
12. **Read-only invariant**: `_map` byte-equal before/after call.

Container-side execution:
```bash
docker exec -w /workspace/rtsm rtsm-dev \
    python3 -m unittest tests.test_find_fragments -v
```

## Live verification

After `--apply` and `docker compose restart rtsm-dev`:

```bash
# 1. Endpoint reachable, anchor present (basketball is movable).
curl -s -X POST http://localhost:8002/objects/18503a243abd46fb/find_fragments \
     -H 'Content-Type: application/json' -d '{}' | jq '.thresholds, .scanned_objects, .returned'
# Expected: dist_threshold_m=9.0, dist_threshold_default_used=true, returned >= 0

# 2. Override distance.
curl -s -X POST http://localhost:8002/objects/18503a243abd46fb/find_fragments \
     -H 'Content-Type: application/json' \
     -d '{"dist_threshold_m": 3.0}' | jq '.thresholds.dist_threshold_m, .thresholds.dist_threshold_default_used'
# Expected: 3.0 and false

# 3. Static anchor uses 3m default (couch).
curl -s -X POST http://localhost:8002/objects/f5b67645c1a2402e/find_fragments \
     -H 'Content-Type: application/json' -d '{}' | jq '.anchor.movability_class, .thresholds.dist_threshold_m'
# Expected: "static" and 3.0

# 4. Sweep all named anchors, summarize fragment counts.
for oid in $(curl -s http://localhost:8002/objects | jq -r '.objects[] | select(.label_user != null) | .id'); do
    label=$(curl -s http://localhost:8002/objects/$oid | jq -r '.label_user')
    count=$(curl -s -X POST http://localhost:8002/objects/$oid/find_fragments \
            -H 'Content-Type: application/json' -d '{}' | jq '.returned')
    printf "%-25s %s (%s)\n" "$label" "$count" "$oid"
done

# 5. Unknown anchor -> 404.
curl -s -o /dev/null -w "%{http_code}\n" -X POST \
     http://localhost:8002/objects/0000000000000000/find_fragments \
     -H 'Content-Type: application/json' -d '{}'
# Expected: 404

# 6. Invalid pose_state -> 422.
curl -s -o /dev/null -w "%{http_code}\n" -X POST \
     http://localhost:8002/objects/18503a243abd46fb/find_fragments \
     -H 'Content-Type: application/json' -d '{"pose_state": "bogus"}'
# Expected: 422
```

## Risk / non-risk

- **Read-only.** No WM mutation, no FAISS write, no behavior change for
  Albert. Pure diagnostic endpoint.
- **No conversation-id concerns.** HTTP path, not Dify.
- **Container restart required** (FastAPI loads routes at startup).
  Standard `docker compose restart rtsm-dev` from `~/rtsm/docker/`.
- **No Albert-side change.** The endpoint is entirely server-side; no
  largemodel patch required, no role update, no Dify change.

## Follow-up items NOT in this deploy

- **Adaptive distance defaults in `cfg/rtsm.yaml`** so the defaults
  table is editable without a code change. Out of scope; ship the
  hardcoded table now, externalize later if Peep wants to tune.
- **`label_user` uniqueness/alias** (Section 6 P2 in roadmap). Related
  but structurally separate — that's a PATCH-handler change.
- **Eviction `dry_run → live` flip** (B.3). Separate concern; use
  `find_fragments` to clean up duplicates before flipping, not after.
- **Camera-down safety gate** for `name_object` (the second issue from
  this session's intro). Albert-side patch; queued for next bench
  session.
