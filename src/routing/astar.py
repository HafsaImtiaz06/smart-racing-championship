import heapq
import time
from ..core.results import PathResult
from ..core import constants as K
from .common import build_result


def astar(g, source, target, preset=K.DEFAULT_PRESET):
    """A* with h(v) = g.heuristic_ratio(preset) * g.euclid(v, target).
    The heuristic is admissible and consistent when every edge distance >= straight-line distance
    (Graph.validate_geometry() == []), because effects and restrictions only ever raise edge costs.
    Same counters as Dijkstra: expanded, relaxed, heap_ops."""
    t0 = time.perf_counter()
    if source not in g.vertices or target not in g.vertices:
        return PathResult(found=False)
    ratio = g.heuristic_ratio(preset)

    def h(v):
        return ratio * g.euclid(v, target)

    best_g = {source: 0.0}
    parent = {source: None}              # vertex -> (previous vertex, edge id)
    done = set()
    counter = 0                          # tie-breaker: deterministic order for equal f
    heap = [(h(source), counter, source)]
    heap_ops = 1
    expanded = relaxed = 0
    while heap:
        _, _, u = heapq.heappop(heap)
        heap_ops += 1
        if u in done:                    # stale entry
            continue
        done.add(u)
        expanded += 1
        if u == target:
            verts, edges, cur = [u], [], u
            while parent[cur] is not None:
                prev, eid = parent[cur]
                verts.append(prev)
                edges.append(eid)
                cur = prev
            verts.reverse()
            edges.reverse()
            return build_result(g, verts, edges, preset=preset, expanded=expanded,
                                relaxed=relaxed, heap_ops=heap_ops,
                                runtime_s=time.perf_counter() - t0)
        gu = best_g[u]
        for e, v in g.neighbors(u):
            relaxed += 1
            if v in done:
                continue
            ng = gu + g.edge_cost(e, preset)
            if ng < best_g.get(v, float("inf")):
                best_g[v] = ng
                parent[v] = (u, e.id)
                counter += 1
                heapq.heappush(heap, (ng + h(v), counter, v))
                heap_ops += 1
    return PathResult(found=False, expanded=expanded, relaxed=relaxed, heap_ops=heap_ops,
                      runtime_s=time.perf_counter() - t0)
