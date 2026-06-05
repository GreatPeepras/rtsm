"""Unit tests for ProximityIndex.nearby_ids max_results parameter.

Confirms the per-query cap override added 2026-06-03:
  - max_results=None  (default)  -> uses self.neighbors_max (historical)
  - max_results=0               -> disables the cap entirely
  - max_results=N>0             -> explicit override

Root cause being verified: with the historical default cap of 128 and
~160 OIDs in a typical small-apartment WM, wide spatial queries silently
dropped the 32 least-recently-touched OIDs. Verified end-to-end on
2026-06-03 against drawer + heater landmarks that consistently fell off
the result set.

Run with:
    cd ~/rtsm && PYTHONPATH=. python3 tests/test_nearby_ids_max_results.py
"""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.environ.get("RTSM_REPO", os.path.expanduser("~/rtsm")))

import numpy as np

from rtsm.stores.proximity_index import ProximityIndex, GridSpec


def _make_pi(neighbors_max: int = 10, per_cell_cap: int = 1000):
    grid = GridSpec(cell_m=1.0, use_3d=False, up_axis="z")
    return ProximityIndex(grid, per_cell_cap=per_cell_cap, neighbors_max=neighbors_max)


def _insert_grid(pi: ProximityIndex, n: int):
    """Insert n OIDs spread across n distinct cells on the X axis."""
    for i in range(n):
        pi.insert(f"oid{i:03d}", np.array([float(i), 0.0, 0.0], dtype=np.float32))


def test_default_uses_neighbors_max():
    """Without max_results, the historical neighbors_max cap applies."""
    pi = _make_pi(neighbors_max=10)
    _insert_grid(pi, 50)
    ids = pi.nearby_ids(np.array([25.0, 0.0, 0.0], dtype=np.float32), rings=100)
    assert len(ids) == 10, f"expected 10 (neighbors_max), got {len(ids)}"


def test_max_results_zero_disables_cap():
    """max_results=0 returns the full gather set."""
    pi = _make_pi(neighbors_max=10)
    _insert_grid(pi, 50)
    ids = pi.nearby_ids(
        np.array([25.0, 0.0, 0.0], dtype=np.float32),
        rings=100,
        max_results=0,
    )
    assert len(ids) == 50, f"expected 50 (uncapped), got {len(ids)}"


def test_max_results_explicit_override():
    """max_results=N applies that exact cap."""
    pi = _make_pi(neighbors_max=10)
    _insert_grid(pi, 50)
    ids = pi.nearby_ids(
        np.array([25.0, 0.0, 0.0], dtype=np.float32),
        rings=100,
        max_results=25,
    )
    assert len(ids) == 25, f"expected 25 (explicit cap), got {len(ids)}"


def test_below_cap_returns_all():
    """When gather set is smaller than the cap, return everything regardless."""
    pi = _make_pi(neighbors_max=10)
    _insert_grid(pi, 5)
    # Default cap (10) >= 5 hits -> no clamp.
    ids = pi.nearby_ids(np.array([2.0, 0.0, 0.0], dtype=np.float32), rings=100)
    assert len(ids) == 5

    # Explicit large cap also returns 5.
    ids = pi.nearby_ids(
        np.array([2.0, 0.0, 0.0], dtype=np.float32),
        rings=100,
        max_results=1000,
    )
    assert len(ids) == 5

    # max_results=0 with small set still returns 5 (uncapped).
    ids = pi.nearby_ids(
        np.array([2.0, 0.0, 0.0], dtype=np.float32),
        rings=100,
        max_results=0,
    )
    assert len(ids) == 5


def test_least_recently_touched_dropped_under_cap():
    """When the cap applies, drop the LEAST-recently-touched. This is the
    exact behavior that bit /landmarks/near on 2026-06-03 (drawer +
    heater both touched only at rehydrate, never re-observed)."""
    pi = _make_pi(neighbors_max=3)
    # Insert in order; later inserts have higher _touch values.
    pi.insert("oldest",  np.array([0.0, 0.0, 0.0], dtype=np.float32))
    pi.insert("older",   np.array([1.0, 0.0, 0.0], dtype=np.float32))
    pi.insert("newer",   np.array([2.0, 0.0, 0.0], dtype=np.float32))
    pi.insert("newest",  np.array([3.0, 0.0, 0.0], dtype=np.float32))

    ids = pi.nearby_ids(
        np.array([1.5, 0.0, 0.0], dtype=np.float32),
        rings=100,
    )
    # neighbors_max=3, so 'oldest' should be dropped (lowest _touch).
    assert "oldest" not in ids, (
        f"oldest should be dropped when cap=3; got {sorted(ids)}"
    )
    assert len(ids) == 3

    # max_results=0 returns all 4 (this is the fix).
    ids = pi.nearby_ids(
        np.array([1.5, 0.0, 0.0], dtype=np.float32),
        rings=100,
        max_results=0,
    )
    assert "oldest" in ids, (
        f"oldest should be present with max_results=0; got {sorted(ids)}"
    )
    assert len(ids) == 4


def _run_all():
    tests = [
        test_default_uses_neighbors_max,
        test_max_results_zero_disables_cap,
        test_max_results_explicit_override,
        test_below_cap_returns_all,
        test_least_recently_touched_dropped_under_cap,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERR   {t.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed (of {len(tests)} total)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(_run_all())
