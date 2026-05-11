# DEMO Config Marker Audit

**Status:** Living doc — table updates as markers get retuned.
**Created:** 2026-05-11 alongside threshold-tightening PR.

## Purpose

The current `rtsm/cfg/rtsm.yaml` was tuned for a 50-frame demo clip and
contains 17 `# DEMO:` markers indicating loosenings from previous
operating points. This doc inventories them, captures the original
values where known, and proposes a retuning order.

**Principle:** retune *with* live data, not before it. Each marker
reverted in isolation is a falsifiable hypothesis ("does tightening
this improve resident-robot precision without hurting recall?"). Reverting
all 17 in a single sitting throws away the chance to A/B and learn.

## The 17 markers

| # | File:Line | Parameter | Demo value | Original (if known) | Pipeline stage | Priority |
|---|-----------|-----------|------------|---------------------|----------------|----------|
| 1  | rtsm.yaml:50  | detector.box_threshold       | 0.18  | ?    | detector | high |
| 2  | rtsm.yaml:51  | detector.text_threshold      | 0.12  | ?    | detector | high |
| 3  | rtsm.yaml:111 | ingestion.keyframe_every_n   | 5     | ?    | ingestion | low |
| 4  | rtsm.yaml:112 | ingestion.nonkf_min_interval_s | 0.3 | ?    | ingestion | low |
| 5  | rtsm.yaml:128 | depth.min_depth_valid        | 0.40  | ?    | depth | medium |
| 6  | rtsm.yaml:136 | seg.min_area_px              | 400   | ?    | segmentation | high |
| 7  | rtsm.yaml:144 | depth.sigma_max_m            | 0.35  | ?    | depth | medium |
| 8  | rtsm.yaml:169 | clip.topk_preclip            | 12    | ?    | CLIP | medium |
| 9  | rtsm.yaml:195 | dedup.dedup_centroid_px      | 35.0  | ?    | dedup | medium |
| 10 | rtsm.yaml:197 | dedup.dedup_bbox_iou_thr     | 0.40  | ?    | dedup | medium |
| 11 | rtsm.yaml:198 | dedup.dedup_iou_thr          | 0.60  | ?    | dedup | medium |
| 12 | rtsm.yaml:231 | merge.gate_dist_base_m       | 0.35  | ?    | merge gating | medium |
| 13 | rtsm.yaml:232 | merge.gate_reproj_px         | 35    | ?    | merge gating | medium |
| 14 | rtsm.yaml:238 | object.proto_ttl_s           | 5.0   | ?    | WM lifecycle | medium |
| 15 | rtsm.yaml:240 | object.stability_promote     | 0.40  | 0.55 | WM promotion | high |
| 16 | rtsm.yaml:242 | object.stab_k                | 0.55  | ?    | WM stability | medium |
| 17 | rtsm.yaml:268 | mapping.tsdf.enable          | false | ?    | mapping | low |

(`#18` at line 294 is `enable: false` for an unidentified subsystem; needs
identification before scoring. Marked TBD.)

Plus, **already addressed in this PR (not on the list above):**

- vocab.yaml: `min_top` 0.06 → 0.20, `min_margin` 0.005 → 0.03.
- working_memory.py:498: hardcoded 0.05 → config `object.promote_min_conf: 0.18`.
- vocab.yaml: deletion of 6 structural classes.

## Retuning order

Upstream first; downstream is wasted effort if upstream is sloppy.

### Phase 1 — labeling layer (this PR)

✅ vocab `min_top` / `min_margin`
✅ `promote_min_conf` config-lift
✅ structural-class deletion

### Phase 2 — detector + segmentation

Next PR after this one collects ~1 week of live data.

- `detector.box_threshold` (currently 0.18; was loosened to catch dolls/
  small items in demo)
- `detector.text_threshold` (currently 0.12)
- `seg.min_area_px` (currently 400)

These three are a coupled set: the detector emits candidate boxes, segmentation
filters by area. Tuning them in isolation breaks the coupling.

### Phase 3 — depth + dedup

- `depth.min_depth_valid`, `depth.sigma_max_m`
- `dedup.*` (three coupled dedup thresholds)
- `merge.gate_dist_base_m`, `merge.gate_reproj_px`

### Phase 4 — WM lifecycle

- `object.proto_ttl_s`, `object.stability_promote`, `object.stab_k`

This phase wants Tier-1 eviction in place first (see persistence.md), so
WM lifecycle behaves predictably under continuous operation rather than
"5-second proto window."

### Phase 5 — performance + mapping

- `ingestion.keyframe_every_n`, `ingestion.nonkf_min_interval_s`
- `mapping.tsdf.enable` (currently false; re-enable when ready for memory
  cost)

## A note on `?` originals

Several "original" values are unknown — the comments in `rtsm.yaml` say
"DEMO:" but don't always state the prior value. Recovering these from
git history is a 10-minute task and should happen before Phase 2:

```bash
git log --all -p rtsm/cfg/rtsm.yaml | grep -B2 -A2 'box_threshold\|text_threshold\|...'
