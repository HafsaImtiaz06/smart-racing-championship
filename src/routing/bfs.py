import time
from collections import deque
from ..core.results import PathResult
from .common import build_result


def bfs_path(g, source, target):
    """Min-edge-count path from source to target. found=False if unreachable."""
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
        for e, v in g.neighbors(u):
            relaxed += 1
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


def reachable_from(g, source):
    """Set of vertex ids reachable from source through traversable edges."""
    if source not in g.vertices:
        return set()
    seen, queue = {source}, deque([source])
    while queue:
        u = queue.popleft()
        for _, v in g.neighbors(u):
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return seen
