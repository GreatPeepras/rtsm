# Persistence Strategy for Resident-Robot Deployment

**Status:** Draft — design captured 2026-05-11 alongside threshold-tightening PR.
**Author:** [Albert team]
**Last updated:** 2026-05-11

## Context

Albert is transitioning from demo-clip validation (50-frame replays of
controlled scenes) to resident-robot deployment (continuous live operation
in a single apartment over months). The configuration that was correct for
demo is wrong for resident-robot, and the failure modes invert.

## The resident-robot principle

> **In a continuous live deployment, false positives accumulate forever and
> false negatives self-correct in days.**

Demo configuration favors recall (catch every object in the 50 frames you
get). Resident-robot configuration favors precision (don't pollute LTM
with ghosts you'll never get rid of, because the robot will keep observing
real objects for months and pick them up eventually).

This principle drives every threshold decision in this PR and subsequent
retuning PRs.

## The current state of LTM persistence

LTM has **no eviction logic**. Every WM object that crosses the promote
gate flows to FAISS and stays there forever. Saved on every upsert
(`faiss_client.py:133, 174` — see TODO in `demo-config-audit.md`).

This means:
- Every false positive is permanent.
- Every legitimate-but-moved object becomes a ghost (the original LTM
  record persists; a new record is created at the new location;
  no relationship between them).
- The system has no way to express "this object is gone" or "this
  object was actually two objects all along."

## Three-tier eviction model (Phase-2, not in this PR)

| Tier | Signal | Action | Latency |
|------|--------|--------|---------|
| Tier 0 | WM `proto_ttl_s` expiry | Drop unconfirmed WM proto | ~10s |
| Tier 1 | Frustum-overlap miss counter | Mark WM object stale; do NOT evict from LTM | ~minutes |
| Tier 2 | LTM-side TTL or absence-evidence accumulator | Soft-evict: move to ghost log, keep embedding for re-id | ~days |

**Tier 1** is the new and important one: when the robot is *looking at*
the place an object should be and not seeing it, accumulate evidence-of-
absence. This requires:

1. Per-keyframe frustum computation (which WM objects' xyz_world fall in
   the current view cone).
2. Per-WM-object miss counter (incremented when in-frustum but not matched
   to any current detection).
3. Stale-flag transition when miss-count exceeds a movability-dependent
   threshold.

**Tier 2** evicts from LTM. The eviction is *soft*: the embedding goes to
a ghost log, not deleted. When a new detection's embedding matches a ghost,
we know the object moved (re-id), and the new detection inherits the
ghost's identity rather than creating a fresh one.

## Movability ladder

Different object types have different priors on motion. Eviction
parameters should respect this. Six-class taxonomy:

| Class | Examples | Movement model | Tier-1 miss budget | Tier-2 TTL |
|-------|----------|----------------|---------------------|-----------|
| permanent  | walls, doors, built-ins | Position is hard prior | ∞ | ∞ |
| static     | couch, fridge, desk     | Months between events  | 200 frames | 90 days |
| semi_static| chair, lamp, basket     | Weekly-ish             | 50 frames  | 14 days |
| movable    | mug, book, remote       | Daily                  | 20 frames  | 3 days |
| roaming    | toys, robot, person     | Constant motion        | 5 frames   | 1 day |
| ephemeral  | snack bag, mail         | Appears/disappears     | 10 frames  | 12 hours |

These numbers are **placeholders for Phase-2 calibration**, not committed
operating points.

### Where does the movability prior come from? (Four options)

1. **Per-label static mapping in `vocab.yaml`.** Each vocab entry gets a
   `movability:` field. Cheap, immediate. Phase-2 starting point.
2. **Learned per-instance from observation.** Track xyz variance over an
   object's lifetime; classify after enough data. Adapts to Albert's
   apartment specifically. Cold-start problem.
3. **Bayesian update of (1) by (2).** Vocab provides prior; observations
   refine to posterior. Phase-3 target.
4. **User override** (this PR). PATCH `/objects/{oid}` with
   `movability_class` field. Always wins over (1)/(2)/(3).

## What this PR ships

- `label_user` field on `ObjectState` — never auto-evicted.
- `movability_class` field on `ObjectState` — currently a placeholder,
  consumed by Phase-2 eviction logic.
- `display_label = label_user or label_primary` flows through the upsert
  payload, FAISS dedup key (`_identity_key`), and `_obj_summary`.
- `PATCH /objects/{oid}` endpoint with sentinel-pattern body parsing.
- Threshold restoration (vocab `min_top`/`min_margin`, `promote_min_conf`)
  to bound false-positive rate at the labeling layer.

## What this PR explicitly does NOT ship

- Tier-1 frustum-overlap miss counter.
- Tier-2 LTM eviction.
- Eviction ghost log.
- Embedding-based re-id of moved objects.
- Movability priors loaded from `vocab.yaml`.
- FAISS save throttling.

These are Phase-2 work. The shipped infrastructure (label_user, movability_
class, display_label) is the forward-compatible substrate.

## Eviction ghost log (designed, not built)

When a Tier-2 eviction fires, the evicted record's embedding + last-known
position go to a ring buffer keyed by movability class:

    ghost_log[movability_class] = [(emb, xyz, evicted_at, original_oid), ...]

On new-object creation, query the ghost log: if the new embedding's
nearest-neighbor in the appropriate movability bucket is closer than
some threshold, the new object inherits `original_oid` and the ghost
entry is removed. This is re-id without storing every evicted object
forever.

Ghost log retention follows the same TTL as the movability class. A
"movable" ghost expires after 3 days; a "permanent" ghost never expires
(but permanents shouldn't be evicting).

## Open questions

- How does `label_user` interact with Tier-2 eviction? Hard guess: user-
  pinned objects never evict, but their *position* can update on re-
  observation. Worth thinking through edge cases.
- Should `display_label` flow into the CLIP pseudo-vocab for re-querying?
  I.e., if Albert renames an object to `albert_filament_inventory`, should
  future detections check that string? Probably no (CLIP can't usefully
  embed "albert_filament_inventory"), but the question deserves a thought.
- Frustum computation is O(N_WM × N_keyframes). At ~hundreds of WM
  objects and ~Hz keyframe rate this is fine; at thousands it isn't.
  Spatial index needed at some scale.
