"""Track generator and validator.
Pipeline: random vertices -> all candidate roads -> MST -> extra roads (cycles, shortcuts, one-way) -> backtracking
placement (finish, checkpoints 1..N, fuel stations, nitro pickups) -> backtracking obstacle placement -> validate_track.
Pruning rules (each safe because it only removes assignments the validator would reject anyway):
  used vertex | degree < 2 (leaves stay dead ends) | finish < 3 hops from start | checkpoint < 2 hops from the previous one |
  fuel stations < sgap hops apart | nitro pickups < 2 hops apart | obstacle on a shortcut or bridge edge |
  obstacle touching start/finish or another obstacle."""
import heapq, math, random
from ..core import constants as K
from ..core.graph import Graph
from ..core.models import Vertex, Edge, VertexType, EdgeStatus
from ..planning.refuel import refuel_plan
from ..routing.bfs import bfs_path
from ..routing.dijkstra import dijkstra
from ..routing.planner import plan_route, route_vertices, route_edges
from .mst import mst_backbone

W, H = 1040, 680
DEFAULTS = dict(n=40, fuel=8, pickups=3, obstacles=3, shortcuts=2, extra=8, oneway=1,
                radius=0, maxlen=350, maxdeg=4, sgap=3, maxnodes=300000, min_gap=60)
TIME_PER_DIST, FUEL_PER_DIST = 0.035, 0.05
_NAMES = {VertexType.START: "Start", VertexType.FINISH: "Finish"}


class _Fail(Exception):
    pass


def _hops(n, edges):
    adj = [[] for _ in range(n)]
    for e in edges:
        adj[e["u"]].append(e["v"])
        adj[e["v"]].append(e["u"])
    hop = []
    for s in range(n):
        d = [99] * n
        d[s] = 0
        q = [s]
        for x in q:
            for y in adj[x]:
                if d[y] == 99:
                    d[y] = d[x] + 1
                    q.append(y)
        hop.append(d)
    return hop


def _connected(n, edges, skip=-1):
    adj = [[] for _ in range(n)]
    for i, e in enumerate(edges):
        if i != skip:
            adj[e["u"]].append(e["v"])
            adj[e["v"]].append(e["u"])
    seen, q = {0}, [0]
    for x in q:
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                q.append(y)
    return len(seen) == n


