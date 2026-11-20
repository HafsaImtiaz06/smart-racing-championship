import os, random, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "experiments"))
from src.core.track_io import load_track
from src.routing.api import bfs_path, dijkstra, astar, dfs_order
import common  # type: ignore

CIRCUIT = os.path.join(os.path.dirname(__file__), "..", "tracks", "circuit1.json")
TINY = os.path.join(os.path.dirname(__file__), "data", "tiny.json")


def counts(events):
    return (sum(1 for e in events if e[0] == "expand"), sum(1 for e in events if e[0] == "relax"))


def same(a, b):
    return (a.found, a.vertices, a.edges, a.cost, a.expanded, a.relaxed, a.heap_ops) == \
           (b.found, b.vertices, b.edges, b.cost, b.expanded, b.relaxed, b.heap_ops)


class TraceHookTests(unittest.TestCase):
    def graphs(self):
        yield load_track(TINY), [(0, 3), (3, 0), (0, 5), (2, 2)]
        c = load_track(CIRCUIT)
        yield c, [(0, 12), (2, 19), (1, 14), (12, 12)]
        g = common.make_grid_graph(8, "medium", 3)
        rnd = random.Random(4)
        yield g, [tuple(rnd.sample(sorted(g.vertices), 2)) for _ in range(8)]

    def test_trace_never_changes_results_and_counts_match_counters(self):
        for g, pairs in self.graphs():
            for s, t in pairs:
                for fn in (bfs_path, dijkstra, astar):
                    ev = []
                    traced = fn(g, s, t, trace=ev.append)
                    self.assertTrue(same(traced, fn(g, s, t)), (fn.__name__, s, t))
                    self.assertEqual(counts(ev), (traced.expanded, traced.relaxed), (fn.__name__, s, t))
                    if ev:
                        self.assertEqual(ev[0][:2], ("expand", s))

    def test_dfs_trace(self):
        for g, pairs in self.graphs():
            for s, _ in pairs:
                ev = []
                order, examined = dfs_order(g, s, trace=ev.append)
                self.assertEqual((order, examined), dfs_order(g, s))
                self.assertEqual([e[1] for e in ev if e[0] == "expand"], order)
                self.assertEqual(counts(ev)[1], examined)

    def test_dijkstra_expands_in_nondecreasing_cost_and_astar_ends_at_target(self):
        g = load_track(CIRCUIT)
        ev = []
        r = dijkstra(g, 0, 12, "Safety", trace=ev.append)
        costs = [e[2] for e in ev if e[0] == "expand"]
        self.assertEqual(costs, sorted(costs))
        ev = []
        r = astar(g, 0, 12, "Safety", trace=ev.append)
        self.assertEqual([e for e in ev if e[0] == "expand"][-1][1], 12)

    def test_relax_event_shape(self):
        g = load_track(TINY)
        ev = []
        dijkstra(g, 0, 3, trace=ev.append)
        for e in ev:
            if e[0] == "relax":
                self.assertEqual(len(e), 5)
                self.assertIn(e[3], g.edges)
                self.assertIsInstance(e[4], bool)


if __name__ == "__main__":
    unittest.main()
