"""PERSON C. CONTRACT (frozen)."""
from ..core.graph import Graph


class RaceEngine:
    """Owns Racer list, clock and the main loop. Calls routing.api.plan_route (A), EventManager.advance_to (B),
    planning.api.refuel_plan (B). Replans a racer when EventManager reports applied events or graph.version changed."""
    def __init__(self, graph: Graph, racers: list, events, preset: str = "Balanced"): raise NotImplementedError
    def step(self, dt: float) -> None: raise NotImplementedError
    def is_finished(self) -> bool: raise NotImplementedError
    def results(self, race_id: int) -> list: raise NotImplementedError   # list[RaceResult]


def award_points(results: list) -> list:
    """Apply K.POINTS_TABLE and K.FASTEST_LAP_BONUS; DNF / time-limit unfinished get 0."""
    raise NotImplementedError