def _attempt(rng, p, n_cp, trace=None):
    n = p["n"]
    pts = []
    for _ in range(n):
        for _try in range(200):
            c = (rng.randrange(W), rng.randrange(H))
            if all((c[0] - q[0]) ** 2 + (c[1] - q[1]) ** 2 >= p["min_gap"] ** 2 for q in pts):
                break
        pts.append(c)
    cand = []
    for i in range(n):
        for j in range(i + 1, n):
            d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            ln = int(math.ceil(d - 1e-9))
            if not p["radius"] or ln <= p["radius"]:
                cand.append((i, j, ln))
    try:
        tree = mst_backbone(pts, cand, "kruskal")
    except ValueError:
        raise _Fail("candidate graph disconnected (spanning forest, not a spanning tree)")
    edges = [dict(u=u, v=v, ln=ln, sc=False, dr=False, obs=False) for u, v, ln in tree]
    in_tree = {(u, v) for u, v, _ in tree}
    deg = [0] * n
    for e in edges:
        deg[e["u"]] += 1
        deg[e["v"]] += 1
    hop = _hops(n, edges)
    extra = [(-hop[u][v], ln, u, v) for u, v, ln in cand if (u, v) not in in_tree and hop[u][v] >= 3 and ln <= p["maxlen"]]
    extra.sort()
    added = 0
    for _, ln, u, v in extra:
        if added >= p["extra"]:
            break
        if deg[u] >= p["maxdeg"] or deg[v] >= p["maxdeg"]:
            continue
        sc = added < p["shortcuts"]
        edges.append(dict(u=u, v=v, ln=ln, sc=sc, dr=(not sc and added < p["shortcuts"] + p["oneway"]), obs=False))
        deg[u] += 1
        deg[v] += 1
        added += 1
    hop = _hops(n, edges)
    off = rng.randrange(n)
    start = next((v for v in ((i + off) % n for i in range(n)) if deg[v] >= 2), None)
    if start is None:
        raise _Fail("placement failed: no vertex with degree >= 2")
    typ = [None] * n
    typ[start] = VertexType.START
    order = {}
    slots = [("fin", 0)] + [("cp", i) for i in range(1, n_cp + 1)] + [("fuel", i) for i in range(p["fuel"])] \
        + [("nitro", i) for i in range(p["pickups"])]
    sv = [None] * len(slots)
    cpv = {}
    nodes = [0]
    soff = rng.randrange(n)

    def ok(s, v):
        kind, idx = slots[s]
        if typ[v] is not None:
            return False
        if deg[v] < 2:
            return False
        if kind == "fin":
            return hop[start][v] >= 3
        if kind == "cp":
            return hop[start if idx == 1 else cpv[idx - 1]][v] >= 2
        if kind == "fuel":
            return all(hop[sv[q]][v] >= p["sgap"] for q in range(s) if slots[q][0] == "fuel")
        return all(hop[sv[q]][v] >= 2 for q in range(s) if slots[q][0] == "nitro")

    def place(s):
        if s == len(slots):
            return True
        kind, idx = slots[s]
        for i in range(n):
            v = (i + soff) % n
            if nodes[0] >= p["maxnodes"]:
                return False
            nodes[0] += 1
            if not ok(s, v):
                continue
            typ[v] = {"fin": VertexType.FINISH, "cp": VertexType.CHECKPOINT, "fuel": VertexType.FUEL_STATION,
                      "nitro": VertexType.NITRO_PICKUP}[kind]
            sv[s] = v
            if kind == "cp":
                cpv[idx] = v
                order[v] = idx
            if trace is not None and len(trace) < 400:
                trace.append(("place", kind, idx, v, pts[v]))
            if place(s + 1):
                return True
            if trace is not None and len(trace) < 400:
                trace.append(("undo", kind, idx, v, pts[v]))
            typ[v] = None
            order.pop(v, None)
        return False
    if not place(0):
        raise _Fail("placement failed (no feasible slot assignment within %d nodes)" % p["maxnodes"])
    finish = sv[0]
    for v in range(n):
        if typ[v] is None:
            typ[v] = VertexType.DEAD_END if deg[v] == 1 else VertexType.INTERSECTION
    bridge = [not _connected(n, edges, i) for i in range(len(edges))]
    used = set()
    onodes = [0]

    def place_obs(k, frm):
        if k == p["obstacles"]:
            return True
        for i in range(frm, len(edges)):
            onodes[0] += 1
            if onodes[0] > p["maxnodes"]:
                return False
            e = edges[i]
            if e["sc"] or bridge[i] or {e["u"], e["v"]} & {start, finish} or e["u"] in used or e["v"] in used:
                continue
            e["obs"] = True
            used.update((e["u"], e["v"]))
            if place_obs(k + 1, i + 1):
                return True
            e["obs"] = False
            used.difference_update((e["u"], e["v"]))
        return False
    if not place_obs(0, 0):
        raise _Fail("obstacle placement failed")
    ids = {start: 0}
    for v in range(n):
        if v != start:
            ids[v] = len(ids)
    g = Graph("Generated")
    for v in sorted(range(n), key=lambda x: ids[x]):
        nm = _NAMES.get(typ[v]) or ("CP%d" % order[v] if v in order else "%s%d" % (typ[v].value, ids[v]))
        g.add_vertex(Vertex(ids[v], pts[v][0], pts[v][1], typ[v], order.get(v)))
    for i, e in enumerate(edges):
        diff = 5 if e["obs"] else (rng.randint(3, 5) if e["sc"] else rng.randint(1, 5))
        g.add_edge(Edge(i, ids[e["u"]], ids[e["v"]], float(e["ln"]), round(e["ln"] * TIME_PER_DIST, 2),
                        round(e["ln"] * FUEL_PER_DIST, 2), diff, EdgeStatus.OPEN, e["sc"], e["dr"]))
    g.finalize()
    return g


def generate_track(seed, n_checkpoints=10, max_attempts=50, params=None, trace=None):
    """Returns (Graph or None, log). Every rejected candidate is logged with its reason. params overrides DEFAULTS
    (n, fuel, pickups, obstacles, shortcuts, extra, oneway, radius, maxlen, maxdeg, sgap, maxnodes)."""
    p = dict(DEFAULTS)
    p.update(params or {})
    log = []
    for k in range(max_attempts):
        rng = random.Random(seed + k)
        try:
            g = _attempt(rng, p, n_checkpoints, trace if k == 0 else None)
        except _Fail as ex:
            log.append("attempt %d (seed %d): REJECTED - %s" % (k, seed + k, ex))
            continue
        problems = validate_track(g)
        if problems:
            log.append("attempt %d (seed %d): REJECTED - %s" % (k, seed + k, "; ".join(problems)))
            continue
        log.append("attempt %d (seed %d): accepted" % (k, seed + k))
        return g, log
    log.append("no valid track in %d attempts" % max_attempts)
    return None, log


