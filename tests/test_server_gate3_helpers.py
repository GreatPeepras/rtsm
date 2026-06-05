"""Unit tests for server.py Gate 3 helpers — 2026-05-26.

Covers the four small helpers added to enable richer /search/semantic
and /search/spatial responses:

  * _display_label(o)            — gated label_user>label_primary
  * _robot_xyz(robot_pose)       — defensive 3-vec extraction
  * _distance_from_robot(a, b)   — euclidean, None-safe
  * _iso_from_wall_utc(t)        — UTC float to ISO-8601, None on 0/missing

The helpers are extracted from server.py by AST so the test doesn't need
to spin up FastAPI / FAISS / numpy WM machinery. Only numpy is imported
(the helpers use it directly).

These functions are nested in create_app() and close over `working_memory`
(for min_label_hits in _display_label). We pass a fake working_memory at
exec time.

Run:  pytest test_server_gate3_helpers.py -v
"""

from __future__ import annotations

import ast
import pathlib
import unittest
from types import SimpleNamespace
from datetime import datetime, timezone

import numpy as np


def _load_helpers():
    """Extract the four helpers from server.py and bind their closure."""
    src_path = pathlib.Path(__file__).resolve().parent / "server.py"
    if not src_path.exists():
        src_path = pathlib.Path("/mnt/project/server.py")

    tree = ast.parse(src_path.read_text())
    wanted = {"_display_label", "_robot_xyz",
              "_distance_from_robot", "_iso_from_wall_utc"}
    found: dict = {}

    def _walk(node):
        if isinstance(node, ast.FunctionDef) and node.name in wanted:
            found[node.name] = node
        for child in ast.iter_child_nodes(node):
            _walk(child)

    _walk(tree)
    missing = wanted - set(found)
    if missing:
        raise RuntimeError(f"Helpers not found in server.py: {missing}")

    # Build a module-shaped namespace and exec the helpers into it. They
    # close over `working_memory` and `np` and `datetime`/`timezone` — we
    # provide all four.
    fake_wm = SimpleNamespace(min_label_hits=5)
    ns = {
        "np": np,
        "datetime": datetime,
        "timezone": timezone,
        "working_memory": fake_wm,
        "Any": object,
        "Optional": type(None),  # we don't enforce types in tests
        "Dict": dict,
    }
    # Strip annotations to avoid `from typing import Optional` resolution
    # issues; behaviour is annotation-agnostic.
    for fn in found.values():
        fn.returns = None
        for a in fn.args.args:
            a.annotation = None

    mod = ast.Module(body=list(found.values()), type_ignores=[])
    exec(compile(mod, str(src_path), "exec"), ns)
    return ns, fake_wm


_NS, _FAKE_WM = _load_helpers()
_display_label = _NS["_display_label"]
_robot_xyz = _NS["_robot_xyz"]
_distance_from_robot = _NS["_distance_from_robot"]
_iso_from_wall_utc = _NS["_iso_from_wall_utc"]


# --------------------------------------------------------------------- #
# _display_label
# --------------------------------------------------------------------- #
class DisplayLabelTests(unittest.TestCase):

    def test_label_user_wins(self):
        o = SimpleNamespace(
            label_user="Quackers",
            label_primary="duck",
            label_scores={"duck": 0.9},
            label_hits={"duck": 100},
        )
        self.assertEqual(_display_label(o), "Quackers")

    def test_gated_argmax_when_no_user_label(self):
        o = SimpleNamespace(
            label_user=None,
            label_primary="bench",
            label_scores={"bench": 0.7, "stool": 0.6},
            label_hits={"bench": 10, "stool": 10},
        )
        self.assertEqual(_display_label(o), "bench")

    def test_falls_through_to_label_primary_when_no_gated_pass(self):
        # All hits below min_label_hits (=5) → gated dict empty, fallback.
        o = SimpleNamespace(
            label_user=None,
            label_primary="rare_thing",
            label_scores={"rare_thing": 0.9},
            label_hits={"rare_thing": 1},
        )
        self.assertEqual(_display_label(o), "rare_thing")

    def test_returns_none_on_completely_unlabeled(self):
        o = SimpleNamespace(
            label_user=None, label_primary=None,
            label_scores={}, label_hits={},
        )
        self.assertIsNone(_display_label(o))

    def test_empty_label_user_falls_through(self):
        # Empty string is falsy; treat same as None.
        o = SimpleNamespace(
            label_user="",
            label_primary="chair",
            label_scores={"chair": 0.8},
            label_hits={"chair": 20},
        )
        self.assertEqual(_display_label(o), "chair")

    def test_swallows_exception(self):
        class Bad:
            @property
            def label_user(self):
                raise RuntimeError("broken")
        self.assertIsNone(_display_label(Bad()))


