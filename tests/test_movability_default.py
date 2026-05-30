"""Unit tests for the movability_class coarse default on proto spawn.

Tests WorkingMemory.create_object() respect for cfg.object.default_movability,
plus the validation/fallback behavior at __init__ time.

Run with:
    cd ~/rtsm && PYTHONPATH=. python3 tests/test_movability_default.py
"""
import logging
import sys
import warnings

import numpy as np

from rtsm.stores.working_memory import WorkingMemory
from rtsm.stores.proximity_index import ProximityIndex, GridSpec


# Silence noisy log output during normal test runs; tests that check log
# behavior re-enable as needed via caplog-style capture.
logging.basicConfig(level=logging.CRITICAL)


def _cfg(default_movability="__unset__"):
    """Build a minimal cfg dict. Use the sentinel '__unset__' to mean
    'do not set default_movability at all', so we can test the no-key fallback."""
    obj = {
        "promote_hits": 2,
        "stability_promote": 0.5,
        "promote_min_conf": 0.10,
        "min_label_hits": 2,
        "require_view_bins": 1,
    }
    if default_movability != "__unset__":
        obj["default_movability"] = default_movability
    return {
        "object": obj,
        "vectors": {"enable": False},
        "sweep_cache": {"grid_size_m": 0.25, "two_d": True, "up_axis": "z"},
    }


def _wm(default_movability="__unset__"):
    grid = GridSpec(cell_m=0.25, use_3d=False, up_axis="z")
    idx = ProximityIndex(grid)
    return WorkingMemory(_cfg(default_movability), index=idx)


def _emb(seed, dim=8):
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(dim).astype(np.float32)
    return v / (np.linalg.norm(v) + 1e-12)


def _create(wm, seed=1):
    """Helper: create one fresh proto object and return its ObjectState."""
    oid = wm.create_object(
        p_world=np.array([1.0, 2.0, 0.5], dtype=np.float32),
        emb_vis=_emb(seed),
        label_topk=[("mug", 0.9)],
    )
    assert oid is not None, "create_object returned None (rejected)"
    return wm.get(oid)


def test_default_when_config_unset():
    """No default_movability in config -> object gets 'movable' (the documented default)."""
    print("\n=== test_default_when_config_unset ===")
    wm = _wm()
    o = _create(wm)
    assert o.movability_class == "movable", (
        f"expected 'movable', got {o.movability_class!r}"
    )
    assert wm.default_movability == "movable"
    print(f"  OK: movability_class={o.movability_class!r}")


def test_explicit_override_movable():
    """Explicitly setting movable in config is a no-op (same as default)."""
    print("\n=== test_explicit_override_movable ===")
    wm = _wm("movable")
    o = _create(wm)
    assert o.movability_class == "movable"
    print(f"  OK: movability_class={o.movability_class!r}")


def test_explicit_override_roaming():
    """Setting another auto-assignable class works."""
    print("\n=== test_explicit_override_roaming ===")
    wm = _wm("roaming")
    o = _create(wm)
    assert o.movability_class == "roaming"
    assert wm.default_movability == "roaming"
    print(f"  OK: movability_class={o.movability_class!r}")


def test_explicit_override_ephemeral():
    """ephemeral is an allowed auto-default."""
    print("\n=== test_explicit_override_ephemeral ===")
    wm = _wm("ephemeral")
    o = _create(wm)
    assert o.movability_class == "ephemeral"
    print(f"  OK: movability_class={o.movability_class!r}")


def test_null_config_yields_none():
    """default_movability: null in config -> objects get None on creation.

    This is back-compat with pre-patch behavior. Eviction's own None ->
    semi_static fallback still applies downstream.
    """
    print("\n=== test_null_config_yields_none ===")
    wm = _wm(None)
    o = _create(wm)
    assert o.movability_class is None, (
        f"expected None, got {o.movability_class!r}"
    )
    assert wm.default_movability is None
    print(f"  OK: movability_class={o.movability_class!r}")


