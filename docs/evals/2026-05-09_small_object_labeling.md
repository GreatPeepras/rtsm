# Small-object labeling fixes — 2026-05-09

## Context

Bedroom test scene: a plushy on the bed was consistently labeled
`night light` rather than anything stuffed-animal-like, and 2-3 other
small objects (a tissue box, the actual night light) were also being
mis-labeled `night light`. Semantic search for "teddy bear" or
"tissue box" returned irrelevant results.

## Hypothesis

Tight crops (6 px padding around staged bboxes) gave SigLIP almost
no spatial context. Small objects were embedding to nearly identical
vectors regardless of what they actually were, and one label
("night light") was dominating the cluster by chance.

A secondary hypothesis: even when the embedding *did* score the
correct concept, our `vocab_topk=5` cap on stored label_scores threw
it away before it could accumulate in the EWMA dictionary.

## Changes

### `staging.crop_pad_px`: 6 → 24

Pads bbox by 24 px on each side before SigLIP encoding. Wider
context lets the model see surrounding texture (bedding around a
plushy, surface around a night light) and produces meaningfully
different embeddings for visually distinct small objects.

### `clip.vocab_topk`: implicit 5 → 30

SigLIP already scores the full vocabulary; this is the storage cap
on per-object `label_scores`. At 5 we were filtering out the
correct concept before EWMA could lock onto it. At 30 we keep the
long tail visible without blowing up object size.

## Eval (bedroom scene replay)

Pre-patch (vocab_topk=5, crop_pad_px=6):

- 3 objects labeled `night light` (real night light, plushy, tissue box)
- Semantic search "teddy bear" → noise
- Semantic search "tissue box" → noise (clock won)
- Plushy `teddy bear` rank: #21 in label_scores
- Plushy `tissue box` rank: #34 in label_scores

Post-patch (vocab_topk=30, crop_pad_px=24):

- 1 object labeled `night light` (the real one), gap to #2 wider than before
- Plushy now labeled `pillow` top-1 (still wrong, but `teddy bear`
  has risen to #9 and `pet toy`, `doll` are now in the dict)
- Semantic search "teddy bear" → plushy at #1 (score 0.054)
- Semantic search "stuffed animal" → plushy at #1 (score 0.050)
- Semantic search "night light" → real night light still in top 5
- Confirmed object count: 14 → 18

## Known follow-ups (filed as TODOs, not blockers)

1. **Adjacent-small-object staging.** A real teddy bear sits
   right next to the plushy on the bed. Only 1 staging hit, never
   confirmed. Likely staging dedup IoU competition between
   overlapping padded crops. Worth investigating but separate from
   this change.

2. **Tissue box still mislabeled.** Now labeled `tablet` (was
   `night light`). Vocab issue, not embedding issue —
   `tissue box` template embedding doesn't beat `tablet`/`cup`/
   `pillow` for any of our actual tissue box views. Either prompt-
   engineer the template or accept vocab as the bottleneck.

3. **Multiple night-light-class objects on far wall.** SigLIP
   correctly clusters them in vector space (all return for "night
   light" search), but only one wins the discrete top-1 label.
   Cosmetic, not a retrieval problem.

## Files touched

- `rtsm/cfg/rtsm.yaml` — both knobs

## Methodology notes

Replay-based eval. Wiped FAISS indexes (`/workspace/workdir/index.faiss`
plus FastAPI WM state) between runs to ensure clean comparison.
Ran the same recording session twice, once with each config, and
compared `/objects` listings, per-object `label_scores` rankings,
and `/search/semantic` query results for "tissue box", "teddy bear",
"stuffed animal", "night light".

Crops dumped from `/objects/{id}/snapshots/{idx}/image` for visual
verification. Per-object `label_scores` ranking was the most
informative diagnostic — it shows where the correct concept sits
in the long tail even when top-1 is wrong.
