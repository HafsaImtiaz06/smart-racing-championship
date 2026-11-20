import os, sys, tempfile, unittest
ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "experiments"))
import challenge2_presets as c2 # type: ignore
from src.core.track_io import load_track
from src.core import constants as K

CIRCUIT = os.path.join(ROOT, "tracks", "circuit1.json")


class Challenge2Tests(unittest.TestCase):
    def test_quick_run_writes_all_outputs_and_restores_presets(self):
        before = dict(K.PRESETS)
        with tempfile.TemporaryDirectory() as tmp:
            c2.main(["--quick", "--out", tmp])
            for name in ("challenge2_lap_presets.csv", "challenge2_cross_cost.csv", "challenge2_weight_sweep.csv",
                         "challenge2_pareto.csv", "challenge2_normalization.csv", "challenge2_report.md"):
                self.assertTrue(os.path.exists(os.path.join(tmp, name)), name)
            with open(os.path.join(tmp, "challenge2_report.md"), encoding="utf-8") as f:
                text = f.read()
            self.assertIn("Weight sweep", text)
            self.assertIn("Pareto", text)
        self.assertEqual(K.PRESETS, before)                      # temporary sweep presets are always removed

    def test_cross_evaluation_diagonal_is_best_for_each_column(self):
        g = load_track(CIRCUIT)
        names = list(K.PRESETS)
        routes = {p: c2.route_edges(c2.lap_plan(g, p)) for p in names}
        for q in names:
            own = c2.dot(K.PRESETS[q], c2.route_terms(g, routes[q]))
            for p in names:
                self.assertGreaterEqual(c2.dot(K.PRESETS[q], c2.route_terms(g, routes[p])) + 1e-9, own)

    def test_route_terms_add_up_to_the_planner_cost(self):
        g = load_track(CIRCUIT)
        plan = c2.lap_plan(g, "Safety")
        self.assertAlmostEqual(c2.dot(K.PRESETS["Safety"], c2.route_terms(g, c2.route_edges(plan))), plan.cost)

    def test_normalization_constant_is_restored(self):
        g = load_track(CIRCUIT)
        t0 = g.t_ref
        with tempfile.TemporaryDirectory() as tmp:
            c2.main(["--quick", "--out", tmp])
        self.assertEqual(load_track(CIRCUIT).t_ref, t0)


if __name__ == "__main__":
    unittest.main()
