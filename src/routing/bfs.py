import time
from collections import deque
from ..core.results import PathResult
from .common import build_result


def bfs_path(g, source, target, trace=None):
    """Min-edge-count path from source to target. found=False if unreachable.
    trace: optional callback for the Algorithm Lab. Called as trace(("expand", u)) when u is dequeued and
    trace(("relax", u, v, edge_id, discovered)) for every road examined. The result never depends on trace."""
    t0 = time.perf_counter()
    if source not in g.vertices or target not in g.vertices:
        return PathResult(found=False)
    if source == target:
        return build_result(g, [source], [], runtime_s=time.perf_counter() - t0)
    parent = {source: None}          # vertex -> (previous vertex, edge id)
    queue = deque([source])
    expanded = relaxed = 0
    while queue:
        u = queue.popleft()
        expanded += 1
        if trace is not None:
            trace(("expand", u))
        for e, v in g.neighbors(u):
            relaxed += 1
            if trace is not None:
                trace(("relax", u, v, e.id, v not in parent))
            if v not in parent:
                parent[v] = (u, e.id)
                if v == target:
                    verts, edges, cur = [v], [], v
                    while parent[cur] is not None:
                        prev, eid = parent[cur]
                        verts.append(prev)
                        edges.append(eid)
                        cur = prev
                    verts.reverse()
                    edges.reverse()
                    return build_result(g, verts, edges, expanded=expanded, relaxed=relaxed,
                                        runtime_s=time.perf_counter() - t0)
                queue.append(v)
    return PathResult(found=False, expanded=expanded, relaxed=relaxed,
                      runtime_s=time.perf_counter() - t0)


def bfs_order(g, source):
    """Full BFS traversal from source over traversable roads. Returns (order, examined):
    order = vertices in the order they are dequeued, examined = number of roads looked at (sum of out-degrees)."""
    if source not in g.vertices:
        return [], 0
    seen, queue, order, examined = {source}, deque([source]), [], 0
    while queue:
        u = queue.popleft()
        order.append(u)
        for _, v in g.neighbors(u):
            examined += 1
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return order, examined


def reachable_from(g, source):
    """Set of vertex ids reachable from source through traversable edges."""
    return set(bfs_order(g, source)[0])
