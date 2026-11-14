"""FROZEN result types returned across module boundaries."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class PathResult:
    found: bool
    vertices: List[int] = field(default_factory=list)   # start..target inclusive
    edges: List[int] = field(default_factory=list)      # edge ids along the path
    cost: float = 0.0          # EXACT scalar cost optimized (same one shown to the player)
    distance: float = 0.0
    time: float = 0.0
    fuel: float = 0.0
    # counters for Experiments 1 and 2 (0 if not applicable)
    expanded: int = 0          # vertices expanded/visited
    relaxed: int = 0           # edges examined/relaxed
    heap_ops: int = 0
    runtime_s: float = 0.0


@dataclass
class RoutePlan:
    """Ordered-checkpoint route: legs go current -> next checkpoint -> ... -> finish."""
    found: bool
    legs: List[PathResult] = field(default_factory=list)
    cost: float = 0.0
    distance: float = 0.0
    time: float = 0.0
    fuel: float = 0.0
    graph_version: int = -1    # Graph.version when planned; if it changed, replan


@dataclass
class KnapsackResult:
    best_value: int
    chosen_ids: List[int]
    total_cost: int
    dp_states: int = 0
    runtime_s: float = 0.0


@dataclass
class RefuelPlan:
    feasible: bool
    purchases: List[float] = field(default_factory=list)  # fuel units bought at each stop
    extra_time: float = 0.0
    dp_states: int = 0


@dataclass
class SortStats:
    comparisons: int = 0
    runtime_s: float = 0.0
