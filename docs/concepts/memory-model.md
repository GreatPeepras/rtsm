# Memory Model

RTSM maintains a two-tier memory system: **Working Memory** for active tracking and **Long-Term Memory** for persistent, queryable storage.

---

## Object Lifecycle

```
Observation → Proto-Object → Confirmed Object → Long-Term Memory
```

---

## Working Memory

Working memory holds `ObjectState` records for all tracked objects:

```python
ObjectState:
  id: str                    # unique identifier
  xyz_world: [x, y, z]       # 3D position in world frame
  cov_world: [3x3]           # position covariance
  emb_mean: [512]            # running mean of CLIP embeddings
  emb_gallery: [[512], ...]  # gallery of view embeddings
  view_bins: set             # viewpoint directions seen
  label_scores: dict         # EWMA label confidences
  stability: float           # embedding consistency score
  hits: int                  # observation count
  confirmed: bool            # promotion status
  image_crops: [bytes, ...]  # JPEG snapshots
  last_seen: timestamp
```

### Proto-Objects

New observations create **proto-objects** — tentative entries that may be noise or transient. Proto-objects expire after `proto_ttl_s` (default: 10 seconds) if not re-observed.

### Promotion Criteria

Proto-objects become **confirmed** when all criteria are met:

| Criterion | Config Key | Default |
|-----------|-----------|---------|
| Observation count | `object.promote_hits` | ≥ 2 |
| Stability score | `object.stability_promote` | ≥ 0.55 |
| View diversity | `object.require_view_bins` | ≥ 1 viewpoint |

This filters out:

- Single-frame noise
- Inconsistent detections (low embedding stability)

!!! note "Loosened defaults"
    The defaults are intentionally permissive (`stability_promote: 0.55`, `require_view_bins: 1`) to allow confirmation even from a stationary camera. Tighten these for multi-viewpoint setups.

---

## Association

When a new observation arrives, RTSM finds the best matching object using a two-gate process:

1. **Spatial gate** — Fetch candidate objects within `gate_dist_base_m` (default: 0.50m) using the sweep cache spatial index
2. **Embedding gate** — Compute cosine similarity of CLIP embeddings against the nearest K candidates (default: K=8)
3. **Match decision** — Accept if cosine similarity ≥ `cos_min` (default: 0.90)

```
if cosine_similarity(observation, candidate) >= 0.90
   AND distance(observation, candidate) <= 0.50m:
    → match: update existing object
else:
    → create new proto-object
```

### Update on Match

When matched, the object state is updated:

- **Position**: Kalman-filtered update with covariance
- **Embedding**: Added to gallery, running mean updated
- **Hits**: Incremented
- **Stability**: Recalculated using EWMA (`stab_k: 0.45`)
- **Labels**: EWMA-updated label scores from vocabulary classification

### Association Config

```yaml
assoc:
  cos_min: 0.90                  # cosine similarity threshold
  gate_dist_base_m: 0.50         # 3D distance gate (meters)
  gate_reproj_px: 60             # reprojection distance gate (pixels)
  nearest_m_for_cos: 8           # compare against K nearest by distance
  use_embeddings: true
  fallback_all_when_empty: true  # fallback to all WM if no spatial neighbors
```

---

## Sweep Cache (Spatial Index)

The sweep cache provides O(1) spatial lookups for association. Objects are indexed into a 2D grid (default cell size: 0.25m):

```yaml
sweep_cache:
  grid_size_m: 0.25
  two_d: true                    # drop Z for indoor scenes
  per_cell_cap: 64
```

View direction is also quantized into bins (`yaw_bins: 12`, `pitch_bins: 5`) to track which directions each cell has been observed from.

---

## Long-Term Memory

Confirmed objects are flushed to **Long-Term Memory** via the vector store:

### Storage

- **FAISS** (default) — Local vector index for semantic search
- **Milvus** (optional) — Distributed vector database

```yaml
vectors:
  enable: true
  backend: faiss
  dim: 512
  flush_period_s: 3.0
```

### Semantic Search

Text queries are encoded via CLIP and matched against stored embeddings:

```
"red mug" → CLIP text encoder → query vector → FAISS top-k → ranked objects
```

### Spatial Search

Objects can also be queried by 3D position:

```
(x=1.0, y=0.5, z=2.0, radius=0.5m) → proximity index → nearby objects
```

---

## Expiry & Demotion

- **Proto expiry**: Unconfirmed objects expire after `proto_ttl_s` (default: 10s)
- **Pose demotion**: Confirmed objects are demoted back to proto if a SLAM loop closure shifts their position by more than `pose.demote_thresh_m` (default: 0.30m)
- **Stability decay**: Objects not re-observed decay via `miss_decay` (default: 0.5)

---

## Next Steps

- [REST API](../api/rest-api.md) — Query the memory
- [Architecture](architecture.md) — Full system overview
- [Perception Pipeline](perception-pipeline.md) — How observations are generated
