import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.track_io import load_track
from src.core.models import Effect, EdgeStatus
from src.core import constants as K

TINY = os.path.join(os.path.dirname(__file__), "data", "tiny.json")


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.g = load_track(TINY)

    def test_presets_sum_to_one(self):
        for name, w in K.PRESETS.items():
            self.assertAlmostEqual(sum(w), 1.0, msg=name)
            self.assertTrue(all(x >= 0 for x in w))

    def test_adjacency_and_blocking(self):
        n0 = {nb for _, nb in self.g.neighbors(1)}
        self.assertIn(0, n0); self.assertIn(2, n0)          # undirected
        v = self.g.version
        self.g.block_edge(0)
        self.assertNotIn(0, {nb for _, nb in self.g.neighbors(1)})
        self.assertGreater(self.g.version, v)
        self.g.unblock_edge(0)
        self.assertIn(0, {nb for _, nb in self.g.neighbors(1)})

    def test_directed_edge(self):
        self.assertIn(3, {nb for _, nb in self.g.neighbors(0)})
        self.assertNotIn(0, {nb for _, nb in self.g.neighbors(3)})

    def test_overlapping_effects_independent(self):
        e = self.g.edges[1]
        self.g.add_effect(1, Effect(1, "speed_cap", 0.6))
        self.g.add_effect(1, Effect(2, "oil", 2))
        self.assertAlmostEqual(self.g.speed_factor(e), 0.6)       # strictest cap
        self.assertEqual(self.g.effective_difficulty(e), 3)
        self.g.remove_effect(1, 1)                                # expire speed cap only
        self.assertAlmostEqual(self.g.speed_factor(e), K.OIL_SPEED_FACTOR)   # oil still active
        self.assertEqual(self.g.effective_difficulty(e), 3)
        self.g.remove_effect(1, 2)
        self.assertAlmostEqual(self.g.speed_factor(e), 1.0)

    def test_cost_nonnegative_and_effects_raise_cost(self):
        for p in K.PRESETS:
            for e in self.g.edges.values():
                self.assertGreaterEqual(self.g.edge_cost(e, p), 0)
        e = self.g.edges[1]; before = self.g.edge_cost(e)
        self.g.add_effect(1, Effect(9, "oil", 2))
        self.assertGreater(self.g.edge_cost(e), before)

    def test_restricted_costs_more(self):
        e = self.g.edges[0]; before = self.g.edge_cost(e)
        self.g.set_status(0, EdgeStatus.RESTRICTED)
        self.assertGreater(self.g.edge_cost(e), before)
        self.assertIn(0, [x.id for x, _ in self.g.neighbors(0)])   # still traversable

    def test_heuristic_is_lower_bound(self):
        self.assertEqual(self.g.validate_geometry(), [])
        for p in K.PRESETS:
            r = self.g.heuristic_ratio(p)
            for e in self.g.edges.values():
                self.assertLessEqual(r * e.distance, self.g.edge_cost(e, p) + 1e-9)

    def test_fuel_multiplier(self):
        self.assertAlmostEqual(K.difficulty_multiplier(1), 1.0)
        self.assertAlmostEqual(K.difficulty_multiplier(5), 1.4)

    def test_ordered_checkpoints(self):
        self.assertEqual(self.g.checkpoints_in_order(), [1])


if __name__ == "__main__":
    unittest.main()
