# 2026-05-11 — Apartment recording replay (first end-to-end live run)

## Summary

First successful end-to-end run of the live pipeline against real apartment
sensor data (`2026-05-06T14-00-15Z`, RealSense D415, 4500 frames). Replayed
500 frames at 15 Hz, drained queue in ~8 minutes, produced 193 confirmed WM
objects across 38 unique CLIP labels. Zero send errors, zero queue drops.

This is the milestone we've been aiming at since the May 8 mock-data run
(12 confirmed objects in synthetic scene).

## Environment

- Container: `rtsm-dev` running `rtsm.run` (live mode, no `--serve`)
- Endpoint: `http://localhost:8002`
- Replay tool: `python3 -m rtsm.tools.replay` with `--synthetic-pose`
- Session: `2026-05-06T14-00-15Z`, 4500 frames available, used frames 0-500
- Pose: identity (synthetic) — no `/tf` capture in this recording

## Pipeline metrics (replay-side)

| Metric | Value |
|---|---|
| Frames sent | 500/500 |
| Mean rate | 14.98 Hz |
| Elapsed (ingest) | 33.30 s |
| Drain (pipeline) | ~8 min |
| Pipeline throughput | ~1.04 FPS |
| Latency p50 / p95 / max | 34.1 / 37.6 / 55.4 ms |
| Decode p50 (server) | 20.4 ms |
| HTTP errors | 0 |
| Queue drops | 0 |

## Working memory state (final)

| Metric | Value |
|---|---|
| Total objects | 196 |
| Confirmed | 193 |
| Unique labels | 38 |
| Avg hits/object | 20.2 |
| Stability ≥0.99 | 92 (48%) |
| Hits 50+ | 32 |
| Hits ≤4 | 61 |

Top labels (confirmed): `edge` (49), `night light` (36), `mirror` (8),
`card box` (8), `television` (7), `bottle` (7), `shoe` (7), `glass` (7),
`webcam` (6), `picture` (5), `phone` (5), `computer` (4), `clock` (4).

## Failure modes (visual ground-truth on 8 spot-checks)

### Pattern 1 — Motion blur → hallucinated label

Pipeline at ~1 FPS sampling 15 Hz video means many processed frames are
mid-motion. Blurry crops collapse to "blurred dark rectangle" which CLIP
labels as `edge`, `couch`, `sofa`, `mirror`, etc.

Examples:
- `049_edge` → blurry PC tower
- `001_couch` → blurry, possibly office chair wheel
- `001_sofa` → blurry, possibly lower part of door

### Pattern 2 — Surface labels for non-objects

CLIP's open-vocab class set includes abstract surface concepts that
aren't apartment objects.

Examples:
- `008_mirror` → glossy cupboard panel (not a mirror)
- `004_clock` → same glossy cupboard panel (not a clock)
- `edge` (49 instances) → mostly blur or boundaries

Approximate share of WM affected by surface-class labels: ~75/193 (~39%).

### Pattern 3 — One physical object → many WM entries

The single most important failure pattern for downstream semantic memory.

**Filament box (one physical item):** appears as
- `night light` × 36
- `card box` × 8
- `hand sanitizer` × 3
- `thermostat` × 2
- `whiteboard` × 2
- = **at least 51 WM entries for 1 thing**

**Cupboard panel (one physical item):**
- `mirror` × 8 + `clock` × 4 = 12 entries

**Coca-cola bottle:**
- `bottle` × 7 + `glass` × 7 = 14 entries

Estimated WM after ideal dedup: ~50-60 distinct apartment objects (from 193).

### Pattern 4 — Wrong label, useful concept

`001_bed` (h=128) is a towel on the floor where Albert (the robot) rests.
CLIP labels it `bed`; the WM correctly identifies it as a persistent
spatial entity. This argues for **decoupling WM identity from CLIP label**:
WM tracks "things that exist"; labels are one source of metadata, mutable
and possibly overrideable from semantic memory.

