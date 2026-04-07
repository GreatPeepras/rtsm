# Configuration

RTSM is configured via `config/rtsm.yaml`. This page covers the main settings grouped by section.

---

## Minimal Configuration

A minimal config to get started — most defaults are sensible:

```yaml
camera:
  width: 640
  height: 480
  fx: 604.6
  fy: 604.9
  cx: 318.8
  cy: 259.2

segmentation:
  backend: grounded_sam2   # Apache-2.0 default

io:
  receiver: websocket      # or zeromq for RealSense + RTABMap
```

---

## Camera Intrinsics

Match these to your RGB-D camera. Values below are for RealSense D435i:

```yaml
camera:
  model: D435i
  width: 640
  height: 480
  aligned_to: color
  fx: 604.634705
  fy: 604.906738
  cx: 318.806030
  cy: 259.239777
```

---

## Segmentation Backend

The segmentation backend determines which models extract object masks from each frame. This is the most impactful setting for both performance and licensing.

```yaml
segmentation:
  backend: grounded_sam2    # default (Apache-2.0)
  retina_masks: false       # false = 640x640 (fast), true = original resolution
```

| Backend | Description | License | Mean Latency |
|---------|-------------|---------|-------------|
| `grounded_sam2` | Grounding DINO + SAM2 (text-prompted) | Apache-2.0 | ~510 ms |
| `sam2` | SAM2 auto-mask (class-agnostic, no labels) | Apache-2.0 | ~860 ms |
| `dual` | FastSAM + YOLOE IoU merge (prompt-free, 1200+ categories) | AGPL-3.0 | ~210 ms |
| `fastsam` | FastSAM only (class-agnostic) | AGPL-3.0 | ~50 ms |
| `yoloe` | YOLOE only (open-vocab, prompt-free) | AGPL-3.0 | ~60 ms |

!!! note "AGPL backends require `ultralytics`"
    Backends using FastSAM or YOLOE require the `ultralytics` package (AGPL-3.0). Install with: `pip install "rtsm[gpu-ultralytics]"`

### Backend-Specific Settings

Each backend has its own configuration block:

```yaml
segmentation:
  # Grounding DINO + SAM2 (default)
  grounded_sam2:
    gdino_model_id: IDEA-Research/grounding-dino-tiny
    sam2_model_id: null          # null = use sam2.model_id
    device: cuda
    box_threshold: 0.25          # detection confidence
    text_threshold: 0.2          # text matching threshold
    vocab: null                  # null = default 30-class indoor vocab

  # SAM2 auto-mask
  sam2:
    model_id: facebook/sam2.1-hiera-small
    device: cuda
    points_per_side: 32
    pred_iou_thresh: 0.7
    stability_score_thresh: 0.92

  # FastSAM (AGPL)
  fastsam:
    model_path: model_store/fastsam/FastSAM-x.pt
    device: cuda
    imgsz: 640
    conf: 0.6
    iou: 0.7

  # YOLOE (AGPL)
  yoloe:
    model_path: model_store/yolo/yoloe-26s-seg-pf.pt
    device: cuda
    imgsz: 640
    conf: 0.25
    iou: 0.5

  # Dual-confirmation settings (backend: dual)
  dual:
    iou_confirm_threshold: 0.40     # IoU for cross-validation
    priority_boost_dual: 0.3        # priority boost for dual-confirmed masks
    prefer_mask: yoloe26            # which mask to keep for dual-confirmed
```

---

## I/O & Receiver

RTSM supports two input receiver backends:

```yaml
io:
  receiver: websocket               # websocket | zeromq
```

### WebSocket Receiver (Calabi Lens / ARKit)

```yaml
io:
  receiver: websocket
  websocket:
    host: "0.0.0.0"
    port: 8765
    require_tracking_normal: true    # drop frames with bad tracking
    keyframe_every_n: 30             # mark every Nth frame as keyframe
    nonkf_min_interval_s: 0.5        # throttle non-keyframes (~2/s)
    confidence_threshold: 2          # 0=all, 1=medium+high, 2=high only
```

### ZeroMQ Receiver (RealSense + RTABMap)

```yaml
io:
  receiver: zeromq
  camera_endpoint: tcp://172.27.240.1:5555   # D435i RGB-D frames
  rtabmap_endpoint: tcp://127.0.0.1:6000     # RTABMap pose topics
```

### Unit Conversion

If your depth source uses millimeters (e.g., RealSense D435i):

```yaml
units:
  depth_m_per_unit: 0.001     # mm → meters
  pose_m_per_unit: 1.0        # RTABMap poses are already in meters
```

---

## Mask Filtering & Heuristics

Controls which masks pass through the perception pipeline:

```yaml
gates:
  min_brightness: 5
  min_std: 5
  min_depth_valid: 0.35          # min fraction of valid depth pixels

masks:
  min_coverage: 0.005
  max_coverage: 0.8              # reject wall/floor-sized masks
  max_border_fraction: 0.15

filters:
  min_area_px: 500               # minimum mask area in pixels
  aspect_ratio: [0.2, 5.0]
  border_touch_max_pct: 0.15     # reject masks with >15% border contact
  depth:
    z_min_m: 0.2                 # minimum depth (meters)
    z_max_m: 8.0                 # maximum depth (meters)
    valid_min_pct: 0.10          # min valid depth pixel fraction
    sigma_max_m: 0.50            # max depth spread
```

