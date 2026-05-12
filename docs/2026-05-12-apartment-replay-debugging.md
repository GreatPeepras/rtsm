# 2026-05-12 — Apartment replay regression debugging

## Symptom
0 confirmed objects on 500-frame apartment replay (vs 193 on 2026-05-11 baseline).

## Root cause
Two coupled threshold changes between 2026-05-11 and today, neither isolated to a
revertable commit:

1. `cfg/clip/vocab.yaml`: `min_top` 0.06→0.08, `min_margin` 0.005→0.03
2. `cfg/rtsm.yaml`: `object.promote_min_conf` 0.05→0.18

Apartment-data CLIP cosines sit at 0.08–0.10, below the 0.18 promote gate.
With (1), most observations hit the `class_idx==-1` branch in
`rtsm/core/pipeline.py:829`, which **empties** `label_topk` (discarding
otherwise-usable top-K evidence). With (2), even surviving observations
fail the label-confidence gate at promotion time.

## Fix applied (2026-05-12)
Reverted both thresholds to demo-baseline values. System restored to
~9 confirmed objects on 500-frame replay (matches `hits≥5` proto count).

## Architectural followup needed
`pipeline.py:829` discards top-K when classifier returns "unknown".
Should keep top-K (soft evidence) and gate strictly at promotion time
via `promote_min_conf`. This decouples per-frame strictness from
multi-observation aggregation in WM.

