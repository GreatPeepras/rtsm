# REST API Reference

RTSM exposes a REST API for querying objects, system state, and runtime analytics.

**Base URL**: `http://localhost:8002`

---

## Health

### Liveness

```http
GET /healthz
```

**Response**:

```json
{"status": "ok"}
```

### Readiness

```http
GET /readyz
```

**Response**:

```json
{"status": "ready"}
```

---

## Objects

### List All Objects

```http
GET /objects
```

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `include_vectors` | bool | Include embedding vectors (default: false) |

**Response**:

```json
{
  "count": 62,
  "objects": [
    {
      "id": "a3f2c1d8",
      "xyz_world": [1.2, 0.4, 2.1],
      "created_wall_utc": 1712345678.0,
      "stability": 0.82,
      "hits": 15,
      "confirmed": true,
      "label_primary": "backpack",
      "view_bins": 3,
      "last_seen_mono": 1712345700.0
    }
  ]
}
```

---

### Get Object by ID

```http
GET /objects/{oid}
```

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `include_vectors` | bool | Include embedding vectors (default: false) |

**Response**:

```json
{
  "id": "a3f2c1d8",
  "xyz_world": [1.2, 0.4, 2.1],
  "stability": 0.82,
  "hits": 15,
  "confirmed": true,
  "label_primary": "backpack",
  "label_scores": {"backpack": 0.87, "bag": 0.45, "suitcase": 0.12},
  "view_bins": 3,
  "cov_world": [0.001, 0.002, 0.001],
  "last_seen_wall_utc": 1712345700.0
}
```

---

### Object Debug Info

```http
GET /objects/{oid}/debug
```

Returns detailed diagnostic information: position with covariance, tracking state, label scores, view diversity, gallery size, and timestamps.

---

### Object Snapshots

```http
GET /objects/{oid}/snapshots
```

Returns base64-encoded JPEG image crops (most recent first).

```http
GET /objects/{oid}/snapshots/{index}/image
```

Returns raw JPEG image for a specific snapshot index.

---

## Search

### Semantic Search

```http
GET /search/semantic?query={text}&top_k={n}&threshold={t}
```

Encodes the query text with CLIP and performs KNN search against all object embeddings.

**Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Natural language query |
| `top_k` | int | 10 | Maximum results |
| `threshold` | float | 0.2 | Minimum cosine similarity |

**Example**:

```bash
curl "http://localhost:8002/search/semantic?query=red%20mug&top_k=5"
```

**Response**:

```json
{
  "query": "red mug",
  "results": [
    {
      "id": "b7d4e2f1",
      "score": 0.82,
      "label_hint": "mug",
      "confirmed": true,
      "xyz_world": [0.8, 0.2, 1.5]
    }
  ]
}
```

### Spatial Search

```http
GET /search/spatial?x={x}&y={y}&z={z}&radius_m={r}
```

Finds objects within a radius of a 3D point in world coordinates.

**Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | float | required | X coordinate (meters, world frame) |
| `y` | float | required | Y coordinate (meters, world frame) |
| `z` | float | required | Z coordinate (meters, world frame) |
| `radius_m` | float | 1.0 | Search radius in meters |

**Example**:

```bash
curl "http://localhost:8002/search/spatial?x=1.0&y=0.5&z=2.0&radius_m=0.5"
```

**Response**:

```json
{
  "center": [1.0, 0.5, 2.0],
  "radius_m": 0.5,
  "results": [
    {
      "id": "b7d4e2f1",
      "distance_m": 0.23,
      "label_primary": "mug",
      "xyz_world": [1.1, 0.4, 2.1],
      "confirmed": true,
      "stability": 0.82
    }
  ]
}
```

Results are sorted by distance (nearest first). Returns `503` if the proximity index is not available.

---

## Statistics

### Basic Stats

```http
GET /stats
```

**Response**:

```json
{
  "objects": 111,
  "confirmed": 62,
  "avg_hits": 4.2,
  "upserts_total": 28,
  "ingest_q": 0
}
```

### Detailed Stats

```http
GET /stats/detailed
```

Returns stats from all components: working memory, sweep cache, frame window, visualization registry.

---

### Runtime Analytics

```http
GET /stats/analytics
```

Returns real-time pipeline analytics with per-second time-series history (up to 1 hour).

**Response**:

