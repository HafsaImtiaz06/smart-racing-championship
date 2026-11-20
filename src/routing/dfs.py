from ..core.models import EdgeStatus, VertexType
from ..core import constants as K


def _neighbors_sorted(g, u):
    """Traversable out-edges of u as (neighbour id, edge), in a fixed order (neighbour id, then edge id)."""
    return sorted(((v, e) for e, v in g.neighbors(u)), key=lambda p: (p[0], p[1].id))


def dfs_analysis(g, source):
    """DFS analysis of the current graph (blocked roads are ignored). Returns a dict:
      'order'      DFS preorder of the vertices reachable from source (neighbours visited in ascending id).
      'has_cycle'  True if, among the vertices reachable from source, there is a closed route that does not just
                   reverse over the same road. One-way roads are respected; two parallel roads between the same
                   pair count; a loop road (from == to) counts.
      'components' connected components of the whole graph (all roads treated as two-way), blocked roads removed.
                   Each component is a sorted id list; components are ordered by smallest id.
      'visited' / 'examined'  counters of the DFS traversal: vertices visited and roads looked at.
      'dead_ends'  sorted ids of dead ends (spec 5.1): non-mandatory vertices (not a checkpoint, not Start/Finish) from
                   which the Finish cannot be reached without reversing, whichever road you arrive by. 'Reversing'
                   means turning straight back over the road you just used; going round a loop and out again is fine."""
    order, examined = dfs_order(g, source)
    return {"order": order, "has_cycle": _has_cycle(g, set(order)),
            "components": _components(g), "dead_ends": _dead_ends(g),
            "visited": len(order), "examined": examined}


def dfs_order(g, source, trace=None):
    """DFS preorder traversal from source (neighbours in ascending id), iterative.
    Returns (order, examined): examined = number of roads looked at (sum of out-degrees of visited vertices).
    trace (optional, for the Algorithm Lab): trace(("expand", u)) when u is first visited and
    trace(("relax", u, v, edge_id, discovered)) for every road examined. The result never depends on trace."""
    order, examined = [], 0
    if source in g.vertices:
        visited = {source}
        order.append(source)
        if trace is not None:
            trace(("expand", source))
        stack = [(source, iter(_neighbors_sorted(g, source)))]
        while stack:
            advanced = False
            u, it = stack[-1]
            for nb, e in it:
                examined += 1
                if trace is not None:
                    trace(("relax", u, nb, e.id, nb not in visited))
                if nb not in visited:
                    visited.add(nb)
                    order.append(nb)
                    if trace is not None:
                        trace(("expand", nb))
                    stack.append((nb, iter(_neighbors_sorted(g, nb))))
                    advanced = True
                    break
            if not advanced:
                stack.pop()
    return order, examined


def _has_cycle(g, reach):
    """Cycle test on the vertices in `reach` (all reachable from the source). Two DFS passes:
    (1) two-way roads only: a DFS that meets an already-visited vertex through a DIFFERENT road has found a cycle;
    (2) strongly connected components (Tarjan, one DFS) over all roads: a one-way road whose two ends are in the
        same component lies on a cycle. Every cycle is either all two-way roads (case 1) or uses a one-way road (case 2)."""
    two_way = {}
    for e in g.edges.values():
        if e.status == EdgeStatus.BLOCKED or e.from_ not in reach:
            continue
        if e.from_ == e.to:
            return True                                      # a loop road
        if not e.directed:
            two_way.setdefault(e.from_, []).append((e.to, e.id))
            two_way.setdefault(e.to, []).append((e.from_, e.id))
    seen = set()
    for root in sorted(two_way):
        if root in seen:
            continue
        seen.add(root)
        stack = [(root, None, iter(sorted(two_way[root])))]
        while stack:
            u, arrival_edge, it = stack[-1]
            advanced = False
            for nb, eid in it:
                if eid == arrival_edge:
                    continue
                if nb in seen:
                    return True
                seen.add(nb)
                stack.append((nb, eid, iter(sorted(two_way[nb]))))
                advanced = True
                break
            if not advanced:
                stack.pop()
    comp = _scc(g, reach)
    for e in g.edges.values():
        if e.status != EdgeStatus.BLOCKED and e.directed and e.from_ in reach and comp[e.from_] == comp[e.to]:
            return True
    return False


def _scc(g, reach):
    """Tarjan's strongly connected components (iterative DFS) over the traversable roads. Returns {vertex: component id}."""
    index, low, comp = {}, {}, {}
    on_stack, tarjan_stack = set(), []
    counter = ncomp = 0
    for root in sorted(reach):
        if root in index:
            continue
        index[root] = low[root] = counter
        counter += 1
        tarjan_stack.append(root)
        on_stack.add(root)
        work = [(root, iter(_neighbors_sorted(g, root)))]
        while work:
            u, it = work[-1]
            pushed = False
            for v, _ in it:
                if v not in index:
                    index[v] = low[v] = counter
                    counter += 1
                    tarjan_stack.append(v)
                    on_stack.add(v)
                    work.append((v, iter(_neighbors_sorted(g, v))))
                    pushed = True
                    break
                if v in on_stack:
                    low[u] = min(low[u], index[v])
            if pushed:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[u])
            if low[u] == index[u]:
                while True:
                    w = tarjan_stack.pop()
                    on_stack.discard(w)
                    comp[w] = ncomp
                    if w == u:
                        break
                ncomp += 1
    return comp


