"""Undirected MST backbone: Kruskal (union-find) or Prim (binary heap)."""
import heapq, math


def _weight(points, ed):
    if len(ed) > 2:
        return ed[2]
    (x1, y1), (x2, y2) = points[ed[0]], points[ed[1]]
    return math.hypot(x1 - x2, y1 - y2)


def mst_backbone(points, candidate_edges, algo="kruskal", trace=None):
    """points: [(x, y)], candidate_edges: [(u, v)] or [(u, v, w)] (w defaults to Euclidean length).
    Raises ValueError if the candidate graph is disconnected (that would only give a spanning forest).
    Returns the chosen edges (same tuples). trace: optional list of (edge, accepted) in decision order (Lab panel).
    Kruskal O(E log E) with union-find; Prim O(E log V) with a binary heap."""
    n = len(points)
    if n == 0:
        return []
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for ed in candidate_edges:
        parent[find(ed[0])] = find(ed[1])
    if len({find(i) for i in range(n)}) != 1:
        raise ValueError("candidate graph is disconnected: no spanning tree exists")
    out = []
    if algo == "kruskal":
        parent = list(range(n))
        for ed in sorted(candidate_edges, key=lambda e: (_weight(points, e), e[0], e[1])):
            a, b = find(ed[0]), find(ed[1])
            if a != b:
                parent[a] = b
                out.append(ed)
            if trace is not None:
                trace.append((ed, a != b))
            if len(out) == n - 1:
                break
    elif algo == "prim":
        adj = [[] for _ in range(n)]
        for ed in candidate_edges:
            w = _weight(points, ed)
            adj[ed[0]].append((w, ed[1], ed))
            adj[ed[1]].append((w, ed[0], ed))
        seen, h = {0}, [(w, v, ed) for w, v, ed in adj[0]]
        heapq.heapify(h)
        while h and len(out) < n - 1:
            w, v, ed = heapq.heappop(h)
            if v in seen:
                if trace is not None:
                    trace.append((ed, False))
                continue
            seen.add(v)
            out.append(ed)
            if trace is not None:
                trace.append((ed, True))
            for item in adj[v]:
                if item[1] not in seen:
                    heapq.heappush(h, item)
    else:
        raise ValueError("algo must be 'kruskal' or 'prim'")
    return out
