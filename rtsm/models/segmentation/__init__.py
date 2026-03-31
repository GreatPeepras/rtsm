"""
Segmentation module with swappable backends.

Usage:
    from rtsm.models.segmentation import get_segmenter, SegmentationResult

    # Create segmenter from config
    segmenter = get_segmenter(cfg)

    # Run segmentation
    result = segmenter.segment(pil_image)

    # Access results
    print(f"Found {result.count} objects")
    if result.has_masks:
        masks = result.masks  # [N, H, W] bool tensor
    if result.labels:
        print(f"Labels: {result.labels}")
"""
from __future__ import annotations
from typing import Dict, Any, Optional
import logging

from rtsm.models.segmentation.base import SegmentationAdapter, SegmentationResult

logger = logging.getLogger(__name__)

# Registry of available backends
_BACKENDS = {}


def register_backend(name: str):
    """Decorator to register a segmentation backend."""
    def decorator(cls):
        _BACKENDS[name] = cls
        return cls
    return decorator


def get_segmenter(cfg: Dict[str, Any]) -> SegmentationAdapter:
    """
    Factory function to create a segmenter from config.

    Config format:
        segmentation:
          backend: fastsam | yoloe | dual
          fastsam:
            model_path: model_store/fastsam/FastSAM-x.pt
            ...
          yoloe:
            model_path: model_store/yolo/yoloe-26s-seg.pt
            ...
          dual:
            iou_confirm_threshold: 0.40
            ...

    Args:
        cfg: Full RTSM config dict

    Returns:
        SegmentationAdapter instance
    """
    seg_cfg = cfg.get("segmentation", {})
    backend = seg_cfg.get("backend", "fastsam")

    logger.info(f"Creating segmenter: backend={backend}")

    if backend == "fastsam":
        return _create_fastsam(cfg, seg_cfg)
    elif backend == "yoloe":
        return _create_yoloe(cfg, seg_cfg)
    elif backend == "dual":
        return _create_dual(cfg, seg_cfg)
    else:
        raise ValueError(
            f"Unknown segmentation backend: {backend}. "
            f"Available: fastsam, yoloe, dual"
        )


def _create_fastsam(cfg: Dict[str, Any], seg_cfg: Dict[str, Any]) -> SegmentationAdapter:
    """Create FastSAM segmenter from config."""
    from rtsm.models.segmentation.fastsam_segmenter import FastSAMSegmenter

    fastsam_cfg = seg_cfg.get("fastsam", {})

    return FastSAMSegmenter(
        model_path=fastsam_cfg.get("model_path", "model_store/fastsam/FastSAM-x.pt"),
        device=fastsam_cfg.get("device", "cuda"),
        imgsz=fastsam_cfg.get("imgsz", 640),
        conf=fastsam_cfg.get("conf", 0.4),
        iou=fastsam_cfg.get("iou", 0.9),
        retina_masks=seg_cfg.get("retina_masks", True),
    )


def _create_yoloe(cfg: Dict[str, Any], seg_cfg: Dict[str, Any]) -> SegmentationAdapter:
    """Create YOLOE segmenter from config."""
    from rtsm.models.segmentation.yoloe_segmenter import YOLOESegmenter

    yoloe_cfg = seg_cfg.get("yoloe", {})

    return YOLOESegmenter(
        model_path=yoloe_cfg.get("model_path", "model_store/yolo/yoloe-26s-seg.pt"),
        device=yoloe_cfg.get("device", "cuda"),
        imgsz=yoloe_cfg.get("imgsz", 640),
        conf=yoloe_cfg.get("conf", 0.25),
        iou=yoloe_cfg.get("iou", 0.7),
        default_vocab=yoloe_cfg.get("vocab", None),
        retina_masks=seg_cfg.get("retina_masks", True),
    )


def _create_dual(cfg: Dict[str, Any], seg_cfg: Dict[str, Any]) -> SegmentationAdapter:
    """Create dual-confirmation segmenter (FastSAM + YOLOE) from config."""
    from rtsm.models.segmentation.dual_segmenter import DualConfirmationSegmenter

    dual_cfg = seg_cfg.get("dual", {})

    # Create child segmenters
    fastsam = _create_fastsam(cfg, seg_cfg)
    yoloe = _create_yoloe(cfg, seg_cfg)

    return DualConfirmationSegmenter(
        fastsam=fastsam,
        yoloe=yoloe,
        iou_confirm_threshold=dual_cfg.get("iou_confirm_threshold", 0.40),
        prefer_mask=dual_cfg.get("prefer_mask", "fastsam"),
    )


# Re-export for convenience
__all__ = [
    "SegmentationAdapter",
    "SegmentationResult",
    "get_segmenter",
]
