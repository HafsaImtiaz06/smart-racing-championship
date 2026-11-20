"""PERSON A. Pure Python (no pygame): everything the Route Planner screen needs to decide and display, so it can be
tested without a window. route_planner.py only draws this and forwards clicks and keys."""
import math
from dataclasses import dataclass, field
from ..core import constants as K
from ..core.models import EdgeStatus, VertexType
from ..routing.api import (bfs_path, dijkstra, astar, reachable_from, alternative_routes, path_cost,
                           plan_route, route_vertices)


def vertex_label(g, vid):
    v = g.vertices[vid]
    if v.checkpointOrder is not None:
        return "CP%d" % v.checkpointOrder
    return {VertexType.START: "Start", VertexType.FINISH: "Finish", VertexType.FUEL_STATION: "Fuel %d" % vid,
            VertexType.NITRO_PICKUP: "Nitro %d" % vid, VertexType.DEAD_END: "DeadEnd %d" % vid}.get(v.type, "#%d" % vid)


def default_endpoints(g):
    """Start and a mid-circuit checkpoint (so the first route shown is interesting); Finish if there are no checkpoints."""
    cps = g.checkpoints_in_order()
    target = cps[len(cps) // 2 - 1] if len(cps) >= 2 else g.finish_vertex()
    return g.start_vertex(), target


class Viewport:
    """Maps world coordinates to pixels inside rect = (x, y, w, h), keeping the aspect ratio."""
    def __init__(self, graph, rect, margin=28):
        x, y, w, h = tuple(rect)
        self.rect, self.g = (x, y, w, h), graph
        xs = [v.x for v in graph.vertices.values()]
        ys = [v.y for v in graph.vertices.values()]
        self.minx, self.miny = min(xs), min(ys)
        span_x, span_y = max(max(xs) - self.minx, 1e-9), max(max(ys) - self.miny, 1e-9)
        avail_w, avail_h = max(w - 2 * margin, 1), max(h - 2 * margin, 1)
        self.scale = min(avail_w / span_x, avail_h / span_y)
        self.ox = x + margin + (avail_w - span_x * self.scale) / 2
        self.oy = y + margin + (avail_h - span_y * self.scale) / 2

    def to_screen(self, wx, wy):
        return (int(round(self.ox + (wx - self.minx) * self.scale)), int(round(self.oy + (wy - self.miny) * self.scale)))

    def vertex_pos(self, vid):
        v = self.g.vertices[vid]
        return self.to_screen(v.x, v.y)

    def contains(self, px, py):
        x, y, w, h = self.rect
        return x <= px < x + w and y <= py < y + h

    def vertex_at(self, px, py, radius=12):
        """Id of the vertex nearest to the pixel, if within radius; else None."""
        best, best_d = None, radius
        for vid in sorted(self.g.vertices):
            sx, sy = self.vertex_pos(vid)
            d = math.hypot(px - sx, py - sy)
            if d <= best_d:
                best, best_d = vid, d
        return best

    def edge_at(self, px, py, tol=6):
        """Id of the road nearest to the pixel, if within tol pixels; else None."""
        best, best_d = None, tol
        for eid in sorted(self.g.edges):
            e = self.g.edges[eid]
            ax, ay = self.vertex_pos(e.from_)
            bx, by = self.vertex_pos(e.to)
            dx, dy = bx - ax, by - ay
            seg = dx * dx + dy * dy
            t = 0.0 if seg == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / seg))
            d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
            if d <= best_d:
                best, best_d = eid, d
        return best


@dataclass
class RouteRow:
    preset: str
    found: bool
    cost: float = 0.0
    distance: float = 0.0
    time: float = 0.0
    fuel: float = 0.0
    vertices: list = field(default_factory=list)


@dataclass
class PlannerResult:
    mode: str
    found: bool
    vertices: list
    cost: float
    distance: float
    time: float
    fuel: float
    expanded: int
    relaxed: int
    heap_ops: int
    rows: list
    alternatives: list              # [(vertex list, cost)] cheapest first (point mode only)
    reachable_cps: list
    unreachable_cps: list
    fewest_roads: object            # (number of roads, cost) or None
    stops: int = 0


