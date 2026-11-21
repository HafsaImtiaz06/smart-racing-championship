"""Refuelling DP. State: dp[j][f] = minimum extra stop time on arrival at stop j with f discrete fuel units."""
import math
from ..core.results import RefuelPlan
from ..core import constants as K

_INF = float("inf")


def refuel_plan(need, station_available, capacity, start_fuel):
    """need[j] = fuel from stop j to stop j+1 (last entry = to the destination). Fuel is scaled by K.FUEL_SCALE
    (tenths): needs are rounded UP, capacity and start fuel DOWN, so a feasible plan is always truly feasible.
    At an available stop buy a units, 0 <= a <= min(cap - f, STATION_MAX_BUY); any a > 0 costs STATION_STOP_TIME.
    Time O(m * C * B) with C = tank in DP units and B = max purchase in DP units."""
    if len(need) != len(station_available):
        raise ValueError("need and station_available must have the same length")
    s = K.FUEL_SCALE
    m = len(need)
    d = [int(math.ceil(x * s - 1e-9)) for x in need]
    cap = int(math.floor(capacity * s + 1e-9))
    f0 = min(cap, int(math.floor(start_fuel * s + 1e-9)))
    maxbuy = int(math.floor(K.STATION_MAX_BUY * s + 1e-9))
    stop_t = K.STATION_STOP_TIME
    if m == 0:
        return RefuelPlan(feasible=True, purchases=[], extra_time=0.0, dp_states=0)
    cur = [_INF] * (cap + 1)
    cur[f0] = 0.0
    layers, states = [], 0
    for j in range(m):
        nxt, pf, pa = [_INF] * (cap + 1), [-1] * (cap + 1), [0] * (cap + 1)
        dj, st = d[j], station_available[j]
        for f in range(cap + 1):
            c = cur[f]
            if c == _INF:
                continue
            if f >= dj and c < nxt[f - dj]:
                nxt[f - dj], pf[f - dj], pa[f - dj] = c, f, 0
            states += 1
            if st:
                c2 = c + stop_t
                for a in range(max(1, dj - f), min(cap - f, maxbuy) + 1):
                    states += 1
                    nf = f + a - dj
                    if c2 < nxt[nf]:
                        nxt[nf], pf[nf], pa[nf] = c2, f, a
        layers.append((pf, pa))
        cur = nxt
    best = min(range(cap + 1), key=lambda f: (cur[f], f))
    if cur[best] == _INF:
        return RefuelPlan(feasible=False, purchases=[], extra_time=0.0, dp_states=states)
    cost, f, buy = cur[best], best, [0.0] * m
    for j in range(m - 1, -1, -1):
        pf, pa = layers[j]
        buy[j] = pa[f] / s
        f = pf[f]
    return RefuelPlan(feasible=True, purchases=buy, extra_time=cost, dp_states=states)
