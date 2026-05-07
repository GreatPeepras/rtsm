from __future__ import annotations
import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", message=".*allow_in_graph is deprecated.*", category=FutureWarning)

# ── GPU-dependent imports (require rtsm[gpu]) ──
_GPU_AVAILABLE = True
_GPU_IMPORT_ERROR = None
try:
    from rtsm.core.pipeline import Pipeline
    from rtsm.models.clip.adapter import CLIPAdapter
    from rtsm.models.clip.vocab_classifier import ClipVocabClassifier
except ImportError as e:
    _GPU_AVAILABLE = False
    _GPU_IMPORT_ERROR = str(e)
    Pipeline = None  # type: ignore[assignment,misc]
    CLIPAdapter = None  # type: ignore[assignment,misc]
    ClipVocabClassifier = None  # type: ignore[assignment,misc]

# ── Core imports (always available) ──
from rtsm.models.segmentation import get_segmenter
from rtsm.stores.working_memory import WorkingMemory
from rtsm.stores.frozen_wm import FrozenWorkingMemory
from rtsm.stores.proximity_index import ProximityIndex, GridSpec
from rtsm.core.association import Associator
from rtsm.core.ingest_gate import IngestGate
from rtsm.stores.sweep_cache import SweepCache
from rtsm.io.ingest_queue import IngestQueue
from rtsm.io.zeromq import ZeroMQSubscriber
from rtsm.io.websocket import WebSocketReceiver
from rtsm.utils.net import print_server_addresses, get_local_ipv4_addresses
from rtsm.stores.sweep_policy import SweepPolicy
from rtsm.api.server import create_app, start_server, ResetComponents
from rtsm.cfg import load_config, cfg_path

import argparse
import sys
import threading
import logging
from pathlib import Path

# Configure logging at module level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
# Reduce verbosity of noisy subsystems
logging.getLogger("rtsm.stores.proximity_index").setLevel(logging.WARNING)
logging.getLogger("rtsm.core.association").setLevel(logging.INFO)

logger = logging.getLogger(__name__)


def _find_static_dir() -> str | None:
    """Locate the built frontend static directory.

    Search order (dev build wins so you never need to copy):
      1. demo/dist/ (dev, after npm run build)
      2. rtsm/static/ (packaged release)
    """
    dev_dist = Path("demo/dist")
    if dev_dist.is_dir() and (dev_dist / "index.html").is_file():
        return str(dev_dist.resolve())
    pkg_static = Path(__file__).parent / "static"
    if pkg_static.is_dir() and (pkg_static / "index.html").is_file():
        return str(pkg_static)
    return None


