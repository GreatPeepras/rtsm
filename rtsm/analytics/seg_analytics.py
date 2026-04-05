"""
Segmentation analytics buffer — tracks dual confirmation breakdown per frame.

Tier 1: Per-frame SegFrameStats in a ring buffer (deque, maxlen=300).
Tier 2: Per-second SegSecondBucket with wall-clock retention (default 1 hour).

Works for all backends (fastsam/yoloe/dual). Single-backend modes leave
irrelevant fields at 0 — never None, never crashes.
"""
from __future__ import annotations

import dataclasses
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SegFrameStats:
    """One entry per processed frame — appended by the pipeline."""
    timestamp: float        # time.monotonic()
    frame_seq: int = 0
    backend: str = "dual"   # "dual" | "fastsam" | "yoloe"
    # Post-merge counts
    n_dual: int = 0
    n_fastsam_only: int = 0
    n_yoloe_only: int = 0
    n_total: int = 0
    # Pre-merge raw model output counts (dual only)
    n_fastsam_raw: int = 0
    n_yoloe_raw: int = 0
    # Post-staging survival
    staged_dual: int = 0
    staged_fastsam_only: int = 0
    staged_yoloe_only: int = 0
    # Post-selection (top-K)
    selected_dual: int = 0
    selected_fastsam_only: int = 0
    selected_yoloe_only: int = 0


@dataclass
class SegSecondBucket:
    """One-second aggregate for Tier 2 time-series."""
    wall_ts: float          # time.time() — x-axis for charts
    backend: str = "dual"
    dual_rate: float = 0.0
    fastsam_only_rate: float = 0.0
    yoloe_only_rate: float = 0.0
    mean_total: float = 0.0
    mean_fastsam_raw: float = 0.0
    mean_yoloe_raw: float = 0.0
    staged_survival_rate: float = 0.0
    frames_in_bucket: int = 0


def _safe_mean(values: List[float]) -> float:
    return sum(values) / max(1, len(values))


class SegAnalyticsBuffer:
    """Thread-safe segmentation analytics with two-tier storage."""

    def __init__(self, max_frames: int = 300, retention_s: float = 3600.0):
        # Tier 1 — per-frame ring buffer
        self._buffer: deque[SegFrameStats] = deque(maxlen=max_frames)
        # Tier 2 — per-second buckets (time-evicted, no maxlen)
        self._second_buckets: deque[SegSecondBucket] = deque()
        self._retention_s = retention_s
        # Rollup cursor
        self._last_rollup_ts: float = time.monotonic()
        self._lock = threading.Lock()

    def append(self, entry: SegFrameStats) -> None:
        """Tier 1 append — called from pipeline thread."""
        if entry is None:
            return
        with self._lock:
            self._buffer.append(entry)

    def roll_up_second(self) -> SegSecondBucket:
        """Aggregate recent Tier 1 frames into a Tier 2 bucket.

        Called by the vis server's push loop (~1 Hz). Never called by the pipeline.
        """
        with self._lock:
            now_mono = time.monotonic()
            elapsed = now_mono - self._last_rollup_ts

            # Stale cursor guard: if no rollup for >2s (e.g., no clients),
            # skip accumulated data — rates would be meaningless.
            if elapsed > 2.0:
                self._last_rollup_ts = now_mono
                bucket = SegSecondBucket(wall_ts=time.time(), frames_in_bucket=0)
                self._second_buckets.append(bucket)
                self._evict_old()
                return bucket

            recent = [f for f in self._buffer if f.timestamp > self._last_rollup_ts]
            n = len(recent)

            total_masks = sum(f.n_total for f in recent) if recent else 0
            total_staged = (
                sum(f.staged_dual + f.staged_fastsam_only + f.staged_yoloe_only for f in recent)
                if recent else 0
            )

            bucket = SegSecondBucket(
                wall_ts=time.time(),
                backend=recent[0].backend if recent else "unknown",
                dual_rate=round(sum(f.n_dual for f in recent) / max(1, total_masks), 3),
                fastsam_only_rate=round(sum(f.n_fastsam_only for f in recent) / max(1, total_masks), 3),
                yoloe_only_rate=round(sum(f.n_yoloe_only for f in recent) / max(1, total_masks), 3),
                mean_total=round(total_masks / max(1, n), 1),
                mean_fastsam_raw=round(sum(f.n_fastsam_raw for f in recent) / max(1, n), 1),
                mean_yoloe_raw=round(sum(f.n_yoloe_raw for f in recent) / max(1, n), 1),
                staged_survival_rate=round(total_staged / max(1, total_masks), 3),
                frames_in_bucket=n,
            )

            self._second_buckets.append(bucket)
            self._evict_old()
            self._last_rollup_ts = now_mono
            return bucket

    def aggregate(self, last_n: Optional[int] = None) -> Dict[str, Any]:
        """Compute rolling stats over Tier 1 for real-time text display."""
        with self._lock:
            entries = list(self._buffer)
            if last_n is not None:
                entries = entries[-last_n:]

        if not entries:
            return {
                "frame_count": 0,
                "backend": "unknown",
                "dual_rate": 0.0,
                "fastsam_only_rate": 0.0,
                "yoloe_only_rate": 0.0,
                "mean_total": 0.0,
                "mean_fastsam_raw": 0.0,
                "mean_yoloe_raw": 0.0,
                "staged_survival_rate": 0.0,
                "selected_rate_by_source": {"dual": 0.0, "fastsam_only": 0.0, "yoloe_only": 0.0},
            }

        total_masks = sum(f.n_total for f in entries)
        total_selected = sum(f.selected_dual + f.selected_fastsam_only + f.selected_yoloe_only for f in entries)
        n = len(entries)

        return {
            "frame_count": n,
            "backend": entries[-1].backend,
            "dual_rate": round(sum(f.n_dual for f in entries) / max(1, total_masks), 3),
            "fastsam_only_rate": round(sum(f.n_fastsam_only for f in entries) / max(1, total_masks), 3),
            "yoloe_only_rate": round(sum(f.n_yoloe_only for f in entries) / max(1, total_masks), 3),
            "mean_total": round(total_masks / max(1, n), 1),
            "mean_fastsam_raw": round(sum(f.n_fastsam_raw for f in entries) / max(1, n), 1),
            "mean_yoloe_raw": round(sum(f.n_yoloe_raw for f in entries) / max(1, n), 1),
            "staged_survival_rate": round(
                sum(f.staged_dual + f.staged_fastsam_only + f.staged_yoloe_only for f in entries)
                / max(1, total_masks), 3
            ),
            "selected_rate_by_source": {
                "dual": round(sum(f.selected_dual for f in entries) / max(1, total_selected), 3),
                "fastsam_only": round(sum(f.selected_fastsam_only for f in entries) / max(1, total_selected), 3),
                "yoloe_only": round(sum(f.selected_yoloe_only for f in entries) / max(1, total_selected), 3),
            },
        }

    def hourly_history(self) -> List[Dict[str, Any]]:
        """Return Tier 2 buckets as list of dicts for chart rendering."""
        with self._lock:
            return [dataclasses.asdict(b) for b in self._second_buckets]

    def clear(self) -> None:
        """Reset all state — called on /reset."""
        with self._lock:
            self._buffer.clear()
            self._second_buckets.clear()
            self._last_rollup_ts = time.monotonic()

    def _evict_old(self) -> None:
        """Remove Tier 2 buckets older than retention window. Must hold lock."""
        cutoff = time.time() - self._retention_s
        while self._second_buckets and self._second_buckets[0].wall_ts < cutoff:
            self._second_buckets.popleft()
