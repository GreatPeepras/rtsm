"""Unit tests for WorkingMemory.find_fragments (added 2026-06-11).

Per-anchor merge-candidate search with adaptive distance threshold and
pose_state filter. See find_fragments_design_2026-06-11.md.

Container-side run:
    docker exec -w /workspace/rtsm rtsm-dev \\
        python3 -m unittest tests.test_find_fragments -v

The real ObjectState requires CLIP/FAISS init at construction; for unit
tests we populate WorkingMemory._map directly with SimpleNamespace
stand-ins that carry only the fields find_fragments actually reads. That
keeps the test fast and isolated from the full subsystem.
"""

from __future__ import annotations

import copy
import threading
import time
import unittest
from types import SimpleNamespace
from typing import Optional

import numpy as np

from rtsm.stores.working_memory import WorkingMemory


def _unit_emb(theta_deg: float) -> np.ndarray:
    """Return a deterministic 2D-on-the-fly L2-normalized vector embedded
    in a higher-D space. The first two dims encode the angle; the rest is
    zero. Two embeddings produced with the same theta have cosine 1.0;
    two produced 90 degrees apart have cosine 0.0.

    Real embeddings are 384/512/768-D; we use 16-D here because
    find_fragments doesn't care about the actual dimensionality so long
    as anchor and candidates match.
    """
    t = np.deg2rad(theta_deg)
    v = np.zeros(16, dtype=np.float32)
    v[0] = float(np.cos(t))
    v[1] = float(np.sin(t))
    # Already unit-length since cos^2 + sin^2 = 1.
    return v


def _mk_object(
    *,
    oid: str,
    emb_theta_deg: float = 0.0,
    xyz: tuple = (0.0, 0.0, 0.0),
    label_user: Optional[str] = None,
    label_primary: str = "unknown",
    movability_class: Optional[str] = None,
    hits: int = 1,
    stability: float = 0.5,
    reference_image_path: Optional[str] = None,
    confirmed: bool = True,
    pose_state_at_observation: str = "on_floor",
    last_seen_wall_utc: Optional[float] = None,
) -> SimpleNamespace:
    """Construct a minimal ObjectState stand-in for find_fragments."""
    return SimpleNamespace(
        id=oid,
        emb_mean=_unit_emb(emb_theta_deg),
        xyz_world=np.array(xyz, dtype=np.float32),
        label_user=label_user,
        label_primary=label_primary,
        movability_class=movability_class,
        hits=hits,
        stability=stability,
        reference_image_path=reference_image_path,
        confirmed=confirmed,
        pose_state_at_observation=pose_state_at_observation,
        last_seen_wall_utc=(last_seen_wall_utc if last_seen_wall_utc is not None else time.time()),
    )


def _fresh_wm() -> WorkingMemory:
    """Bypass __init__ side effects (file I/O, CLIP loading, etc.) by
    using __new__ + manual attribute setup. find_fragments only touches
    self._lock and self._map.
    """
    wm = WorkingMemory.__new__(WorkingMemory)
    wm._lock = threading.RLock()
    wm._map = {}
    return wm


