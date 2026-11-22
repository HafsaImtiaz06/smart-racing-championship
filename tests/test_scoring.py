import math
import unittest
from src.core import constants as K
from src.core.models import RaceResult as R
from src.game.scoring import award_points
from src.game.championship import Championship
from src.ranking.api import quick_sort, heap_sort

INF = math.inf


def race(rid, rows):
    """rows: (racerId, position, finishTime, fastestLap)"""
    return [R(rid, r, p, t, f) for r, p, t, f in rows]


class TestAwardPoints(unittest.TestCase):
    def test_table_and_bonus(self):
        res = award_points(race(1, [(0, 1, 100, 40), (1, 2, 105, 38), (2, 3, 110, 41), (3, 4, 120, 42)]))
        self.assertEqual([r.pointsAwarded for r in res], [25, 18 + 1, 15, 12])   # racer 1 has fastest lap
        self.assertEqual([r.bonusPoints for r in res], [0, 1, 0, 0])

    def test_input_not_mutated_and_order_kept(self):
        rows = race(1, [(5, 1, 100, 40), (2, 2, 105, 41)])
        out = award_points(rows)
        self.assertEqual(rows[0].pointsAwarded, 0)
        self.assertEqual([r.racerId for r in out], [5, 2])

    def test_dnf_and_time_limit_get_nothing(self):
        res = award_points(race(1, [(0, 1, 100, 40), (1, 2, INF, 30), (2, 3, INF, INF)]))
        self.assertEqual([r.pointsAwarded for r in res], [25 + 1, 0, 0])   # DNF's 30s lap earns no bonus

    def test_bonus_tie_goes_to_lower_racer_id(self):
        res = award_points(race(1, [(3, 1, 100, 40), (1, 2, 105, 40)]))
        self.assertEqual(res[1].bonusPoints, 1); self.assertEqual(res[0].bonusPoints, 0)

    def test_all_dnf(self):
        res = award_points(race(1, [(0, 1, INF, INF), (1, 2, INF, INF)]))
        self.assertTrue(all(r.pointsAwarded == 0 for r in res))

    def test_full_table_ten_racers_and_11th_zero(self):
        rows = [(i, i + 1, 100 + i, 50 + i) for i in range(11)]
        res = award_points(race(1, rows))
        base = [r.pointsAwarded - r.bonusPoints for r in res]
        self.assertEqual(base, K.POINTS_TABLE + [0])

    def test_bad_positions_rejected(self):
        with self.assertRaises(ValueError):
            award_points(race(1, [(0, 1, 100, 40), (1, 1, 101, 41)]))
        with self.assertRaises(ValueError):
            award_points(race(1, [(0, 1, INF, INF), (1, 2, 100, 40)]))   # DNF ahead of finisher


class TestChampionship(unittest.TestCase):
    def three_races(self):
        c = Championship([0, 1, 2, 3], total_races=3)
        c.record_race(race(1, [(0, 1, 100, 40), (1, 2, 105, 41), (2, 3, 110, 42), (3, 4, INF, INF)]))
        c.record_race(race(2, [(1, 1, 100, 39), (0, 2, 105, 40), (3, 3, 110, 43), (2, 4, INF, 44)]))
        c.record_race(race(3, [(0, 1, 100, 38), (1, 2, 101, 45), (2, 3, 102, 46), (3, 4, 103, 47)]))
        return c

    def test_totals_wins_positions(self):
        c = self.three_races()
        e0, e1 = c.entries[0], c.entries[1]
        self.assertEqual((e0.totalPoints, e0.wins, e0.sumOfFinishPositions), (25 + 18 + 25 + 1 + 1, 2, 4))
        self.assertEqual(e0.bestFastestLap, 38)
        self.assertEqual((e1.wins, e1.sumOfFinishPositions), (1, 5))

    def test_standings_and_champion(self):
        c = self.three_races()
        self.assertTrue(c.is_complete())
        order = [e.racerId for e in c.standings()]
        self.assertEqual(order[0], 0)
        self.assertEqual(c.champion().racerId, 0)
        self.assertEqual([e.racerId for e in c.standings(sort=quick_sort)], order)
        self.assertEqual([e.racerId for e in c.standings(sort=heap_sort)], order)
        self.assertEqual([e.racerId for e in c.top(2)], order[:2])

    def test_champion_none_until_done(self):
        c = Championship([0, 1], 2)
        c.record_race(race(1, [(0, 1, 100, 40), (1, 2, 101, 41)]))
        self.assertIsNone(c.champion())

    def test_full_tie_falls_through_to_racer_id(self):
        c = Championship([0, 1], 2)
        # Each racer wins once and is second once (44 pts, 1 win, position sum 3, best lap 40): racer id decides.
        c.record_race(race(1, [(0, 1, 100, 40), (1, 2, 101, 41)]))
        c.record_race(race(2, [(1, 1, 100, 40), (0, 2, 101, 41)]))
        a, b = c.entries[0], c.entries[1]
        self.assertEqual((a.totalPoints, a.wins, a.sumOfFinishPositions, a.bestFastestLap),
                         (b.totalPoints, b.wins, b.sumOfFinishPositions, b.bestFastestLap))
        self.assertEqual([e.racerId for e in c.standings()], [0, 1])

    def test_validation(self):
        c = Championship([0, 1], 1)
        with self.assertRaises(ValueError):
            c.record_race(race(1, [(0, 1, 100, 40)]))                      # racer 1 missing
        c.record_race(race(1, [(0, 1, 100, 40), (1, 2, 101, 41)]))
        with self.assertRaises(ValueError):
            c.record_race(race(2, [(0, 1, 100, 40), (1, 2, 101, 41)]))     # already complete
        with self.assertRaises(ValueError):
            Championship([0, 0], 1)


if __name__ == "__main__":
    unittest.main()
