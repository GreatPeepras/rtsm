# Handoff — 2026-05-12: split-gate promotion

**Status**: shipped. Committed as `2bbd255`.
**Predecessor**: yesterday's loose-gate restoration (`ff1daf5`).
**Replay artifacts**: `/tmp/apartment_replay_500_split_gate.log`, `/tmp/objects_after_split_gate.json`

## What we set out to do

The May 11 patch tightened `promote_min_conf` from 0.05 to 0.18, intending to
restore resident-robot precision after the demo run had loosened it. On the
apartment session (`2026-05-06T14-00-15Z`), this collapsed confirmation rate
to near zero, because apartment-scale CLIP cosines on this data sit at
0.08-0.10. The threshold was being applied to the wrong scale.

Reverting to 0.05 restored recall but reintroduced the noise tail (phantom
labels like `drill`, `tape measure` confirming on single-frame
high-cosine flukes).

The fix had to address both: keep the loose per-frame score, but require
**multi-frame agreement** before promotion.

## What shipped

**Two-gate promotion logic in :**

- `promote_min_conf` (0.05): per-label EWMA score threshold. Unchanged.
- `min_label_hits` (5): per-label observation-count threshold. New.

Both must pass. The first is the score gate (is the label confident?); the
second is the evidence gate (have we seen this label enough times?).

**Pipeline change ():** when the per-frame classifier
rejects a crop (`class_idx == -1`), the soft top-K is now still passed to WM.
Previously, rejection zeroed the top-K, which meant evidence aggregation
never had a chance to fire on apartment-scale cosines. Per-frame strictness
is now decoupled from multi-observation aggregation.

**Schema ():** new `label_hits: Dict[str, int]` field mirroring
`label_scores`, monotonically incremented per top-K observation.

**API ():** `_obj_summary` exposes `label_top_hits`
(scalar for primary). `_obj_detail` exposes the full `label_hits` dict.

**Config ():** `min_label_hits: 5` added to `object:`
block, with comment explaining the joint gate.

## Smoke result

500-frame replay of `2026-05-06T14-00-15Z`:

- Pre-patch (loose gate, classifier rejection): 195 / 199 confirmed
- Post-patch (split gate, soft top-K to WM):    133 / 137 confirmed
- Trajectory: pre-patch climbed 1:1 with proto creation; post-patch shows
  expected confirmation plateaus at 52 and 96 where the evidence gate
  holds protos pending the 5th label observation.

Label tail before: `drill`, `tape measure`, other absent objects.
Label tail after: `blender`, `shoe`, `dishwasher`, `cup`, `chair` —
all plausible apartment things, each with hits >= 5.

## Spot-check on actual crops

Image inspection of top categories revealed:

- Labels are often wrong: `bench` cluster = cables / chair wheels / a
  towel; `computer` cluster = office-chair wheels; `card box` x3 = the
  same cardboard box from three views; `mirror` cluster largely wrong;
  `monitor` cluster blurry.
- Objects are mostly real: each confirmed proto corresponds to some
  persistent thing at world coordinates, even when the noun is wrong.
- The `webcam` cluster includes the data-collection camera seeing itself.
- The noise tail (`drill`, `tape measure`) is absent, as designed.

This is the intended outcome. The gate's job is to filter phantom protos,
not to fix CLIP vocabulary. Per the resident-robot framing, confirmed
objects are stable world-anchored slots ready for user/robot relabeling;
the CLIP label is scaffolding, not ground truth.

## Known issues

### display_label post-promotion drift

A confirmed object's `label_primary` is currently `argmax(label_scores)`
across all labels. After promotion fires (at which point some label X had
both score >= 0.05 AND hits >= 5), continued EWMA updates can reorder
scores such that a different label Y becomes the new max — even if
`label_hits[Y] < min_label_hits`. Result: `label_top_hits` in the
summary can read below the gate threshold for confirmed objects.

Witnessed in this run: 1 / 133 (the `cup` object `6f2833317b384bc0`,
`label_top_hits=4`). Promotion was correctly gated on a different label
with hits=7 at the time; `cup` overtook it post-confirmation by score.

Fix (followup): in `_obj_summary`, redefine `label_primary` as
`argmax(score)` over the subset `{label : hits >= min_label_hits}`.
Falls back to global argmax if subset is empty (shouldn't happen for
confirmed objects). About 5 lines, no schema change.

### Cross-view duplication

The three `card box` confirmations are the same physical box from
different views. This is a known cross-view association weakness, not
addressed by the split gate. Tracked separately.

### Vocabulary mismatch

CLIP's vocabulary doesn't include "office-chair wheels" or "power strip,"
so semantically near misses (`bench`, `computer`) attach to nearby
words. Vocabulary curation is a separate workstream. The resident-robot
relabel flow is the intended user-facing fix.

## What to do next session

Choose one:

1. **Display-drift fix** (small, ~5 lines, clean win). Promotes the
   reported gate self-consistency from 132/133 to 133/133.

2. **Image-validation pass at scale.** Pull crops for all 133 confirmed
   objects, score them yes/no for "is this a real persistent object."
   Gives a precision number for the resident-robot demo.

3. **Tune min_label_hits.** Current setting (5) is at the edge for
   short-dwell objects. Consider 3 (more recall, more noise risk) or 7
   (less recall, tighter precision). Requires a sweep across the
   500-frame replay; ~30 min of work.

4. **Cross-view association.** The card-box triplet is a known case;
   pulling on this thread is larger but lands closer to the
   resident-robot value prop than (3).

Recommendation: (1) is small and ships clean state. (2) is the most
informative for demo readiness. (4) is the most work but the most
strategic.

## Replay / repro

```bash
docker restart rtsm-dev
docker exec rtsm-dev python3 -m rtsm.tools.replay \
    --session 2026-05-06T14-00-15Z \
    --rate 15 --limit 500 --start 1 \
    --synthetic-pose --progress 50

# Drain, then snapshot
curl -s 'http://localhost:8002/objects?limit=500' > /tmp/objects.json
```

## Files touched (this commit)

```
rtsm/api/server.py              | +3
rtsm/cfg/rtsm.yaml              | +7 -1
rtsm/core/pipeline.py           | +11 -8
rtsm/stores/working_memory.py   | +17 -2
```
