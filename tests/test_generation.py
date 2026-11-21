import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.track_io import load_track
from src.core.graph import Graph
from src.core.models import Vertex, Edge, VertexType, EdgeStatus
from src.generation.api import mst_backbone, generate_track, validate_track, export_extras

TRACK = os.path.join(os.path.dirname(__file__), "..", "tracks", "circuit1.json")


class MstTests(unittest.TestCase):
    pts = [(0, 0), (10, 0), (10, 10), (0, 10), (5, 5)]
    cand = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 0), (4, 1), (4, 2), (4, 3)]

    def test_kruskal_and_prim_same_weight(self):
        w = lambda ed: sum(((self.pts[a][0] - self.pts[b][0]) ** 2 + (self.pts[a][1] - self.pts[b][1]) ** 2) ** .5 for a, b in ed)
        k, p = mst_backbone(self.pts, self.cand, "kruskal"), mst_backbone(self.pts, self.cand, "prim")
        self.assertEqual((len(k), len(p)), (4, 4))
        self.assertAlmostEqual(w(k), w(p))

    def test_disconnected_raises(self):
        with self.assertRaises(ValueError):
            mst_backbone(self.pts, [(0, 1), (2, 3)])

    def test_explicit_weights_and_single_vertex(self):
        self.assertEqual(mst_backbone([(0, 0), (1, 1), (2, 2)], [(0, 1, 5), (1, 2, 1), (0, 2, 2)]), [(1, 2, 1), (0, 2, 2)])
        self.assertEqual(mst_backbone([(0, 0)], []), [])


class GeneratorTests(unittest.TestCase):
    def test_generated_track_valid_and_playable(self):
        g, log = generate_track(7)
        self.assertIsNotNone(g)
        self.assertEqual(validate_track(g), [])
        self.assertEqual(g.start_vertex(), 0)
        self.assertEqual(len(g.checkpoints_in_order()), 10)
        self.assertEqual(g.validate_geometry(), [])
        self.assertTrue(any("accepted" in s for s in log))

    def test_deterministic(self):
        a, _ = generate_track(11)
        b, _ = generate_track(11)
        self.assertEqual([(e.from_, e.to, e.distance, e.difficulty) for e in a.edges.values()],
                         [(e.from_, e.to, e.distance, e.difficulty) for e in b.edges.values()])

    def test_invalid_candidates_rejected_with_reason(self):
        g, log = generate_track(7, max_attempts=3, params={"fuel": 0})
        self.assertIsNone(g)
        self.assertTrue(all("REJECTED" in s for s in log[:3]))
        self.assertTrue(any("fuel plan" in s for s in log))
        g, log = generate_track(7, max_attempts=2, params={"radius": 120})
        self.assertIsNone(g)
        self.assertTrue(any("disconnected" in s for s in log))

    def test_circuit1_passes_validator(self):
        self.assertEqual(validate_track(load_track(TRACK)), [])

    def test_validator_catches_broken_tracks(self):
        g = load_track(TRACK)
        g.edges[next(e.id for e in g.edges.values() if e.isShortcut)].isShortcut = False
        for e in g.edges.values():
            e.isShortcut = False
        self.assertIn("fewer than 2 shortcuts", validate_track(g))
        g = load_track(TRACK)
        for v in g.vertices.values():
            if v.type == VertexType.DEAD_END:
                v.type = VertexType.INTERSECTION
        self.assertIn("no dead end", validate_track(g))
        g = load_track(TRACK)
        g.vertices[g.checkpoints_in_order()[0]].checkpointOrder = 5
        self.assertTrue(any("checkpoint" in p for p in validate_track(g)))

    def test_validator_one_way_breaks_reachability(self):
        g = load_track(TRACK)
        cp = g.checkpoints_in_order()[3]
        for e in g.edges.values():
            if e.to == cp and not e.directed:
                e.from_, e.to, e.directed = cp, e.from_, True      # every road at cp now leaves it: unreachable
            elif e.from_ == cp:
                e.directed = True
        g2 = Graph("x")
        for v in g.vertices.values(): g2.add_vertex(v)
        for e in g.edges.values(): g2.add_edge(e)
        g2.finalize()
        self.assertTrue(any("unreachable" in p for p in validate_track(g2)))

    def test_export_extras(self):
        g, _ = generate_track(7)
        ex = export_extras(g)
        self.assertEqual(ex["lap_boundary"], g.finish_vertex())
        self.assertEqual(ex["main_route"][0], 0)
        self.assertEqual(ex["main_route"][-1], g.finish_vertex())


if __name__ == "__main__":
    unittest.main()
