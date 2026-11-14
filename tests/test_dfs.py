import os, random, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.graph import Graph
from src.core.models import Vertex, Edge, VertexType, EdgeStatus
from src.core.track_io import load_track
from src.routing.api import (dfs_analysis, alternative_routes, path_cost, reachable_from, dijkstra)

TINY = os.path.join(os.path.dirname(__file__), "data", "tiny.json")


def random_graph(seed):
    rnd = random.Random(seed)
    n = rnd.randint(3, 6)
    g = Graph("rnd")
    for i in range(n):
        g.add_vertex(Vertex(i, i * 10.0, 0.0, VertexType.INTERSECTION))
    for k in range(rnd.randint(0, 9)):
        a, b = rnd.sample(range(n), 2)
        g.add_edge(Edge(k, a, b, 10.0, 10.0, 5.0, 1,
                        EdgeStatus.BLOCKED if rnd.random() < 0.15 else EdgeStatus.OPEN,
                        False, rnd.random() < 0.4))
    g.finalize()
    return g


def brute_has_cycle(g, source):
    """A closed route with distinct roads and no repeated vertex (except returning to its start), reachable from source."""
    def go(start, u, seen, used):
        for e, v in g.neighbors(u):
            if e.id in used:
                continue
            if v == start:
                return True
            if v not in seen and go(start, v, seen | {v}, used | {e.id}):
                return True
        return False
    return any(go(s, s, {s}, frozenset()) for s in reachable_from(g, source))


class DfsTests(unittest.TestCase):
    def setUp(self):
        self.g = load_track(TINY)

    def test_order_is_a_valid_dfs_of_reachable_vertices(self):
        r = dfs_analysis(self.g, 0)
        self.assertEqual(r["order"][0], 0)
        self.assertEqual(sorted(r["order"]), sorted(reachable_from(self.g, 0)))
        self.assertEqual(len(r["order"]), len(set(r["order"])))
        self.assertEqual(r["order"], [0, 1, 2, 3, 5, 4])

    def test_order_deterministic(self):
        self.assertEqual(dfs_analysis(self.g, 0)["order"], dfs_analysis(self.g, 0)["order"])

    def test_cycle_detected_with_parallel_roads(self):
        self.assertTrue(dfs_analysis(self.g, 0)["has_cycle"])

    def test_one_way_shortcut_plus_road_back_is_a_cycle(self):
        self.g.block_edge(6)                       # remove the parallel road 1-2
        self.assertTrue(dfs_analysis(self.g, 0)["has_cycle"])    # drive 0->3 on the shortcut, return 3-2-1-0
        self.g.block_edge(3)                       # without the shortcut the roads form a tree
        self.assertFalse(dfs_analysis(self.g, 0)["has_cycle"])
        self.g.unblock_edge(6)                     # parallel roads 1-2 form a cycle again
        self.assertTrue(dfs_analysis(self.g, 0)["has_cycle"])

    def test_one_way_road_with_no_way_back_is_not_a_cycle(self):
        g = Graph("oneway")
        for i, (x, y) in enumerate([(0, 0), (10, 0), (20, 0)]):
            g.add_vertex(Vertex(i, x, y, VertexType.INTERSECTION))
        g.add_edge(Edge(0, 0, 1, 10.0, 10.0, 5.0, 1, EdgeStatus.OPEN, False, True))   # 0 -> 1 only
        g.add_edge(Edge(1, 1, 2, 10.0, 10.0, 5.0, 1, EdgeStatus.OPEN, False, True))   # 1 -> 2 only
        g.finalize()
        self.assertFalse(dfs_analysis(g, 0)["has_cycle"])

    def test_two_way_loop_is_a_cycle(self):
        g = Graph("loop")
        for i, (x, y) in enumerate([(0, 0), (10, 0), (10, 10)]):
            g.add_vertex(Vertex(i, x, y, VertexType.INTERSECTION))
        for k, (a, b) in enumerate([(0, 1), (1, 2), (2, 0)]):
            g.add_edge(Edge(k, a, b, 15.0, 10.0, 5.0, 1))
        g.finalize()
        self.assertTrue(dfs_analysis(g, 0)["has_cycle"])
        g.block_edge(2)
        self.assertFalse(dfs_analysis(g, 0)["has_cycle"])

    def test_cycle_matches_brute_force_on_random_mixed_graphs(self):
        for seed in range(600):
            g = random_graph(seed)
            for s in g.vertices:
                self.assertEqual(dfs_analysis(g, s)["has_cycle"], brute_has_cycle(g, s), (seed, s))

    def test_components(self):
        self.assertEqual(dfs_analysis(self.g, 0)["components"], [[0, 1, 2, 3, 4, 5]])
        self.g.block_edge(0)
        self.g.block_edge(3)
        self.assertEqual(dfs_analysis(self.g, 0)["components"], [[0], [1, 2, 3, 4, 5]])
        self.assertEqual(dfs_analysis(self.g, 0)["order"], [0])

    def test_dead_ends(self):
        self.assertEqual(dfs_analysis(self.g, 0)["dead_ends"], [4, 5])   # Start and Finish never listed
        self.g.block_edge(4)                                             # 4 now has no road at all (isolated)
        self.assertNotIn(4, dfs_analysis(self.g, 0)["dead_ends"])

    def test_unknown_source(self):
        r = dfs_analysis(self.g, 99)
        self.assertEqual(r["order"], [])
        self.assertFalse(r["has_cycle"])


