import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.track_io import load_track
from src.core.models import Event, EventType as ET, EdgeStatus, VertexType
from src.events.api import EventQueue, EventManager

TRACK = os.path.join(os.path.dirname(__file__), "..", "tracks", "circuit1.json")


def ev(i, t, p, s):
    return Event(i, ET.OIL_SPILL, t, p, s, 0)


class QueueTests(unittest.TestCase):
    def test_order_time_priority_sequence(self):
        q = EventQueue()
        for e in (ev(1, 5, 3, 0), ev(2, 5, 1, 1), ev(3, 5, 1, 2), ev(4, 2, 6, 3), ev(5, 5, 3, 4)):
            q.push(e)
        self.assertEqual([q.pop().eventId for _ in range(5)], [4, 2, 3, 1, 5])

    def test_lazy_cancel_and_len(self):
        q = EventQueue()
        for i in range(4):
            q.push(ev(i + 1, i, 1, i))
        self.assertTrue(q.cancel(2))
        self.assertFalse(q.cancel(2))
        self.assertFalse(q.cancel(99))
        self.assertEqual(len(q), 3)
        self.assertEqual([q.pop().eventId for _ in range(3)], [1, 3, 4])
        self.assertEqual(q.lazy_dropped, 1)
        with self.assertRaises(IndexError):
            q.pop()

    def test_cancelled_top_skipped_by_peek(self):
        q = EventQueue()
        q.push(ev(1, 1, 1, 0)); q.push(ev(2, 2, 1, 1))
        q.cancel(1)
        self.assertEqual(q.peek().eventId, 2)

    def test_many_random_events_sorted(self):
        import random
        r = random.Random(5)
        q, evs = EventQueue(), []
        for i in range(500):
            e = ev(i + 1, r.randint(0, 20), r.randint(1, 6), i)
            evs.append(e); q.push(e)
        got = [q.pop().key() for _ in range(500)]
        self.assertEqual(got, sorted(e.key() for e in evs))
        self.assertGreater(q.heap_ops, 0)