class PlannerModel:
    """State of the Route Planner. Modes: 'point' (source -> target) and 'checkpoints' (source -> every remaining
    checkpoint in order -> Finish)."""
    ALGOS = ("astar", "dijkstra")

    def __init__(self, graph):
        self.g = graph
        self.source, self.target = default_endpoints(graph)
        self.preset = K.DEFAULT_PRESET
        self.algo = "astar"
        self.mode = "point"
        self.selected_alt = 0
        self.next_click = "source"
        self._cache, self._key = None, None

    # ---------- user actions ----------
    def click_vertex(self, vid):
        if self.next_click == "source":
            self.source, self.next_click = vid, "target"
        else:
            self.target, self.next_click = vid, "source"
        self.selected_alt = 0

    def reset_endpoints(self):
        self.source, self.target = default_endpoints(self.g)
        self.next_click, self.selected_alt = "source", 0

    def set_preset(self, name):
        if name in K.PRESETS:
            self.preset, self.selected_alt = name, 0

    def cycle_algo(self):
        self.algo = self.ALGOS[(self.ALGOS.index(self.algo) + 1) % len(self.ALGOS)]

    def toggle_mode(self):
        self.mode = "checkpoints" if self.mode == "point" else "point"
        self.selected_alt = 0

    def toggle_block(self, eid):
        """Block an open/restricted road, or reopen a blocked one. Returns True if it is blocked now."""
        if eid not in self.g.edges:
            return False
        if self.g.edges[eid].status == EdgeStatus.BLOCKED:
            self.g.unblock_edge(eid)
            return False
        self.g.block_edge(eid)
        self.selected_alt = 0
        return True

    def step_alternative(self, delta):
        n = len(self.result().alternatives)
        if n:
            self.selected_alt = (self.selected_alt + delta) % n

    def blocked_count(self):
        return sum(1 for e in self.g.edges.values() if e.status == EdgeStatus.BLOCKED)

    # ---------- computation ----------
    def _search(self, s, t, preset):
        return (astar if self.algo == "astar" else dijkstra)(self.g, s, t, preset)

    def _remaining_checkpoints(self):
        cps = self.g.checkpoints_in_order()
        order = self.g.vertices[self.source].checkpointOrder
        if order is None:
            return cps
        return [c for c in cps if self.g.vertices[c].checkpointOrder > order]

    def _plan(self, preset):
        return plan_route(self.g, self.source, self._remaining_checkpoints(), self.g.finish_vertex(), preset, self.algo)

    def result(self):
        key = (self.g.version, self.source, self.target, self.preset, self.algo, self.mode)
        if key != self._key:
            self._cache, self._key = self._compute(), key
            self.selected_alt = min(self.selected_alt, max(len(self._cache.alternatives) - 1, 0))
        return self._cache

    def _compute(self):
        g = self.g
        reach = reachable_from(g, self.source)
        cps = g.checkpoints_in_order()
        reachable = [g.vertices[c].checkpointOrder for c in cps if c in reach]
        unreachable = [g.vertices[c].checkpointOrder for c in cps if c not in reach]
        if self.mode == "checkpoints":
            stops = self._remaining_checkpoints()
            plan = self._plan(self.preset)
            rows = []
            for p in K.PRESETS:
                pl = self._plan(p)
                rows.append(RouteRow(p, pl.found, pl.cost, pl.distance, pl.time, pl.fuel,
                                     route_vertices(pl) if pl.found else []))
            return PlannerResult("checkpoints", plan.found, route_vertices(plan) if plan.found else [], plan.cost,
                                 plan.distance, plan.time, plan.fuel, sum(l.expanded for l in plan.legs),
                                 sum(l.relaxed for l in plan.legs), sum(l.heap_ops for l in plan.legs), rows, [],
                                 reachable, unreachable, None, len(stops))
        main = self._search(self.source, self.target, self.preset)
        rows = []
        for p in K.PRESETS:
            r = self._search(self.source, self.target, p)
            rows.append(RouteRow(p, r.found, r.cost, r.distance, r.time, r.fuel, list(r.vertices)))
        alts = []
        for route in alternative_routes(g, self.source, self.target, max_routes=30, max_len=40):
            alts.append((route, path_cost(g, route, self.preset)))
        alts.sort(key=lambda a: (a[1], len(a[0]), a[0]))
        fewest = None
        b = bfs_path(g, self.source, self.target)
        if b.found:
            fewest = (len(b.edges), path_cost(g, b.vertices, self.preset))
        return PlannerResult("point", main.found, list(main.vertices), main.cost, main.distance, main.time, main.fuel,
                             main.expanded, main.relaxed, main.heap_ops, rows, alts[:8], reachable, unreachable,
                             fewest)

    # ---------- text for the side panel (each line kept short) ----------
    def info_lines(self):
        r, g = self.result(), self.g
        algo = "A*" if self.algo == "astar" else "Dijkstra"
        out = []
        if r.mode == "point":
            out.append("Route: %s -> %s" % (vertex_label(g, self.source), vertex_label(g, self.target)))
        else:
            out.append("Checkpoint route: %s -> Finish" % vertex_label(g, self.source))
            out.append("%d checkpoint stops in order" % r.stops)
        out.append("%s | preset %s" % (algo, self.preset))
        if r.found:
            out.append("Cost %.2f  Dist %.0f  Time %.0fs  Fuel %.0f" % (r.cost, r.distance, r.time, r.fuel))
            out.append("Expanded %d  Relaxed %d  Heap ops %d" % (r.expanded, r.relaxed, r.heap_ops))
        else:
            out.append("NO ROUTE FOUND (roads blocked?)")
        if r.fewest_roads:
            out.append("Fewest roads: %d (cost %.2f)" % r.fewest_roads)
        if r.unreachable_cps:
            out.append("Unreachable: " + ", ".join("CP%d" % c for c in r.unreachable_cps))
        else:
            out.append("Checkpoints reachable: %d/%d" % (len(r.reachable_cps), len(r.reachable_cps) + len(r.unreachable_cps)))
        out.append("Blocked roads: %d" % self.blocked_count())
        out.append("--- All presets (cost dist time fuel) ---")
        best_route = next((row.vertices for row in r.rows if row.preset == self.preset), [])
        for row in r.rows:
            if row.found:
                tag = "same" if row.vertices == best_route else "differs"
                out.append("%-8s %5.2f %5.0f %4.0fs %4.0f %s" % (row.preset, row.cost, row.distance, row.time,
                                                                    row.fuel, tag))
            else:
                out.append("%-8s no route" % row.preset)
        if r.alternatives:
            best = r.alternatives[0][1]
            out.append("--- Alternatives (N/P to browse) ---")
            route, cost = r.alternatives[self.selected_alt]
            pct = 0.0 if best <= 0 else (cost - best) / best * 100.0
            out.append("Alt %d/%d  cost %.2f (+%.0f%%)" % (self.selected_alt + 1, len(r.alternatives), cost, pct))
            out.append("Selected route uses %d roads" % (len(route) - 1))
        return out
