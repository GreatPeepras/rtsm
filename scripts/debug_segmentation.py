"""
A/B segmentation debugger — compare FastSAM vs YOLOE on recorded sessions.

Generates colored mask overlays for each frame and an HTML viewer for
side-by-side comparison. Skips frames that are already rendered (cache).

Usage:
    # Generate overlays (skips existing)
    python scripts/debug_segmentation.py --recording recordings/session1

    # Force re-generate all
    python scripts/debug_segmentation.py --recording recordings/session1 --force

    # Custom output directory
    python scripts/debug_segmentation.py --recording recordings/session1 --output debug/my_test

Output layout:
    debug/session1/
      fastsam/{timestamp}.jpg     colored mask overlays
      yoloe/{timestamp}.jpg       colored mask overlays
      compare/{timestamp}.jpg     side-by-side (fastsam | yoloe)
      compare.html                interactive viewer with prev/next
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import struct
import sys
import time

import cv2
import numpy as np
import torch
from PIL import Image

# Add project root to path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Mask overlay rendering ──

def _generate_colors(n: int) -> list:
    """Generate N visually distinct colors using HSV spacing."""
    colors = []
    for i in range(n):
        hue = int(180 * i / max(n, 1))  # OpenCV hue is 0-179
        hsv = np.uint8([[[hue, 200, 230]]])
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0][0]
        colors.append(tuple(int(c) for c in bgr))
    return colors


def render_overlay(
    rgb_bgr: np.ndarray,
    masks: torch.Tensor,
    labels: list[str] | None = None,
    alpha: float = 0.45,
) -> np.ndarray:
    """Draw colored mask overlays on the RGB image.

    Args:
        rgb_bgr: (H, W, 3) uint8 BGR image
        masks: (N, H, W) bool tensor
        labels: optional list of N label strings
        alpha: overlay transparency

    Returns:
        (H, W, 3) uint8 BGR image with overlays
    """
    canvas = rgb_bgr.copy()
    n = masks.shape[0] if masks is not None and masks.ndim == 3 else 0
    if n == 0:
        # No masks — draw "no detections" text
        cv2.putText(canvas, "No detections", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        return canvas

    colors = _generate_colors(n)
    overlay = canvas.copy()

    for i in range(n):
        mask_np = masks[i].numpy() if isinstance(masks[i], torch.Tensor) else masks[i]
        color = colors[i]
        overlay[mask_np] = color

    canvas = cv2.addWeighted(overlay, alpha, canvas, 1 - alpha, 0)

    # Draw labels and contours
    for i in range(n):
        mask_np = masks[i].numpy() if isinstance(masks[i], torch.Tensor) else masks[i]
        mask_u8 = mask_np.astype(np.uint8) * 255
        contours, _ = cv2.findContours(mask_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(canvas, contours, -1, colors[i], 1)

        if labels and i < len(labels) and labels[i]:
            # Place label at mask centroid
            ys, xs = np.where(mask_np)
            if len(ys) > 0:
                cy, cx = int(ys.mean()), int(xs.mean())
                label_text = labels[i]
                cv2.putText(canvas, label_text, (cx - 20, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1,
                            cv2.LINE_AA)

    # Count badge
    cv2.putText(canvas, f"{n} masks", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    return canvas


# ── Frame decoding (reuse WebSocket binary parser) ──

def decode_frame_rgb(raw_bytes: bytes) -> tuple[np.ndarray | None, str]:
    """Decode raw WebSocket binary message to BGR image + timestamp key.

    Returns (bgr_image, timestamp_key) or (None, "") on failure.
    """
    from rtsm.io.websocket import decode_rgb

    offset = 0
    n = len(raw_bytes)

    # JSON header
    if n < 4:
        return None, ""
    (json_len,) = struct.unpack_from("<I", raw_bytes, offset)
    offset += 4
    if n < offset + json_len:
        return None, ""
    header = json.loads(raw_bytes[offset:offset + json_len].decode("utf-8"))
    offset += json_len

    # RGB payload
    if n < offset + 4:
        return None, ""
    (rgb_len,) = struct.unpack_from("<I", raw_bytes, offset)
    offset += 4
    if n < offset + rgb_len:
        return None, ""
    rgb_bytes = raw_bytes[offset:offset + rgb_len]

    # Decode RGB
    rgb_fmt = header.get("rgb_format", "jpeg")
    rgb_w = int(header.get("rgb_width", 0))
    rgb_h = int(header.get("rgb_height", 0))
    bgr = decode_rgb(rgb_bytes, fmt=rgb_fmt, width=rgb_w, height=rgb_h)

    # Timestamp key for filenames
    ts_ns = header.get("timestamp_ns", 0)
    frame_id = header.get("frame_id", 0)
    ts_key = f"{ts_ns}_{frame_id}"

    return bgr, ts_key


# ── Main logic ──

def run_segmentation_debug(
    recording_dir: str,
    output_dir: str,
    force: bool = False,
    quality: int = 85,
):
    import yaml

    # Load recording index
    idx_path = os.path.join(recording_dir, "index.jsonl")
    bin_path = os.path.join(recording_dir, "messages.bin")
    if not os.path.isfile(idx_path) or not os.path.isfile(bin_path):
        logger.error(f"Recording not found: {recording_dir}")
        return

    with open(idx_path, "r") as f:
        entries = [json.loads(line) for line in f if line.strip()]
    logger.info(f"Recording: {len(entries)} frames from {recording_dir}")

    # Create output dirs
    fastsam_dir = os.path.join(output_dir, "fastsam")
    yoloe_dir = os.path.join(output_dir, "yoloe")
    compare_dir = os.path.join(output_dir, "compare")
    os.makedirs(fastsam_dir, exist_ok=True)
    os.makedirs(yoloe_dir, exist_ok=True)
    os.makedirs(compare_dir, exist_ok=True)

    # Load config for model params
    cfg_path = os.path.join(ROOT, "config", "rtsm.yaml")
    cfg = yaml.safe_load(open(cfg_path, "r"))
    seg_cfg = cfg.get("segmentation", {})

    # Lazy-init models (only when needed)
    fastsam_model = None
    yoloe_model = None

    def get_fastsam():
        nonlocal fastsam_model
        if fastsam_model is None:
            from rtsm.models.segmentation.fastsam_segmenter import FastSAMSegmenter
            fc = seg_cfg.get("fastsam", {})
            fastsam_model = FastSAMSegmenter(
                model_path=fc.get("model_path", "model_store/fastsam/FastSAM-x.pt"),
                device=fc.get("device", "cuda"),
                imgsz=fc.get("imgsz", 640),
                conf=fc.get("conf", 0.6),
                iou=fc.get("iou", 0.7),
                retina_masks=seg_cfg.get("retina_masks", True),
                max_det=fc.get("max_det", 300),
            )
            fastsam_model.warmup()
            logger.info("FastSAM model loaded")
        return fastsam_model

    def get_yoloe():
        nonlocal yoloe_model
        if yoloe_model is None:
            from rtsm.models.segmentation.yoloe_segmenter import YOLOESegmenter
            yc = seg_cfg.get("yoloe", {})
            yoloe_model = YOLOESegmenter(
                model_path=yc.get("model_path", "model_store/yolo/yoloe-26s-seg-pf.pt"),
                device=yc.get("device", "cuda"),
                imgsz=yc.get("imgsz", 640),
                conf=yc.get("conf", 0.25),
                iou=yc.get("iou", 0.5),
                retina_masks=seg_cfg.get("retina_masks", True),
                max_det=yc.get("max_det", 300),
            )
            yoloe_model.warmup()
            logger.info("YOLOE model loaded")
        return yoloe_model

    processed = 0
    skipped = 0
    t_start = time.monotonic()

    with open(bin_path, "rb") as bin_f:
        for i, entry in enumerate(entries):
            # Read raw frame
            bin_f.seek(entry["offset"])
            raw = bin_f.read(entry["length"])

            bgr, ts_key = decode_frame_rgb(raw)
            if bgr is None:
                continue

            fastsam_path = os.path.join(fastsam_dir, f"{ts_key}.jpg")
            yoloe_path = os.path.join(yoloe_dir, f"{ts_key}.jpg")
            compare_path = os.path.join(compare_dir, f"{ts_key}.jpg")

            fastsam_exists = os.path.isfile(fastsam_path)
            yoloe_exists = os.path.isfile(yoloe_path)

            if fastsam_exists and yoloe_exists and not force:
                # Both cached — just regenerate compare if missing
                if not os.path.isfile(compare_path):
                    fs_img = cv2.imread(fastsam_path)
                    ye_img = cv2.imread(yoloe_path)
                    if fs_img is not None and ye_img is not None:
                        combined = np.hstack([fs_img, ye_img])
                        cv2.imwrite(compare_path, combined, [cv2.IMWRITE_JPEG_QUALITY, quality])
                skipped += 1
                continue

            pil_img = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))

            # FastSAM
            if not fastsam_exists or force:
                model = get_fastsam()
                result = model.segment(pil_img)
                overlay = render_overlay(bgr, result.masks, labels=None)
                cv2.imwrite(fastsam_path, overlay, [cv2.IMWRITE_JPEG_QUALITY, quality])

            # YOLOE
            if not yoloe_exists or force:
                model = get_yoloe()
                result = model.segment(pil_img)
                overlay = render_overlay(bgr, result.masks, labels=result.labels)
                cv2.imwrite(yoloe_path, overlay, [cv2.IMWRITE_JPEG_QUALITY, quality])

            # Side-by-side compare
            fs_img = cv2.imread(fastsam_path)
            ye_img = cv2.imread(yoloe_path)
            if fs_img is not None and ye_img is not None:
                # Add model name headers
                h, w = fs_img.shape[:2]
                cv2.putText(fs_img, "FastSAM", (w - 130, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                cv2.putText(ye_img, "YOLOE", (w - 100, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                combined = np.hstack([fs_img, ye_img])
                cv2.imwrite(compare_path, combined, [cv2.IMWRITE_JPEG_QUALITY, quality])

            processed += 1
            if processed <= 3 or processed % 10 == 0:
                logger.info(f"  frame {i+1}/{len(entries)}: {ts_key} ({processed} processed)")

    elapsed = time.monotonic() - t_start
    logger.info(
        f"Done: {processed} processed, {skipped} cached, "
        f"{elapsed:.1f}s total"
    )

    # Generate HTML viewer
    _generate_html_viewer(output_dir, compare_dir)
    logger.info(f"Viewer: {os.path.join(output_dir, 'compare.html')}")


def _generate_html_viewer(output_dir: str, compare_dir: str):
    """Generate a simple HTML viewer with prev/next navigation."""
    images = sorted(
        f for f in os.listdir(compare_dir)
        if f.endswith((".jpg", ".jpeg", ".png"))
    )
    if not images:
        return

    html = """<!DOCTYPE html>
