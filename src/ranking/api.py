"""PERSON C. CONTRACT (frozen). ONE comparator for everything."""
from typing import List
from ..core.models import ChampionshipEntry
from ..core.results import SortStats


def championship_key(e: ChampionshipEntry) -> tuple:
    """Total order (spec 4.6): more points, more wins, lower sum of positions, lower best fastest lap, lower racer id.
    Smaller tuple = better rank."""
    return (-e.totalPoints, -e.wins, e.sumOfFinishPositions, e.bestFastestLap, e.racerId)


def better(a: ChampionshipEntry, b: ChampionshipEntry) -> bool:
    return championship_key(a) < championship_key(b)


def merge_sort(entries: List[ChampionshipEntry], stats: SortStats = None) -> List[ChampionshipEntry]: raise NotImplementedError
def quick_sort(entries: List[ChampionshipEntry], stats: SortStats = None) -> List[ChampionshipEntry]: raise NotImplementedError
def heap_sort(entries: List[ChampionshipEntry], stats: SortStats = None) -> List[ChampionshipEntry]: raise NotImplementedError
def top_k(entries: List[ChampionshipEntry], k: int, stats: SortStats = None) -> List[ChampionshipEntry]: raise NotImplementedError
