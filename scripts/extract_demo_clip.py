#!/usr/bin/env python3
"""
Extract a small demo clip from a full RTSM recording.

Reads the first N frames from a session recording, transcodes NV12 RGB to JPEG
(~20x smaller), and writes a new compact recording suitable for in-repo storage.

Usage:
    python scripts/extract_demo_clip.py recordings/session1 recordings/demo_clip --frames 50
"""

from __future__ import annotations

import argparse
import json
import os
import struct
import sys
from pathlib import Path

import cv2
import numpy as np


def parse_frame(data: bytes) -> dict:
    """Parse a single binary frame into its components.

    Returns dict with keys: header, rgb_bytes, depth_bytes, conf_bytes, tail_offset.
    """
    offset = 0
    n = len(data)

    # 1. JSON header
    json_len = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    header = json.loads(data[offset : offset + json_len].decode("utf-8"))
    offset += json_len

    # 2. RGB payload
    rgb_len = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    rgb_bytes = data[offset : offset + rgb_len]
    offset += rgb_len

    # 3. Depth payload
    depth_len = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    depth_bytes = data[offset : offset + depth_len]
    offset += depth_len

    # 4. Confidence payload (optional)
    conf_bytes = b""
    if offset < n:
        remaining = n - offset
        if remaining >= 4:
            conf_len = struct.unpack_from("<I", data, offset)[0]
            offset += 4
            if conf_len > 0 and (n - offset) >= conf_len:
                conf_bytes = data[offset : offset + conf_len]
                offset += conf_len

    return {
        "header": header,
        "rgb_bytes": rgb_bytes,
        "depth_bytes": depth_bytes,
        "conf_bytes": conf_bytes,
    }


def transcode_rgb_to_jpeg(
    rgb_bytes: bytes, fmt: str, width: int, height: int, quality: int = 85
) -> bytes:
    """Convert RGB payload from any format to JPEG.

    Args:
        rgb_bytes: Raw RGB payload bytes.
        fmt: Source format ('nv12', 'jpeg', 'png', 'bgra').
        width: Image width.
        height: Image height.
        quality: JPEG quality (1-100).

    Returns:
        JPEG-encoded bytes.
    """
    if fmt == "jpeg":
        return rgb_bytes  # Already JPEG, pass through

    if fmt == "nv12":
        expected = height * width * 3 // 2
        if len(rgb_bytes) != expected:
            raise ValueError(
                f"NV12 buffer size mismatch: got {len(rgb_bytes)}, "
                f"expected {expected} ({width}x{height})"
            )
        yuv = np.frombuffer(rgb_bytes, dtype=np.uint8).reshape(height * 3 // 2, width)
        bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV12)
    elif fmt == "bgra":
        bgr_arr = np.frombuffer(rgb_bytes, dtype=np.uint8).reshape(height, width, 4)
        bgr = cv2.cvtColor(bgr_arr, cv2.COLOR_BGRA2BGR)
    elif fmt == "png":
        buf = np.frombuffer(rgb_bytes, dtype=np.uint8)
        bgr = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        if bgr is None:
            raise ValueError("Failed to decode PNG RGB")
    else:
        raise ValueError(f"Unsupported rgb_format: {fmt!r}")

    ok, jpeg_buf = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("JPEG encoding failed")
    return jpeg_buf.tobytes()


def reassemble_frame(header: dict, rgb_jpeg: bytes, depth_bytes: bytes, conf_bytes: bytes) -> bytes:
    """Reassemble a binary frame with updated RGB payload.

    Returns the complete binary frame bytes.
    """
    header_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")

    parts = [
        struct.pack("<I", len(header_bytes)),
        header_bytes,
        struct.pack("<I", len(rgb_jpeg)),
        rgb_jpeg,
        struct.pack("<I", len(depth_bytes)),
        depth_bytes,
    ]

    # Include confidence if present
    if conf_bytes:
        parts.append(struct.pack("<I", len(conf_bytes)))
        parts.append(conf_bytes)

    return b"".join(parts)


