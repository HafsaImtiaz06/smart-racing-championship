from ..core.results import PathResult
from ..core import constants as K


def build_result(g, vertices, edge_ids, preset=K.DEFAULT_PRESET,
                 expanded=0, relaxed=0, heap_ops=0, runtime_s=0.0):
    """Build a PathResult (with cost, distance, time, fuel sums) from a path."""
    r = PathResult(found=True, vertices=vertices, edges=edge_ids,
                   expanded=expanded, relaxed=relaxed, heap_ops=heap_ops, runtime_s=runtime_s)
    for eid in edge_ids:
        e = g.edges[eid]
        r.cost += g.edge_cost(e, preset)
        r.distance += e.distance
        r.time += g.effective_time(e)
        r.fuel += g.effective_fuel(e)
    return r
