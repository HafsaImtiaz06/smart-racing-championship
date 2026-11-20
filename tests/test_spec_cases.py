"""Spec section 9.1 minimum coverage for graph and routing, one explicit test per named case."""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.graph import Graph
from src.core.models import Vertex, Edge, VertexType, EdgeStatus
from src.routing.api import (bfs_path, dijkstra, astar, dfs_analysis, dfs_order, reachable_from, alternative_routes,
                             plan_route, route_vertices, is_stale)


def make(points, roads):
    """points: [(x, y)], roads: [(a, b, distance, time, fuel, difficulty, directed)]"""
    g = Graph("t")
    for i, (x, y) in enumerate(points):
        g.add_vertex(Vertex(i, x, y, VertexType.INTERSECTION))
    for k, (a, b, d, t, f, diff, directed) in enumerate(roads):
        g.add_edge(Edge(k, a, b, d, t, f, diff, EdgeStatus.OPEN, False, directed))
    g.finalize()
    return g


class GraphCases(unittest.TestCase):
    def test_single_vertex_graph(self):
        g = make([(0, 0)], [])
        for fn in (bfs_path, dijkstra, astar):
            r = fn(g, 0, 0)
            self.assertTrue(r.found)
            self.assertEqual((r.vertices, r.edges), ([0], []))
        a = dfs_analysis(g, 0)
        self.assertEqual((a["order"], a["has_cycle"], a["components"], a["dead_ends"]), ([0], False, [[0]], []))
        self.assertEqual(reachable_from(g, 0), {0})
        self.assertEqual(alternative_routes(g, 0, 0), [[0]])

    def test_connected_graph(self):
        g = make([(0, 0), (10, 0), (20, 0)], [(0, 1, 10, 5, 3, 1, False), (1, 2, 10, 5, 3, 1, False)])
        self.assertEqual(dfs_analysis(g, 0)["components"], [[0, 1, 2]])
        self.assertEqual(bfs_path(g, 0, 2).vertices, [0, 1, 2])

    def test_disconnected_graph(self):
        g = make([(0, 0), (10, 0), (50, 0), (60, 0)], [(0, 1, 10, 5, 3, 1, False), (2, 3, 10, 5, 3, 1, False)])
        a = dfs_analysis(g, 0)
        self.assertEqual(a["components"], [[0, 1], [2, 3]])
        self.assertEqual(a["order"], [0, 1])
        for fn in (bfs_path, dijkstra, astar):
            self.assertFalse(fn(g, 0, 3).found)
        self.assertEqual(reachable_from(g, 2), {2, 3})

    def test_cyclic_graph(self):
        g = make([(0, 0), (10, 0), (5, 9)], [(0, 1, 10, 5, 3, 1, False), (1, 2, 11, 5, 3, 1, False), (2, 0, 11, 5, 3, 1, False)])
        self.assertTrue(dfs_analysis(g, 0)["has_cycle"])
        self.assertEqual(len(alternative_routes(g, 0, 2)), 2)             # direct and around the triangle

    def test_branching_graph_is_a_tree(self):
        #        3
        #        |
        #  0 --- 1 --- 2        a star: no cycle, three leaves
        g = make([(0, 0), (10, 0), (20, 0), (10, 10)], [(0, 1, 10, 5, 3, 1, False), (1, 2, 10, 5, 3, 1, False), (1, 3, 10, 5, 3, 1, False)])
        a = dfs_analysis(g, 1)
        self.assertFalse(a["has_cycle"])
        self.assertEqual(sorted(a["order"]), [0, 1, 2, 3])
        self.assertEqual(a["order"][0], 1)

    def test_dead_end_graph(self):
        g = Graph("de")
        types = [VertexType.START, VertexType.INTERSECTION, VertexType.FINISH, VertexType.INTERSECTION]
        for i, (x, y) in enumerate([(0, 0), (10, 0), (20, 0), (10, 10)]):
            g.add_vertex(Vertex(i, x, y, types[i]))
        for k, (a, b) in enumerate([(0, 1), (1, 2), (1, 3)]):
            g.add_edge(Edge(k, a, b, 10, 5, 3, 1))
        g.finalize()
        self.assertEqual(dfs_analysis(g, 0)["dead_ends"], [3])

    def test_directed_versus_undirected(self):
        one_way = make([(0, 0), (10, 0)], [(0, 1, 10, 5, 3, 1, True)])
        two_way = make([(0, 0), (10, 0)], [(0, 1, 10, 5, 3, 1, False)])
        self.assertTrue(bfs_path(one_way, 0, 1).found)
        self.assertFalse(bfs_path(one_way, 1, 0).found)
        self.assertFalse(astar(one_way, 1, 0).found)
        self.assertTrue(bfs_path(two_way, 1, 0).found)
        self.assertTrue(dijkstra(two_way, 1, 0).found)


