"""Unit tests for the hybrid emb_mean update in WorkingMemory.update_object.

Tests the second half of Gate 2.5 (EWMA tail on the canonical embedding).
The first half (cosine re-id at tau=0.92) shipped 2026-05-25 in commit
9606244 and is covered by test_gate_2_5.py.

Coverage:
1. test_running_mean_phase
   While hits < emb_mean_hits_threshold, emb_mean matches the closed-form
   running mean of all observations (back-compat with pre-2026-05-27).
2. test_ewma_phase_active
   Once hits >= threshold, each new observation contributes alpha=0.05
   (before normalization), independent of how many observations preceded.
3. test_phase_boundary_is_threshold
   At hits == threshold-1, last running-mean update. At hits == threshold,
   first EWMA update.
4. test_output_always_l2_normalized
   Every update result is unit norm (within float32 tolerance).
5. test_anti_ossification
   The whole point of the EWMA tail: at hits=200, an orthogonal
   observation should shift emb_mean measurably (~alpha), whereas the
   old running-mean behavior would shift it by ~1/201 = 0.5%.
6. test_alpha_configurable
   Setting object.emb_mean_ewma_alpha actually changes the EWMA weight.
7. test_threshold_configurable
   Setting object.emb_mean_hits_threshold actually changes the boundary.
8. test_default_back_compat
   Without explicit config, defaults are 20 and 0.05 (the original Gate
   2.5 spec values).

Run from repo root with:
    cd /workspace/rtsm && PYTHONPATH=. python3 test_emb_mean_hybrid.py
"""
import sys
sys.path.insert(0, "/workspace/rtsm")

import numpy as np

from rtsm.stores.working_memory import WorkingMemory, _l2norm
from rtsm.stores.proximity_index import ProximityIndex, GridSpec
from rtsm.core.association import AssocUpdate


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

def _make_cfg(threshold=20, alpha=0.05, dim=8, omit_knobs=False):
    """Build a minimal WM config with the new knobs (or without, to
    exercise the default-fallback path)."""
    obj = {
        "promote_hits": 2,
        "stability_promote": 0.5,
        "promote_min_conf": 0.18,
        "min_label_hits": 5,
        "require_view_bins": 2,
        "max_gallery": 6,
        "gallery_dupe_cos": 0.995,
    }
    if not omit_knobs:
        obj["emb_mean_hits_threshold"] = threshold
        obj["emb_mean_ewma_alpha"] = alpha
    return {
        "vectors": {"enable": False, "dim": dim},
        "sweep_cache": {"grid_size_m": 0.25, "two_d": True, "up_axis": "z"},
        "object": obj,
    }


def _make_wm(cfg):
    grid = GridSpec(cell_m=0.25, use_3d=False, up_axis="z")
    idx = ProximityIndex(grid)
    return WorkingMemory(cfg, index=idx)


def _emb(seed, dim=8):
    """Unit-norm embedding from a seed."""
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(dim).astype(np.float32)
    return v / (np.linalg.norm(v) + 1e-12)


def _orthogonal_pair(dim=8, seed=0):
    """Two unit vectors with dot product ~= 0."""
    rng = np.random.default_rng(seed)
    a = rng.standard_normal(dim).astype(np.float32)
    a = a / np.linalg.norm(a)
    # Build b in the orthogonal complement of a
    b = rng.standard_normal(dim).astype(np.float32)
    b = b - np.dot(a, b) * a
    b = b / np.linalg.norm(b)
    return a, b


def _make_obs(p_world, emb_vis):
    """Build a minimal AssocUpdate. Non-keyframe so position EMA is
    gentle (we don't care about xyz in these tests). No labels, no
    crop, no view_dir_cam (-> no view-bin update)."""
    return AssocUpdate(
        p_world=p_world.astype(np.float32),
        emb_vis=emb_vis.astype(np.float32),
        view_dir_cam=None,
        centroid_px=None,
        depth_valid=1.0,
        quality=1.0,
        cos_sim=0.95,
        dist_m=0.01,
        label_topk=None,
        crop=None,
        is_keyframe=False,
        frame_id=None,
    )


