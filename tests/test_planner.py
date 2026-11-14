import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.track_io import load_track
from src.core.models import Effect
from src.routing.api import plan_route, route_vertices, route_edges, is_stale, dijkstra

TINY = os.path.join(os.path.dirname(__file__), "data", "tiny.json")


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.g = load_track(TINY)
        self.cps = self.g.checkpoints_in_order()          # [1]
        self.finish = self.g.finish_vertex()              # 3
        self.start = self.g.start_vertex()                # 0

    def test_visits_checkpoint_before_finish(self):
        plan = plan_route(self.g, self.start, self.cps, self.finish)
        self.assertTrue(plan.found)
        self.assertEqual(len(plan.legs), 2)
        verts = route_vertices(plan)
        self.assertEqual(verts[0], 0)
        self.assertEqual(verts[-1], 3)
        self.assertIn(1, verts)
        self.assertLess(verts.index(1), verts.index(3))

    def test_never_skips_checkpoint_even_when_shortcut_is_cheaper(self):
        direct = dijkstra(self.g, 0, 3)
        self.assertEqual(direct.vertices, [0, 3])           # shortcut skips checkpoint 1
        plan = plan_route(self.g, 0, self.cps, 3)
        self.assertIn(1, route_vertices(plan))

    def test_order_is_enforced(self):
        plan = plan_route(self.g, 0, [4, 5], 3)             # dead end 4 first, then station 5
        verts = route_vertices(plan)
        self.assertTrue(plan.found)
        i4 = verts.index(4)
        i5 = verts.index(5, i4)
        self.assertLess(i4, i5)
        self.assertEqual(verts[-1], 3)

    def test_no_checkpoints_goes_straight_to_finish(self):
        plan = plan_route(self.g, 0, [], 3)
        self.assertEqual(len(plan.legs), 1)
        self.assertEqual(route_vertices(plan), [0, 3])

    def test_totals_equal_sum_of_legs_and_edges(self):
        plan = plan_route(self.g, 0, [1, 2], 3, "Safety")
        self.assertAlmostEqual(plan.cost, sum(l.cost for l in plan.legs))
        edge_cost = sum(self.g.edge_cost(self.g.edges[e], "Safety") for e in route_edges(plan))
        self.assertAlmostEqual(plan.cost, edge_cost)
        self.assertAlmostEqual(plan.distance, sum(l.distance for l in plan.legs))

    def test_unreachable_leg_gives_found_false(self):
        self.g.block_edge(2)       # 2-3
        self.g.block_edge(3)       # shortcut 0->3
        plan = plan_route(self.g, 0, self.cps, 3)
        self.assertFalse(plan.found)
        self.assertFalse(plan.legs[-1].found)

    def test_blocked_road_changes_route_and_marks_old_plan_stale(self):
        plan = plan_route(self.g, 0, [1], 3)
        self.assertFalse(is_stale(plan, self.g))
        self.g.block_edge(1)       # 1-2
        self.assertTrue(is_stale(plan, self.g))
        new = plan_route(self.g, 0, [1], 3)
        self.assertTrue(new.found)
        self.assertNotIn(1, route_edges(new))      # replanned without the blocked edge
        self.assertFalse(is_stale(new, self.g))

    def test_effects_also_make_plan_stale(self):
        plan = plan_route(self.g, 0, [1], 3)
        self.g.add_effect(2, Effect(1, "oil", 2))
        self.assertTrue(is_stale(plan, self.g))

    def test_two_laps_repeat_checkpoint(self):
        plan = plan_route(self.g, 0, [1, 0, 1], 3)          # lap 1 cp, back to start, lap 2 cp
        self.assertTrue(plan.found)
        self.assertEqual(len(plan.legs), 4)

    def test_current_vertex_is_the_next_checkpoint(self):
        plan = plan_route(self.g, 1, [1], 3)
        self.assertTrue(plan.found)
        self.assertEqual(plan.legs[0].vertices, [1])
        self.assertEqual(route_vertices(plan)[0], 1)

    def test_astar_and_dijkstra_plans_have_same_cost(self):
        for preset in ("Balanced", "Speed", "Economy", "Safety"):
            a = plan_route(self.g, 0, [1, 2], 3, preset, "astar")
            d = plan_route(self.g, 0, [1, 2], 3, preset, "dijkstra")
            self.assertAlmostEqual(a.cost, d.cost)

    def test_bfs_option_and_unknown_algo(self):
        self.assertTrue(plan_route(self.g, 0, [1], 3, algo="bfs").found)
        with self.assertRaises(ValueError):
            plan_route(self.g, 0, [1], 3, algo="magic")

    def test_route_vertices_has_no_duplicate_joints(self):
        verts = route_vertices(plan_route(self.g, 0, [1, 2], 3))
        for a, b in zip(verts, verts[1:]):
            self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