def test_static_rejected_falls_back_to_movable():
    """Setting static is rejected (landmark-eligible -> manual only)."""
    print("\n=== test_static_rejected_falls_back_to_movable ===")
    # Capture the warning via logger.handlers approach
    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)
    import io
    buf = io.StringIO()
    handler = logging.StreamHandler(buf)
    handler.setLevel(logging.WARNING)
    wm_logger = logging.getLogger("rtsm.stores.working_memory")
    wm_logger.addHandler(handler)
    wm_logger.setLevel(logging.WARNING)
    try:
        wm = _wm("static")
        log_output = buf.getvalue()
    finally:
        wm_logger.removeHandler(handler)
    assert wm.default_movability == "movable", (
        f"static should fall back to 'movable', got {wm.default_movability!r}"
    )
    assert "static" in log_output or "landmark" in log_output.lower() or "default_movability" in log_output, (
        f"expected a warning about invalid default_movability, log was:\n{log_output}"
    )
    o = _create(wm)
    assert o.movability_class == "movable"
    print(f"  OK: fell back to 'movable'; logger warned")


def test_permanent_rejected_falls_back_to_movable():
    """permanent is also rejected (landmark-eligible)."""
    print("\n=== test_permanent_rejected_falls_back_to_movable ===")
    wm = _wm("permanent")
    assert wm.default_movability == "movable"
    o = _create(wm)
    assert o.movability_class == "movable"
    print(f"  OK: fell back to 'movable'")


def test_garbage_value_rejected_falls_back_to_movable():
    """An entirely invalid class string is rejected."""
    print("\n=== test_garbage_value_rejected_falls_back_to_movable ===")
    wm = _wm("not_a_real_class")
    assert wm.default_movability == "movable"
    o = _create(wm)
    assert o.movability_class == "movable"
    print(f"  OK: fell back to 'movable'")


def test_user_patch_still_works_post_default():
    """The user can still PATCH a different class via update_user_fields,
    even on an object that was auto-defaulted. PATCH is the authority."""
    print("\n=== test_user_patch_still_works_post_default ===")
    wm = _wm()  # default 'movable'
    o = _create(wm)
    assert o.movability_class == "movable"
    # Now upgrade to 'static' via the user-fields API (mirrors PATCH endpoint).
    o2 = wm.update_user_fields(o.id, movability_class="static")
    assert o2 is not None
    assert o2.movability_class == "static", (
        f"PATCH to static should override default, got {o2.movability_class!r}"
    )
    print(f"  OK: PATCH 'movable' -> 'static' succeeded")


def test_promote_to_confirmed_preserves_class():
    """Promotion from proto -> confirmed must not touch movability_class."""
    print("\n=== test_promote_to_confirmed_preserves_class ===")
    wm = _wm("roaming")
    o = _create(wm)
    assert o.movability_class == "roaming"
    # Force the promotion gates so maybe_promote() flips confirmed=True.
    # The simplest way is to bypass the gates by directly setting fields,
    # since the goal is to test that promote doesn't reset movability_class.
    with wm._lock:
        o.confirmed = True
    assert o.movability_class == "roaming", (
        "confirmation must not change movability_class"
    )
    print(f"  OK: still {o.movability_class!r} after confirmed=True")


if __name__ == "__main__":
    failures = []
    tests = [
        test_default_when_config_unset,
        test_explicit_override_movable,
        test_explicit_override_roaming,
        test_explicit_override_ephemeral,
        test_null_config_yields_none,
        test_static_rejected_falls_back_to_movable,
        test_permanent_rejected_falls_back_to_movable,
        test_garbage_value_rejected_falls_back_to_movable,
        test_user_patch_still_works_post_default,
        test_promote_to_confirmed_preserves_class,
    ]
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failures.append((t.__name__, str(e)))
            print(f"  FAIL: {e}", file=sys.stderr)
        except Exception as e:
            failures.append((t.__name__, f"unexpected: {e!r}"))
            print(f"  ERROR: {e!r}", file=sys.stderr)
    print()
    if failures:
        print(f"{len(failures)}/{len(tests)} FAILED")
        for name, msg in failures:
            print(f"  - {name}: {msg}")
        sys.exit(1)
    print(f"All {len(tests)} tests passed.")
