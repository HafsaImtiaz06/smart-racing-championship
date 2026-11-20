import os, sys, unittest
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")        # real pygame: no window needed
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
try:
    import pygame
    FAKE = False
except ImportError:                                      # no pygame installed: use the recording stand-in
    import fake_pygame
    pygame = fake_pygame.install()
    FAKE = True

from src.core.track_io import load_track
from src.core.models import EdgeStatus
from src.core import constants as K
from src.gui.route_view import Viewport, PlannerModel, vertex_label, default_endpoints
from src.gui.lab_trace import TraceRunner, ALGORITHMS
from src.gui.route_planner import RoutePlannerScreen
from src.gui.lab_a import PANELS_A
from src.routing.api import dijkstra, astar, bfs_path, dfs_order

CIRCUIT = os.path.join(HERE, "..", "tracks", "circuit1.json")


def in_order(seq, wanted):
    it = iter(seq)
    return all(any(x == w for x in it) for w in wanted)


class ViewportTests(unittest.TestCase):
    def setUp(self):
        self.g = load_track(CIRCUIT)
        self.vp = Viewport(self.g, (0, 0, 800, 600))

    def test_all_vertices_inside_rect_and_aspect_kept(self):
        for vid in self.g.vertices:
            x, y = self.vp.vertex_pos(vid)
            self.assertTrue(self.vp.contains(x, y), vid)
        a, b = self.g.vertices[0], self.g.vertices[8]
        (ax, ay), (bx, by) = self.vp.vertex_pos(0), self.vp.vertex_pos(8)
        self.assertAlmostEqual(abs(bx - ax) / max(abs(b.x - a.x), 1e-9), self.vp.scale, delta=0.05)

    def test_hit_testing(self):
        for vid in self.g.vertices:
            self.assertEqual(self.vp.vertex_at(*self.vp.vertex_pos(vid)), vid)
        self.assertIsNone(self.vp.vertex_at(-500, -500))
        for e in self.g.edges.values():
            (ax, ay), (bx, by) = self.vp.vertex_pos(e.from_), self.vp.vertex_pos(e.to)
            self.assertIsNotNone(self.vp.edge_at((ax + bx) // 2, (ay + by) // 2), e.id)
        self.assertIsNone(self.vp.edge_at(-500, -500))

    def test_works_with_tiny_rect_and_single_vertex_span(self):
        Viewport(self.g, (10, 10, 5, 5))
        self.assertTrue(Viewport(self.g, (0, 0, 300, 200)).contains(10, 10))


class PlannerModelTests(unittest.TestCase):
    def setUp(self):
        self.g = load_track(CIRCUIT)
        self.m = PlannerModel(self.g)

    def test_defaults_and_text_lines(self):
        self.assertEqual(self.m.source, self.g.start_vertex())
        self.assertEqual(self.g.vertices[self.m.target].checkpointOrder, 5)
        lines = self.m.info_lines()
        self.assertTrue(all(len(l) <= 50 for l in lines), [l for l in lines if len(l) > 50])
        text = "\n".join(lines)
        for word in ("Route: Start -> CP5", "Balanced", "Speed", "Economy", "Safety", "Alt 1/"):
            self.assertIn(word, text)

    def test_result_is_cached_until_something_changes(self):
        r1 = self.m.result()
        self.assertIs(r1, self.m.result())
        self.m.set_preset("Safety")
        self.assertIsNot(r1, self.m.result())

    def test_clicks_alternate_between_source_and_target(self):
        self.m.click_vertex(5)
        self.assertEqual(self.m.source, 5)
        self.m.click_vertex(8)
        self.assertEqual(self.m.target, 8)
        self.m.click_vertex(2)
        self.assertEqual(self.m.source, 2)
        self.m.reset_endpoints()
        self.assertEqual((self.m.source, self.m.target), default_endpoints(self.g))

    def test_astar_and_dijkstra_modes_agree(self):
        for preset in K.PRESETS:
            self.m.set_preset(preset)
            self.m.algo = "astar"
            a = self.m.result().cost
            self.m.algo = "dijkstra"
            self.assertAlmostEqual(a, self.m.result().cost)

    def test_presets_differ_in_checkpoint_mode(self):
        self.m.toggle_mode()
        r = self.m.result()
        self.assertEqual(r.mode, "checkpoints")
        self.assertEqual(r.stops, 10)
        self.assertTrue(in_order(r.vertices, self.g.checkpoints_in_order() + [self.g.finish_vertex()]))
        self.assertEqual(len(r.rows), 4)
        self.assertGreaterEqual(len({tuple(row.vertices) for row in r.rows}), 3)
        self.assertEqual(r.alternatives, [])

    def test_checkpoint_mode_from_a_checkpoint_only_plans_the_remaining_ones(self):
        self.m.toggle_mode()
        self.m.click_vertex(self.g.checkpoints_in_order()[3])        # source = CP4
        self.assertEqual(self.m.result().stops, 6)

    def test_alternatives_sorted_and_browsable(self):
        r = self.m.result()
        costs = [c for _, c in r.alternatives]
        self.assertEqual(costs, sorted(costs))
        self.assertGreaterEqual(len(r.alternatives), 2)
        n = len(r.alternatives)
        for _ in range(n):
            self.m.step_alternative(1)
        self.assertEqual(self.m.selected_alt, 0)
        self.m.step_alternative(-1)
        self.assertEqual(self.m.selected_alt, n - 1)

    def test_blocking_roads_updates_everything_and_reopening_restores(self):
        base = self.m.result().cost
        target = self.m.target
        touching = [e.id for e in self.g.edges.values() if target in (e.from_, e.to)]
        for eid in touching:
            self.assertTrue(self.m.toggle_block(eid))
        r = self.m.result()
        self.assertFalse(r.found)
        self.assertIn(5, r.unreachable_cps)
        self.assertIn("NO ROUTE FOUND", "\n".join(self.m.info_lines()))
        self.assertEqual(self.m.blocked_count(), len(touching))
        for eid in touching:
            self.assertFalse(self.m.toggle_block(eid))
        self.assertAlmostEqual(self.m.result().cost, base)
        self.assertEqual(self.m.result().unreachable_cps, [])

    def test_labels(self):
        self.assertEqual(vertex_label(self.g, self.g.start_vertex()), "Start")
        self.assertEqual(vertex_label(self.g, self.g.checkpoints_in_order()[0]), "CP1")


class TraceRunnerTests(unittest.TestCase):
    def setUp(self):
        self.g = load_track(CIRCUIT)

    def test_playback_matches_algorithm_results(self):
        for algo in ALGORITHMS:
            t = TraceRunner(self.g, algo, 0, 12, "Speed")
            self.assertFalse(t.finished)
            seen, last = 0, None
            while t.step():
                c = t.counters()
                self.assertGreaterEqual(c["relaxed"] + c["expanded"], seen)
                seen = c["relaxed"] + c["expanded"]
            self.assertTrue(t.finished)
            c = t.counters()
            self.assertEqual((c["expanded"], c["relaxed"]), (c["expanded_total"], c["relaxed_total"]))
            if algo == "dfs":
                self.assertEqual(t.expanded_order, dfs_order(self.g, 0)[0])
            else:
                ref = {"bfs": bfs_path(self.g, 0, 12), "dijkstra": dijkstra(self.g, 0, 12, "Speed"),
                       "astar": astar(self.g, 0, 12, "Speed")}[algo]
                self.assertEqual(t.path_vertices(), ref.vertices)
                self.assertEqual(c["expanded"], ref.expanded)

    def test_path_hidden_until_finished_and_rewind_resets(self):
        t = TraceRunner(self.g, "astar", 0, 12)
        self.assertEqual(t.path_vertices(), [])
        t.step_to_end()
        self.assertTrue(t.path_vertices())
        t.rewind()
        self.assertEqual((t.pos, t.expanded_order, t.relaxed_edges), (0, [], []))
        self.assertEqual(t.path_vertices(), [])

    def test_unreachable_target_and_bad_algorithm(self):
        for e in list(self.g.edges.values()):
            if 12 in (e.from_, e.to):
                self.g.block_edge(e.id)
        t = TraceRunner(self.g, "dijkstra", 0, 12)
        t.step_to_end()
        self.assertFalse(t.counters()["found"])
        self.assertEqual(t.path_vertices(), [])
        with self.assertRaises(ValueError):
            TraceRunner(self.g, "magic")


class DrawingSmokeTests(unittest.TestCase):
    """Runs the real drawing code (real pygame with a hidden window if installed, else the recording stand-in)."""
    def setUp(self):
        self.g = load_track(CIRCUIT)
        pygame.font.init()
        self.surface = pygame.Surface((1000, 700))

    def key(self, k):
        return pygame.event.Event(pygame.KEYDOWN, key=k)

    def click(self, pos):
        return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)

    def test_route_planner_screen_full_interaction(self):
        s = RoutePlannerScreen()
        s.on_enter(None, graph=self.g)
        s.draw(self.surface)
        for vid in (3, 12):                                           # pick source then target by clicking vertices
            s.handle_event(self.click(s.vp.vertex_pos(vid)))
        self.assertEqual((s.model.source, s.model.target), (3, 12))
        for k in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_a, pygame.K_n, pygame.K_p, pygame.K_c,
                  pygame.K_c, pygame.K_r):
            self.assertIsNone(s.handle_event(self.key(k)))
            s.update(0.016)
            s.draw(self.surface)
        s.handle_event(self.key(pygame.K_x))
        self.assertTrue(s.block_mode)
        eid = next(iter(self.g.edges))
        e = self.g.edges[eid]
        (ax, ay), (bx, by) = s.vp.vertex_pos(e.from_), s.vp.vertex_pos(e.to)
        s.handle_event(self.click(((ax + bx) // 2, (ay + by) // 2)))
        self.assertGreaterEqual(s.model.blocked_count(), 1)
        s.draw(self.surface)
        self.assertEqual(s.handle_event(self.key(pygame.K_ESCAPE)), "main_menu")

    def test_screen_needs_a_graph_and_survives_resize(self):
        with self.assertRaises(ValueError):
            RoutePlannerScreen().on_enter(None)
        s = RoutePlannerScreen()
        s.on_enter(type("App", (), {"graph": self.g})())             # graph taken from app.graph
        s.draw(self.surface)
        s.draw(pygame.Surface((420, 300)))

    def test_every_lab_panel_draws_through_a_full_playback(self):
        for cls in PANELS_A:
            p = cls()
            p.reset(self.g)
            p.draw(self.surface, (0, 0, 900, 600))
            for _ in range(15):
                p.step()
                p.draw(self.surface, (0, 0, 900, 600))
            p.runner.step_to_end()
            self.assertTrue(p.finished)
            p.draw(self.surface, (10, 10, 600, 400))
            self.assertIn("expanded", p.counters())
            p.rewind()
            self.assertFalse(p.finished)

    def test_fake_pygame_actually_recorded_drawing(self):
        if not FAKE:
            self.skipTest("real pygame in use")
        import fake_pygame
        fake_pygame.CALLS.clear()
        s = RoutePlannerScreen()
        s.on_enter(None, graph=self.g)
        s.draw(self.surface)
        self.assertGreater(fake_pygame.CALLS.count("line"), len(self.g.edges) - 1)
        self.assertGreater(fake_pygame.CALLS.count("circle"), len(self.g.vertices) - 1)


if __name__ == "__main__":
    unittest.main()
