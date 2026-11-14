import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.graph import Graph
from src.core.models import Vertex, Edge, VertexType, Effect
from src.core.track_io import load_track
from src.core import constants as K
from src.routing.api import dijkstra

TINY = os.path.join(os.path.dirname(__file__), "data", "tiny.json")


def brute_force_best(g, s, t, preset):
    """Cheapest cost over ALL simple paths (only for tiny graphs)."""
    best = [float("inf")]

    def go(u, seen, cost):
        if u == t:
            best[0] = min(best[0], cost)
            return
        for e, v in g.neighbors(u):
            if v not in seen:
                go(v, seen | {v}, cost + g.edge_cost(e, preset))
    go(s, {s}, 0.0)
    return best[0]


def make_graph(vertices, edges):
    g = Graph("test")
    for i, (x, y) in enumerate(vertices):
        g.add_vertex(Vertex(i, x, y, VertexType.INTERSECTION))
    for i, (a, b, d, t, f, diff) in enumerate(edges):
        g.add_edge(Edge(i, a, b, d, t, f, diff))
    g.finalize()
    return g


class DijkstraTests(unittest.TestCase):
    def setUp(self):
        self.g = load_track(TINY)

    def test_matches_brute_force_all_pairs_all_presets(self):
        for preset in K.PRESETS:
            for s in self.g.vertices:
                for t in self.g.vertices:
                    r = dijkstra(self.g, s, t, preset)
                    best = brute_force_best(self.g, s, t, preset)
                    if best == float("inf"):
                        self.assertFalse(r.found, (s, t, preset))
                    else:
                        self.assertTrue(r.found, (s, t, preset))
                        self.assertAlmostEqual(r.cost, best, msg=(s, t, preset))

    def test_reported_cost_equals_sum_of_edge_costs(self):
        r = dijkstra(self.g, 0, 3, "Safety")
        total = sum(self.g.edge_cost(self.g.edges[e], "Safety") for e in r.edges)
        self.assertAlmostEqual(r.cost, total)

    def test_presets_choose_different_routes(self):
        self.assertEqual(dijkstra(self.g, 0, 3, "Balanced").vertices, [0, 3])
        self.assertEqual(dijkstra(self.g, 0, 3, "Safety").vertices, [0, 1, 2, 3])

    def test_blocked_edge_changes_route(self):
        self.g.block_edge(3)
        self.assertEqual(dijkstra(self.g, 0, 3).vertices, [0, 1, 2, 3])

    def test_unreachable(self):
        self.g.block_edge(0)
        self.g.block_edge(3)
        self.assertFalse(dijkstra(self.g, 0, 3).found)

    def test_source_equals_target(self):
        r = dijkstra(self.g, 2, 2)
        self.assertTrue(r.found)
        self.assertEqual(r.vertices, [2])
        self.assertEqual(r.cost, 0.0)

    def test_directed_edge(self):
        self.assertEqual(dijkstra(self.g, 3, 0).vertices, [3, 2, 1, 0])

    def test_effect_changes_cost_and_can_change_route(self):
        before = dijkstra(self.g, 1, 2)
        self.assertEqual(before.edges, [1])                    # easy road (difficulty 1)
        self.g.add_effect(1, Effect(1, "oil", 2))
        self.g.add_effect(1, Effect(2, "speed_cap", 0.5))
        after = dijkstra(self.g, 1, 2)
        self.assertEqual(after.edges, [6])                     # detour road is now cheaper
        self.g.remove_effect(1, 1)
        self.g.remove_effect(1, 2)
        self.assertEqual(dijkstra(self.g, 1, 2).edges, [1])

    def test_zero_weight_edge(self):
        g = make_graph([(0, 0), (1, 0), (2, 0)],
                       [(0, 1, 0, 0, 0, 1), (1, 2, 10, 10, 5, 1), (0, 2, 10, 20, 9, 2)])
        r = dijkstra(g, 0, 2)
        self.assertEqual(r.vertices, [0, 1, 2])

    def test_equal_cost_paths_are_deterministic(self):
        g = make_graph([(0, 0), (5, 5), (5, -5), (10, 0)],
                       [(0, 1, 8, 8, 4, 1), (1, 3, 8, 8, 4, 1), (0, 2, 8, 8, 4, 1), (2, 3, 8, 8, 4, 1)])
        first = dijkstra(g, 0, 3)
        for _ in range(5):
            self.assertEqual(dijkstra(g, 0, 3).vertices, first.vertices)

    def test_counters(self):
        r = dijkstra(self.g, 0, 3)
        self.assertGreater(r.expanded, 0)
        self.assertGreater(r.relaxed, 0)
        self.assertGreater(r.heap_ops, 0)
        self.assertGreaterEqual(r.runtime_s, 0)

    def test_unknown_vertex(self):
        self.assertFalse(dijkstra(self.g, 0, 99).found)


if __name__ == "__main__":
    unittest.main()
