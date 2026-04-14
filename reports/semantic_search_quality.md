# Semantic Search Quality Report

**Date:** 2026-04-14
**Dataset:** `recordings/session1` (240 frames, 75.8s, grounded_sam2 backend)
**System:** RTX 5090, CUDA 13.0, Python 3.12
**CLIP model:** SigLIP ViT-B-16 (WebLI), 768-D

---

## Problem

RTSM semantic search must reliably return the correct physical object for natural-language queries. Prior investigation (April 2026) showed that SigLIP ViT-B-16 dramatically outperforms CLIP ViT-B/32 and ViT-L/14 for masked-crop retrieval. This report validates those findings on the current session1 recording.

## Methodology

- Replayed `recordings/session1` through the full pipeline (grounded_sam2 segmentation + SigLIP embedding + association + promote)
- Extracted all 42 confirmed object embeddings via the REST API
- Encoded query text locally using SigLIP ViT-B-16
- Computed cosine similarity against all confirmed objects
- Measured: rank of correct object, score, margin, spread
- Tested 5 prompt templates across 6 target objects

Ground truth established by visual inspection of object snapshots.

## Results

### 1. Template Comparison (SigLIP ViT-B-16, 42 confirmed objects)

| Template | Found | Top-1 | Top-3 | Mean Rank | Mean Score |
|----------|-------|-------|-------|-----------|------------|
| `{}` (raw) | 5/6 | 3/6 | 4/6 | 2.60 | 0.0831 |
| `a photo of a {}` | 5/6 | 3/6 | 4/6 | 2.00 | 0.0907 |
| **`a cropped photo of a {}`** | **5/6** | **3/6** | **5/6** | **1.60** | **0.0887** |
| `a close-up photo of a {}` | 5/6 | 3/6 | 5/6 | 1.80 | 0.0822 |
| `an indoor photo of a {}` | 5/6 | 3/6 | 4/6 | 3.20 | 0.0789 |

**Finding:** `"a cropped photo of a {}"` achieves the best mean rank (1.60) and top-3 rate (5/6). This matches SigLIP's strength with object-crop retrieval.

### 2. Per-Target Breakdown (best template: cropped_photo)

| Target | Rank | Score | Top-1 Label | Margin | Notes |
|--------|------|-------|-------------|--------|-------|
| **TV** | **1** | 0.0847 | monitor | 0.0051 | Correctly identified. Labeled "monitor" in WM. |
| **air conditioner** | **1** | 0.1060 | portable air conditioner | 0.0257 | Strong discrimination. Highest score of all targets. |
| **speaker** | **1** | 0.0983 | speaker | 0.0291 | Strong discrimination. Correct label. |
| **laptop** | **2** | 0.0707 | tablet | 0.0034 | Tablet ranked first — both are laptop-class objects. |
| **pillow** | **3** | 0.0840 | cushion | — | Cushion ranked first; semantically adjacent. |
| doll | — | — | — | — | Not detected in this recording. |

### 3. Per-Target Rank Stability Across Templates

| Target | raw | a_photo_of | cropped_photo | closeup_photo | indoor_photo |
|--------|-----|------------|---------------|---------------|--------------|
| TV | 1 | 1 | 1 | 3 | 1 |
| pillow | 7 | 5 | 3 | 3 | 10 |
| doll | — | — | — | — | — |
| air conditioner | 1 | 1 | 1 | 1 | 1 |
| speaker | 1 | 1 | 1 | 1 | 1 |
| laptop | 3 | 2 | 2 | 1 | 3 |

**Finding:** Air conditioner and speaker are template-invariant (always rank 1). TV is stable across most templates. Pillow is template-sensitive (rank 3-10). Laptop varies (rank 1-3).

## Key Findings

### SigLIP delivers reliable top-3 retrieval

5/6 targets found across all templates. 3/6 consistently at rank 1. The cropped_photo template achieves 5/6 in top-3. This represents production-viable semantic search for indoor object queries.

### Score ranges are characteristic of SigLIP

Cosine scores range 0.05-0.10 (vs 0.25-0.31 for CLIP ViT-B/32). Lower absolute scores but dramatically better inter-object discrimination. Score margins of 0.005-0.029 are sufficient for reliable ranking.

### Template choice matters for edge cases

Core objects (speaker, AC, TV) are robust to template choice. Edge cases (pillow, laptop) benefit from "a cropped photo of a {}" framing, which matches the masked-crop input format.

## Historical Comparison

| Metric | April 9 (old session1, 18 obj) | April 14 (new session1, 42 obj) |
|--------|-------------------------------|--------------------------------|
| Top-1 rate (best template) | 3/6 | 3/6 |
| Top-3 rate (best template) | 3/6 | **5/6** |
| Mean rank (best template) | 1.75 | **1.60** |
| Objects searched | 18 | 42 |

**Finding:** Search quality improved despite 2.3x more objects (harder search space). The "cropped_photo" template now achieves 5/6 top-3 vs 3/6 previously.

## Remaining Limitations

1. **Doll not detected** — the cow-pattern cushion from the old recording is not present in this session.
2. **Pillow-cushion confusion** — SigLIP can't distinguish cushion from pillow at the embedding level; both are semantically valid.
3. **Laptop-tablet confusion** — the MacBook is labeled "tablet" by grounded_sam2; SigLIP ranks it close to the actual laptop.
4. **Score margins are tight** (0.003-0.029). Top-3 retrieval with visual verification remains more reliable than trusting top-1 alone.

## Configuration

- **Segmentation:** Grounded SAM2 (GDINO Tiny + SAM2.1 Hiera Small, Apache 2.0)
- **Embedding:** SigLIP ViT-B-16 via open_clip (Apache 2.0)
- **Vector dimension:** 768
- **Background fill:** Mean color (default)

All default dependencies are permissive (Apache 2.0 / MIT).

---

*Generated by RTSM semantic search evaluation framework (`scripts/eval_semantic_search.py`).*
*Raw data: `reports/semantic_eval_siglip.json`*