def main():
    # Dispatch 'demo' subcommand before argparse (preserves backward compat)
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        from rtsm.demo import run_demo
        run_demo(sys.argv[2:])
        return

    parser = argparse.ArgumentParser(description="RTSM - Real-Time Spatio-Semantic Memory")
    parser.add_argument("--replay", type=str, default=None, metavar="DIR",
                        help="Replay a recorded session from DIR at original rate")
    parser.add_argument("--record", type=str, default=None, metavar="DIR",
                        help="Record raw WebSocket session to DIR")
    parser.add_argument("--replay-speed", type=float, default=1.0,
                        help="Replay speed multiplier (<1 = slower, e.g. 0.5 = half speed)")
    parser.add_argument("--record-only", action="store_true",
                        help="Record without running pipeline (no GPU needed)")
    # PATCHED 20260430: serve-only mode
    parser.add_argument("--serve", action="store_true",
                        help="Serve API from persisted FAISS state without running the pipeline (fast-boot, query-only)")
    args = parser.parse_args()


    # PATCHED 20260430: serve-only mode
    # Fast-boot path: load FAISS sidecars and serve /search/* without any pipeline.
    # Mutually exclusive with --replay and --record.
    if getattr(args, "serve", False):
        if args.replay or args.record:
            parser.error("--serve is mutually exclusive with --replay/--record")

        import threading as _threading
        logger.info("[run] SERVE-ONLY MODE — loading persisted state, pipeline disabled")

        cfg = load_config("rtsm.yaml")
        logger.info(f"Configuration loaded from {cfg_path('rtsm.yaml')}")

        # Minimal state: proximity index + empty WM + FaissClient (auto-loads disk)
        scfg = cfg.get("sweep_cache", {})
        two_d = bool(scfg.get("two_d", True))
        io_cfg = cfg.get("io", {})
        receiver_type = str(io_cfg.get("receiver", "zeromq")).lower()
        up_axis_default = "y" if receiver_type == "websocket" else "z"
        pi_grid = GridSpec(
            cell_m=float(scfg.get("grid_size_m", 0.25)),
            use_3d=not two_d,
            up_axis=str(scfg.get("up_axis", up_axis_default)),
        )
        proximity_index = ProximityIndex(
            pi_grid,
            per_cell_cap=int(scfg.get("per_cell_cap", 64)),
            neighbors_max=int(scfg.get("neighbors_max", 128)),
        )
        # [Patch G] Load FAISS FIRST so we can resolve the meta sidecar path,
        # then hydrate a FrozenWorkingMemory from that sidecar.
        vectors = None
        meta_path = None
        vec_cfg = cfg.get("vectors", {})
        if bool(vec_cfg.get("enable", True)):
            backend = str(vec_cfg.get("backend", "faiss")).lower()
            if backend == "faiss":
                from rtsm.stores.vectors.faiss_client import FaissClient
                vectors = FaissClient(cfg)  # auto-loads sidecars from disk
                n_loaded = len(getattr(vectors, "_row_to_id", []))
                logger.info(f"[serve] FaissClient loaded {n_loaded} persisted objects")
                # Resolve meta sidecar path for FrozenWM hydration.
                # FaissClient stores its index path on one of these attributes
                # depending on version; fall back to the canonical location.
                idx_path = (
                    getattr(vectors, "_index_path", None)
                    or getattr(vectors, "index_path", None)
                    or "/mnt/rtsm-data/model_store/faiss/index.flatip"
                )
                meta_path = idx_path + ".meta.json"
            else:
                logger.warning(f"[serve] backend '{backend}' not supported in serve mode, skipping")

        if meta_path is not None:
            wm = FrozenWorkingMemory(meta_path)
            logger.info(f"[serve] FrozenWorkingMemory active with {len(wm.iter_objects())} objects")
            # PATCH II 20260501: sidecar freshness check at startup
            try:
                import os as _os, time as _time
                _stale_days = float(_os.environ.get("RTSM_SIDECAR_STALE_DAYS", "7"))
                _mtime = _os.path.getmtime(meta_path)
                _age_days = (_time.time() - _mtime) / 86400.0
                _mtime_iso = _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime(_mtime))
                _msg = (f"[serve] sidecar age={_age_days:.2f}d threshold={_stale_days:.2f}d "
                        f"mtime={_mtime_iso} path={meta_path}")
                if _age_days > _stale_days:
                    logger.warning(_msg + " STALE")
                else:
                    logger.info(_msg + " fresh")
            except OSError as _e:
                logger.error(f"[serve] sidecar freshness check failed: {_e} path={meta_path}")
        else:
            # No vectors backend ⇒ fall back to empty live WM (legacy behavior)
            wm = WorkingMemory(cfg, index=proximity_index)
            logger.info("[serve] Working memory initialized (empty, no vectors backend)")

        # PATCH IV 20260501: load CLIP adapter for /search/semantic in serve mode.
        # Mirrors replay-mode init at run.py:266. Failure is non-fatal; other
        # endpoints continue to work and /search/semantic returns 503 as before.
        clip_adapter = None
        if CLIPAdapter is not None:
            clip_cfg = cfg.get("clip", {})
            clip_model = clip_cfg.get("model", "ViT-B-16-SigLIP")
            clip_pretrained = clip_cfg.get("pretrained", "webli")
            clip_local = clip_cfg.get("local_dir", "model_store/clip")
            try:
                logger.info(f"[serve] loading CLIP ({clip_model}/{clip_pretrained}) \u2014 this takes a few seconds...")
                _t0 = _time.time()
                clip_adapter = CLIPAdapter(clip_model, clip_pretrained, clip_local,
                                           device=cfg.get("device", "cuda"))
                logger.info(f"[serve] CLIP loaded in {_time.time() - _t0:.1f}s \u2014 /search/semantic enabled")
            except Exception as e:
                logger.warning(f"[serve] CLIP load failed ({e}); /search/semantic will return 503")
                clip_adapter = None
        else:
            logger.warning("[serve] CLIPAdapter unavailable (GPU deps not installed); /search/semantic disabled")

        app = create_app(
            working_memory=wm,
            vectors=vectors,
            clip_adapter=clip_adapter,
            static_dir=_find_static_dir(),
        )
        api_cfg = cfg.get("api", {})
        host = api_cfg.get("host", "0.0.0.0")
        port = int(api_cfg.get("port", 8002))

        local_ips = get_local_ipv4_addresses()
        display_host = local_ips[0] if local_ips else "0.0.0.0"

        start_server(app, host=host, port=port)
        logger.info(f"[serve] FastAPI server started on http://{display_host}:{port}")
        logger.info("[serve] Ready. Blocking forever. Ctrl-C to exit.")

        try:
            _threading.Event().wait()
        except KeyboardInterrupt:
            logger.info("[serve] Shutdown requested")
        return
    # END PATCHED serve-only mode

    print("=" * 60)
    print("  RTSM - Real-Time Spatio-Semantic Memory")
    print("=" * 60)

    # ── Check GPU dependencies unless in record-only mode ──
    if not (args.record and args.record_only) and not _GPU_AVAILABLE:
        print(f"\nERROR: GPU dependencies not installed: {_GPU_IMPORT_ERROR}")
        print("Install with:  pip install \"rtsm[gpu]\"  or  pip install \"rtsm[all]\"")
        print("For CUDA support, add:  --extra-index-url https://download.pytorch.org/whl/cu128")
        return

    cfg = load_config("rtsm.yaml")
    logger.info(f"Configuration loaded from {cfg_path('rtsm.yaml')}")

    # ── Record-only mode: skip all heavy init, just record raw WebSocket ──
    if args.record and args.record_only:
        from rtsm.io.recorder import SessionRecorder
        recorder = SessionRecorder(output_dir=args.record, config_snapshot=cfg)

        io_cfg = cfg.get("io", {})
        ws_cfg = io_cfg.get("websocket", {})
        vis_cfg = cfg.get("visualization", {})
        ingest_q = IngestQueue(maxsize=512)

        ws_receiver = WebSocketReceiver(
            ingest_queue=ingest_q,
            host=str(ws_cfg.get("host", "0.0.0.0")),
            port=int(ws_cfg.get("port", 8765)),
            require_tracking_normal=bool(ws_cfg.get("require_tracking_normal", True)),
            keyframe_every_n=int(ws_cfg.get("keyframe_every_n", 30)),
            nonkf_min_interval_s=float(ws_cfg.get("nonkf_min_interval_s", 0.5)),
            confidence_threshold=int(ws_cfg.get("confidence_threshold", 1)),
            apply_camera_flip=bool(vis_cfg.get("apply_camera_flip", False)),
            on_raw_message=recorder.on_message,
            on_handshake_done=recorder.on_handshake,
        )
        ws_receiver.start()
        ws_port = int(ws_cfg.get("port", 8765))
        local_ips = get_local_ipv4_addresses()
        display_host = local_ips[0] if local_ips else "0.0.0.0"
        print_server_addresses(ws_port)
        logger.info(f"Record-only mode: ws://{display_host}:{ws_port}/stream -> {args.record}")
        print(f"  Recording to: {args.record}")
        print("  Press Ctrl+C to stop recording")

        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            recorder.close()
        return

    # Create segmenter from config
    segmenter = get_segmenter(cfg)
    logger.info(f"Segmentation backend created: {segmenter.name}")
    segmenter.warmup()
    logger.info(f"Segmentation models loaded and ready: {segmenter.name}")

    # ── Runtime analytics buffers (optional) ──
    from rtsm.analytics import SegAnalyticsBuffer, PipelineLatencyBuffer
    analytics_cfg = cfg.get("analytics", {})
    seg_analytics = None
    latency_analytics = None
    if analytics_cfg.get("enable", True):
        retention_s = float(analytics_cfg.get("retention_s", 3600))
        buffer_frames = int(analytics_cfg.get("buffer_frames", 300))
        seg_analytics = SegAnalyticsBuffer(max_frames=buffer_frames, retention_s=retention_s)
        latency_analytics = PipelineLatencyBuffer(max_frames=buffer_frames, retention_s=retention_s)
        logger.info(f"Runtime analytics initialized (retention={retention_s}s, buffer={buffer_frames} frames)")
    clip_cfg = cfg.get("clip", {})
    clip_model = clip_cfg.get("model", "ViT-B-32")
    clip_pretrained = clip_cfg.get("pretrained", "openai")
    clip_local = clip_cfg.get("local_dir", "model_store/clip")
    clip = CLIPAdapter(clip_model, clip_pretrained, clip_local, device=cfg.get("device","cuda"))
    logger.info(f"CLIP model loaded: {clip_model} ({clip_pretrained})")
    # Determine world-frame up axis from receiver type (ARKit=Y-up, D435i/ROS=Z-up)
    io_cfg = cfg.get("io", {})
    receiver_type = str(io_cfg.get("receiver", "zeromq")).lower()
    up_axis_default = "y" if receiver_type == "websocket" else "z"

    # Proximity index config
    scfg = cfg.get("sweep_cache", {})
    two_d = bool(scfg.get("two_d", True))
    cell_m = float(scfg.get("grid_size_m", 0.25))
    per_cell_cap = int(scfg.get("per_cell_cap", 64))
    neighbors_max = int(scfg.get("neighbors_max", 128))
    up_axis = str(scfg.get("up_axis", up_axis_default))
    pi_grid = GridSpec(cell_m=cell_m, use_3d=not two_d, up_axis=up_axis)
    proximity_index = ProximityIndex(pi_grid, per_cell_cap=per_cell_cap, neighbors_max=neighbors_max)
    logger.info(f"Proximity index successfully initialized")
    wm = WorkingMemory(cfg, index=proximity_index)
    logger.info(f"Working memory successfully initialized")
    assoc = Associator(cfg)
    ingest_gate = IngestGate(cfg)
    logger.info(f"Ingest gate successfully initialized")
    vocab_clf = ClipVocabClassifier(clip.artifacts.model, clip.artifacts.tokenizer, clip.artifacts.preprocess, str(cfg_path("clip/vocab.yaml")), device=cfg.get("device","cuda"))
    logger.info(f"CLIP vocabulary classifier successfully initialized")
    vec_cfg = cfg.get("vectors", {})
    backend = str(vec_cfg.get("backend", "faiss")).lower()
    vectors = None
    if bool(vec_cfg.get("enable", True)):
        if backend == "milvus":
            from rtsm.stores.vectors.milvus_client import MilvusClient
            vectors = MilvusClient(cfg)
        else:
            from rtsm.stores.vectors.faiss_client import FaissClient
            vectors = FaissClient(cfg)
            logger.info(f"Faiss vectors successfully initialized")

    # Prepare ingest plumbing
    # Note: Intrinsics are now dynamic per-frame from camera.rgbd topic
    ingest_q = IngestQueue(maxsize=512)
    sweep_cache = SweepCache(
        grid_size_m=float(cfg.get("sweep_cache", {}).get("grid_size_m", 0.25)),
        per_cell_cap=int(cfg.get("sweep_cache", {}).get("per_cell_cap", 64)),
        neighbors_max=int(cfg.get("sweep_cache", {}).get("neighbors_max", 128)),
        two_d=bool(cfg.get("sweep_cache", {}).get("two_d", True)),
        yaw_bins=int(cfg.get("sweep_cache", {}).get("yaw_bins", 12)),
        pitch_bins=int(cfg.get("sweep_cache", {}).get("pitch_bins", 5)),
        pitch_deg=float(cfg.get("sweep_cache", {}).get("pitch_deg", 60.0)),
        look_lru_keep=int(cfg.get("sweep_cache", {}).get("look_lru_keep", 8)),
        up_axis=up_axis,
    )
    logger.info(f"Sweep cache successfully initialized")

    # ---------------- Visualization Server (optional) ----------------
    vis_cfg = cfg.get("visualization", {})
    vis_server = None
    if vis_cfg.get("enable", True):
        from rtsm.visualization.server import VisualizationServer
        vis_server = VisualizationServer(
            cfg=cfg,
            working_memory=wm,
            host=vis_cfg.get("host", "0.0.0.0"),
            port=int(vis_cfg.get("port", 8081)),
            seg_analytics=seg_analytics,
            latency_analytics=latency_analytics,
        )
        logger.info("Visualization server initialized")

    # Resolve display IP (use real network IP instead of 0.0.0.0)
    local_ips = get_local_ipv4_addresses()
    display_host = local_ips[0] if local_ips else "0.0.0.0"

    # ---------------- Receiver (Replay, WebSocket, or ZMQ) ----------------
    units_cfg = cfg.get("units", {})
    ws_cfg = io_cfg.get("websocket", {})
    recorder = None

    # Will be set to FrameWindow or None depending on receiver
    frame_window_for_reset = None

    if args.replay:
        # Replay mode: feed recorded session through the pipeline
        from rtsm.io.replayer import ReplayReceiver
        replay_receiver = ReplayReceiver(
            recording_dir=args.replay,
            ingest_queue=ingest_q,
            require_tracking_normal=bool(ws_cfg.get("require_tracking_normal", True)),
            keyframe_every_n=int(ws_cfg.get("keyframe_every_n", 30)),
            nonkf_min_interval_s=float(ws_cfg.get("nonkf_min_interval_s", 0.5)),
            confidence_threshold=int(ws_cfg.get("confidence_threshold", 1)),
            apply_camera_flip=bool(vis_cfg.get("apply_camera_flip", False)),
            on_keyframe=vis_server.handle_frame_packet if vis_server else None,
            on_camera_frame=vis_server.broadcast_camera_frame if vis_server else None,
            on_pose_corrections=vis_server.handle_kf_pose_update if vis_server else None,
            on_pose_corrections_batch=vis_server.handle_pose_corrections_batch if vis_server else None,
            latency_analytics=latency_analytics,
            replay_speed=args.replay_speed,
        )
        replay_receiver.start()
        logger.info(f"Replay receiver started from {args.replay} (speed={args.replay_speed}x)")

    elif receiver_type == "websocket":
        # Optional: attach recorder if --record is set
        if args.record:
            from rtsm.io.recorder import SessionRecorder
            recorder = SessionRecorder(output_dir=args.record, config_snapshot=cfg)

        ws_receiver = WebSocketReceiver(
            ingest_queue=ingest_q,
            host=str(ws_cfg.get("host", "0.0.0.0")),
            port=int(ws_cfg.get("port", 8765)),
            require_tracking_normal=bool(ws_cfg.get("require_tracking_normal", True)),
            keyframe_every_n=int(ws_cfg.get("keyframe_every_n", 30)),
            nonkf_min_interval_s=float(ws_cfg.get("nonkf_min_interval_s", 0.5)),
            confidence_threshold=int(ws_cfg.get("confidence_threshold", 1)),
            apply_camera_flip=bool(vis_cfg.get("apply_camera_flip", False)),
            on_keyframe=vis_server.handle_frame_packet if vis_server else None,
            on_camera_frame=vis_server.broadcast_camera_frame if vis_server else None,
            on_pose_corrections=vis_server.handle_kf_pose_update if vis_server else None,
            on_pose_corrections_batch=vis_server.handle_pose_corrections_batch if vis_server else None,
            on_raw_message=recorder.on_message if recorder else None,
            on_handshake_done=recorder.on_handshake if recorder else None,
            latency_analytics=latency_analytics,
        )
        ws_receiver.start()
        ws_port = int(ws_cfg.get("port", 8765))
        print_server_addresses(ws_port)
        logger.info(f"WebSocket receiver started on ws://{display_host}:{ws_port}/stream")
        if recorder:
            logger.info(f"Recording to {args.record}")

    elif receiver_type == "zeromq":
        sub = ZeroMQSubscriber(
            camera_endpoint=io_cfg.get("camera_endpoint", "tcp://127.0.0.1:5555"),
            rtabmap_endpoint=io_cfg.get("rtabmap_endpoint", "tcp://127.0.0.1:6000"),
            ingest_queue=ingest_q,
            depth_m_per_unit=float(units_cfg.get("depth_m_per_unit", 0.001)),
            pose_m_per_unit=float(units_cfg.get("pose_m_per_unit", 1.0)),
            on_kf_packet=vis_server.handle_kf_packet if vis_server else None,
            on_kf_pose_update=vis_server.handle_kf_pose_update if vis_server else None,
            latency_analytics=latency_analytics,
        )
        t = threading.Thread(target=sub.run_forever, daemon=True)
        t.start()
        logger.info(f"ZeroMQ dual-socket subscriber started (camera + RTABMap)")
        frame_window_for_reset = sub.fw

    else:
        raise ValueError(
            f"Unknown io.receiver: {receiver_type!r}. Choose 'zeromq' or 'websocket'."
        )

    # Visualization tasks start via API server lifespan (start_tasks())
    if vis_server:
        logger.info("Visualization server initialized (tasks start with API server)")

    pipe = Pipeline(
        cfg=cfg,
        segmenter=segmenter,
        clip=clip,
        working_mem=wm,
        proximity_index=proximity_index,
        associator=assoc,
        ingest_gate=ingest_gate,
        vocab_clf=vocab_clf,
        vectors=vectors,
        ingest_q=ingest_q,
        sweep_cache=sweep_cache,
        seg_analytics=seg_analytics,
        latency_analytics=latency_analytics,
    )

    # ---------------- Start FastAPI control-plane ----------------
    api_cfg = cfg.get("api", {})
    host = str(api_cfg.get("host", "0.0.0.0"))
    port = int(api_cfg.get("port", 8000))

    # Components that can be reset without restarting RTSM
    reset_components = ResetComponents(
        sweep_cache=sweep_cache,
        frame_window=frame_window_for_reset,  # FrameWindow (ZMQ) or None (WebSocket)
        vis_server=vis_server,
    )

    mcp_cfg = cfg.get("mcp", {})
    mcp_enabled = bool(mcp_cfg.get("enable", False))

    # Resolve frontend static dir and viz broadcaster for single-port serving
    static_dir = _find_static_dir()
    vis_broadcaster = vis_server.broadcaster if vis_server else None
    vis_server_registry = vis_server.registry if vis_server else None

    app = create_app(
        working_memory=wm,
        clip_adapter=clip,
        vectors=vectors,
        ingest_queue=ingest_q,
        extra_stats_provider=lambda: {
            "ingest_q": ingest_q.qsize(),
        },
        reset_components=reset_components,
        seg_analytics=seg_analytics,
        latency_analytics=latency_analytics,
        mcp_enabled=mcp_enabled,
        vis_server=vis_server,
        vis_broadcaster=vis_broadcaster,
        vis_registry=vis_server_registry,
        static_dir=static_dir,
    )
    start_server(app, host=host, port=port)
    logger.info(f"FastAPI server started on http://{display_host}:{port}")
    if mcp_enabled:
        logger.info(f"MCP server (SSE) available at http://{display_host}:{port}/mcp/sse")

    print("=" * 60)
    print("  RTSM is running! Waiting for data...")
    if args.replay:
        print(f"  Receiver: Replay ({args.replay})")
    elif receiver_type == "websocket":
        ws_port = int(io_cfg.get("websocket", {}).get("port", 8765))
        print(f"  Receiver: WebSocket (ws://{display_host}:{ws_port}/stream)")
        if recorder:
            print(f"  Recording: {args.record}")
    else:
        print(f"  Receiver: ZeroMQ")
        print(f"  Camera:  {io_cfg.get('camera_endpoint', 'tcp://127.0.0.1:5555')}")
        print(f"  RTABMap: {io_cfg.get('rtabmap_endpoint', 'tcp://127.0.0.1:6000')}")
    print(f"  API:     http://{display_host}:{port}")
    if static_dir:
        print(f"  Web UI:  http://{display_host}:{port}")
    if vis_broadcaster:
        print(f"  Viz WS:  ws://{display_host}:{port}/ws")
    if mcp_enabled:
        print(f"  MCP:     http://{display_host}:{port}/mcp/sse")
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    # Auto-open browser to the web UI
    if vis_server:
        from rtsm.utils.browser import open_browser
        url = f"http://localhost:{port}"
        threading.Timer(1.5, open_browser, args=[url]).start()

    # Force-flush all confirmed objects to FAISS after replay completes.
    # Without this, most confirmed objects aren't upserted because the
    # flush timer can't keep up with the replay speed.
    if args.replay and vectors is not None:
        def _flush_after_replay():
            replay_receiver.wait()
            import time as _time
            # Wait for pipeline to drain queue + finish processing last frames
            for _ in range(120):
                if ingest_q.qsize() == 0:
                    _time.sleep(5.0)  # wait 5s after queue empty for pipeline to finish
                    break
                _time.sleep(0.5)
            ready = wm.collect_ready_for_upsert(force_all=True)
            if ready:
                try:
                    vectors.upsert_batch(ready)
                    logger.info(f"[run] Force-flushed {len(ready)} objects to vector store after replay")
                except Exception as e:
                    logger.warning(f"[run] Force flush failed: {e}")
            # Persist FAISS state to disk so it survives restart.
            try:
                index_path = cfg["vectors"]["faiss"]["index_path"]
                # PATCH H 20260501 — refuse to overwrite persisted index with empty one
                _n_current = len(getattr(vectors, "_embeddings", []) or [])
                if _n_current == 0:
                    logger.warning(
                        f"[run] FAISS save SKIPPED: in-memory index is empty; "
                        f"refusing to overwrite {index_path}"
                    )
                else:
                    vectors.save(index_path)
                    logger.info(f"[run] FAISS state saved to {index_path} ({_n_current} objects)")
            except Exception as e:
                logger.warning(f"[run] FAISS save failed: {e}")

        flush_thread = threading.Thread(target=_flush_after_replay, daemon=True, name="replay-flush")
        flush_thread.start()

    try:
        pipe.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if recorder is not None:
            recorder.close()