def _components(g):
    adj = {v: [] for v in g.vertices}
    for e in g.edges.values():
        if e.status != EdgeStatus.BLOCKED:
            adj[e.from_].append(e.to)
            adj[e.to].append(e.from_)
    seen, comps = set(), []
    for start in sorted(g.vertices):
        if start in seen:
            continue
        seen.add(start)
        stack, comp = [start], []
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        comps.append(sorted(comp))
    return comps


def _dead_ends(g):
    """Dead ends per the spec: a non-mandatory vertex from which the Finish cannot be reached without reversing.
    Search state = (road used to arrive, direction). From an arrival you may leave by any traversable road EXCEPT the
    one you arrived by. A vertex is a dead end if it can be arrived at, yet no arrival at it can still reach the Finish."""
    finishes = {vid for vid, v in g.vertices.items() if v.type == VertexType.FINISH}
    arcs = []                                        # (edge id, tail, head)
    for e in g.edges.values():
        if e.status == EdgeStatus.BLOCKED or e.from_ == e.to:
            continue
        arcs.append((e.id, e.from_, e.to))
        if not e.directed:
            arcs.append((e.id, e.to, e.from_))
    into = {}                                        # head vertex -> arcs arriving there
    for arc in arcs:
        into.setdefault(arc[2], []).append(arc)
    good = {arc for arc in arcs if arc[2] in finishes}           # arriving at the Finish counts as reaching it
    queue = list(good)
    while queue:
        eid, tail, _ = queue.pop()
        for prev in into.get(tail, []):
            if prev[0] != eid and prev not in good:             # you may not turn straight back over the same road
                good.add(prev)
                queue.append(prev)
    out = []
    for vid, v in g.vertices.items():
        if v.type in (VertexType.START, VertexType.FINISH) or v.checkpointOrder is not None:
            continue
        arrivals = into.get(vid, [])
        if arrivals and not any(a in good for a in arrivals):
            out.append(vid)
    return sorted(out)


def _can_reach(g, target):
    """Vertices from which target can be reached over traversable roads (reverse search)."""
    rev = {}
    for e in g.edges.values():
        if e.status == EdgeStatus.BLOCKED:
            continue
        rev.setdefault(e.to, []).append(e.from_)
        if not e.directed:
            rev.setdefault(e.from_, []).append(e.to)
    seen, stack = {target}, [target]
    while stack:
        u = stack.pop()
        for v in rev.get(u, []):
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def alternative_routes(g, source, target, max_routes=20, max_len=40, max_expansions=200000):
    """Simple (no repeated vertex) routes from source to target, found by bounded backtracking.
    LIMITS (state them in the report): at most max_routes routes; each route has at most max_len roads;
    at most max_expansions neighbour checks. Routes are found in DFS order, so the list is NOT guaranteed to
    contain the cheapest route (use dijkstra/astar for that). Parallel roads give one vertex list.
    Only vertices that can still reach the target are explored. Result is sorted by (length, ids)."""
    if source not in g.vertices or target not in g.vertices:
        return []
    if source == target:
        return [[source]]
    can_reach = _can_reach(g, target)
    if source not in can_reach:
        return []
    routes = []
    path, on_path = [source], {source}
    stack = [iter(sorted({v for v, _ in _neighbors_sorted(g, source)}))]
    budget = max_expansions
    while stack and len(routes) < max_routes and budget > 0:
        it = stack[-1]
        advanced = False
        for nb in it:
            budget -= 1
            if budget <= 0:
                break
            if nb in on_path or nb not in can_reach:
                continue
            if nb == target:
                if len(path) <= max_len:                    # edges used = len(path)
                    routes.append(path + [nb])
                    if len(routes) >= max_routes:
                        break
                continue
            if len(path) + 1 > max_len:                     # still needs at least one more road
                continue
            path.append(nb)
            on_path.add(nb)
            stack.append(iter(sorted({v for v, _ in _neighbors_sorted(g, nb)})))
            advanced = True
            break
        if not advanced:
            stack.pop()
            on_path.discard(path.pop())
    routes.sort(key=lambda r: (len(r), r))
    return routes


def path_cost(g, vertices, preset=K.DEFAULT_PRESET):
    """Cost of a vertex-list route, taking the cheapest traversable road at each hop. inf if a hop is impossible."""
    total = 0.0
    for a, b in zip(vertices, vertices[1:]):
        costs = [g.edge_cost(e, preset) for e, v in g.neighbors(a) if v == b]
        if not costs:
            return float("inf")
        total += min(costs)
    return total