```json
{
  "latency": {
    "aggregate": {
      "frame_count": 247,
      "processing_hz": 2.8,
      "input_hz": 4.7,
      "t_total": {"mean": 0.362, "p50": 0.340, "p95": 0.612, "max": 1.2},
      "t_segmentation": {"mean": 0.117, "p50": 0.110, "p95": 0.116, "max": 0.235},
      "t_heuristics": {"mean": 0.135, "p50": 0.130, "p95": 0.196, "max": 0.25},
      "t_scoring": {"mean": 0.0, "p50": 0.0, "p95": 0.0, "max": 0.001},
      "t_clip": {"mean": 0.075, "p50": 0.073, "p95": 0.092, "max": 0.1},
      "t_association": {"mean": 0.005, "p50": 0.005, "p95": 0.008, "max": 0.01},
      "mean_masks_in": 28.1,
      "mean_candidates": 13.9,
      "mask_survival_rate": 0.49
    },
    "hourly": [
      {"wall_ts": 1712345678.0, "input_hz": 4.7, "processing_hz": 2.8, "t_total_ms": 362, "queue_drops": 0, "assoc_matched": 5, "assoc_created": 3, "wm_confirmed": 62, "wm_total": 111}
    ]
  },
  "segmentation": {
    "aggregate": {
      "backend": "dual",
      "dual_rate": 0.23,
      "fastsam_only_rate": 0.61,
      "yoloe_only_rate": 0.16,
      "mean_fastsam_raw": 24.0,
      "mean_yoloe_raw": 11.2,
      "staged_survival_rate": 0.61
    },
    "hourly": [
      {"wall_ts": 1712345678.0, "dual_rate": 0.23, "fastsam_only_rate": 0.61, "yoloe_only_rate": 0.16}
    ]
  }
}
```

Returns `503` if analytics is disabled (`analytics.enable: false` in config).

---

## System Control

### Reset

```http
POST /reset
```

Clears working memory, sweep cache, frame window, visualization registry, TSDF state, and analytics buffers. Models stay loaded.

**Response**:

```json
{
  "status": "ok",
  "reset_time_utc": 1712345678.0,
  "cleared": {
    "working_memory": {"objects_cleared": 111},
    "sweep_cache": true,
    "visualization": {"keyframes_cleared": 45, "tsdf_reset": true, "clients_notified": true},
    "seg_analytics": true,
    "latency_analytics": true
  }
}
```

---

## Prometheus Metrics

```http
GET /metrics
```

Exposes Prometheus-format metrics for external monitoring:

| Metric | Type | Description |
|--------|------|-------------|
| `rtsm_working_objects` | gauge | Total objects in working memory |
| `rtsm_confirmed_objects` | gauge | Confirmed objects |
| `rtsm_upserts_total` | gauge | Total LTM upserts emitted |

---

## MCP (Model Context Protocol)

When `mcp.enable: true` in `config/rtsm.yaml`, RTSM mounts an MCP server on the API:

```
SSE endpoint: http://localhost:8002/mcp/sse
```

This exposes RTSM's spatial memory as tools for AI agents (Claude, GPT, local LLMs). Agents can query objects, search by text or location, and read world state through the standard MCP protocol.

Enable in config:

```yaml
mcp:
  enable: true
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `rtsm.semantic_query` | Search spatial memory by natural language (e.g., "where is the coffee mug?"). Returns objects with 3D positions and similarity scores. |
| `rtsm.spatial_query` | Find objects within a radius of a 3D point in world coordinates. |
| `rtsm.relational_query` | Find objects near a named reference object (e.g., "what is next to the laptop?"). |
| `rtsm.list_objects` | List all objects currently tracked in spatial memory with positions and labels. |
| `rtsm.get_object` | Get full details for a specific object by ID. |
| `rtsm.status` | Get system status: health, object counts, and pipeline statistics. |

#### Tool Parameters

**`rtsm.semantic_query`**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Natural language search query |
| `top_k` | int | 5 | Max results to return |
| `threshold` | float | 0.2 | Min cosine similarity (0–1) |

**`rtsm.spatial_query`**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | float | required | X coordinate (meters) |
| `y` | float | required | Y coordinate (meters) |
| `z` | float | required | Z coordinate (meters) |
| `radius_m` | float | 1.0 | Search radius in meters |

**`rtsm.relational_query`**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Name of reference object to search around |
| `radius_m` | float | 1.0 | Search radius in meters |

**`rtsm.get_object`**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `object_id` | string | required | Object ID |
| `include_vectors` | bool | false | Include embedding vectors |

A standalone stdio bridge (`rtsm-mcp`) is also available for direct integration with agent frameworks.

---

## Error Responses

```json
{
  "detail": "Object a3f2c1d8 not found"
}
```

| Status | Meaning |
|--------|---------|
| 404 | Object not found |
| 503 | Service unavailable (analytics disabled, search not configured) |
| 500 | Internal server error |

---

## Next Steps

- [WebSocket API](websocket.md) — Real-time mesh, object, and analytics streaming
- [Quick Start](../getting-started/quick-start.md) — Try these endpoints