---

## Staging & Top-K

Controls how masks are prioritized before CLIP encoding:

```yaml
staging:
  topk_preclip: 15               # max masks sent to CLIP per frame
  crop_pad_px: 6                 # padding around mask crops
  clip_input: 224                # CLIP input resolution

  # Priority weights
  w_coverage: 1.0
  w_border_fraction: -1.0
  w_depth_valid: 1.0
  w_depth_spread: -0.5
```

---

## Association

Controls how new observations are matched to existing objects:

```yaml
assoc:
  cos_min: 0.90                  # minimum cosine similarity for match
  gate_dist_base_m: 0.50         # 3D distance gate (meters)
  gate_reproj_px: 60             # reprojection distance gate (pixels)
  nearest_m_for_cos: 8           # compare cosine against K nearest by distance
  use_embeddings: true           # use CLIP embeddings for matching
  fallback_all_when_empty: true  # fallback to all WM objects if no nearby ones
```

---

## Object Promotion

Controls when proto-objects become confirmed:

```yaml
object:
  proto_ttl_s: 10.0              # seconds before unconfirmed proto expires
  promote_hits: 2                # observations needed to promote
  stability_promote: 0.55        # minimum stability score
  require_view_bins: 1           # minimum viewpoint directions
  stab_k: 0.45                   # stability update factor
  miss_decay: 0.5                # stability decay on missed frames
```

| Criterion | Config Key | Default |
|-----------|-----------|---------|
| Observation count | `promote_hits` | ≥ 2 |
| Stability score | `stability_promote` | ≥ 0.55 |
| View diversity | `require_view_bins` | ≥ 1 viewpoint |

---

## Sweep Cache & Spatial Grid

Controls the spatial indexing used for efficient neighbor lookups:

```yaml
sweep_cache:
  grid_size_m: 0.25              # cell size (meters)
  per_cell_cap: 64               # max object IDs per cell
  two_d: true                    # drop Z axis for indoor scenes
  yaw_bins: 12                   # 360° / 12 = 30° per bin
  pitch_bins: 5
```

---

## Vector Storage

Configure the embedding store for semantic search:

```yaml
vectors:
  enable: true
  backend: faiss                 # faiss | milvus
  dim: 512                       # CLIP ViT-B/32 embedding size
  faiss:
    index_path: model_store/faiss/index.flatip
  flush_period_s: 3.0
```

---

## API Server

```yaml
api:
  host: "0.0.0.0"
  port: 8002
```

The REST API is available at `http://localhost:8002`. See [REST API Reference](../api/rest-api.md).

---

## MCP (Model Context Protocol)

Enable the embedded MCP server to expose spatial memory to AI agents:

```yaml
mcp:
  enable: true                   # mounts at /mcp/ on the API server
```

When enabled, the MCP SSE endpoint is available at `http://localhost:8002/mcp/sse`. See [REST API — MCP](../api/rest-api.md#mcp-model-context-protocol) for available tools.

---

## Visualization

```yaml
visualization:
  enable: true
  host: 0.0.0.0
  port: 8083                     # WebSocket port for 3D frontend

  depth:
    min_m: 0.1
    max_m: 3.5                   # max depth for point cloud

  tsdf:
    enable: true
    voxel_size: 0.01             # 1cm voxels
    sdf_trunc: 0.04              # truncation distance
    max_depth_m: 3.5
    extract_every_n: 30          # extract mesh every N frames

  objects:
    push_interval_ms: 200        # push WM objects to clients
    include_proto: true          # include unconfirmed objects

  analytics:
    push_interval_ms: 1000       # analytics push cadence
    full_sync_interval_s: 30     # full history re-send interval
```

The 3D visualization frontend connects via WebSocket at `ws://localhost:8083/ws`. See [WebSocket API](../api/websocket.md).

---

## Analytics

```yaml
analytics:
  enable: true                   # enable runtime analytics buffers
  retention_s: 3600              # Tier 2 history retention (1 hour)
  buffer_frames: 300             # Tier 1 per-frame ring buffer size
```

When enabled, analytics are available via `GET /stats/analytics` and pushed to visualization clients.

---

## SLAM (On-Device)

Settings for handling SLAM-corrected poses from Calabi Lens (on-device RTABMap):

```yaml
slam:
  log_pose_source: true
  accept_pose_corrections: true     # accept loop closure corrections
  correct_working_memory: true      # update WM positions on correction
```

---

## Logging

```yaml
logging:
  periodic_summary: true
  summary_interval_s: 10.0
```

---

## Next Steps

- [Architecture](../concepts/architecture.md) — Understand the system design
- [REST API](../api/rest-api.md) — API reference
- [Benchmarks](../benchmarks.md) — Performance data per backend
