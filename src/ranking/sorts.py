"""PERSON C. Merge Sort (primary), Quick Sort (alternative), Heap Sort, and size-k top-k.

All return a NEW list ranked best-first and never mutate the input. All use comparator.compare.
stats (SortStats, optional): comparisons ACCUMULATE across calls (pass a fresh one per run);
runtime_s is overwritten and includes copying the input list, excludes nothing else.
"""
from time import perf_counter
from typing import List
from ..core.models import ChampionshipEntry
from ..core.results import SortStats
from .comparator import compare


def _timed(fn):
    def wrapper(entries, *args, stats: SortStats = None):
        t0 = perf_counter()
        out = fn(entries, *args, stats=stats)
        if stats is not None:
            stats.runtime_s = perf_counter() - t0
        return out
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


# ---------- Merge Sort: O(n log n) best/avg/worst, O(n) extra space, STABLE ----------
def _merge(a, stats):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left, right = _merge(a[:mid], stats), _merge(a[mid:], stats)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if compare(right[j], left[i], stats) < 0:      # right only if STRICTLY better -> stable
            out.append(right[j]); j += 1
        else:
            out.append(left[i]); i += 1
    out.extend(left[i:]); out.extend(right[j:])
    return out


@_timed
def merge_sort(entries: List[ChampionshipEntry], stats: SortStats = None):
    return _merge(list(entries), stats)


# ---------- Quick Sort: O(n log n) average, O(n^2) worst ----------
# Pivot: median of first/middle/last element (deterministic; avoids the worst case on sorted/reverse input).
# Partition: three-way (< pivot | == pivot | > pivot) so duplicate-heavy input does not degrade.
# Recurse on the smaller side, loop on the larger: stack depth O(log n).
def _median_of_three(a, lo, hi, stats):
    mid = (lo + hi) // 2
    trio = [a[lo], a[mid], a[hi]]
    for i in range(1, 3):                              # 3-element insertion sort
        k = i
        while k > 0 and compare(trio[k], trio[k - 1], stats) < 0:
            trio[k], trio[k - 1] = trio[k - 1], trio[k]; k -= 1
    return trio[1]


def _quick(a, lo, hi, stats):
    while lo < hi:
        pivot = _median_of_three(a, lo, hi, stats)
        lt, i, gt = lo, lo, hi
        while i <= gt:
            c = compare(a[i], pivot, stats)
            if c < 0:
                a[lt], a[i] = a[i], a[lt]; lt += 1; i += 1
            elif c > 0:
                a[i], a[gt] = a[gt], a[i]; gt -= 1
            else:
                i += 1
        if lt - lo < hi - gt:
            _quick(a, lo, lt - 1, stats); lo = gt + 1
        else:
            _quick(a, gt + 1, hi, stats); hi = lt - 1


@_timed
def quick_sort(entries: List[ChampionshipEntry], stats: SortStats = None):
    a = list(entries)
    _quick(a, 0, len(a) - 1, stats)
    return a


# ---------- Heap Sort: O(n log n), in place, NOT stable ----------
# Max-heap where "larger" = ranks LATER. Moving the root to the end repeatedly leaves best-first order.
def _sift_down(a, i, n, stats):
    while True:
        l, r, big = 2 * i + 1, 2 * i + 2, i
        if l < n and compare(a[l], a[big], stats) > 0:
            big = l
        if r < n and compare(a[r], a[big], stats) > 0:
            big = r
        if big == i:
            return
        a[i], a[big] = a[big], a[i]; i = big


def _heap_sort_inplace(a, stats):
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(a, i, n, stats)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        _sift_down(a, 0, end, stats)


@_timed
def heap_sort(entries: List[ChampionshipEntry], stats: SortStats = None):
    a = list(entries)
    _heap_sort_inplace(a, stats)
    return a


# ---------- Top-k with a size-k heap: O(n log k) time, O(k) space ----------
# Keep the k best seen so far in a max-heap whose ROOT is the worst of the k; a new entry
# replaces the root only if it ranks strictly better. Survivors are then ordered best-first.
def _sift_up(a, i, stats):
    while i > 0:
        p = (i - 1) // 2
        if compare(a[i], a[p], stats) > 0:
            a[i], a[p] = a[p], a[i]; i = p
        else:
            return


@_timed
def top_k(entries: List[ChampionshipEntry], k: int, stats: SortStats = None):
    if k <= 0:
        return []
    heap = []
    for x in entries:
        if len(heap) < k:
            heap.append(x); _sift_up(heap, len(heap) - 1, stats)
        elif compare(x, heap[0], stats) < 0:
            heap[0] = x; _sift_down(heap, 0, len(heap), stats)
    _heap_sort_inplace(heap, stats)
    return heap
