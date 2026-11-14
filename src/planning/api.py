"""PERSON B owns planning/, events/, generation/. CONTRACT (frozen)."""
from typing import List
from ..core.results import KnapsackResult, RefuelPlan


def knapsack_dp(costs: List[int], benefits: List[int], budget: int) -> KnapsackResult:
    """0/1 knapsack, integer costs, item reconstruction. chosen_ids are INDICES into the input lists."""
    raise NotImplementedError


def greedy_select(costs: List[int], benefits: List[int], budget: int) -> KnapsackResult:
    """Ratio greedy. Zero-cost positive-benefit items first; ties -> lower index."""
    raise NotImplementedError


def refuel_plan(need: List[float], station_available: List[bool], capacity: float, start_fuel: float) -> RefuelPlan:
    """need[j] = fuel from stop j to stop j+1 (last entry = to destination). Uses K.FUEL_SCALE, K.STATION_MAX_BUY,
    K.STATION_STOP_TIME. Minimises extra stop time. feasible=False if impossible."""
    raise NotImplementedError


def recommend_pickups(g, route_plan, racer, preset: str) -> list:
    """Glue used by GUI/race engine: build costs/benefits for optional pickups near the route, run DP, return chosen vertex ids.
    Must never recommend a plan that violates tank capacity, availability, or race rules."""
    raise NotImplementedError
