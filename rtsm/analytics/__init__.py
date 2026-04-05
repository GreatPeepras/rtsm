"""
RTSM Runtime Analytics — two-tier buffer system for real-time insight.

Tier 1: Per-frame raw data in ring buffers (short window, ~75s)
Tier 2: Per-second aggregated buckets (1-hour retention, wall-clock eviction)

Usage:
    from rtsm.analytics import SegAnalyticsBuffer, PipelineLatencyBuffer
"""
from rtsm.analytics.seg_analytics import SegAnalyticsBuffer, SegFrameStats, SegSecondBucket
from rtsm.analytics.latency_analytics import PipelineLatencyBuffer, FrameTimingStats, LatencySecondBucket

__all__ = [
    "SegAnalyticsBuffer",
    "SegFrameStats",
    "SegSecondBucket",
    "PipelineLatencyBuffer",
    "FrameTimingStats",
    "LatencySecondBucket",
]