class RoutingCases(unittest.TestCase):
    def test_spec_example_bfs_minimizes_edges_not_distance(self):
        # direct S-T has length 10; S-A-B-T has three edges of length 2 (spec 4.1)
        g = make([(0, 0), (2, 0), (4, 0), (6, 0)],
                 [(0, 3, 10, 10, 5, 1, False), (0, 1, 2, 2, 1, 1, False), (1, 2, 2, 2, 1, 1, False), (2, 3, 2, 2, 1, 1, False)])
        bfs = bfs_path(g, 0, 3)
        self.assertEqual(bfs.vertices, [0, 3])
        self.assertEqual(bfs.distance, 10)
        self.assertEqual(dijkstra(g, 0, 3, "Speed").distance, 6)           # time and fuel grow with distance, so the 3-edge route is cheaper

    def test_equal_cost_paths_dijkstra_and_astar_agree_and_are_repeatable(self):
        g = make([(0, 0), (5, 5), (5, -5), (10, 0)],
                 [(0, 1, 8, 8, 4, 1, False), (1, 3, 8, 8, 4, 1, False), (0, 2, 8, 8, 4, 1, False), (2, 3, 8, 8, 4, 1, False)])
        d, a = dijkstra(g, 0, 3), astar(g, 0, 3)
        self.assertAlmostEqual(d.cost, a.cost)
        for _ in range(3):
            self.assertEqual(dijkstra(g, 0, 3).vertices, d.vertices)
            self.assertEqual(astar(g, 0, 3).vertices, a.vertices)

    def test_zero_weight_edges_for_both_algorithms(self):
        g = make([(0, 0), (0, 0), (10, 0)], [(0, 1, 0, 0, 0, 1, False), (1, 2, 10, 10, 5, 1, False), (0, 2, 10, 20, 9, 2, False)])
        self.assertEqual(dijkstra(g, 0, 2).vertices, [0, 1, 2])
        self.assertEqual(astar(g, 0, 2).vertices, [0, 1, 2])
        self.assertEqual(dijkstra(g, 0, 1).cost, 0.0)

    def test_long_route_does_not_overflow_the_stack(self):
        n = 3000
        g = make([(i * 10.0, 0.0) for i in range(n)], [(i, i + 1, 10, 5, 2, 1, False) for i in range(n - 1)])
        for fn in (bfs_path, dijkstra, astar):
            r = fn(g, 0, n - 1)
            self.assertTrue(r.found)
            self.assertEqual(len(r.edges), n - 1)
        self.assertEqual(len(dfs_order(g, 0)[0]), n)                        # iterative DFS: no recursion limit
        a = dfs_analysis(g, 0)
        self.assertFalse(a["has_cycle"])
        self.assertEqual(a["dead_ends"], [])                               # no Finish vertex in this graph: no dead ends defined

    def test_immediate_recalculation_after_a_blocked_edge(self):
        g = make([(0, 0), (10, 0), (20, 0), (10, 15)],
                 [(0, 1, 10, 5, 3, 1, False), (1, 2, 10, 5, 3, 1, False), (0, 3, 18, 10, 6, 1, False), (3, 2, 18, 10, 6, 1, False)])
        plan = plan_route(g, 0, [], 2)
        self.assertEqual(route_vertices(plan), [0, 1, 2])
        g.block_edge(1)                                                      # road 1-2 closes during the race
        self.assertTrue(is_stale(plan, g))
        new = plan_route(g, 0, [], 2)
        self.assertEqual(route_vertices(new), [0, 3, 2])
        self.assertFalse(is_stale(new, g))
        g.block_edge(3)
        self.assertFalse(plan_route(g, 0, [], 2).found)

    def test_target_unreachable_recorded_with_counters(self):
        g = make([(0, 0), (10, 0), (50, 0)], [(0, 1, 10, 5, 3, 1, False)])
        for fn in (bfs_path, dijkstra, astar):
            r = fn(g, 0, 2)
            self.assertFalse(r.found)
            self.assertGreater(r.expanded, 0)


if __name__ == "__main__":
    unittest.main()