def _seed_object(wm, dim=8):
    """Create one confirmed object via create_object. Returns oid and the
    initial embedding (which becomes emb_mean on creation)."""
    e0 = _emb(seed=1, dim=dim)
    p = np.zeros(3, dtype=np.float32)
    oid = wm.create_object(p_world=p, emb_vis=e0, view_dir_cam=None,
                           label_topk=[("widget", 0.5)], crop=None)
    assert oid is not None, "create_object returned None"
    return oid, e0


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_running_mean_phase():
    """While hits < threshold, behavior matches the pre-2026-05-27 running
    mean. The actual formula is iterative (l2norm between steps), so we
    verify by replicating it step-by-step rather than via closed-form
    sum (which would only hold if there were no normalization in between)."""
    print("\n=== test_running_mean_phase ===")
    wm = _make_wm(_make_cfg(threshold=20, alpha=0.05))
    oid, e0 = _seed_object(wm)

    # Replicate the iterative formula in lockstep.
    expected = e0.copy()
    expected_hits = 1
    for i in range(5):
        e = _emb(seed=100 + i)
        wm.update_object(oid, _make_obs(np.zeros(3, np.float32), e))
        # In the running-mean branch (which we're in throughout this loop),
        # the line is: emb_mean = _l2norm(emb_mean * hits + e). hits here
        # is the pre-increment value.
        expected = _l2norm(expected * expected_hits + e)
        expected_hits += 1

    o = wm.get(oid)
    assert o is not None and o.hits == expected_hits, (
        f"expected hits={expected_hits}, got hits={o.hits}"
    )
    cos = float(np.dot(o.emb_mean, expected))
    assert cos > 0.9999, f"running-mean replication failed: cos={cos:.6f}"
    print(f"  OK: emb_mean tracks running mean at hits={expected_hits} "
          f"(cos={cos:.6f})")


def test_ewma_phase_active():
    """Once past the threshold, a single new observation should change
    emb_mean by the EWMA formula. Test: lift an object to hits >=
    threshold with constant embedding (so emb_mean = that embedding),
    then apply one orthogonal observation. The new emb_mean should be
    l2norm((1-alpha)*old + alpha*orthogonal)."""
    print("\n=== test_ewma_phase_active ===")
    threshold = 5  # small for test speed
    alpha = 0.10
    wm = _make_wm(_make_cfg(threshold=threshold, alpha=alpha))

    e_canonical, e_other = _orthogonal_pair(seed=42)
    # Bootstrap with e_canonical at create.
    p = np.zeros(3, dtype=np.float32)
    oid = wm.create_object(p_world=p, emb_vis=e_canonical, view_dir_cam=None,
                           label_topk=[("widget", 0.5)], crop=None)
    # Push hits up using e_canonical so emb_mean stays equal to e_canonical
    # (within float). Need to reach hits = threshold so the NEXT update
    # is the first EWMA one.
    while wm.get(oid).hits < threshold:
        wm.update_object(oid, _make_obs(p, e_canonical))
    assert wm.get(oid).hits == threshold
    # emb_mean should still be ~ e_canonical
    pre = wm.get(oid).emb_mean.copy()
    assert float(np.dot(pre, e_canonical)) > 0.999

    # The next update is the first EWMA one (hits=threshold, threshold ==
    # threshold -> hits < threshold is False -> EWMA branch).
    wm.update_object(oid, _make_obs(p, e_other))
    post = wm.get(oid).emb_mean
    expected = _l2norm((1.0 - alpha) * pre + alpha * e_other)
    cos = float(np.dot(post, expected))
    assert cos > 0.9999, f"EWMA formula mismatch: cos={cos:.6f}"
    print(f"  OK: post emb_mean matches EWMA closed form (cos={cos:.6f})")


