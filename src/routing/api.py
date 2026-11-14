"""PERSON A owns this folder. CONTRACT (frozen): these signatures are what Person C and Person B call.
All functions use Graph.neighbors() and Graph.edge_cost() only. Return PathResult / RoutePlan from core.results."""
from ..core.graph import Graph
from ..core.results import PathResult, RoutePlan
from ..core import constants as K


def bfs_path(g: Graph, source: int, target: int) -> PathResult:
    """Min-edge-count path. found=False if unreachable. Fill expanded/relaxed counters."""
    raise NotImplementedError


def reachable_from(g: Graph, source: int) -> set:
    """Set of vertex ids reachable from source via traversable edges (BFS)."""
    raise NotImplementedError


def dfs_analysis(g: Graph, source: int) -> dict:
    """Return {'order': [...], 'has_cycle': bool, 'components': [[ids]], 'dead_ends': [ids]}."""
    raise NotImplementedError


def alternative_routes(g: Graph, source: int, target: int, max_routes: int = 20, max_len: int = 40) -> list:
    """Bounded simple-path enumeration (documented limits). Returns list of vertex-id lists."""
    raise NotImplementedError


def dijkstra(g: Graph, source: int, target: int, preset: str = K.DEFAULT_PRESET) -> PathResult:
    raise NotImplementedError


def astar(g: Graph, source: int, target: int, preset: str = K.DEFAULT_PRESET) -> PathResult:
    """h(v) = g.heuristic_ratio(preset) * g.euclid(v, target)."""
    raise NotImplementedError


def plan_route(g: Graph, current_vertex: int, remaining_checkpoints: list, finish: int,
               preset: str = K.DEFAULT_PRESET, algo: str = "astar") -> RoutePlan:
    """Ordered legs: current -> cp1 -> cp2 ... -> finish. NEVER skips a checkpoint.
    remaining_checkpoints = vertex ids still to visit, in required order. Set plan.graph_version = g.version."""
    raise NotImplementedError
