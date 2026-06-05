"""Unit tests for Gate 2.5 (embedding-based re-id) in Associator.

Tests the _gate_2_5_match helper directly with a minimal WM-like stub.
Covers:
1. Happy path: same-label, above-tau cosine -> match
2. Below-tau cosine -> no match (spawn would proceed)
3. Different-label, above-tau -> no match (same-label filter)
4. Multiple candidates: returns highest cosine
5. Skips unconfirmed (proto) objects
6. Disabled via config
7. Honors label_user over label_primary

Run with:
    cd /workspace/rtsm && PYTHONPATH=. python3 test_gate_2_5.py
"""
import sys
sys.path.insert(0, "/home/claude/rtsm")

import numpy as np

from rtsm.core.association import Associator


def _emb(seed, dim=8):
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(dim).astype(np.float32)
    return v / (np.linalg.norm(v) + 1e-12)


def _noisy(base_emb, seed, sigma=0.01):
    """Add small Gaussian noise then re-normalize. Simulates a re-observation
    of the same object."""
    rng = np.random.default_rng(seed)
    v = base_emb + rng.normal(0, sigma, size=base_emb.shape).astype(np.float32)
    return v / (np.linalg.norm(v) + 1e-12)


class _Obj:
    """Minimal duck-typed ObjectState for testing."""
    def __init__(self, oid, emb_mean, label_primary, confirmed=True,
                 label_user=None):
        self.id = oid
        self.emb_mean = emb_mean
        self.label_primary = label_primary
        self.label_user = label_user
        self.confirmed = confirmed
        self.xyz_world = np.zeros(3, dtype=np.float32)


class _WM:
    """Minimal duck-typed WorkingMemory for testing."""
    def __init__(self, objects):
        self._objects = list(objects)

    def iter_objects(self):
        return list(self._objects)


def _assoc(extra_cfg=None):
    cfg = {'assoc': {}}
    if extra_cfg:
        cfg['assoc'].update(extra_cfg)
    return Associator(cfg)


def test_happy_path_match():
    """Same label, above-tau cosine -> returns matched oid."""
    print("\n=== test_happy_path_match ===")
    base = _emb(1)
    wm = _WM([
        _Obj("aaa", base, "couch"),
        _Obj("bbb", _emb(2), "table"),
    ])
    assoc = _assoc()
    incoming = _noisy(base, seed=10, sigma=0.01)  # very similar to "couch"
    result = assoc._gate_2_5_match(incoming, "couch", wm)
    assert result is not None, "Should match the couch"
    matched_oid, sim = result
    assert matched_oid == "aaa", f"Expected aaa, got {matched_oid}"
    assert sim >= 0.92, f"Expected sim >= 0.92, got {sim}"
    print(f"  OK: matched oid=aaa cos={sim:.4f}")


def test_below_tau_no_match():
    """Below-tau cosine -> no match (would proceed to spawn)."""
    print("\n=== test_below_tau_no_match ===")
    wm = _WM([
        _Obj("aaa", _emb(1), "couch"),
    ])
    assoc = _assoc()
    # Use a totally unrelated embedding
    incoming = _emb(99)
    result = assoc._gate_2_5_match(incoming, "couch", wm)
    assert result is None, f"Expected no match for unrelated emb, got {result}"
    print(f"  OK: no match for unrelated embedding")


def test_different_label_no_match():
    """Above-tau cosine but different label -> no match (same-label filter)."""
    print("\n=== test_different_label_no_match ===")
    base = _emb(1)
    wm = _WM([
        # Even though embedding matches almost perfectly, the label differs
        _Obj("aaa", base, "couch"),
    ])
    assoc = _assoc()
    incoming = _noisy(base, seed=10, sigma=0.001)  # virtually identical
    # Same-label filter: incoming label = "table" != existing "couch"
    result = assoc._gate_2_5_match(incoming, "table", wm)
    assert result is None, (
        f"Same-label filter should block cross-label match; got {result}"
    )
    print(f"  OK: same-label filter blocks cross-label match")


