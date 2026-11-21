"""PERSON B owns planning/, events/, generation/. CONTRACT (frozen): signatures below are what others call.
Implementations live in knapsack.py, refuel.py and recommend.py (optional trailing arguments only)."""
from .knapsack import knapsack_dp, greedy_select, knapsack_bruteforce      # (costs, benefits, budget) -> KnapsackResult
from .refuel import refuel_plan             # (need, station_available, capacity, start_fuel) -> RefuelPlan
from .recommend import recommend_pickups    # (g, route_plan, racer, preset) -> list of vertex ids