def test_phase_boundary_is_threshold():
    """At hits == threshold-1, the next update is the LAST running-mean
    update (so post-update hits == threshold but the math was running
    mean). At hits == threshold, the next update is the FIRST EWMA
    update. Verify by checking the cosine signature of each."""
    print("\n=== test_phase_boundary_is_threshold ===")
    threshold = 5
    alpha = 0.10
    cfg = _make_cfg(threshold=threshold, alpha=alpha)
    wm = _make_wm(cfg)
    e_canonical, e_other = _orthogonal_pair(seed=7)
    p = np.zeros(3, dtype=np.float32)

    # Bootstrap so hits = threshold-1 with emb_mean very close to e_canonical
    oid = wm.create_object(p_world=p, emb_vis=e_canonical, view_dir_cam=None,
                           label_topk=[("widget", 0.5)], crop=None)
    while wm.get(oid).hits < threshold - 1:
        wm.update_object(oid, _make_obs(p, e_canonical))
    assert wm.get(oid).hits == threshold - 1

    # Test 1: at hits=threshold-1, applying e_other should still be
    # running mean. Closed form: l2norm(emb_mean*hits + e_other)
    pre = wm.get(oid).emb_mean.copy()
    pre_hits = wm.get(oid).hits
    wm.update_object(oid, _make_obs(p, e_other))
    expected_rm = _l2norm(pre * pre_hits + e_other)
    cos_rm = float(np.dot(wm.get(oid).emb_mean, expected_rm))
    assert cos_rm > 0.9999, (
        f"at hits=threshold-1, expected last running-mean update "
        f"(cos with running-mean formula={cos_rm:.6f})"
    )

    # Test 2: hits is now threshold. Next update should be EWMA.
    assert wm.get(oid).hits == threshold
    pre2 = wm.get(oid).emb_mean.copy()
    wm.update_object(oid, _make_obs(p, e_other))
    expected_ewma = _l2norm((1.0 - alpha) * pre2 + alpha * e_other)
    cos_ewma = float(np.dot(wm.get(oid).emb_mean, expected_ewma))
    # Also verify it does NOT match the running-mean prediction
    expected_rm_wrong = _l2norm(pre2 * threshold + e_other)
    cos_rm_wrong = float(np.dot(wm.get(oid).emb_mean, expected_rm_wrong))
    assert cos_ewma > 0.9999, (
        f"at hits=threshold, expected EWMA (cos with EWMA={cos_ewma:.6f})"
    )
    assert cos_ewma > cos_rm_wrong, (
        f"EWMA prediction ({cos_ewma:.6f}) should fit better than "
        f"running-mean prediction ({cos_rm_wrong:.6f})"
    )
    print(f"  OK: last running mean at hits-1, first EWMA at hits "
          f"(cos_rm={cos_rm:.6f} cos_ewma={cos_ewma:.6f})")


def test_output_always_l2_normalized():
    """Every emb_mean after every update is unit-norm. Tests both phases."""
    print("\n=== test_output_always_l2_normalized ===")
    threshold = 5
    wm = _make_wm(_make_cfg(threshold=threshold, alpha=0.05))
    oid, _ = _seed_object(wm)
    p = np.zeros(3, dtype=np.float32)
    # Run 30 updates (spans both phases)
    for i in range(30):
        wm.update_object(oid, _make_obs(p, _emb(seed=200 + i)))
        n = float(np.linalg.norm(wm.get(oid).emb_mean))
        assert abs(n - 1.0) < 1e-5, (
            f"emb_mean not unit-norm after update {i}: |emb|={n:.8f}"
        )
    print(f"  OK: emb_mean stays unit-norm across 30 updates "
          f"(spans hits=2..31, threshold={threshold})")


