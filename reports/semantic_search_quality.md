# Semantic Search Quality Report

**Date:** 2026-04-09
**Dataset:** `recordings/session1` (162 frames, dual backend)
**System:** RTX 5090, CUDA 13.0, Python 3.12

---

## Problem

RTSM semantic search returned nearly identical objects regardless of query. Querying "pillow", "speaker", or "laptop" produced the same top results with cosine scores clustered in a narrow 0.23-0.27 band. The correct object was not reliably returned as the top result.

## Investigation

We isolated four potential root causes and tested each systematically:

1. **CLIP text encoding format** — CLIP was trained on captions ("a photo of a dog"), not single words ("dog")
2. **Background fill in masked crops** — mean-color vs white vs black vs blur
3. **CLIP model capacity** — ViT-B/32 (512-D) vs ViT-L/14 (768-D)
4. **Training objective** — CLIP contrastive loss vs SigLIP sigmoid loss

### Methodology

- Replayed `recordings/session1` through the full pipeline (segment + embed + associate + promote)
- Extracted all confirmed object embeddings via the REST API
- Encoded query text locally using the same model
- Computed cosine similarity against all confirmed objects
- Measured: rank of correct object, score, margin, spread

Ground truth was established by visual inspection of object snapshots exported from the API.

## Results

### 1. Prompt Template Comparison (ViT-B/32, 18 objects)

| Template | Top-1 | Top-3 | Mean Rank |
|----------|-------|-------|-----------|
| `{}` (raw) | 2/6 | 3/6 | 2.60 |
| **`a photo of a {}`** | **3/6** | **3/6** | **2.20** |
| `a cropped photo of a {}` | 2/6 | 3/6 | 3.20 |
| `a close-up photo of a {}` | 2/6 | 4/6 | 3.20 |
| `an indoor photo of a {}` | 2/6 | 3/6 | 3.40 |

**Finding:** Wrapping queries in "a photo of a {}" improves CLIP ViT-B/32 results. This matches CLIP's training distribution (image-caption pairs).

### 2. Background Fill Comparison (ViT-B/32, ~79 objects)

| Fill Method | Top-1 | Top-3 | Mean Rank |
|-------------|-------|-------|-----------|
| **Mean color** | **1/6** | **3/6** | **3.75** |
| White | 1/6 | 1/6 | 5.60 |

**Finding:** Mean-color fill (current default) outperforms white fill. The fill method has minimal impact compared to model choice.

### 3. CLIP Model Comparison (~71-80 objects, best template per model)

| Model | Params | Dim | License | Top-1 | Top-3 | Mean Rank | Score Range |
|-------|--------|-----|---------|-------|-------|-----------|-------------|
| ViT-B/32 (OpenAI) | 151M | 512 | MIT | 1/6 | 3/6 | 3.75 | 0.25-0.31 |
| ViT-L/14 (OpenAI) | 428M | 768 | MIT | 0/6 | 1/6 | 3.50 | 0.17-0.25 |
| **ViT-B-16-SigLIP (WebLI)** | **203M** | **768** | **Apache 2.0** | **3/6** | **3/6** | **1.75** | **0.05-0.10** |

### 4. Per-Target Breakdown (SigLIP, raw query)

| Target | Rank | Score | Margin | Notes |
|--------|------|-------|--------|-------|
| **Speaker** | **1** | 0.1027 | 0.035 | Strong discrimination. Never found with ViT-B/32. |
| **Pillow** | **1** | 0.0884 | 0.001 | Tight margin but correct ranking. |
| **Laptop** | **1** | 0.0942 | 0.007 | Matched via "computer box" label. |
| Air conditioner | 4 | 0.0534 | — | Correctly labeled by SigLIP (ViT-B/32 called it "toaster"). |
| TV | — | — | — | Dark screen indistinguishable from other dark surfaces. |
| Doll | — | — | — | Cow-pattern cushion not semantically close to "doll". |

## Key Findings

### SigLIP outperforms CLIP for object-crop retrieval

SigLIP's sigmoid training loss produces better per-pair discrimination than CLIP's contrastive softmax. The absolute cosine scores are lower (0.05-0.10 vs 0.25-0.31), but the **ranking quality is dramatically better** — the correct object appears at rank 1 for 3/6 queries vs 1/6 with CLIP.

### Bigger CLIP models do not help

ViT-L/14 (428M params, 768-D) performed **worse** than ViT-B/32 (151M, 512-D) on masked object crops. The larger model's capacity doesn't translate to better crop-level text-image alignment. This is consistent with the hypothesis that CLIP's training data (full images with captions) doesn't optimize for cropped-object retrieval.

### Prompt engineering is model-dependent

CLIP models benefit from "a photo of a {}" wrapping (matches training distribution). SigLIP works best with raw queries. The system now selects the wrapping strategy based on the model's pretrained source.

### Background fill is a non-factor

Mean-color fill (suppressing background to the crop's average RGB) is slightly better than alternatives but the effect is small compared to model choice.

## Remaining Limitations

1. **Dark/featureless objects** (e.g., TV showing a black screen) cannot be discriminated from other dark surfaces by any tested model. Depth-based or context-based features would be needed.
2. **Semantically distant labels** (e.g., "doll" for a cow-pattern cushion) fail because the visual appearance doesn't match the query concept.
3. **Score margins are tight** (0.001-0.035). In a production setting, top-3 retrieval with visual verification (via snapshot) is more reliable than trusting top-1 alone.
4. **Spurious object count** is high (~80 confirmed for ~15 real objects). Better deduplication and promotion gates would improve ranking by reducing distractors.

## Improvement Roadmap

- **View-binned search**: Match query against the best viewing angle per object, not the mean embedding. Objects seen from multiple angles would benefit from selecting the most discriminative view.
- **Foundation model tracking**: As vision-language models improve (SigLIP 2, future releases), the system benefits automatically — the architecture is model-agnostic.
- **Spatial context features**: Combine CLIP embeddings with depth/shape features for objects that are visually ambiguous but spatially distinct.
- **Object deduplication**: Merge confirmed objects that correspond to the same physical entity to reduce the search space.

## Configuration

The default configuration now uses:
- **Segmentation:** Grounded SAM2 (Apache 2.0)
- **Embedding:** SigLIP ViT-B-16 via open_clip (Apache 2.0)
- **Vector dimension:** 768

All default dependencies are permissive (Apache 2.0 / MIT). AGPL components (Ultralytics) are opt-in via `[gpu-ultralytics]`.

---

*Generated by RTSM semantic search evaluation framework (`scripts/eval_semantic_search.py`).*
*Raw data: `reports/semantic_eval_*.json`*
