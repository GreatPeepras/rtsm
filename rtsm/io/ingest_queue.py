from __future__ import annotations

import queue
from typing import Optional

from rtsm.core.datamodel import FramePacket


class IngestQueue:
    """
    Thread-safe queue for delivering FramePacket objects from IO/subscribers
    to the core pipeline.
    """

    # INGEST_SATURATION_2026-07-06: drop-oldest mode + eviction accounting.
    def __init__(self, maxsize: int = 256, drop_oldest: bool = False) -> None:
        self._q: "queue.Queue[FramePacket]" = queue.Queue(maxsize=maxsize)
        self.maxsize = int(maxsize)
        self.drop_oldest = bool(drop_oldest)
        self.evicted_oldest = 0

    def put(self, pkt: FramePacket, block: bool = False, timeout: Optional[float] = None) -> bool:
        try:
            self._q.put(pkt, block=block, timeout=0.0 if timeout is None else timeout)
            return True
        except queue.Full:
            # INGEST_SATURATION_2026-07-06: freshness over completeness.
            # Evict the oldest queued frame and enqueue the new one so the
            # pipeline always works on the most recent view of the world.
            if not self.drop_oldest:
                return False
            try:
                self._q.get_nowait()
                self.evicted_oldest += 1
            except queue.Empty:
                pass
            try:
                self._q.put_nowait(pkt)
                return True
            except queue.Full:
                return False

    def get(self, timeout: Optional[float] = None) -> Optional[FramePacket]:
        try:
            return self._q.get(timeout=0.0 if timeout is None else timeout)
        except queue.Empty:
            return None

    def qsize(self) -> int:
        return self._q.qsize()


