#!/usr/bin/env python3
"""Poll rtsm-dev /stats once per second to CSV.

Stdlib only. Clean exit on SIGINT/SIGTERM. Flushes every write so
we don't lose tail data if the run is killed.
"""
import argparse
import csv
import json
import signal
import sys
import time
import urllib.request


COLUMNS = [
    "t_wall_ns",
    "objects",
    "confirmed",
    "avg_hits",
    "upserts_total",
    "ingest_q",
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://localhost:8002/stats")
    p.add_argument("--out", required=True,
                   help="Output CSV path")
    p.add_argument("--interval", type=float, default=1.0,
                   help="Poll interval in seconds (default: 1.0)")
    a = p.parse_args()

    stop = {"v": False}
    def _sig(*_): stop["v"] = True
    signal.signal(signal.SIGINT,  _sig)
    signal.signal(signal.SIGTERM, _sig)

    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        f.flush()

        next_t = time.monotonic()
        n_ok = 0
        n_err = 0
        while not stop["v"]:
            try:
                with urllib.request.urlopen(a.url, timeout=2.0) as r:
                    d = json.loads(r.read())
                row = {"t_wall_ns": time.monotonic_ns()}
                for c in COLUMNS[1:]:
                    row[c] = d.get(c)
                w.writerow(row)
                f.flush()
                n_ok += 1
            except Exception as e:
                n_err += 1
                print(f"[stats-poller] poll error #{n_err}: {e}",
                      file=sys.stderr)

            next_t += a.interval
            sleep_for = max(0.0, next_t - time.monotonic())
            # Sleep in small chunks so SIGINT is responsive
            end = time.monotonic() + sleep_for
            while not stop["v"] and time.monotonic() < end:
                time.sleep(min(0.1, end - time.monotonic()))

    print(f"[stats-poller] done. n_ok={n_ok} n_err={n_err} -> {a.out}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
