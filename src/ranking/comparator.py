"""PERSON C. The ONE championship comparator (spec 4.6). Every sort and top-k goes through compare().

Total order, best first: more points, more wins, lower sum of finish positions,
lower best fastest lap, lower racer id. Racer id is unique, so no two different entries tie.
"""
from ..core.models import ChampionshipEntry
from ..core.results import SortStats


def championship_key(e: ChampionshipEntry) -> tuple:
    """Smaller tuple = better rank."""
    return (-e.totalPoints, -e.wins, e.sumOfFinishPositions, e.bestFastestLap, e.racerId)


def better(a: ChampionshipEntry, b: ChampionshipEntry) -> bool:
    return championship_key(a) < championship_key(b)


def compare(a: ChampionshipEntry, b: ChampionshipEntry, stats: SortStats = None) -> int:
    """-1 if a ranks before b, 1 if after, 0 only for identical keys. Counts ONE comparison per call."""
    if stats is not None:
        stats.comparisons += 1
    ka, kb = championship_key(a), championship_key(b)
    return -1 if ka < kb else (1 if ka > kb else 0)
