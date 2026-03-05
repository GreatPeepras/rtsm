"""Network utility functions for RTSM."""

from __future__ import annotations
import socket
import logging
from typing import List

logger = logging.getLogger(__name__)


def get_local_ipv4_addresses() -> List[str]:
    """
    Return list of non-loopback IPv4 addresses for this machine.
    Uses stdlib only — no external dependencies.
    """
    addrs: List[str] = []

    # Preferred method: UDP connect trick to find outbound IP
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            preferred = s.getsockname()[0]
            if preferred and preferred != "0.0.0.0":
                addrs.append(preferred)
    except Exception:
        pass

    # Fallback: getaddrinfo on hostname
    if not addrs:
        try:
            hostname = socket.gethostname()
            for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
                addr = info[4][0]
                if addr and not addr.startswith("127."):
                    if addr not in addrs:
                        addrs.append(addr)
        except Exception:
            pass

    return addrs


def print_server_addresses(port: int, protocol: str = "ws") -> None:
    """
    Print reachable server addresses for the given port.
    Called at startup so user can configure the iOS client.
    """
    addrs = get_local_ipv4_addresses()
    if addrs:
        logger.info(f"WebSocket receiver listening on port {port}")
        for addr in addrs:
            url = f"{protocol}://{addr}:{port}/stream"
            logger.info(f"  -> {url}")
            print(f"  Calabi Lens: {url}")
    else:
        logger.warning(
            "Could not detect local IP address; "
            "client must use hostname or IP manually"
        )
