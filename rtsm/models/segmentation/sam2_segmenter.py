"""
SAM2 segmentation backend.

Class-agnostic "segment everything" using SAM2's automatic mask generator.
Apache 2.0 licensed — no AGPL dependency.

SAM2 provides:
  - Instance masks at native image resolution
  - Predicted IoU scores per mask
  - Bounding boxes derived from masks
  - No labels (class-agnostic, like FastSAM)
"""
from __future__ import annotations
from typing import List, Optional
from PIL import Image
import torch
import numpy as np
import logging

from rtsm.models.segmentation.base import SegmentationAdapter, SegmentationResult

logger = logging.getLogger(__name__)


class SAM2Segmenter(SegmentationAdapter):
    """
    Class-agnostic segmentation using SAM2 automatic mask generation.

    This is the Apache 2.0-licensed replacement for FastSAM.  It segments
    every object in the image without needing a vocabulary or text prompt.

    Model variants (SAM 2.1, Hiera backbone):
    - facebook/sam2.1-hiera-tiny    — 38.9M params, fastest
    - facebook/sam2.1-hiera-small   — 46M params, good quality/speed trade-off
    - facebook/sam2.1-hiera-base-plus — 80.8M params
    - facebook/sam2.1-hiera-large   — 224.4M params, best quality
    """

    def __init__(
        self,
        model_id: str = "facebook/sam2.1-hiera-small",
        device: str = "cuda",
        points_per_side: int = 32,
        points_per_batch: int = 64,
        pred_iou_thresh: float = 0.7,
        stability_score_thresh: float = 0.92,
        box_nms_thresh: float = 0.7,
        min_mask_region_area: int = 100,
    ):
        self._model_id = model_id
        self._device = device
        self._points_per_side = points_per_side
        self._points_per_batch = points_per_batch
        self._pred_iou_thresh = pred_iou_thresh
        self._stability_score_thresh = stability_score_thresh
        self._box_nms_thresh = box_nms_thresh
        self._min_mask_region_area = min_mask_region_area

        self._generator = None
        self._predictor = None  # exposed for sharing with GDinoSAM2Segmenter

        logger.info(
            f"SAM2Segmenter initialized: model={model_id}, device={device}, "
            f"points_per_side={points_per_side}"
        )

    def _load_model(self):
        """Lazy-load SAM2 model and create automatic mask generator."""
        if self._generator is not None:
            return

        try:
            from sam2.sam2_image_predictor import SAM2ImagePredictor
            from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
        except ImportError:
            raise ImportError(
                "SAM2 requires the 'sam2' package. "
                "Install with: pip install sam2"
            )

        logger.info(f"Loading SAM2 model: {self._model_id} ...")
        self._predictor = SAM2ImagePredictor.from_pretrained(
            self._model_id, device=self._device,
        )
        self._generator = SAM2AutomaticMaskGenerator(
            model=self._predictor.model,
            points_per_side=self._points_per_side,
            points_per_batch=self._points_per_batch,
            pred_iou_thresh=self._pred_iou_thresh,
            stability_score_thresh=self._stability_score_thresh,
            box_nms_thresh=self._box_nms_thresh,
            min_mask_region_area=self._min_mask_region_area,
        )
        logger.info(f"SAM2 model loaded: {self._model_id}")

    def segment(
        self,
        image: Image.Image,
        vocab: Optional[List[str]] = None,
    ) -> SegmentationResult:
        """
        Segment all objects in the image (class-agnostic).

        Args:
            image: PIL RGB image
            vocab: Ignored (SAM2 auto-mask is class-agnostic)

        Returns:
            SegmentationResult with masks, boxes, and IoU scores
        """
        self._load_model()

        np_image = np.array(image)  # HWC uint8

        anns = self._generator.generate(np_image)

        if not anns:
            return self._empty_result(image.size)

        # Sort by area descending (largest masks first, consistent with FastSAM)
        anns = sorted(anns, key=lambda a: a["area"], reverse=True)

        # Extract masks: each ann["segmentation"] is a bool ndarray [H, W]
        masks = torch.from_numpy(
            np.stack([a["segmentation"] for a in anns])
        ).bool()  # [N, H, W]

        # Extract IoU scores
        scores = torch.tensor(
            [a["predicted_iou"] for a in anns], dtype=torch.float32
        )

        # Convert bboxes from xywh to xyxy
        boxes = torch.tensor(
            [
                [b[0], b[1], b[0] + b[2], b[1] + b[3]]
                for b in (a["bbox"] for a in anns)
            ],
            dtype=torch.float32,
        )

        return SegmentationResult(
            masks=masks,
            boxes=boxes,
            scores=scores,
        )

    def warmup(self) -> None:
        """Eagerly load SAM2 model (downloads from HuggingFace if needed)."""
        self._load_model()

    def _empty_result(self, image_size: tuple) -> SegmentationResult:
        """Return empty result for no detections."""
        W, H = image_size
        return SegmentationResult(
            masks=torch.empty(0, H, W, dtype=torch.bool),
            boxes=torch.empty(0, 4),
            scores=torch.empty(0),
        )

    def close(self) -> None:
        """Release model resources."""
        if self._generator is not None:
            del self._generator
            self._generator = None
        if self._predictor is not None:
            del self._predictor
            self._predictor = None
        torch.cuda.empty_cache()

    @property
    def name(self) -> str:
        return "sam2"

    @property
    def supports_vocab(self) -> bool:
        return False

    @property
    def provides_embeddings(self) -> bool:
        return False

    @property
    def provides_masks(self) -> bool:
        return True
