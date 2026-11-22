"""PERSON C. Championship state: accumulates race results and ranks standings with the common comparator.

Rules (documented):
  * Every race must contain exactly one RaceResult per registered racer.
  * totalPoints += pointsAwarded;  wins += 1 for finishPosition 1 when that racer finished;
    sumOfFinishPositions += finishPosition (DNF / unfinished racers count at the position they were ranked);
    bestFastestLap = min over all races of any finite fastestLap.
"""
import math
from typing import Callable, Dict, List
from ..core.models import ChampionshipEntry, RaceResult
from ..core.results import SortStats
from ..ranking.api import merge_sort, top_k
from .scoring import award_points, is_finisher


class Championship:
    def __init__(self, racer_ids, total_races: int):
        ids = list(racer_ids)
        if len(ids) != len(set(ids)) or not ids:
            raise ValueError("racer ids must be non-empty and unique")
        self.total_races = total_races
        self.entries: Dict[int, ChampionshipEntry] = {i: ChampionshipEntry(racerId=i) for i in ids}
        self.history: List[List[RaceResult]] = []      # scored results, one list per race

    @property
    def races_done(self) -> int:
        return len(self.history)

    def is_complete(self) -> bool:
        return self.races_done >= self.total_races

    def record_race(self, results: List[RaceResult]) -> List[RaceResult]:
        """Score one race, update every entry, return the scored results."""
        if self.is_complete():
            raise ValueError("championship already complete")
        if sorted(r.racerId for r in results) != sorted(self.entries):
            raise ValueError("race must contain exactly one result per registered racer")
        scored = award_points(results)
        for r in scored:
            e = self.entries[r.racerId]
            e.totalPoints += r.pointsAwarded
            if is_finisher(r) and r.finishPosition == 1:
                e.wins += 1
            e.sumOfFinishPositions += r.finishPosition
            if math.isfinite(r.fastestLap):
                e.bestFastestLap = min(e.bestFastestLap, r.fastestLap)
        self.history.append(scored)
        return scored

    def standings(self, sort: Callable = merge_sort, stats: SortStats = None) -> List[ChampionshipEntry]:
        """Full ranking, best first. `sort` may be merge_sort (default), quick_sort or heap_sort."""
        return sort(list(self.entries.values()), stats=stats)

    def top(self, k: int, stats: SortStats = None) -> List[ChampionshipEntry]:
        return top_k(list(self.entries.values()), k, stats=stats)

    def champion(self):
        """Champion entry once all races are done, else None."""
        return self.standings()[0] if self.is_complete() else None