class FindFragmentsTests(unittest.TestCase):

    # ------------------------------------------------------------------
    # 1. Anchor lookup
    # ------------------------------------------------------------------

    def test_unknown_anchor_returns_not_found(self):
        wm = _fresh_wm()
        wm._map["aaaaaaaaaaaa0001"] = _mk_object(oid="aaaaaaaaaaaa0001")
        result = wm.find_fragments(anchor_oid="ffffffffffffffff")
        self.assertEqual(result, {"error": "not_found", "id": "ffffffffffffffff"})

    def test_empty_pool_returns_empty_fragments(self):
        wm = _fresh_wm()
        wm._map["aaaaaaaaaaaa0001"] = _mk_object(
            oid="aaaaaaaaaaaa0001", movability_class="movable",
        )
        result = wm.find_fragments(anchor_oid="aaaaaaaaaaaa0001")
        self.assertEqual(result["fragments"], [])
        self.assertEqual(result["scanned_objects"], 0)
        self.assertEqual(result["returned"], 0)
        self.assertEqual(result["total_above_thresholds"], 0)
        self.assertEqual(result["anchor"]["oid"], "aaaaaaaaaaaa0001")

    # ------------------------------------------------------------------
    # 2. Adaptive distance defaults
    # ------------------------------------------------------------------

    def test_adaptive_default_for_movable(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", movability_class="movable")
        wm._map["b"] = _mk_object(oid="b", xyz=(8.0, 0.0, 0.0))  # within 9m
        result = wm.find_fragments(anchor_oid="a")
        self.assertEqual(result["thresholds"]["dist_threshold_m"], 9.0)
        self.assertTrue(result["thresholds"]["dist_threshold_default_used"])
        self.assertEqual(len(result["fragments"]), 1)
        self.assertEqual(result["fragments"][0]["oid"], "b")

    def test_adaptive_default_for_static(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", movability_class="static")
        # b is 2.5m away from anchor — inside 3m default for static.
        wm._map["b"] = _mk_object(oid="b", xyz=(2.5, 0.0, 0.0))
        # c is 4m away — outside 3m default for static.
        wm._map["c"] = _mk_object(oid="c", xyz=(4.0, 0.0, 0.0))
        result = wm.find_fragments(anchor_oid="a")
        self.assertEqual(result["thresholds"]["dist_threshold_m"], 3.0)
        oids = [f["oid"] for f in result["fragments"]]
        self.assertIn("b", oids)
        self.assertNotIn("c", oids)

    def test_adaptive_default_for_semi_static(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", movability_class="semi_static")
        result = wm.find_fragments(anchor_oid="a")
        self.assertEqual(result["thresholds"]["dist_threshold_m"], 3.0)

    def test_adaptive_fallback_for_unset_class(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", movability_class=None)
        result = wm.find_fragments(anchor_oid="a")
        self.assertEqual(result["thresholds"]["dist_threshold_m"], 5.0)
        self.assertTrue(result["thresholds"]["dist_threshold_default_used"])

    def test_explicit_dist_overrides_default(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", movability_class="movable")
        wm._map["b"] = _mk_object(oid="b", xyz=(8.0, 0.0, 0.0))
        result = wm.find_fragments(anchor_oid="a", dist_threshold_m=1.0)
        self.assertEqual(result["thresholds"]["dist_threshold_m"], 1.0)
        self.assertFalse(result["thresholds"]["dist_threshold_default_used"])
        # b at 8m is now outside the 1m gate.
        self.assertEqual(result["fragments"], [])

    # ------------------------------------------------------------------
    # 3. Cosine threshold and ordering
    # ------------------------------------------------------------------

    def test_cos_below_threshold_excluded(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", emb_theta_deg=0.0, movability_class="movable")
        # 45deg apart: cosine = cos(45) ~= 0.707
        wm._map["b"] = _mk_object(oid="b", emb_theta_deg=45.0)
        result = wm.find_fragments(anchor_oid="a", cos_threshold=0.85)
        self.assertEqual(result["fragments"], [])

    def test_fragments_sorted_by_cosine_desc_then_distance_asc(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", emb_theta_deg=0.0, movability_class="movable")
        # All within 9m, all above cos 0.85. Different cosines so the sort is unambiguous.
        wm._map["b"] = _mk_object(oid="b", emb_theta_deg=10.0, xyz=(1.0, 0.0, 0.0))  # cos ~0.985
        wm._map["c"] = _mk_object(oid="c", emb_theta_deg=20.0, xyz=(0.5, 0.0, 0.0))  # cos ~0.940
        wm._map["d"] = _mk_object(oid="d", emb_theta_deg=5.0,  xyz=(2.0, 0.0, 0.0))  # cos ~0.996
        result = wm.find_fragments(anchor_oid="a")
        oids = [f["oid"] for f in result["fragments"]]
        # Expected: d (cos 0.996), b (cos 0.985), c (cos 0.940)
        self.assertEqual(oids, ["d", "b", "c"])

    def test_limit_truncates_after_sort(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", emb_theta_deg=0.0, movability_class="movable")
        wm._map["b"] = _mk_object(oid="b", emb_theta_deg=10.0, xyz=(1.0, 0.0, 0.0))
        wm._map["c"] = _mk_object(oid="c", emb_theta_deg=20.0, xyz=(0.5, 0.0, 0.0))
        wm._map["d"] = _mk_object(oid="d", emb_theta_deg=5.0,  xyz=(2.0, 0.0, 0.0))
        result = wm.find_fragments(anchor_oid="a", limit=2)
        self.assertEqual(result["returned"], 2)
        self.assertEqual(result["total_above_thresholds"], 3)
        # Highest two cosines kept.
        self.assertEqual([f["oid"] for f in result["fragments"]], ["d", "b"])

    # ------------------------------------------------------------------
    # 4. Filter flags
    # ------------------------------------------------------------------

    def test_exclude_named_filters_pinned_oids(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", emb_theta_deg=0.0, movability_class="movable")
        wm._map["b"] = _mk_object(oid="b", emb_theta_deg=5.0, xyz=(1.0, 0.0, 0.0),
                                  label_user=None)
        wm._map["c"] = _mk_object(oid="c", emb_theta_deg=5.0, xyz=(1.0, 0.0, 0.0),
                                  label_user="basketball 2")
        result_default = wm.find_fragments(anchor_oid="a")
        result_filtered = wm.find_fragments(anchor_oid="a", exclude_named=True)
        oids_default = {f["oid"] for f in result_default["fragments"]}
        oids_filtered = {f["oid"] for f in result_filtered["fragments"]}
        self.assertEqual(oids_default, {"b", "c"})
        self.assertEqual(oids_filtered, {"b"})

    def test_include_unconfirmed_false_filters_protos(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", emb_theta_deg=0.0, movability_class="movable")
        wm._map["b"] = _mk_object(oid="b", emb_theta_deg=5.0, xyz=(1.0, 0.0, 0.0),
                                  confirmed=True)
        wm._map["c"] = _mk_object(oid="c", emb_theta_deg=5.0, xyz=(1.0, 0.0, 0.0),
                                  confirmed=False)
        # Default include_unconfirmed=True
        result_default = wm.find_fragments(anchor_oid="a")
        # Override to False
        result_strict = wm.find_fragments(anchor_oid="a", include_unconfirmed=False)
        self.assertEqual({f["oid"] for f in result_default["fragments"]}, {"b", "c"})
        self.assertEqual({f["oid"] for f in result_strict["fragments"]}, {"b"})

    # ------------------------------------------------------------------
    # 5. pose_state filter
    # ------------------------------------------------------------------

    def test_pose_state_any_surfaces_both_buckets(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", emb_theta_deg=0.0, movability_class="movable",
                                  pose_state_at_observation="on_floor")
        wm._map["b"] = _mk_object(oid="b", emb_theta_deg=5.0, xyz=(1.0, 0.0, 0.0),
                                  pose_state_at_observation="on_floor")
        wm._map["c"] = _mk_object(oid="c", emb_theta_deg=5.0, xyz=(1.0, 0.0, 0.7),
                                  pose_state_at_observation="elevated")
        result = wm.find_fragments(anchor_oid="a", pose_state="any")
        self.assertEqual({f["oid"] for f in result["fragments"]}, {"b", "c"})
        self.assertEqual(result["thresholds"]["pose_state"], "any")
        self.assertEqual(result["thresholds"]["pose_state_resolved"], "any")

    def test_pose_state_match_anchor_filters_to_anchor_bucket(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", emb_theta_deg=0.0, movability_class="movable",
                                  pose_state_at_observation="on_floor")
        wm._map["b"] = _mk_object(oid="b", emb_theta_deg=5.0, xyz=(1.0, 0.0, 0.0),
                                  pose_state_at_observation="on_floor")
        wm._map["c"] = _mk_object(oid="c", emb_theta_deg=5.0, xyz=(1.0, 0.0, 0.7),
                                  pose_state_at_observation="elevated")
        result = wm.find_fragments(anchor_oid="a", pose_state="match_anchor")
        self.assertEqual({f["oid"] for f in result["fragments"]}, {"b"})
        self.assertEqual(result["thresholds"]["pose_state"], "match_anchor")
        self.assertEqual(result["thresholds"]["pose_state_resolved"], "on_floor")

    def test_pose_state_on_floor_filters_elevated(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", emb_theta_deg=0.0, movability_class="movable",
                                  pose_state_at_observation="elevated")
        wm._map["b"] = _mk_object(oid="b", emb_theta_deg=5.0, xyz=(1.0, 0.0, 0.0),
                                  pose_state_at_observation="on_floor")
        wm._map["c"] = _mk_object(oid="c", emb_theta_deg=5.0, xyz=(1.0, 0.0, 0.5),
                                  pose_state_at_observation="elevated")
        result = wm.find_fragments(anchor_oid="a", pose_state="on_floor")
        self.assertEqual({f["oid"] for f in result["fragments"]}, {"b"})

    def test_invalid_pose_state_raises(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", movability_class="movable")
        with self.assertRaises(ValueError):
            wm.find_fragments(anchor_oid="a", pose_state="floating")

    # ------------------------------------------------------------------
    # 6. Response shape
    # ------------------------------------------------------------------

    def test_response_shape_anchor_block(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(
            oid="a", emb_theta_deg=0.0, xyz=(1.0, 2.0, 3.0),
            label_user="basketball", label_primary="ball",
            movability_class="movable",
            hits=12, stability=0.85,
            reference_image_path="/refs/a.jpg",
            confirmed=True,
            pose_state_at_observation="on_floor",
        )
        result = wm.find_fragments(anchor_oid="a")
        a = result["anchor"]
        self.assertEqual(a["oid"], "a")
        self.assertEqual(a["label_user"], "basketball")
        self.assertEqual(a["label_primary"], "ball")
        self.assertEqual(a["movability_class"], "movable")
        self.assertEqual(a["xyz"], [1.0, 2.0, 3.0])
        self.assertEqual(a["hits"], 12)
        self.assertEqual(a["stability"], 0.85)
        self.assertTrue(a["has_reference"])
        self.assertTrue(a["confirmed"])
        self.assertEqual(a["pose_state_at_observation"], "on_floor")

    def test_response_shape_fragment(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", emb_theta_deg=0.0, movability_class="movable")
        wm._map["b"] = _mk_object(
            oid="b", emb_theta_deg=10.0, xyz=(1.0, 2.0, 3.0),
            label_user=None, label_primary="ball",
            movability_class="movable",
            hits=3, stability=0.6,
            reference_image_path=None,
            confirmed=True,
            pose_state_at_observation="elevated",
        )
        result = wm.find_fragments(anchor_oid="a")
        self.assertEqual(len(result["fragments"]), 1)
        f = result["fragments"][0]
        self.assertEqual(f["oid"], "b")
        self.assertIsNone(f["label_user"])
        self.assertEqual(f["label_primary"], "ball")
        self.assertEqual(f["movability_class"], "movable")
        self.assertIn("cosine", f)
        self.assertIn("distance_m", f)
        self.assertEqual(f["hits"], 3)
        self.assertEqual(f["stability"], 0.6)
        self.assertFalse(f["has_reference"])
        self.assertTrue(f["confirmed"])
        self.assertEqual(f["pose_state_at_observation"], "elevated")
        self.assertEqual(f["xyz"], [1.0, 2.0, 3.0])

    # ------------------------------------------------------------------
    # 7. Read-only invariant
    # ------------------------------------------------------------------

    def test_read_only_does_not_mutate_map(self):
        wm = _fresh_wm()
        wm._map["a"] = _mk_object(oid="a", emb_theta_deg=0.0, movability_class="movable")
        wm._map["b"] = _mk_object(oid="b", emb_theta_deg=5.0, xyz=(1.0, 0.0, 0.0))
        wm._map["c"] = _mk_object(oid="c", emb_theta_deg=180.0, xyz=(50.0, 0.0, 0.0))

        # Snapshot the map state pre-call.
        pre_oids = sorted(wm._map.keys())
        pre_emb_a = wm._map["a"].emb_mean.copy()
        pre_xyz_b = wm._map["b"].xyz_world.copy()
        pre_hits_b = wm._map["b"].hits

        _ = wm.find_fragments(anchor_oid="a", pose_state="any")
        _ = wm.find_fragments(anchor_oid="a", exclude_named=True)
        _ = wm.find_fragments(anchor_oid="a", dist_threshold_m=0.5)

        post_oids = sorted(wm._map.keys())
        self.assertEqual(pre_oids, post_oids)
        np.testing.assert_array_equal(pre_emb_a, wm._map["a"].emb_mean)
        np.testing.assert_array_equal(pre_xyz_b, wm._map["b"].xyz_world)
        self.assertEqual(pre_hits_b, wm._map["b"].hits)


if __name__ == "__main__":
    unittest.main()