def test_anti_ossification():
    """The main reason for the patch. At hits=200 with constant emb,
    a single orthogonal observation should shift emb_mean meaningfully
    under the new EWMA branch but barely at all under the old running-
    mean behavior. Measured as cos(new_mean, orthogonal_observation):
    EWMA at alpha=0.05 yields ~0.05; running mean at hits=201 yields
    ~1/201 ~= 0.005."""
    print("\n=== test_anti_ossification ===")
    threshold = 20
    alpha = 0.05
    wm = _make_wm(_make_cfg(threshold=threshold, alpha=alpha))

    e_canonical, e_other = _orthogonal_pair(seed=99)
    p = np.zeros(3, dtype=np.float32)
    oid = wm.create_object(p_world=p, emb_vis=e_canonical, view_dir_cam=None,
                           label_topk=[("widget", 0.5)], crop=None)
    # 200 updates with the same emb -> emb_mean stays ~ e_canonical.
    # hits ends at 201.
    for _ in range(200):
        wm.update_object(oid, _make_obs(p, e_canonical))
    assert wm.get(oid).hits == 201
    assert float(np.dot(wm.get(oid).emb_mean, e_canonical)) > 0.999

    # One orthogonal observation.
    wm.update_object(oid, _make_obs(p, e_other))
    shift = float(np.dot(wm.get(oid).emb_mean, e_other))
    # EWMA prediction is alpha exactly (since e_canonical ⊥ e_other and the
    # post-EWMA vector projected onto e_other is alpha/norm). With alpha
    # = 0.05 and (1-alpha)*1 = 0.95, the norm is sqrt(0.95^2+0.05^2)~=0.9513
    # so the projected cosine is 0.05/0.9513 ~= 0.0526.
    expected_ewma_shift = alpha / np.sqrt((1 - alpha) ** 2 + alpha ** 2)
    expected_rm_shift = 1.0 / np.sqrt(201.0 ** 2 + 1.0)  # ~ 1/201
    # Tighter: shift should be close to EWMA prediction, NOT to running mean.
    assert abs(shift - expected_ewma_shift) < 0.005, (
        f"shift {shift:.4f} not near EWMA prediction {expected_ewma_shift:.4f}"
    )
    assert shift > expected_rm_shift * 5, (
        f"shift {shift:.4f} is not meaningfully larger than running-mean "
        f"prediction {expected_rm_shift:.5f} (would indicate ossification)"
    )
    print(f"  OK: orthogonal obs moves emb_mean by {shift:.4f} "
          f"(EWMA pred {expected_ewma_shift:.4f}, "
          f"running-mean pred {expected_rm_shift:.5f})")


def test_alpha_configurable():
    """Changing object.emb_mean_ewma_alpha changes the EWMA weight."""
    print("\n=== test_alpha_configurable ===")
    threshold = 3

    def shift_for_alpha(alpha):
        wm = _make_wm(_make_cfg(threshold=threshold, alpha=alpha))
        e_canonical, e_other = _orthogonal_pair(seed=11)
        p = np.zeros(3, dtype=np.float32)
        oid = wm.create_object(p_world=p, emb_vis=e_canonical,
                               view_dir_cam=None,
                               label_topk=[("widget", 0.5)], crop=None)
        while wm.get(oid).hits < threshold:
            wm.update_object(oid, _make_obs(p, e_canonical))
        wm.update_object(oid, _make_obs(p, e_other))
        return float(np.dot(wm.get(oid).emb_mean, e_other))

    s_low = shift_for_alpha(0.02)
    s_high = shift_for_alpha(0.20)
    assert s_high > s_low * 5, (
        f"larger alpha should produce larger shift: low={s_low:.4f} "
        f"high={s_high:.4f}"
    )
    print(f"  OK: alpha=0.02 -> shift={s_low:.4f}, "
          f"alpha=0.20 -> shift={s_high:.4f}")


