from ..core.results import RoutePlan
from ..core import constants as K
from .astar import astar
from .dijkstra import dijkstra
from .bfs import bfs_path

_ALGOS = {"astar": astar, "dijkstra": dijkstra}


def plan_route(g, current_vertex, remaining_checkpoints, finish, preset=K.DEFAULT_PRESET, algo="astar"):
    """Ordered route: current -> cp1 -> cp2 -> ... -> finish. NEVER skips or reorders a checkpoint.
    remaining_checkpoints: vertex ids still to visit, in required order (repeat ids for extra laps).
    found=False if ANY leg is unreachable (legs holds what was planned, last entry is the failed leg).
    plan.graph_version = g.version at planning time; use is_stale(plan, g) to know when to replan."""
    if algo == "bfs":
        search = lambda graph, s, t, p: bfs_path(graph, s, t)
    elif algo in _ALGOS:
        search = lambda graph, s, t, p: _ALGOS[algo](graph, s, t, p)
    else:
        raise ValueError("unknown algo: %r (use 'astar', 'dijkstra' or 'bfs')" % (algo,))
    plan = RoutePlan(found=True, graph_version=g.version)
    stops = list(remaining_checkpoints) + [finish]
    here = current_vertex
    for nxt in stops:
        leg = search(g, here, nxt, preset)
        plan.legs.append(leg)
        if not leg.found:
            plan.found = False
            return plan
        plan.cost += leg.cost
        plan.distance += leg.distance
        plan.time += leg.time
        plan.fuel += leg.fuel
        here = nxt
    return plan


def route_vertices(plan):
    """Flat vertex list of the whole plan (leg joints appear once)."""
    out = []
    for leg in plan.legs:
        if not leg.found:
            break
        out.extend(leg.vertices if not out else leg.vertices[1:])
    return out


def route_edges(plan):
    """Flat edge-id list of the whole plan."""
    out = []
    for leg in plan.legs:
        if leg.found:
            out.extend(leg.edges)
    return out


def is_stale(plan, g):
    """True if the graph changed since planning (block, unblock, effect, station change) -> replan."""
    return plan.graph_version != g.version
