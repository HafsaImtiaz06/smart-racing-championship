import json, os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.track_io import load_track
from src.core.models import VertexType
from src.core import constants as K
from src.routing.api import (dfs_analysis, alternative_routes, reachable_from, dijkstra, astar,
                             plan_route, route_vertices)

PATH = os.path.join(os.path.dirname(__file__), "..", "tracks", "circuit1.json")


def in_order(seq, wanted):
    """True if `wanted` appears in `seq` as a subsequence (in that order)."""
    it = iter(seq)
    return all(any(x == w for x in it) for w in wanted)


class Circuit1Tests(unittest.TestCase):
    def setUp(self):
        self.g = load_track(PATH)
        with open(PATH, encoding="utf-8") as f:
            self.raw = json.load(f)
        self.cps = self.g.checkpoints_in_order()
        self.S, self.F = self.g.start_vertex(), self.g.finish_vertex()

    def test_required_contents(self):
        types = [v.type for v in self.g.vertices.values()]
        orders = sorted(v.checkpointOrder for v in self.g.vertices.values() if v.checkpointOrder is not None)
        self.assertEqual(orders, list(range(1, 11)))
        self.assertEqual(types.count(VertexType.START), 1)
        self.assertEqual(types.count(VertexType.FINISH), 1)
        self.assertGreaterEqual(types.count(VertexType.FUEL_STATION), 3)
        self.assertGreaterEqual(types.count(VertexType.NITRO_PICKUP), 1)
        self.assertGreaterEqual(types.count(VertexType.DEAD_END), 1)
        shortcuts = [e for e in self.g.edges.values() if e.isShortcut]
        self.assertGreaterEqual(len(shortcuts), 2)
        self.assertTrue(any(e.directed for e in self.g.edges.values()), "needs a one-way road")
        self.assertGreaterEqual(len([v for v in types if v == VertexType.INTERSECTION]), 5)

    def test_geometry_and_connectivity(self):
        self.assertEqual(self.g.validate_geometry(), [])
        self.assertEqual(reachable_from(self.g, self.S), set(self.g.vertices))
        self.assertEqual(len(dfs_analysis(self.g, self.S)["components"]), 1)
        for e in self.g.edges.values():
            self.assertTrue(1 <= e.difficulty <= 5)
            self.assertGreater(e.distance, 0)

    def test_cycle_and_dead_ends(self):
        r = dfs_analysis(self.g, self.S)
        self.assertTrue(r["has_cycle"])
        self.assertTrue(r["dead_ends"])
        typed = {vid for vid, v in self.g.vertices.items() if v.type == VertexType.DEAD_END}
        self.assertTrue(typed <= set(r["dead_ends"]))
        for vid in r["dead_ends"]:
            self.assertIsNone(self.g.vertices[vid].checkpointOrder)

    def test_at_least_two_alternative_start_finish_routes(self):
        routes = alternative_routes(self.g, self.S, self.F, max_routes=20, max_len=40)
        self.assertGreaterEqual(len(routes), 2)
        self.assertEqual(len({tuple(r) for r in routes}), len(routes))

    def test_two_laps_visit_checkpoints_in_order_for_every_preset_and_algo(self):
        stops = self.cps + [self.F] + self.cps
        for preset in K.PRESETS:
            a = plan_route(self.g, self.S, stops, self.F, preset, "astar")
            d = plan_route(self.g, self.S, stops, self.F, preset, "dijkstra")
            self.assertTrue(a.found and d.found, preset)
            self.assertAlmostEqual(a.cost, d.cost, msg=preset)
            verts = route_vertices(a)
            self.assertEqual((verts[0], verts[-1]), (self.S, self.F))
            self.assertTrue(in_order(verts, stops), preset)

    def test_presets_choose_different_routes(self):
        stops = self.cps + [self.F]
        routes = {p: tuple(route_vertices(plan_route(self.g, self.S, stops, self.F, p))) for p in K.PRESETS}
        self.assertGreaterEqual(len(set(routes.values())), 3)
        self.assertNotEqual(routes["Speed"], routes["Economy"])
        self.assertNotEqual(routes["Safety"], routes["Balanced"])

    def test_shortcuts_really_save_distance(self):
        for e in [e for e in self.g.edges.values() if e.isShortcut]:
            self.g.block_edge(e.id)
            around = dijkstra(self.g, e.from_, e.to, "Speed")
            self.g.unblock_edge(e.id)
            if around.found:
                self.assertLess(e.distance, around.distance, e.id)
            self.assertGreater(e.difficulty, 3)                      # costs something: harder road

    def test_astar_matches_dijkstra_on_all_pairs(self):
        ids = sorted(self.g.vertices)
        for preset in ("Speed", "Safety"):
            for s in ids:
                for t in ids:
                    a, d = astar(self.g, s, t, preset), dijkstra(self.g, s, t, preset)
                    self.assertEqual(a.found, d.found)
                    if d.found:
                        self.assertAlmostEqual(a.cost, d.cost, msg=(s, t, preset))

    def _road(self, a, b):
        return next(e for e, v in self.g.neighbors(a) if v == b)

    def test_main_route_and_fuel_spacing(self):
        main = self.raw["main_route"]
        self.assertEqual((main[0], main[-1]), (self.S, self.F))
        self.assertTrue(in_order(main, self.cps))
        stations = {vid for vid, v in self.g.vertices.items() if v.type == VertexType.FUEL_STATION}
        lap = main + [main[0]] + main[1:]                                     # lap 1, then Finish -> Start -> lap 2
        acc, longest = 0.0, 0.0
        for a, b in zip(lap, lap[1:]):
            acc += self.g.effective_fuel(self._road(a, b))
            if b in stations:
                longest, acc = max(longest, acc), 0.0
        self.assertLessEqual(longest, K.MAX_FUEL)                    # a full tank always reaches the next station
        self.assertLessEqual(acc, K.MAX_FUEL)

    def test_fixed_detours_are_valid(self):
        detours = self.raw["fixed_detour"]
        main = self.raw["main_route"]
        ring_edges = set()
        for a, b in zip(main, main[1:] + [main[0]]):
            ring_edges.add(self._road(a, b).id)
        self.assertEqual({int(k) for k in detours}, ring_edges)
        for key, path in detours.items():
            e = self.g.edges[int(key)]
            self.assertEqual({path[0], path[-1]}, {e.from_, e.to})
            self.assertEqual(len(path), len(set(path)))
            for a, b in zip(path, path[1:]):
                road = self._road(a, b)
                self.assertNotEqual(road.id, e.id)                   # the detour avoids the blocked road

    def test_every_main_route_road_can_be_closed_and_a_race_still_possible(self):
        stops = self.cps + [self.F] + self.cps
        main = self.raw["main_route"]
        for a, b in zip(main, main[1:] + [main[0]]):
            road = self._road(a, b)
            self.g.block_edge(road.id)
            plan = plan_route(self.g, self.S, stops, self.F, "Balanced")
            self.g.unblock_edge(road.id)
            self.assertTrue(plan.found, "closing road %d disconnects the circuit" % road.id)


if __name__ == "__main__":
    unittest.main()