class ManagerTests(unittest.TestCase):
    def setUp(self):
        self.g = load_track(TRACK)
        self.m = EventManager(self.g)
        self.e0 = next(iter(self.g.edges))
        self.sc = next(e.id for e in self.g.edges.values() if e.isShortcut)
        self.st = next(v.id for v in self.g.vertices.values() if v.type == VertexType.FUEL_STATION)
        self.np = next(v.id for v in self.g.vertices.values() if v.type == VertexType.NITRO_PICKUP)

    def test_blockage_blocks_and_stays_until_reversed(self):
        self.m.schedule(ET.ROAD_BLOCKAGE, 5, self.e0)
        self.assertEqual(self.m.advance_to(4.9), [])
        self.assertEqual(len(self.m.advance_to(5)), 1)
        self.assertEqual(self.g.edges[self.e0].status, EdgeStatus.BLOCKED)
        self.m.advance_to(1000)
        self.assertEqual(self.g.edges[self.e0].status, EdgeStatus.BLOCKED)

    def test_blocked_edge_excluded_then_restored_on_expiry(self):
        self.m.schedule(ET.ROAD_BLOCKAGE, 1, self.e0, duration=10)
        self.m.advance_to(2)
        self.assertNotIn(self.e0, [e.id for u in self.g.vertices for e, _ in self.g.neighbors(u)])
        self.m.advance_to(11)
        self.assertEqual(self.g.edges[self.e0].status, EdgeStatus.OPEN)

    def test_overlapping_oil_effects_independent(self):
        v0 = self.g.version
        self.m.schedule(ET.OIL_SPILL, 0, self.e0, duration=20)
        self.m.schedule(ET.OIL_SPILL, 10, self.e0, duration=20)
        self.m.advance_to(15)
        self.assertEqual(len(self.g.effects_on(self.e0)), 2)
        self.m.advance_to(21)                                   # first expired, second still active
        self.assertEqual(len(self.g.effects_on(self.e0)), 1)
        self.m.advance_to(31)
        self.assertEqual(self.g.effects_on(self.e0), [])
        self.assertGreater(self.g.version, v0)

    def test_overlapping_blockages_edge_stays_blocked(self):
        self.m.schedule(ET.ROAD_BLOCKAGE, 0, self.e0, duration=10)
        self.m.schedule(ET.ROAD_BLOCKAGE, 5, self.e0, duration=20)
        self.m.advance_to(12)
        self.assertEqual(self.g.edges[self.e0].status, EdgeStatus.BLOCKED)
        self.m.advance_to(26)
        self.assertEqual(self.g.edges[self.e0].status, EdgeStatus.OPEN)

    def test_speed_restriction_expires(self):
        self.m.schedule(ET.SPEED_RESTRICTION, 0, self.e0)
        self.m.advance_to(1)
        self.assertLess(self.g.speed_factor(self.g.edges[self.e0]), 1.0)
        self.m.advance_to(16)
        self.assertEqual(self.g.speed_factor(self.g.edges[self.e0]), 1.0)

    def test_simultaneous_events_one_batch_in_priority_order(self):
        a = self.m.schedule(ET.OIL_SPILL, 3, self.e0)
        b = self.m.schedule(ET.ROAD_BLOCKAGE, 3, self.e0)
        applied = self.m.advance_to(3)
        self.assertEqual([e.eventId for e in applied], [b, a])

    def test_cancel_pending_and_applied(self):
        a = self.m.schedule(ET.ROAD_BLOCKAGE, 5, self.e0)
        self.assertTrue(self.m.cancel(a))
        self.assertEqual(self.m.advance_to(10), [])
        self.assertEqual(self.g.edges[self.e0].status, EdgeStatus.OPEN)
        b = self.m.schedule(ET.ROAD_BLOCKAGE, 11, self.e0)
        self.m.advance_to(12)
        self.assertTrue(self.m.cancel(b))
        self.assertEqual(self.g.edges[self.e0].status, EdgeStatus.OPEN)
        self.assertFalse(self.m.cancel(12345))

    def test_missing_or_invalid_targets_and_past_time(self):
        with self.assertRaises(ValueError): self.m.schedule(ET.ROAD_BLOCKAGE, 1, 99999)
        with self.assertRaises(ValueError): self.m.schedule(ET.STATION_AVAILABILITY, 1, self.e0 + 10 ** 6)
        with self.assertRaises(ValueError): self.m.schedule(ET.NITRO_BOOSTER, 1, self.st)       # wrong vertex type
        plain = next(e.id for e in self.g.edges.values() if not e.isShortcut)
        with self.assertRaises(ValueError): self.m.schedule(ET.SHORTCUT_TOGGLE, 1, plain)
        self.m.advance_to(10)
        with self.assertRaises(ValueError): self.m.schedule(ET.ROAD_BLOCKAGE, 5, self.e0)

    def test_shortcut_close_then_reverse(self):
        self.m.schedule(ET.SHORTCUT_TOGGLE, 1, self.sc)
        self.m.advance_to(2)
        self.assertEqual(self.g.edges[self.sc].status, EdgeStatus.BLOCKED)
        self.m.schedule(ET.SHORTCUT_TOGGLE, 5, self.sc)
        self.m.advance_to(6)
        self.assertEqual(self.g.edges[self.sc].status, EdgeStatus.OPEN)

    def test_station_off_then_back(self):
        self.m.schedule(ET.STATION_AVAILABILITY, 1, self.st)
        self.m.advance_to(2)
        self.assertFalse(self.g.vertices[self.st].active)
        self.m.advance_to(32)
        self.assertTrue(self.g.vertices[self.st].active)

    def test_nitro_booster_activates_and_collect_ends_it(self):
        self.g.set_station_active(self.np, False)
        self.m.schedule(ET.NITRO_BOOSTER, 1, self.np)
        self.m.advance_to(2)
        self.assertTrue(self.g.vertices[self.np].active)
        self.m.notify_collected(self.np)
        self.assertFalse(self.g.vertices[self.np].active)

    def test_log_and_determinism(self):
        def run():
            g = load_track(TRACK); m = EventManager(g)
            m.schedule(ET.ROAD_BLOCKAGE, 2, self.e0, 5); m.schedule(ET.OIL_SPILL, 2, self.e0)
            m.advance_to(50)
            return m.log
        self.assertEqual(run(), run())
        self.assertTrue(any("expired" in s for s in run()))