def _undirected_connected(g):
    adj = {v: [] for v in g.vertices}
    for e in g.edges.values():
        adj[e.from_].append(e.to)
        adj[e.to].append(e.from_)
    first = next(iter(adj))
    seen, q = {first}, [first]
    for x in q:
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                q.append(y)
    return len(seen) == len(adj)


def _fuel_route(g, a, b):
    """Min-fuel path a -> b over traversable roads. Returns (vertices, edge ids) or None."""
    dist, par, h = {a: 0.0}, {}, [(0.0, a)]
    while h:
        d, u = heapq.heappop(h)
        if d > dist[u]:
            continue
        if u == b:
            break
        for e, v in g.neighbors(u):
            nd = d + g.effective_fuel(e)
            if nd < dist.get(v, float("inf")):
                dist[v], par[v] = nd, (u, e.id)
                heapq.heappush(h, (nd, v))
    if b not in dist:
        return None
    vs, es, x = [b], [], b
    while x != a:
        x, eid = par[x]
        es.append(eid)
        vs.append(x)
    return vs[::-1], es[::-1]


def validate_track(g):
    """Returns a list of problems (empty = valid)."""
    out = []
    starts = [v for v in g.vertices.values() if v.type == VertexType.START]
    fins = [v for v in g.vertices.values() if v.type == VertexType.FINISH]
    if len(starts) != 1 or len(fins) != 1:
        return ["need exactly one Start and one Finish"]
    cps = g.checkpoints_in_order()
    orders = sorted(g.vertices[c].checkpointOrder for c in cps)
    if len(cps) < 10 or orders != list(range(1, len(cps) + 1)):
        out.append("fewer than 10 checkpoints or checkpoint orders are not 1..N")
    if sum(1 for e in g.edges.values() if e.isShortcut) < 2:
        out.append("fewer than 2 shortcuts")
    if g.validate_geometry():
        out.append("edge shorter than straight line (breaks A* admissibility)")
    if not _undirected_connected(g):
        return out + ["graph is not connected"]
    if len(g.edges) < len(g.vertices):
        out.append("no cycle")
    if not any(v.type == VertexType.DEAD_END for v in g.vertices.values()):
        out.append("no dead end")
    s, f = starts[0].id, fins[0].id
    chain = [s] + cps + [f, s]
    if not all(bfs_path(g, chain[i], chain[i + 1]).found for i in range(len(chain) - 1)):
        return out + ["ordered checkpoints / lap return unreachable in the directed graph"]
    main = bfs_path(g, s, f)
    alt = False
    for eid in main.edges:                       # an alternative route exists if some main-route road can be avoided
        old = g.edges[eid].status
        g.block_edge(eid)
        alt = bfs_path(g, s, f).found
        g.set_status(eid, old)
        if alt:
            break
    if not alt:
        out.append("no alternative start-finish route")
    route, stops_at = [s], []
    for a, b in zip([s] + cps, cps + [f]):
        r = _fuel_route(g, a, b)
        if r is None:
            return out + ["no feasible fuel plan (leg unreachable)"]
        vs, es = r
        route += vs[1:]
        stops_at += es
    idx = [0] + [i for i in range(1, len(route) - 1)
                 if g.vertices[route[i]].type == VertexType.FUEL_STATION and g.vertices[route[i]].active] + [len(route) - 1]
    need = []
    for a, b in zip(idx, idx[1:]):
        need.append(sum(g.effective_fuel(g.edges[e]) for e in stops_at[a:b]))
    if not refuel_plan(need, [False] + [True] * (len(need) - 1), K.MAX_FUEL, K.MAX_FUEL).feasible:
        out.append("no feasible fuel plan")
    return out


def export_extras(g):
    """Extra JSON keys for save_track: lap_boundary, main_route (Opponent 1) and fixed_detour for every route road."""
    s, f = g.start_vertex(), g.finish_vertex()
    plan = plan_route(g, s, g.checkpoints_in_order(), f)
    main = route_vertices(plan)
    detour = {}
    for eid in dict.fromkeys(route_edges(plan)):
        e = g.edges[eid]
        old = e.status
        g.block_edge(eid)
        r = dijkstra(g, e.from_, e.to)
        g.set_status(eid, old)
        if r.found:
            detour[str(eid)] = r.vertices
    return {"lap_boundary": f, "main_route": main, "fixed_detour": detour}