def test_threshold_configurable():
    """Changing object.emb_mean_hits_threshold actually changes the
    phase boundary. With threshold=2, the second update is already
    EWMA. With threshold=10, it's still running mean."""
    print("\n=== test_threshold_configurable ===")
    alpha = 0.10
    e_canonical, e_other = _orthogonal_pair(seed=13)
    p = np.zeros(3, dtype=np.float32)

    # threshold=2: hits start at 1 after create. After one obs, hits=2,
    # so hits < 2 is False -> EWMA branch chosen.
    wm_low = _make_wm(_make_cfg(threshold=2, alpha=alpha))
    oid_low = wm_low.create_object(p_world=p, emb_vis=e_canonical,
                                   view_dir_cam=None,
                                   label_topk=[("widget", 0.5)], crop=None)
    wm_low.update_object(oid_low, _make_obs(p, e_other))
    # First post-create update at threshold=2: hits=1 so 1<2 -> running
    # mean. emb_mean = l2norm(e_canonical*1 + e_other) ~ equal weight.
    cos_rm = float(np.dot(wm_low.get(oid_low).emb_mean,
                          _l2norm(e_canonical + e_other)))
    assert cos_rm > 0.999, f"threshold=2 first update should be running mean"

    # threshold=10: same single update should also be running mean.
    wm_high = _make_wm(_make_cfg(threshold=10, alpha=alpha))
    oid_high = wm_high.create_object(p_world=p, emb_vis=e_canonical,
                                     view_dir_cam=None,
                                     label_topk=[("widget", 0.5)], crop=None)
    wm_high.update_object(oid_high, _make_obs(p, e_other))
    cos_rm2 = float(np.dot(wm_high.get(oid_high).emb_mean,
                           _l2norm(e_canonical + e_other)))
    assert cos_rm2 > 0.999, f"threshold=10 first update should be running mean"

    # Now drive both to hits=4. Under threshold=2, updates 2,3,4 are EWMA.
    # Under threshold=10, they're running mean. Use a fresh pair each
    # time to amplify divergence.
    while wm_low.get(oid_low).hits < 4:
        wm_low.update_object(oid_low, _make_obs(p, e_other))
    while wm_high.get(oid_high).hits < 4:
        wm_high.update_object(oid_high, _make_obs(p, e_other))
    # Both should now be pulled toward e_other, but by different amounts.
    sim_low_to_other = float(np.dot(wm_low.get(oid_low).emb_mean, e_other))
    sim_high_to_other = float(np.dot(wm_high.get(oid_high).emb_mean, e_other))
    # Under running mean at hits=4, mean is l2norm(e_canonical + 3*e_other);
    # cosine with e_other is 3/sqrt(10) ~= 0.949.
    # Under threshold=2, the trajectory is mostly EWMA at alpha=0.10 so it
    # converges much more slowly. Should be lower.
    assert sim_high_to_other > sim_low_to_other, (
        f"At threshold=10 (all running mean), should pull harder toward "
        f"e_other than threshold=2 (mostly EWMA): "
        f"high={sim_high_to_other:.4f} low={sim_low_to_other:.4f}"
    )
    print(f"  OK: threshold gates the boundary "
          f"(low={sim_low_to_other:.4f}, high={sim_high_to_other:.4f})")


def test_default_back_compat():
    """If rtsm.yaml lacks the new knobs, defaults take over. The defaults
    are the original Gate 2.5 spec values."""
    print("\n=== test_default_back_compat ===")
    wm = _make_wm(_make_cfg(omit_knobs=True))
    assert wm.emb_mean_hits_threshold == 20, (
        f"default threshold should be 20, got {wm.emb_mean_hits_threshold}"
    )
    assert abs(wm.emb_mean_ewma_alpha - 0.05) < 1e-9, (
        f"default alpha should be 0.05, got {wm.emb_mean_ewma_alpha}"
    )
    print(f"  OK: defaults are threshold=20, alpha=0.05 (Gate 2.5 spec)")


if __name__ == "__main__":
    test_running_mean_phase()
    test_ewma_phase_active()
    test_phase_boundary_is_threshold()
    test_output_always_l2_normalized()
    test_anti_ossification()
    test_alpha_configurable()
    test_threshold_configurable()
    test_default_back_compat()
    print("\nAll emb_mean hybrid tests passed.")