<html>
<head>
<title>Segmentation A/B Compare</title>
<style>
  body { background: #1a1a1a; color: #eee; font-family: monospace; margin: 0; padding: 20px; }
  .viewer { text-align: center; }
  img { max-width: 95vw; max-height: 80vh; border: 1px solid #444; }
  .controls { margin: 15px 0; }
  button { font-size: 18px; padding: 8px 24px; margin: 0 8px; cursor: pointer;
           background: #333; color: #eee; border: 1px solid #666; border-radius: 4px; }
  button:hover { background: #555; }
  .info { font-size: 14px; color: #aaa; margin: 10px 0; }
  .nav-hint { font-size: 12px; color: #666; }
</style>
</head>
<body>
<div class="viewer">
  <h2>FastSAM vs YOLOE &mdash; Segmentation Compare</h2>
  <div class="controls">
    <button onclick="prev()">&larr; Prev</button>
    <span id="counter">1 / """ + str(len(images)) + """</span>
    <button onclick="next()">Next &rarr;</button>
  </div>
  <div><img id="img" src="" /></div>
  <div class="info" id="filename"></div>
  <div class="nav-hint">Keyboard: &larr; / &rarr; arrow keys</div>
</div>
<script>
const images = """ + json.dumps(images) + """;
let idx = 0;
function show(i) {
  idx = Math.max(0, Math.min(images.length - 1, i));
  document.getElementById('img').src = 'compare/' + images[idx];
  document.getElementById('counter').textContent = (idx + 1) + ' / ' + images.length;
  document.getElementById('filename').textContent = images[idx];
}
function prev() { show(idx - 1); }
function next() { show(idx + 1); }
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowLeft') prev();
  else if (e.key === 'ArrowRight') next();
});
show(0);
</script>
</body>
</html>"""

    with open(os.path.join(output_dir, "compare.html"), "w") as f:
        f.write(html)


def main():
    ap = argparse.ArgumentParser(
        description="A/B segmentation debugger — compare FastSAM vs YOLOE"
    )
    ap.add_argument("--recording", required=True,
                    help="Path to recorded session directory")
    ap.add_argument("--output", default=None,
                    help="Output directory (default: debug/<session_name>)")
    ap.add_argument("--force", action="store_true",
                    help="Re-generate all frames even if cached")
    ap.add_argument("--quality", type=int, default=85,
                    help="JPEG quality (default: 85)")
    args = ap.parse_args()

    recording = os.path.abspath(args.recording)
    session_name = os.path.basename(recording)

    if args.output:
        output = os.path.abspath(args.output)
    else:
        output = os.path.join(ROOT, "debug", session_name)

    run_segmentation_debug(
        recording_dir=recording,
        output_dir=output,
        force=args.force,
        quality=args.quality,
    )


if __name__ == "__main__":
    main()
