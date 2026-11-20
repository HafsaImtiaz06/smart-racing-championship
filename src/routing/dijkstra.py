import heapq
import time
from ..core.results import PathResult
from ..core import constants as K
from .common import build_result


def dijkstra(g, source, target, preset=K.DEFAULT_PRESET, trace=None):
    """Least-cost path using Graph.edge_cost(e, preset). found=False if unreachable.
    trace (optional, for the Algorithm Lab): trace(("expand", u, cost_so_far)) when u is settled and
    trace(("relax", u, v, edge_id, improved)) for every road examined. The result never depends on trace.
    Counters: expanded = vertices popped and settled, relaxed = edges examined, heap_ops = pushes + pops."""
    t0 = time.perf_counter()
    if source not in g.vertices or target not in g.vertices:
        return PathResult(found=False)
    dist = {source: 0.0}
    parent = {source: None}              # vertex -> (previous vertex, edge id)
    done = set()
    counter = 0                          # tie-breaker: equal costs pop in insertion order (deterministic)
    heap = [(0.0, counter, source)]
    heap_ops = 1
    expanded = relaxed = 0
    while heap:
        d, _, u = heapq.heappop(heap)
        heap_ops += 1
        if u in done:                    # stale entry
            continue
        done.add(u)
        expanded += 1
        if trace is not None:
            trace(("expand", u, d))
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
        for e, v in g.neighbors(u):
            relaxed += 1
            if v in done:
                if trace is not None:
                    trace(("relax", u, v, e.id, False))
                continue
            nd = d + g.edge_cost(e, preset)
            better = nd < dist.get(v, float("inf"))
            if trace is not None:
                trace(("relax", u, v, e.id, better))
            if better:
                dist[v] = nd
                parent[v] = (u, e.id)
                counter += 1
                heapq.heappush(heap, (nd, counter, v))
                heap_ops += 1
    return PathResult(found=False, expanded=expanded, relaxed=relaxed, heap_ops=heap_ops,
                      runtime_s=time.perf_counter() - t0)
