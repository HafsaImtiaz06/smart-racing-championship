import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.track_io import load_track
from src.routing.api import bfs_path, reachable_from

TINY = os.path.join(os.path.dirname(__file__), "data", "tiny.json")


class BfsTests(unittest.TestCase):
    def setUp(self):
        self.g = load_track(TINY)

    def test_shortcut_is_fewest_edges(self):
        r = bfs_path(self.g, 0, 3)
        self.assertEqual(r.vertices, [0, 3])

    def test_blocked_shortcut_forces_long_way(self):
        self.g.block_edge(3)
        r = bfs_path(self.g, 0, 3)
        self.assertTrue(r.found)
        self.assertEqual(len(r.edges), 3)

    def test_directed_edge_not_reversible(self):
        r = bfs_path(self.g, 3, 0)
        self.assertEqual(len(r.edges), 3)          # cannot use 0->3 backwards

    def test_unreachable(self):
        self.g.block_edge(0)
        self.g.block_edge(3)
        self.assertFalse(bfs_path(self.g, 0, 3).found)
        self.assertEqual(reachable_from(self.g, 0), {0})

    def test_source_equals_target(self):
        r = bfs_path(self.g, 2, 2)
        self.assertTrue(r.found)
        self.assertEqual(r.vertices, [2])


if __name__ == "__main__":
    unittest.main()
