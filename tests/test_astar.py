import os, random, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.graph import Graph
from src.core.models import Vertex, Edge, VertexType, Effect
from src.core.track_io import load_track
from src.core import constants as K
from src.routing.api import astar, dijkstra

TINY = os.path.join(os.path.dirname(__file__), "data", "tiny.json")


def grid_graph(n=10, seed=1):
    """n x n grid, edge distance >= straight line, random times/fuel/difficulty. Reproducible."""
    rnd = random.Random(seed)
    g = Graph("grid")
    for r in range(n):
        for c in range(n):
            g.add_vertex(Vertex(r * n + c, c * 10.0, r * 10.0, VertexType.INTERSECTION))
    eid = 0
    for r in range(n):
        for c in range(n):
            for dr, dc in ((0, 1), (1, 0)):
                r2, c2 = r + dr, c + dc
                if r2 < n and c2 < n:
                    dist = 10.0 * rnd.uniform(1.0, 1.6)
                    g.add_edge(Edge(eid, r * n + c, r2 * n + c2, dist, dist * rnd.uniform(0.5, 1.5),
                                    dist * rnd.uniform(0.2, 0.8), rnd.randint(1, 5)))
                    eid += 1
    g.finalize()
    return g


class AStarTests(unittest.TestCase):
    def setUp(self):
        self.g = load_track(TINY)

    def test_geometry_is_valid_so_heuristic_is_admissible(self):
        self.assertEqual(self.g.validate_geometry(), [])
        self.assertEqual(grid_graph().validate_geometry(), [])

    def test_matches_dijkstra_tiny_all_pairs_all_presets(self):
        for preset in K.PRESETS:
            for s in self.g.vertices:
                for t in self.g.vertices:
                    a, d = astar(self.g, s, t, preset), dijkstra(self.g, s, t, preset)
                    self.assertEqual(a.found, d.found, (s, t, preset))
                    if d.found:
                        self.assertAlmostEqual(a.cost, d.cost, msg=(s, t, preset))

    def test_matches_dijkstra_on_random_grid_pairs(self):
        g = grid_graph(10, seed=7)
        rnd = random.Random(99)
        n = len(g.vertices)
        for _ in range(60):
            s, t = rnd.randrange(n), rnd.randrange(n)
            for preset in K.PRESETS:
                a, d = astar(g, s, t, preset), dijkstra(g, s, t, preset)
                self.assertTrue(a.found and d.found)
                self.assertAlmostEqual(a.cost, d.cost, msg=(s, t, preset))

    def test_still_optimal_after_blocks_and_effects(self):
        g = grid_graph(8, seed=3)
        rnd = random.Random(5)
        for eid in rnd.sample(list(g.edges), 12):
            g.block_edge(eid)
        for k, eid in enumerate(rnd.sample(list(g.edges), 10)):
            g.add_effect(eid, Effect(k, "oil", 2))
            g.add_effect(eid, Effect(100 + k, "speed_cap", 0.6))
        n = len(g.vertices)
        for _ in range(40):
            s, t = rnd.randrange(n), rnd.randrange(n)
            a, d = astar(g, s, t, "Speed"), dijkstra(g, s, t, "Speed")
            self.assertEqual(a.found, d.found)
            if d.found:
                self.assertAlmostEqual(a.cost, d.cost)

    def test_expands_fewer_vertices_than_dijkstra_overall(self):
        g = grid_graph(15, seed=11)
        rnd = random.Random(2)
        n = len(g.vertices)
        a_total = d_total = 0
        for _ in range(40):
            s, t = rnd.randrange(n), rnd.randrange(n)
            a_total += astar(g, s, t, "Balanced").expanded
            d_total += dijkstra(g, s, t, "Balanced").expanded
        self.assertLess(a_total, d_total)

    def test_source_equals_target_and_unreachable_and_unknown(self):
        r = astar(self.g, 2, 2)
        self.assertTrue(r.found)
        self.assertEqual(r.cost, 0.0)
        self.g.block_edge(0)
        self.g.block_edge(3)
        self.assertFalse(astar(self.g, 0, 3).found)
        self.assertFalse(astar(self.g, 0, 99).found)

    def test_counters(self):
        r = astar(self.g, 0, 3)
        self.assertGreater(r.expanded, 0)
        self.assertGreater(r.relaxed, 0)
        self.assertGreater(r.heap_ops, 0)

    def test_deterministic(self):
        g = grid_graph(8, seed=4)
        first = astar(g, 0, 63, "Economy")
        for _ in range(3):
            self.assertEqual(astar(g, 0, 63, "Economy").vertices, first.vertices)


if __name__ == "__main__":
    unittest.main()
