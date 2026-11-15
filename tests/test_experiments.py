import importlib.util, os, random, sys, unittest
ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "experiments"))
import common  # type: ignore
from src.routing.api import reachable_from


def load_exp1():
    spec = importlib.util.spec_from_file_location("exp1", os.path.join(ROOT, "experiments", "exp1_bfs_dfs.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class GeneratorTests(unittest.TestCase):
    def test_graphs_are_connected_and_valid_for_astar(self):
        for density in common.DENSITIES:
            g = common.make_grid_graph(8, density, 1)
            self.assertEqual(len(g.vertices), 64)
            self.assertEqual(reachable_from(g, 0), set(g.vertices))
            self.assertEqual(g.validate_geometry(), [], density)

    def test_density_ordering_and_sparse_has_cycles_but_few(self):
        e = {d: len(common.make_grid_graph(12, d, 1).edges) for d in common.DENSITIES}
        self.assertGreaterEqual(e["sparse"], 144)            # spanning tree (V-1) plus extras
        self.assertLess(e["sparse"], e["medium"])
        self.assertLess(e["medium"], e["dense"])

    def test_reproducible_and_seed_changes_graph(self):
        a, b, c = (common.make_grid_graph(8, "dense", s) for s in (1, 1, 2))
        self.assertEqual([(x.from_, x.to, x.distance) for x in a.edges.values()],
                         [(x.from_, x.to, x.distance) for x in b.edges.values()])
        self.assertNotEqual([x.distance for x in a.edges.values()], [x.distance for x in c.edges.values()])

    def test_express_lanes_break_geometry_on_purpose(self):
        g = common.make_grid_graph(12, "medium", 1, express_frac=0.10)
        self.assertGreater(len(g.validate_geometry()), 0)

    def test_timing_helpers(self):
        calls = []
        times, last = common.time_call(lambda: calls.append(1) or len(calls), 2, 3)
        self.assertEqual(len(times), 3)
        self.assertEqual(len(calls), 5)
        self.assertEqual(last, 5)
        mean, median, sd = common.summarize([1.0, 2.0, 3.0])
        self.assertEqual((mean, median), (2.0, 2.0))
        self.assertAlmostEqual(sd, 1.0)


class Exp1VerificationTests(unittest.TestCase):
    def test_reference_checks_all_pass(self):
        exp1 = load_exp1()
        rnd = random.Random(3)
        for density in common.DENSITIES:
            for check, ok, total in exp1.verify_graph(8, density, 1, rnd):
                self.assertEqual(ok, total, (density, check))


if __name__ == "__main__":
    unittest.main()
