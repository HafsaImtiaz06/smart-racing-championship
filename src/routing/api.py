"""PERSON A owns this folder. CONTRACT (frozen): these signatures are what Person C and Person B call.
All functions use Graph.neighbors() and Graph.edge_cost() only. Return PathResult / RoutePlan from core.results."""
from ..core.graph import Graph
from ..core.results import PathResult, RoutePlan
from ..core import constants as K
from .bfs import bfs_path, reachable_from   # implemented in bfs.py
from .dijkstra import dijkstra               # implemented in dijkstra.py
from .astar import astar                     # implemented in astar.py


def dfs_analysis(g: Graph, source: int) -> dict:
    """Return {'order': [...], 'has_cycle': bool, 'components': [[ids]], 'dead_ends': [ids]}."""
    raise NotImplementedError


def alternative_routes(g: Graph, source: int, target: int, max_routes: int = 20, max_len: int = 40) -> list:
    """Bounded simple-path enumeration (documented limits). Returns list of vertex-id lists."""
    raise NotImplementedError


def plan_route(g: Graph, current_vertex: int, remaining_checkpoints: list, finish: int,
               preset: str = K.DEFAULT_PRESET, algo: str = "astar") -> RoutePlan:
    """Ordered legs: current -> cp1 -> cp2 ... -> finish. NEVER skips a checkpoint.
    remaining_checkpoints = vertex ids still to visit, in required order. Set plan.graph_version = g.version."""
    raise NotImplementedError
