![RTSM](repo_media/background.jpg)

# RTSM — Real-Time Spatio-Semantic Memory

RTSM is a real-time spatial memory system that turns RGB-D streams into a **persistent, queryable 3D object-centric world state**.

Instead of treating perception as disposable frames, RTSM maintains **stable object identities over time**, enabling robots and embodied agents to answer questions like:
- *What objects exist in this space?*
- *Where are they right now?*
- *What changed, and when?*

**[Watch Demo Video](https://youtu.be/abhXsbvOLQg)** · **[Documentation](https://calabi-inc.github.io/rtsm)**

---

## Why RTSM

Modern perception systems can detect objects, but they lack **memory**.
SLAM systems build geometry, vision models detect semantics, and language models reason abstractly—but there is no shared layer that connects **space, objects, and history**.

RTSM fills this gap by acting as an explicit **spatial memory layer**:
- SLAM provides geometry and poses
- Vision models provide object masks and semantics
- RTSM fuses them into a persistent world representation

This makes spatial state **inspectable, queryable, and reusable** across robots, agents, and applications.

---

## What RTSM Does

- Builds a live 3D map from RGB-D + pose streams
- Assigns **persistent IDs** to objects across viewpoints and time
- Stores spatial, semantic, and temporal metadata per object
- Supports semantic + spatial queries (e.g. *"red bin near dock 3"*)
- Exposes a programmatic API and real-time 3D visualizer

RTSM is **SLAM-agnostic** and designed to sit above existing perception stacks.

---

## Who This Is For

- Robotics and embodied AI researchers
- Developers building agentic or world-model-based systems
- Teams exploring persistent perception, spatial reasoning, or digital twins

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                 RTSM — Real-Time Spatio-Semantic Memory                  │
└──────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
  │  Calabi Lens     │   │   D435i + SLAM   │   │  Recorded        │
  │  (ARKit iOS)     │   │   (RTABMap)      │   │  Session         │
  └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘
           │ WebSocket            │ ZeroMQ               │ --replay
           ▼                      ▼                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  I/O Layer                                                               │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  WebSocket  │  │  ZMQ Bridge │  │   Replay     │  │  Recorder    │   │
│  │  Receiver   │  │  (sensors)  │  │  Receiver    │  │  (--record)  │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘  └──────────────┘   │
│         └────────────────┴────────────────┘                              │
│                          │                                               │
│                   ┌──────▼───────┐     ┌──────────────┐                  │
│                   │ IngestQueue  │────>│ FramePacket  │                  │
│                   │  (buffer)    │     │ (RGB,D,Pose) │                  │
│                   └──────────────┘     └──────┬───────┘                  │
│                                               │                          │
└───────────────────────────────────────────────┼──────────────────────────┘
                                                │
                          ┌─────────────────────▼───────────────────────┐
                          │              Ingest Gate                    │
                          │   (keyframe priority, sweep-based skip)     │
                          └─────────────────────┬───────────────────────┘
                                                │
┌───────────────────────────────────────────────▼──────────────────────────┐
│  Perception Pipeline                                                     │
│                                                                          │
│  ┌────────────────┐  ┌────────────────┐                                   │
│  │ Grounding DINO │  │     SAM2       │    Default: grounded_sam2          │
│  │ (detection +   │─>│ (box-prompted  │    GDINO detects → SAM2 segments   │
│  │  labels)       │  │  masks)        │    (Apache 2.0, no AGPL)           │
│  └────────────────┘  └───────┬────────┘                                   │
│                              │                                            │
│                 ▼                                                        │
│  ┌───────────────┐     ┌──────────────┐     ┌──────────────┐             │
│  │ Mask Staging  │────>│ Top-K Select │────>│ CLIP Encode  │             │
│  │ (heuristics)  │     │  (priority)  │     │(224x224 crop)│             │
│  └───────────────┘     └──────────────┘     └──────┬───────┘             │
│                                                    │                     │
│                     ┌───────────────┐        ┌─────▼────────┐            │
│                     │ Vocab Classify│<───────│  Embeddings  │            │
│                     │ (label + conf)│        │  (512-D L2)  │            │
│                     └───────┬───────┘        └──────────────┘            │
│                             │                                            │
└─────────────────────────────┼────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  Association                                                             │
│                                                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌───────────────┐               │
│  │  Proximity  │────>│  Embedding  │────>│  Score Fusion │               │
│  │   Query     │     │  Cosine Sim │     │ (match/create)│               │
│  └─────────────┘     └─────────────┘     └───────────────┘               │
│                                                                          │
└───────────────┬──────────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  Working Memory                                                          │
│                                                                          │
│  ObjectState:                                                            │
│    - id, xyz_world (3D position)                                         │
│    - emb_mean, emb_gallery (CLIP embeddings)                             │
│    - view_bins (multi-view fusion)                                       │
│    - label_scores (EWMA label confidence)                                │
│    - stability, hits, confirmed                                          │
│    - image_crops (JPEG snapshots)                                        │
│                                                                          │
│  Proto -> Confirmed (hits >= 2, stability >= 0.55, views >= 1)           │
│                                                                          │
└───────────────┬──────────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  Long-Term Memory (FAISS / Milvus)                                       │
│                                                                          │
│  Semantic Search: query(text) -> CLIP -> top-k objects                   │
│                                                                          │
└───────────────┬──────────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  API & Visualization                                                     │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐           │
│  │    REST API     │  │    WebSocket    │  │     3D Demo     │           │
│  │    /objects     │  │  point clouds   │  │    (Three.js)   │           │
│  │    /search      │  │  objects_update │  │                 │           │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘           │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- pip (or [uv](https://docs.astral.sh/uv/))
- CUDA-capable GPU (tested on RTX 3080, RTX 5090)
- **One of:**
  - iPhone with [Calabi Lens](https://github.com/calabi-inc) app (ARKit, no external SLAM needed)
  - RGB-D camera (Intel RealSense D435i) + SLAM system (RTAB-Map)
  - A recorded session (for replay — no hardware needed)

> **Tested on:** WSL2 Ubuntu 22.04 with RTAB-Map, and macOS/Windows with Calabi Lens.

### Installation

```bash
git clone https://github.com/calabi-inc/rtsm.git
cd rtsm

# Core only (API server, I/O transports — no GPU needed)
pip install .

# With GPU — permissive license (SAM2 + Grounding DINO, Apache 2.0)
pip install ".[gpu]" --extra-index-url https://download.pytorch.org/whl/cu128

# With GPU — ultralytics backends (FastSAM + YOLOE, AGPL-3.0)
pip install ".[gpu-ultralytics]" --extra-index-url https://download.pytorch.org/whl/cu128

# Everything (GPU + visualization)
pip install ".[all]" --extra-index-url https://download.pytorch.org/whl/cu128
```

> **License note:** `rtsm[gpu]` uses only Apache 2.0 / MIT dependencies. `rtsm[gpu-ultralytics]` adds the `ultralytics` package (AGPL-3.0) for FastSAM and YOLOE backends.
>
> **CUDA version:** Use `cu128` for most GPUs (RTX 3080–5090). For Blackwell-only features use `cu130`. See [PyTorch install](https://pytorch.org/get-started/locally/) for other options.

### Download Models

```bash
# Fetch default models (SAM2, Grounding DINO, CLIP)
python scripts/fetch_models.py

# Or fetch individually
python scripts/fetch_models.py --only sam2
python scripts/fetch_models.py --only gdino
python scripts/fetch_models.py --only clip

# Ultralytics models (only if you installed rtsm[gpu-ultralytics])
python scripts/fetch_models.py --only fastsam
python scripts/fetch_models.py --only yolo
```

### Run

```bash
# Live — Calabi Lens (ARKit over WebSocket)
python -m rtsm

# Live — D435i + RTAB-Map (ZeroMQ)
# Set io.receiver: zeromq in config/rtsm.yaml first
python -m rtsm

# Replay a recorded session (no device needed)
python -m rtsm --replay recordings/session1
```

RTSM will start:
- **Perception pipeline** — processing frames
- **REST API** — `http://localhost:8000`
- **Visualization WebSocket** — `ws://localhost:8081`

### Record & Replay

Record a session for offline testing and reproducible iteration:

```bash
# Record only (no GPU needed, no pipeline — works with core-only install)
python -m rtsm --record recordings/my_session --record-only

# Record while running pipeline
python -m rtsm --record recordings/my_session

# Replay at original recording rate
python -m rtsm --replay recordings/my_session
```

Recordings are self-contained directories with raw WebSocket data. Replay feeds the exact same bytes through the full decode + pipeline path, preserving all time-dependent behavior (TTL caches, throttles).

### A/B Segmentation Debug

Compare FastSAM vs YOLOE segmentation on a recorded session:

```bash
# Generate side-by-side overlays (cached — skips existing frames)
python scripts/debug_segmentation.py --recording recordings/session1

# Open the viewer
# → debug/session1/compare.html (arrow keys to navigate)
```

### API Examples

```bash
# List all objects
curl http://localhost:8000/objects

# Semantic search
curl "http://localhost:8000/search/semantic?query=red%20mug&top_k=5"

# Get system stats
curl http://localhost:8000/stats/detailed

# Runtime analytics (latency, throughput, dual confirmation rates)
curl http://localhost:8000/stats/analytics
```

---

## Configuration

See [`config/rtsm.yaml`](config/rtsm.yaml) for full configuration options:

- **Camera intrinsics** — focal length, resolution
- **I/O endpoints** — ZeroMQ addresses for camera and SLAM
- **Pipeline tuning** — mask filtering, association thresholds
- **Memory settings** — object promotion, expiry, vector store

---

## Segmentation Backends

RTSM supports multiple segmentation backends via `segmentation.backend` in `config/rtsm.yaml`:

| Backend | License | Description | Seg time* | Pipeline total* | Labels |
|---------|---------|-------------|-----------|-----------------|--------|
| `grounded_sam2` | Apache 2.0 | Grounding DINO detect + SAM2 segment | 222 ms | 510 ms | Open-vocab (text-prompted) |
| `sam2` | Apache 2.0 | SAM2 auto-mask (segment everything) | ~860 ms | ~1000 ms | None (class-agnostic) |
| `fastsam` | AGPL-3.0 | FastSAM (segment everything) | ~50 ms | ~200 ms | None (class-agnostic) |
| `yoloe` | AGPL-3.0 | YOLOE detection + segmentation | ~60 ms | ~210 ms | Open-vocab / 1200+ built-in |
| `dual` | AGPL-3.0 | FastSAM + YOLOE with IoU merge | 116 ms | 210 ms | Dual-confirmed labels |

*Mean on RTX 5090, 640x480 input. `dual` and `grounded_sam2` measured via replay benchmark; others estimated.*

**Default:** `grounded_sam2` — permissive license, open-vocabulary, no AGPL dependency.

To switch backends, edit `config/rtsm.yaml`:
```yaml
segmentation:
  backend: grounded_sam2    # or: sam2, fastsam, yoloe, dual
```

> `fastsam`, `yoloe`, and `dual` require `pip install "rtsm[gpu-ultralytics]"`.

---

## Project Structure

```
rtsm/
├── core/           # Pipeline, association, ingest gate, data models
├── models/         # SAM2, Grounding DINO, FastSAM, YOLOE, CLIP adapters
├── stores/         # Working memory, proximity index, sweep cache, vector stores
├── io/             # WebSocket + ZeroMQ receivers, recorder, replayer
├── analytics/      # Runtime analytics (latency, segmentation, congestion buffers)
├── api/            # REST API server (FastAPI)
├── visualization/  # WebSocket server, TSDF fusion, 3D demo
└── utils/          # Mask staging, transforms, helpers
config/
├── rtsm.yaml       # Main configuration (models, thresholds, I/O)
└── clip/vocab.yaml  # CLIP vocabulary
scripts/
├── fetch_models.py          # Download all models (SAM2, GDINO, CLIP, FastSAM, YOLOE)
├── debug_segmentation.py    # A/B segmentation viewer (FastSAM vs YOLOE)
└── benchmark_backends.py    # Backend comparison benchmark (generates reports/)
reports/                     # Benchmark results and comparison reports
recordings/                  # Recorded sessions for replay testing (git-lfs)
tests/                       # Unit + integration tests
```

---

## Performance

Benchmarked on RTX 5090 (32 GB), iPhone ARKit recording (162 frames, 458s indoor scene), 640x480 RGB input. Both backends run the same replay session through the identical 10-stage pipeline.

### Backend Comparison

| Metric | dual (FastSAM + YOLOE) | grounded_sam2 (GDINO + SAM2) |
|--------|------------------------|------------------------------|
| **Mean latency** | **210 ms** | **510 ms** |
| P50 latency | 170 ms | 502 ms |
| P95 latency | 509 ms | 721 ms |
| Masks/frame | 28.8 | 13.4 |
| Objects confirmed | 60 | 35 |
| Confirmation rate | 52.2% | 45.5% |
| License | AGPL-3.0 | Apache-2.0 |

> Per-stage breakdown, dual confirmation analysis, and full methodology: **[Benchmarks](https://calabi-inc.github.io/rtsm/benchmarks/)** | [`reports/backend_comparison.md`](reports/backend_comparison.md)

---

## Roadmap

- [x] Dual-confirmation segmentation (FastSAM + YOLOE)
- [x] AGPL-clean default (SAM2 + Grounding DINO, Apache 2.0)
- [x] YOLOE prompt-free (1200+ LVIS categories)
- [x] WebSocket receiver for Calabi Lens (ARKit iOS)
- [x] Record/replay system for offline testing
- [x] A/B segmentation debug tooling
- [x] Real-time analytics dashboard (Looker-style, per-stage latency, dual confirmation rates, congestion detection)
- [ ] Evaluation framework (ArUco ground truth, precision/recall metrics)
- [x] Agent architecture (MCP interface)
- [ ] More communication protocols (ROS 2, gRPC)
- [ ] LLM integration for high-level queries (agentic mode)
- [ ] Dockerization

---

## Acknowledgments

RTSM builds on excellent open-source work:

- **SAM 2** — Ravi et al., *SAM 2: Segment Anything in Images and Videos*, 2024.
  [arXiv:2408.00714](https://arxiv.org/abs/2408.00714) · [GitHub](https://github.com/facebookresearch/sam2)

- **Grounding DINO** — Liu et al., *Grounding DINO: Marrying DINO with Grounded Pre-Training for Open-Set Object Detection*, 2023.
  [arXiv:2303.05499](https://arxiv.org/abs/2303.05499) · [GitHub](https://github.com/IDEA-Research/GroundingDINO)

- **FastSAM** — Zhao et al., *Fast Segment Anything*, 2023.
  [arXiv:2306.12156](https://arxiv.org/abs/2306.12156) · [GitHub](https://github.com/CASIA-IVA-Lab/FastSAM)

- **YOLOE** — THU-MIG, *YOLOE: Real-Time Seeing Anything*, ICCV 2025.
  [GitHub](https://github.com/THU-MIG/yoloe) · [Ultralytics](https://docs.ultralytics.com/models/yoloe/)

- **CLIP** — Radford et al., *Learning Transferable Visual Models From Natural Language Supervision*, 2021.
  [arXiv:2103.00020](https://arxiv.org/abs/2103.00020) · [GitHub](https://github.com/openai/CLIP)

- **RTAB-Map** — Labbé & Michaud, *RTAB-Map as an Open-Source Lidar and Visual SLAM Library for Large-Scale and Long-Term Online Operation*, Journal of Field Robotics, 2019.
  [Paper](https://doi.org/10.1002/rob.21831) · [GitHub](https://github.com/introlab/rtabmap)

---

## Cite This

If you use RTSM in your research, please cite:

```bibtex
@software{chang2025rtsm,
  author       = {Chang, Chi Feng},
  title        = {{RTSM}: Real-Time Spatio-Semantic Memory},
  year         = {2025},
  url          = {https://github.com/calabi-inc/rtsm},
  note         = {Object-centric queryable memory for spatial AI and robotics}
}
```

---

## Community

This project is under active development. If you have questions or run into issues, feel free to open an issue — I'm happy to help.

If you find RTSM useful, please consider giving it a star! I'm also looking for design partners — reach out to [Calabi](https://github.com/calabi-team) if you're interested in collaborating.

---

## License

Apache-2.0

---

## Author

Built by [Chi Feng, Chang](https://github.com/vipipi)