def test_multiple_candidates_picks_best():
    """When multiple objects share the label, return the highest-cosine one."""
    print("\n=== test_multiple_candidates_picks_best ===")
    base = _emb(1)
    # Two "couch" objects with different embeddings
    wm = _WM([
        _Obj("aaa", _noisy(base, seed=20, sigma=0.1), "couch"),    # less similar
        _Obj("bbb", _noisy(base, seed=21, sigma=0.001), "couch"),  # nearly identical
    ])
    assoc = _assoc()
    incoming = _noisy(base, seed=22, sigma=0.005)
    result = assoc._gate_2_5_match(incoming, "couch", wm)
    assert result is not None
    matched_oid, _ = result
    assert matched_oid == "bbb", (
        f"Should pick the more-similar 'bbb', got {matched_oid}"
    )
    print(f"  OK: picked highest-similarity candidate")


def test_skips_unconfirmed():
    """Proto (unconfirmed) objects shouldn't be considered for re-id."""
    print("\n=== test_skips_unconfirmed ===")
    base = _emb(1)
    wm = _WM([
        _Obj("aaa", base, "couch", confirmed=False),  # proto, not eligible
    ])
    assoc = _assoc()
    incoming = _noisy(base, seed=10, sigma=0.001)
    result = assoc._gate_2_5_match(incoming, "couch", wm)
    assert result is None, f"Proto should not be matched, got {result}"
    print(f"  OK: proto object skipped")


def test_disabled_via_config():
    """gate_2_5_enabled=false returns None unconditionally."""
    print("\n=== test_disabled_via_config ===")
    base = _emb(1)
    wm = _WM([_Obj("aaa", base, "couch")])
    assoc = _assoc({'gate_2_5_enabled': False})
    incoming = _noisy(base, seed=10, sigma=0.001)
    result = assoc._gate_2_5_match(incoming, "couch", wm)
    assert result is None, f"Disabled gate should return None, got {result}"
    print(f"  OK: disabled gate returns None")


def test_honors_label_user():
    """When label_user is set, it takes precedence over label_primary for filtering."""
    print("\n=== test_honors_label_user ===")
    base = _emb(1)
    wm = _WM([
        # label_primary differs from incoming, but label_user matches.
        _Obj("aaa", base, label_primary="couch", label_user="reading_chair"),
    ])
    assoc = _assoc()
    incoming = _noisy(base, seed=10, sigma=0.001)
    # Match against the user-pinned label
    result = assoc._gate_2_5_match(incoming, "reading_chair", wm)
    assert result is not None, f"Should match via label_user, got {result}"
    matched_oid, _ = result
    assert matched_oid == "aaa"
    print(f"  OK: label_user honored over label_primary")

    # Conversely, the original label_primary should NOT match
    result2 = assoc._gate_2_5_match(incoming, "couch", wm)
    assert result2 is None, (
        f"Should NOT match label_primary when label_user overrides; got {result2}"
    )
    print(f"  OK: label_primary blocked when label_user is set")


def test_tau_configurable():
    """A higher tau makes matching stricter."""
    print("\n=== test_tau_configurable ===")
    base = _emb(1)
    wm = _WM([_Obj("aaa", base, "couch")])
    # Add small noise -> cosine ~0.9-0.99 depending on sigma; we'll measure.
    incoming = _noisy(base, seed=10, sigma=0.15)  # noticeable noise
    real_sim = float(np.dot(incoming, base))
    print(f"  observed cosine = {real_sim:.4f}")

    # Set tau just above the observed sim -> no match
    assoc_strict = _assoc({'gate_2_5_tau': real_sim + 0.01})
    assert assoc_strict._gate_2_5_match(incoming, "couch", wm) is None
    # Set tau just below -> match
    assoc_loose = _assoc({'gate_2_5_tau': real_sim - 0.01})
    assert assoc_loose._gate_2_5_match(incoming, "couch", wm) is not None
    print(f"  OK: tau threshold cleanly toggles match/no-match")


if __name__ == "__main__":
    test_happy_path_match()
    test_below_tau_no_match()
    test_different_label_no_match()
    test_multiple_candidates_picks_best()
    test_skips_unconfirmed()
    test_disabled_via_config()
    test_honors_label_user()
    test_tau_configurable()
    print("\nAll Gate 2.5 tests passed.")
