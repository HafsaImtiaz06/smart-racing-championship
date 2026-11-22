"""PERSON C. Race scoring (spec 4.6).

CONVENTIONS (documented rules; the race engine must follow them):
  * A racer FINISHED the race iff finishTime is finite.
    DNF and time-limit-unfinished racers have finishTime = math.inf  ->  they get NO points and NO bonus.
  * finishPosition is set by the race engine: unique, 1-based, finishers first (by finishTime, then racer id),
    then non-finishers (DNF / time-limit order per spec 4.2 rule 8).
  * fastestLap = best single-lap time, math.inf if the racer completed no lap.
  * Bonus: K.FASTEST_LAP_BONUS to the FINISHER with the lowest finite fastestLap (tie -> lower racer id),
    awarded regardless of finishing position.
"""
import math
from dataclasses import replace
from typing import List
from ..core import constants as K
from ..core.models import RaceResult


def is_finisher(r: RaceResult) -> bool:
    return math.isfinite(r.finishTime)


def points_for_position(position: int) -> int:
    return K.POINTS_TABLE[position - 1] if 1 <= position <= len(K.POINTS_TABLE) else 0


def award_points(results: List[RaceResult]) -> List[RaceResult]:
    """Apply K.POINTS_TABLE and K.FASTEST_LAP_BONUS. Returns NEW RaceResult objects in the same order."""
    positions = [r.finishPosition for r in results]
    if any(p < 1 for p in positions) or len(set(positions)) != len(positions):
        raise ValueError("finishPosition must be unique and >= 1: %r" % (positions,))
    worst_finisher = max([r.finishPosition for r in results if is_finisher(r)] or [0])
    best_non_finisher = min([r.finishPosition for r in results if not is_finisher(r)] or [math.inf])
    if worst_finisher > best_non_finisher:
        raise ValueError("a non-finisher is ranked ahead of a finisher")

    laps = [r for r in results if is_finisher(r) and math.isfinite(r.fastestLap)]
    bonus_id = min(laps, key=lambda r: (r.fastestLap, r.racerId)).racerId if laps and K.FASTEST_LAP_BONUS else None

    out = []
    for r in results:
        if is_finisher(r):
            bonus = K.FASTEST_LAP_BONUS if r.racerId == bonus_id else 0
            out.append(replace(r, bonusPoints=bonus, pointsAwarded=points_for_position(r.finishPosition) + bonus))
        else:
            out.append(replace(r, bonusPoints=0, pointsAwarded=0))
    return out