class AlternativeRouteTests(unittest.TestCase):
    def setUp(self):
        self.g = load_track(TINY)

    def test_finds_both_routes_and_dedupes_parallel_roads(self):
        self.assertEqual(alternative_routes(self.g, 0, 3), [[0, 3], [0, 1, 2, 3]])

    def test_blocked_shortcut(self):
        self.g.block_edge(3)
        self.assertEqual(alternative_routes(self.g, 0, 3), [[0, 1, 2, 3]])

    def test_limits(self):
        self.assertEqual(len(alternative_routes(self.g, 0, 3, max_routes=1)), 1)
        self.assertEqual(alternative_routes(self.g, 0, 3, max_len=1), [[0, 3]])
        self.assertEqual(alternative_routes(self.g, 0, 3, max_len=2), [[0, 3]])
        self.assertEqual(alternative_routes(self.g, 0, 3, max_expansions=1), [])

    def test_unreachable_and_trivial_and_unknown(self):
        self.g.block_edge(0)
        self.g.block_edge(3)
        self.assertEqual(alternative_routes(self.g, 0, 3), [])
        self.assertEqual(alternative_routes(self.g, 2, 2), [[2]])
        self.assertEqual(alternative_routes(self.g, 0, 99), [])

    def test_routes_are_simple_valid_and_no_cheaper_than_dijkstra(self):
        rnd = random.Random(8)
        n = 12
        g = Graph("dense")
        for i in range(n):
            g.add_vertex(Vertex(i, i * 10.0, (i % 3) * 10.0, VertexType.INTERSECTION))
        k = 0
        for a in range(n):
            for b in range(a + 1, n):
                if rnd.random() < 0.35:
                    g.add_edge(Edge(k, a, b, 100.0, rnd.uniform(5, 20), rnd.uniform(2, 9), rnd.randint(1, 5)))
                    k += 1
        g.finalize()
        for s, t in [(0, 11), (2, 9), (5, 6)]:
            routes = alternative_routes(g, s, t, max_routes=15, max_len=8)
            self.assertLessEqual(len(routes), 15)
            best = dijkstra(g, s, t)
            for r in routes:
                self.assertEqual((r[0], r[-1]), (s, t))
                self.assertEqual(len(r), len(set(r)))
                self.assertLessEqual(len(r) - 1, 8)
                c = path_cost(g, r)
                self.assertLess(c, float("inf"))
                if best.found:
                    self.assertGreaterEqual(c + 1e-9, best.cost)

    def test_path_cost(self):
        r = dijkstra(self.g, 0, 3, "Safety")
        self.assertAlmostEqual(path_cost(self.g, r.vertices, "Safety"), r.cost)
        self.assertEqual(path_cost(self.g, [3, 0]), float("inf"))   # one-way road cannot be used backwards

    def test_deterministic(self):
        self.assertEqual(alternative_routes(self.g, 3, 0), alternative_routes(self.g, 3, 0))


if __name__ == "__main__":
    unittest.main()
