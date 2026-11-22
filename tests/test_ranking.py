import random
import unittest
from functools import cmp_to_key
from src.core.models import ChampionshipEntry as E
from src.core.results import SortStats
from src.ranking.api import (championship_key, better, compare, merge_sort, quick_sort,
                             heap_sort, top_k)

SORTS = [merge_sort, quick_sort, heap_sort]


def entries(n, seed, dup_heavy=False):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        if dup_heavy:
            out.append(E(i, rng.choice([0, 10, 25]), rng.choice([0, 1]), 6, 30.0))
        else:
            out.append(E(i, rng.randint(0, 99), rng.randint(0, 3), rng.randint(3, 12),
                         round(rng.uniform(20, 40), 1)))
    return out


def reference(items):
    return sorted(items, key=cmp_to_key(compare))


class TestComparator(unittest.TestCase):
    def test_every_tiebreak_level(self):
        self.assertLess(compare(E(2, 50), E(1, 40)), 0)                           # points
        self.assertLess(compare(E(2, 50, 3), E(1, 50, 2)), 0)                     # wins
        self.assertLess(compare(E(2, 50, 2, 5), E(1, 50, 2, 9)), 0)               # sum of positions
        self.assertLess(compare(E(2, 50, 2, 5, 30.0), E(1, 50, 2, 5, 31.0)), 0)   # fastest lap
        self.assertLess(compare(E(1, 50, 2, 5, 30.0), E(2, 50, 2, 5, 30.0)), 0)   # racer id
        self.assertEqual(compare(E(1), E(1)), 0)

    def test_better_matches_key(self):
        self.assertTrue(better(E(1, 10), E(2, 5)))
        self.assertFalse(better(E(2, 5), E(1, 10)))

    def test_counts_one_comparison_per_call(self):
        s = SortStats(); compare(E(1), E(2), s); compare(E(2), E(1), s)
        self.assertEqual(s.comparisons, 2)


class TestSorts(unittest.TestCase):
    def check(self, data):
        ref = reference(data)
        for s in SORTS:
            self.assertEqual(s(data), ref, s.__name__)

    def test_empty_and_single(self):
        self.check([]); self.check([E(7, 10)])

    def test_random(self):
        for seed in range(25):
            self.check(entries(60, seed))

    def test_sorted_and_reverse(self):
        d = reference(entries(80, 1))
        self.check(d); self.check(d[::-1])

    def test_duplicate_heavy(self):
        self.check(entries(300, 3, dup_heavy=True))

    def test_final_racer_id_tiebreak_needed(self):
        d = [E(3, 25, 1, 4, 30.0), E(1, 25, 1, 4, 30.0), E(2, 25, 1, 4, 30.0)]
        for s in SORTS:
            self.assertEqual([e.racerId for e in s(d)], [1, 2, 3])

    def test_input_not_mutated(self):
        d = entries(40, 5); copy = list(d)
        for s in SORTS:
            s(d); self.assertEqual(d, copy)

    def test_all_three_identical(self):
        d = entries(120, 8)
        self.assertEqual(merge_sort(d), quick_sort(d))
        self.assertEqual(merge_sort(d), heap_sort(d))

    def test_stats_filled(self):
        d = entries(64, 2)
        for s in SORTS:
            st = SortStats(); s(d, stats=st)
            self.assertGreater(st.comparisons, 0); self.assertGreaterEqual(st.runtime_s, 0)

    def test_big_sorted_input_no_recursion_error(self):
        d = reference(entries(5000, 11))
        self.assertEqual(quick_sort(d), d)


class TestTopK(unittest.TestCase):
    def test_equals_prefix_of_full_sort(self):
        d = entries(100, 9); ref = reference(d)
        for k in (0, 1, 3, 10, 99, 100, 150):
            self.assertEqual(top_k(d, k), ref[:k], "k=%d" % k)

    def test_duplicate_heavy(self):
        d = entries(200, 4, dup_heavy=True)
        self.assertEqual(top_k(d, 5), reference(d)[:5])

    def test_empty(self):
        self.assertEqual(top_k([], 3), [])

    def test_small_k_uses_fewer_comparisons_than_full_sort(self):
        d = entries(2000, 6)
        a, b = SortStats(), SortStats()
        top_k(d, 5, stats=a); merge_sort(d, stats=b)
        self.assertLess(a.comparisons, b.comparisons)


if __name__ == "__main__":
    unittest.main()