def extract_demo_clip(
    input_dir: str,
    output_dir: str,
    num_frames: int = 50,
    jpeg_quality: int = 85,
) -> dict:
    """Extract and transcode frames from a recording.

    Args:
        input_dir: Path to source recording directory.
        output_dir: Path to output directory (created if needed).
        num_frames: Number of frames to extract.
        jpeg_quality: JPEG quality for transcoded RGB.

    Returns:
        Dict with extraction stats.
    """
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    idx_path = os.path.join(input_dir, "index.jsonl")
    bin_path = os.path.join(input_dir, "messages.bin")
    meta_path = os.path.join(input_dir, "meta.json")

    if not os.path.isfile(idx_path):
        raise FileNotFoundError(f"Missing index.jsonl: {idx_path}")
    if not os.path.isfile(bin_path):
        raise FileNotFoundError(f"Missing messages.bin: {bin_path}")

    # Load index
    with open(idx_path, "r", encoding="utf-8") as f:
        all_entries = [json.loads(line) for line in f if line.strip()]

    entries = all_entries[:num_frames]
    if not entries:
        raise ValueError("No frames to extract")

    # Re-zero timestamps relative to first frame
    t0 = entries[0]["t_mono_s"]

    os.makedirs(output_dir, exist_ok=True)

    out_bin_path = os.path.join(output_dir, "messages.bin")
    out_idx_path = os.path.join(output_dir, "index.jsonl")
    out_meta_path = os.path.join(output_dir, "meta.json")

    total_in_bytes = 0
    total_out_bytes = 0
    out_offset = 0

    with open(bin_path, "rb") as bin_f, \
         open(out_bin_path, "wb") as out_bin_f, \
         open(out_idx_path, "w", encoding="utf-8") as out_idx_f:

        for i, entry in enumerate(entries):
            bin_f.seek(entry["offset"])
            raw = bin_f.read(entry["length"])
            total_in_bytes += len(raw)

            # Parse frame
            parsed = parse_frame(raw)
            header = parsed["header"]

            # Transcode RGB to JPEG
            rgb_fmt = header.get("rgb_format", "jpeg")
            rgb_w = int(header.get("rgb_width", 0))
            rgb_h = int(header.get("rgb_height", 0))

            rgb_jpeg = transcode_rgb_to_jpeg(
                parsed["rgb_bytes"], rgb_fmt, rgb_w, rgb_h, jpeg_quality
            )

            # Update header for JPEG format
            header["rgb_format"] = "jpeg"

            # Reassemble frame
            new_frame = reassemble_frame(
                header, rgb_jpeg, parsed["depth_bytes"], parsed["conf_bytes"]
            )

            # Write to output
            out_bin_f.write(new_frame)
            out_bin_f.flush()

            # Write index entry (re-zeroed timestamp)
            out_entry = {
                "seq": i,
                "offset": out_offset,
                "length": len(new_frame),
                "t_mono_s": round(entry["t_mono_s"] - t0, 6),
            }
            out_idx_f.write(json.dumps(out_entry) + "\n")
            out_idx_f.flush()

            out_offset += len(new_frame)
            total_out_bytes += len(new_frame)

            ratio = len(raw) / len(new_frame) if new_frame else 0
            print(
                f"  [{i+1:3d}/{len(entries)}] "
                f"{len(raw):>10,}B -> {len(new_frame):>8,}B "
                f"({ratio:.1f}x) "
                f"rgb: {rgb_fmt}->jpeg "
                f"t={out_entry['t_mono_s']:.3f}s"
            )

    # Write meta.json
    meta = {}
    if os.path.isfile(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

    duration = entries[-1]["t_mono_s"] - t0 if len(entries) > 1 else 0.0

    out_meta = {
        "format_version": meta.get("format_version", 1),
        "session_id": meta.get("session_id", "demo_clip"),
        "device_name": meta.get("device_name", "unknown"),
        "hello": meta.get("hello"),
        "ack": meta.get("ack"),
        "total_binary_messages": len(entries),
        "duration_s": round(duration, 3),
        "source_recording": input_dir,
        "source_frames": f"0-{len(entries)-1}",
        "jpeg_quality": jpeg_quality,
    }

    with open(out_meta_path, "w", encoding="utf-8") as f:
        json.dump(out_meta, f, indent=2)

    stats = {
        "frames": len(entries),
        "input_bytes": total_in_bytes,
        "output_bytes": total_out_bytes,
        "compression_ratio": total_in_bytes / total_out_bytes if total_out_bytes else 0,
        "duration_s": duration,
        "output_dir": output_dir,
    }

    print(f"\n  Done: {stats['frames']} frames")
    print(f"  Input:  {total_in_bytes:>12,} bytes ({total_in_bytes/1024/1024:.1f} MB)")
    print(f"  Output: {total_out_bytes:>12,} bytes ({total_out_bytes/1024/1024:.1f} MB)")
    print(f"  Ratio:  {stats['compression_ratio']:.1f}x")
    print(f"  Duration: {duration:.1f}s")
    print(f"  Output: {output_dir}")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Extract a small demo clip from an RTSM recording"
    )
    parser.add_argument("input_dir", help="Source recording directory")
    parser.add_argument("output_dir", help="Output directory for demo clip")
    parser.add_argument(
        "--frames", type=int, default=50, help="Number of frames to extract (default: 50)"
    )
    parser.add_argument(
        "--quality", type=int, default=85, help="JPEG quality 1-100 (default: 85)"
    )
    args = parser.parse_args()

    print(f"Extracting demo clip: {args.input_dir} -> {args.output_dir}")
    print(f"  Frames: {args.frames}, JPEG quality: {args.quality}")

    extract_demo_clip(args.input_dir, args.output_dir, args.frames, args.quality)


if __name__ == "__main__":
    main()
