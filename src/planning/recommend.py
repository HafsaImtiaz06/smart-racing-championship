"""Glue: which optional nitro pickups are worth a detour? Uses knapsack_dp (same function the Lab shows)."""
import heapq, math
from ..core import constants as K
from ..core.models import VertexType
from ..routing.planner import route_vertices
from .knapsack import knapsack_dp


def _fuel_from(g, src):
    """Min fuel from src to every vertex it can reach, following directed roads and skipping blocked ones."""
    dist, h = {src: 0.0}, [(0.0, src)]
    while h:
        d, u = heapq.heappop(h)
        if d > dist[u]:
            continue
        for e, v in g.neighbors(u):
            nd = d + g.effective_fuel(e)
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(h, (nd, v))
    return dist


def round_trips(g, rverts, targets):
    """For each target, the cheapest REAL round trip: leave the route at r, reach the target, come back to the SAME r.
    Both directions are searched on the directed graph, so one-way spurs and expensive returns are priced correctly.
    rverts: route vertices in route order (ties go to the earliest). Returns {target: (fuel, r)}; targets with no
    complete round trip are left out."""
    out = {r: _fuel_from(g, r) for r in rverts}
    res = {}
    for t in targets:
        back = _fuel_from(g, t)
        best = None
        for r in rverts:
            if t in out[r] and r in back:
                c = out[r][t] + back[r]
                if best is None or c < best[0] - 1e-12:
                    best = (c, r)
        if best is not None:
            res[t] = best
    return res


def recommend_pickups(g, route_plan, racer, preset=K.DEFAULT_PRESET):
    """Cost of a pickup = fuel of the cheapest real round trip (out and back to the same route vertex, directed edges
    respected; pickups with no complete round trip are never recommended). Scaled and rounded up.
    Budget = spare fuel (racer.fuel - route fuel), rounded down, so recommended detours always fit in the tank.
    Benefit = 10 + 90 * (share of the route still ahead of the pickup). At most MAX_NITRO - nitroCharges are returned
    (if the DP picks more, the lowest-benefit pick is dropped and the DP re-run)."""
    if not route_plan.found:
        return []
    slots = K.MAX_NITRO - racer.nitroCharges
    rv = route_vertices(route_plan)
    if slots <= 0 or not rv:
        return []
    first = {}
    for i, v in enumerate(rv):
        first.setdefault(v, i)
    pickups = [v.id for v in g.vertices.values() if v.type == VertexType.NITRO_PICKUP and v.active]
    trips = round_trips(g, list(first), pickups)
    ids, costs, benefits = [], [], []
    for vid in pickups:
        if vid not in trips:
            continue                                   # no way back to the route: never recommend
        fuel, src = trips[vid]
        ids.append(vid)
        costs.append(int(math.ceil(fuel * K.FUEL_SCALE - 1e-9)))
        benefits.append(10 + int(90 * (1 - first[src] / max(1, len(rv) - 1))))
    spare = racer.fuel - route_plan.fuel
    budget = int(math.floor(spare * K.FUEL_SCALE + 1e-9)) if spare > 0 else 0
    while True:
        res = knapsack_dp(costs, benefits, budget)
        if len(res.chosen_ids) <= slots:
            return [ids[i] for i in res.chosen_ids]
        worst = min(res.chosen_ids, key=lambda i: (benefits[i], -i))
        del ids[worst], costs[worst], benefits[worst]