class BlockageRestoreTests(unittest.TestCase):
    """Regression: a blockage must give the edge back its ORIGINAL status (Graph.unblock_edge would force OPEN)."""

    def setUp(self):
        self.g = load_track(TRACK)
        self.m = EventManager(self.g)
        self.e = next(iter(self.g.edges))
        self.sc = next(e.id for e in self.g.edges.values() if e.isShortcut)
        self.st = lambda eid=None: self.g.edges[self.e if eid is None else eid].status

    def test_restricted_edge_returns_to_restricted(self):
        self.g.set_status(self.e, EdgeStatus.RESTRICTED)
        self.m.schedule(ET.ROAD_BLOCKAGE, 1, self.e, duration=10)
        self.m.advance_to(2)
        self.assertEqual(self.st(), EdgeStatus.BLOCKED)
        self.m.advance_to(12)
        self.assertEqual(self.st(), EdgeStatus.RESTRICTED)

    def test_open_edge_still_returns_to_open(self):
        self.m.schedule(ET.ROAD_BLOCKAGE, 1, self.e, duration=10)
        self.m.advance_to(12)
        self.assertEqual(self.st(), EdgeStatus.OPEN)

    def test_overlapping_blockages_restore_only_after_last_expires(self):
        self.g.set_status(self.e, EdgeStatus.RESTRICTED)
        self.m.schedule(ET.ROAD_BLOCKAGE, 0, self.e, duration=10)
        self.m.schedule(ET.ROAD_BLOCKAGE, 5, self.e, duration=20)     # outlives the first
        self.m.advance_to(12)
        self.assertEqual(self.st(), EdgeStatus.BLOCKED)
        self.m.advance_to(26)
        self.assertEqual(self.st(), EdgeStatus.RESTRICTED)

    def test_overlap_where_later_blockage_ends_first(self):
        self.g.set_status(self.e, EdgeStatus.RESTRICTED)
        self.m.schedule(ET.ROAD_BLOCKAGE, 0, self.e, duration=30)
        self.m.schedule(ET.ROAD_BLOCKAGE, 5, self.e, duration=5)      # nested inside the first
        self.m.advance_to(12)
        self.assertEqual(self.st(), EdgeStatus.BLOCKED)
        self.m.advance_to(31)
        self.assertEqual(self.st(), EdgeStatus.RESTRICTED)

    def test_blockage_plus_shortcut_closure_overlap(self):
        self.g.set_status(self.sc, EdgeStatus.RESTRICTED)
        self.m.schedule(ET.ROAD_BLOCKAGE, 0, self.sc, duration=10)
        self.m.schedule(ET.SHORTCUT_TOGGLE, 5, self.sc, duration=20)
        self.m.advance_to(12)
        self.assertEqual(self.st(self.sc), EdgeStatus.BLOCKED)
        self.m.advance_to(26)
        self.assertEqual(self.st(self.sc), EdgeStatus.RESTRICTED)

    def test_second_blockage_after_restore_remembers_status_again(self):
        self.g.set_status(self.e, EdgeStatus.RESTRICTED)
        self.m.schedule(ET.ROAD_BLOCKAGE, 0, self.e, duration=5)
        self.m.schedule(ET.ROAD_BLOCKAGE, 10, self.e, duration=5)
        self.m.advance_to(7)
        self.assertEqual(self.st(), EdgeStatus.RESTRICTED)
        self.m.advance_to(12)
        self.assertEqual(self.st(), EdgeStatus.BLOCKED)
        self.m.advance_to(20)
        self.assertEqual(self.st(), EdgeStatus.RESTRICTED)

    def test_cancelling_applied_blockage_restores_original_status(self):
        self.g.set_status(self.e, EdgeStatus.RESTRICTED)
        i = self.m.schedule(ET.ROAD_BLOCKAGE, 1, self.e)
        self.m.advance_to(2)
        self.assertTrue(self.m.cancel(i))
        self.assertEqual(self.st(), EdgeStatus.RESTRICTED)

    def test_edge_blocked_in_the_file_is_not_opened_by_expiry(self):
        self.g.set_status(self.e, EdgeStatus.BLOCKED)
        self.m.schedule(ET.ROAD_BLOCKAGE, 1, self.e, duration=5)
        self.m.advance_to(10)
        self.assertEqual(self.st(), EdgeStatus.BLOCKED)

    def test_restricted_time_penalty_survives_blockage(self):
        self.g.set_status(self.e, EdgeStatus.RESTRICTED)
        t0 = self.g.effective_time(self.g.edges[self.e])
        self.m.schedule(ET.ROAD_BLOCKAGE, 1, self.e, duration=5)
        self.m.advance_to(10)
        self.assertEqual(self.g.effective_time(self.g.edges[self.e]), t0)


if __name__ == "__main__":
    unittest.main()