## Open issues

### Blocking for production

1. **WM duplication (Pattern 3)** — same physical object becomes N entries.
   Top priority because it directly breaks downstream semantic-memory
   linking ("Albert's filament box" can't refer to 51 oids).

### Non-blocking but important

2. **FAISS persistence not wired in live mode.** `upserts_total: 0` after
   193 confirmed, FAISS dir empty. Confirmed objects exist in working
   memory only and will not survive container restart.
3. **Blur gating** — pipeline processes blurry frames as if they were
   sharp, producing low-quality detections that still pass promotion.
4. **CLIP surface-class leak** — `edge`, `corner`, `floor`, `sheet`, etc.
   shouldn't promote to WM as objects.

### Known, deferred

5. **WebSocket `/static/*` AssertionErrors** in dev container — cosmetic.
6. **GUI shows "black void"** — no SLAM mesh layer; objects render as
   markers in empty space. Needs `/tf` + reconstruction work.
7. **Synthetic identity pose** — `xyz_world` values are camera-frame, not
   apartment-frame. Cross-session spatial reasoning is meaningless until
   real `/tf` is captured. This recording does not have `/tf`.

## Prioritized next-session work

Goal: make 1 WM entry = 1 physical apartment object.

### P1 — De-duplication (multi-signal merge)

Merge two confirmed objects A, B iff **all**:
- $\|xyz_A - xyz_B\| < d_{\text{spatial}}$ (try 15-25 cm)
- $\cos(e_A^{\text{CLIP}}, e_B^{\text{CLIP}}) > \tau_{\text{embed}}$ (try 0.85)
- A and B were **never co-detected** in the same frame as separate masks
  (hard constraint — distinguishes "same thing seen twice" from "two
  things sitting next to each other")

The third criterion is what protects "filament box on cupboard" from
being merged with the cupboard. Two co-visible masks in a single frame
prove they are physically distinct.

### P2 — Blur gate (pre-FastSAM)

Laplacian variance over the input frame; reject frames below threshold.
Cheap (~1 ms). Should remove a large share of `edge`/`couch`/`sofa`
mislabels.

### P3 — CLIP class blocklist

Don't promote objects whose top label is in `{edge, corner, floor, sheet,
wall, surface, room, ceiling, ...}`. Add a `promote_blocklist` config
key.

### P4 — FAISS live-write path

Wire WM→FAISS so confirmed objects persist across restarts. Bump
`upserts_total` counter when writing. Validate with restart-and-check.

### P5 — `/tf` capture in recording tool

So world coordinates are stable across sessions and `xyz_world` actually
means "in the apartment frame."

### P6 — WM label override hook

So Albert's semantic memory can rename a WM object (`oid=c2ec9236` →
"my filament box") without fighting CLIP.

## Diagnostic recipes that worked this session

```bash
# Check for hung pipeline / queue state
curl -s http://localhost:8002/stats | python3 -m json.tool
curl -s http://localhost:8002/stats/ingest | python3 -m json.tool

# Pull WM dump
curl -s 'http://localhost:8002/objects?limit=500' > /tmp/wm_dump.json

# Replay N frames from a recording
docker exec rtsm-dev python3 -m rtsm.tools.replay \
    --session <SESSION_ID> \
    --rate 15 --limit N --start 1 \
    --synthetic-pose --progress 50

# Save 1 representative snapshot per unique label
# (see session log for full python block — produces /tmp/wm_inspect/)
```

## Files / artifacts

- Replay log: `/tmp/apartment_replay_500.log`
- WM dump (final): `/tmp/wm_dump.json`
- Visual ground-truth set: `/tmp/wm_inspect/` (38 representative crops)
- Pipeline log: in container at `/tmp/rtsm.log`

These are in container/host `/tmp` and will be lost on reboot — copy
anywhere worth keeping before then.