# --------------------------------------------------------------------- #
# _robot_xyz
# --------------------------------------------------------------------- #
class RobotXyzTests(unittest.TestCase):

    def test_dict_with_xyz(self):
        out = _robot_xyz({"xyz": [1.0, 2.0, 3.0]})
        np.testing.assert_allclose(out, [1, 2, 3])

    def test_dict_with_position_alias(self):
        out = _robot_xyz({"position": [4.0, 5.0, 6.0]})
        np.testing.assert_allclose(out, [4, 5, 6])

    def test_list(self):
        out = _robot_xyz([7.0, 8.0, 9.0])
        np.testing.assert_allclose(out, [7, 8, 9])

    def test_tuple_longer_than_3(self):
        # Robot pose may include orientation; just take first 3 (xyz).
        out = _robot_xyz((1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 1.0))
        np.testing.assert_allclose(out, [1, 2, 3])

    def test_numpy_array(self):
        out = _robot_xyz(np.array([1.5, 2.5, 3.5]))
        np.testing.assert_allclose(out, [1.5, 2.5, 3.5])

    def test_none_returns_none(self):
        self.assertIsNone(_robot_xyz(None))

    def test_empty_dict_returns_none(self):
        self.assertIsNone(_robot_xyz({}))

    def test_short_sequence_returns_none(self):
        self.assertIsNone(_robot_xyz([1.0, 2.0]))

    def test_garbage_returns_none(self):
        self.assertIsNone(_robot_xyz("not-a-pose"))


# --------------------------------------------------------------------- #
# _distance_from_robot
# --------------------------------------------------------------------- #
class DistanceTests(unittest.TestCase):

    def test_simple(self):
        r = np.array([0.0, 0.0, 0.0])
        d = _distance_from_robot([3.0, 4.0, 0.0], r)
        self.assertAlmostEqual(d, 5.0, places=3)

    def test_3d_distance(self):
        r = np.array([1.0, 1.0, 1.0])
        d = _distance_from_robot([4.0, 5.0, 1.0], r)
        # sqrt(3^2 + 4^2 + 0^2) = 5
        self.assertAlmostEqual(d, 5.0, places=3)

    def test_zero_when_colocated(self):
        r = np.array([2.0, 3.0, 4.0])
        self.assertEqual(_distance_from_robot([2.0, 3.0, 4.0], r), 0.0)

    def test_none_obj_returns_none(self):
        self.assertIsNone(_distance_from_robot(None, np.array([0, 0, 0])))

    def test_none_robot_returns_none(self):
        self.assertIsNone(_distance_from_robot([1, 2, 3], None))

    def test_short_obj_returns_none(self):
        self.assertIsNone(_distance_from_robot([1, 2], np.array([0, 0, 0])))

    def test_rounded_to_3dp(self):
        # Make sure long decimals get rounded
        r = np.array([0.0, 0.0, 0.0])
        d = _distance_from_robot([1.0, 1.0, 1.0], r)
        # sqrt(3) ~= 1.7320508...  rounded to 1.732
        self.assertEqual(d, 1.732)


# --------------------------------------------------------------------- #
# _iso_from_wall_utc
# --------------------------------------------------------------------- #
class IsoTests(unittest.TestCase):

    def test_zero_returns_none(self):
        self.assertIsNone(_iso_from_wall_utc(0))

    def test_negative_returns_none(self):
        self.assertIsNone(_iso_from_wall_utc(-1.0))

    def test_none_returns_none(self):
        self.assertIsNone(_iso_from_wall_utc(None))

    def test_valid_epoch(self):
        # 2026-05-25T13:14:36Z — the morning session recording timestamp
        # from yesterday's handoff. round trip and check.
        ts = datetime(2026, 5, 25, 13, 14, 36, tzinfo=timezone.utc).timestamp()
        out = _iso_from_wall_utc(ts)
        self.assertIsNotNone(out)
        # Re-parse and compare
        parsed = datetime.fromisoformat(out)
        self.assertEqual(parsed.year, 2026)
        self.assertEqual(parsed.month, 5)
        self.assertEqual(parsed.day, 25)
        self.assertIn("+00:00", out)  # timezone-aware

    def test_garbage_returns_none(self):
        self.assertIsNone(_iso_from_wall_utc("not-a-time"))

    def test_float_input(self):
        out = _iso_from_wall_utc(1700000000.123)
        self.assertIsNotNone(out)
        self.assertIn("T", out)  # ISO marker


if __name__ == "__main__":
    unittest.main(verbosity=2)
