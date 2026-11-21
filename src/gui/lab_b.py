"""Person B Algorithm Lab panels: knapsack DP + greedy, refuelling DP, event heap, MST (Kruskal), backtracking placement.
Every panel calls the same functions the game uses (planning.api, events.api, generation.api). Panels never mutate the
graph they are given (the event panel works on a deep copy)."""
import copy
import pygame
from ..core import constants as K
from ..core.models import EventType as ET, VertexType
from ..planning.api import knapsack_dp, greedy_select, refuel_plan
from ..planning.recommend import round_trips
from ..routing.planner import plan_route, route_vertices, route_edges
from ..events.api import EventManager
from ..generation.api import mst_backbone, generate_track
from .base import LabPanel

BG, FG, DIM = (18, 22, 30), (225, 230, 240), (120, 130, 150)
GREEN, RED, YEL, BLUE, ORG = (80, 200, 120), (230, 90, 90), (240, 200, 70), (90, 150, 240), (240, 150, 60)
_fonts = {}


def font(size):
    if not pygame.font.get_init():
        pygame.font.init()
    if size not in _fonts:
        _fonts[size] = pygame.font.SysFont(None, size)
    return _fonts[size]


def text(surface, s, pos, color=FG, size=20):
    surface.blit(font(size).render(str(s), True, color), pos)


def _frame(surface, rect, title):
    pygame.draw.rect(surface, BG, rect)
    pygame.draw.rect(surface, DIM, rect, 1)
    text(surface, title, (rect[0] + 10, rect[1] + 8), YEL, 26)


def _mapper(rect, top=40, pad=14):
    x, y, w, h = rect
    sx, sy = (w - 2 * pad) / 1040.0, (h - top - pad) / 680.0
    s = min(sx, sy)
    return lambda px, py: (int(x + pad + px * s), int(y + top + py * s))


class _BPanel(LabPanel):
    finished = False

    def reset(self, graph):
        self.g = graph
        self.i = 0
        self.finished = False
        self._build()

    def rewind(self):
        self.reset(self.g)

    def step(self):
        if not self.finished:
            self._advance()

    def counters(self):
        return {}


class KnapsackPanel(_BPanel):
    title = "0/1 Knapsack DP vs Greedy (nitro pickups)"

    def _build(self):
        g = self.g
        pk = [v for v in g.vertices.values() if v.type == VertexType.NITRO_PICKUP]
        det = round_trips(g, [g.start_vertex()], [v.id for v in pk])
        self.names, costs, ben = [], [], []
        far = max([d[0] for d in det.values()] or [1.0]) or 1.0
        for v in pk[:9]:
            if v.id in det:
                self.names.append("N%d" % v.id)
                costs.append(max(1, int(det[v.id][0] * K.FUEL_SCALE)))
                ben.append(10 + int(90 * (1 - det[v.id][0] / far)))
        self.budget = max(1, min(600, sum(costs) // 2))
        if len(costs) < 4:                              # too few pickups to be interesting: show the spec example
            self.names, costs, ben, self.budget = ["A", "B", "C"], [6, 5, 5], [30, 24, 24], 10
        self.rows = []
        self.dp = knapsack_dp(costs, ben, self.budget, trace=self.rows)
        self.gr = greedy_select(costs, ben, self.budget)
        self.costs, self.ben = costs, ben

    def _advance(self):
        self.i += 1
        self.finished = self.i >= len(self.rows)

    def counters(self):
        return {"items": len(self.costs), "budget": self.budget, "rows shown": self.i, "dp states": self.dp.dp_states,
                "dp value": self.dp.best_value, "greedy value": self.gr.best_value}

    def draw(self, surface, rect):
        _frame(surface, rect, self.title)
        x, y, w, h = rect
        cols = min(self.budget + 1, 60)
        cw, ch = max(4, (w - 170) // cols), 22
        mx = max(1, self.dp.best_value)
        for r in range(len(self.names)):
            text(surface, "%s c=%d v=%d" % (self.names[r], self.costs[r], self.ben[r]), (x + 8, y + 50 + r * ch), FG, 18)
            for cidx in range(cols):
                b = cidx * self.budget // max(1, cols - 1)
                if r < self.i:
                    t = self.rows[r][b] / mx
                    col = (30 + int(60 * t), 60 + int(150 * t), 90 + int(100 * t))
                else:
                    col = (35, 40, 52)
                pygame.draw.rect(surface, col, (x + 160 + cidx * cw, y + 50 + r * ch, cw - 1, ch - 2))
        yy = y + 60 + len(self.names) * ch
        text(surface, "budget 0 .. %d (DP units, 1 unit = %.1f fuel)" % (self.budget, 1.0 / K.FUEL_SCALE), (x + 160, yy), DIM, 18)
        if self.finished:
            pick = lambda res: ", ".join(self.names[i] for i in res.chosen_ids) or "-"
            text(surface, "DP     value %d  picks %s" % (self.dp.best_value, pick(self.dp)), (x + 10, yy + 28), GREEN, 22)
            col = RED if self.gr.best_value < self.dp.best_value else GREEN
            text(surface, "Greedy value %d  picks %s" % (self.gr.best_value, pick(self.gr)), (x + 10, yy + 52), col, 22)
        else:
            text(surface, "press step: DP row %d / %d" % (self.i, len(self.rows)), (x + 10, yy + 28), DIM, 22)


class RefuelPanel(_BPanel):
    title = "Refuelling DP along the main route"

    def _build(self):
        g = self.g
        s, f = g.start_vertex(), g.finish_vertex()
        plan = plan_route(g, s, g.checkpoints_in_order(), f)
        vs, es = route_vertices(plan), route_edges(plan)
        idx = [0] + [i for i in range(1, len(vs) - 1) if g.vertices[vs[i]].type == VertexType.FUEL_STATION
                     and g.vertices[vs[i]].active] + [max(0, len(vs) - 1)]
        self.stops = [vs[i] for i in idx[:-1]]
        self.need = [sum(g.effective_fuel(g.edges[e]) for e in es[a:b]) for a, b in zip(idx, idx[1:])]
        self.plan = refuel_plan(self.need, [False] + [True] * (len(self.need) - 1), K.MAX_FUEL, K.MAX_FUEL)
        self.arrive, fuel = [], K.MAX_FUEL
        for j, nd in enumerate(self.need):
            self.arrive.append(fuel)
            fuel += self.plan.purchases[j] if self.plan.feasible else 0
            fuel -= nd

    def _advance(self):
        self.i += 1
        self.finished = self.i >= len(self.need)

    def counters(self):
        return {"stops": len(self.need), "feasible": self.plan.feasible, "extra stop time": round(self.plan.extra_time, 1),
                "dp states": self.plan.dp_states}

    def draw(self, surface, rect):
        _frame(surface, rect, self.title)
        x, y, w, h = rect
        n = max(1, len(self.need))
        bw = max(10, min(70, (w - 40) // n - 6))
        base = y + h - 40
        for j in range(min(self.i, len(self.need))):
            bx = x + 20 + j * (bw + 6)
            a = max(0, self.arrive[j])
            bh = int((h - 120) * a / K.MAX_FUEL)
            pygame.draw.rect(surface, BLUE, (bx, base - bh, bw, bh))
            if self.plan.feasible and self.plan.purchases[j] > 0:
                ph = int((h - 120) * self.plan.purchases[j] / K.MAX_FUEL)
                pygame.draw.rect(surface, GREEN, (bx, base - bh - ph, bw, ph))
            text(surface, "%.0f" % a, (bx, base + 4), FG, 16)
            text(surface, "v%d" % self.stops[j], (bx, base + 20), DIM, 16)
        s = "feasible, extra stop time %.1f s" % self.plan.extra_time if self.plan.feasible else "INFEASIBLE: no valid refuel plan"
        text(surface, "blue = fuel on arrival, green = fuel bought   |   " + s, (x + 10, y + 34), GREEN if self.plan.feasible else RED, 18)


class EventHeapPanel(_BPanel):
    title = "Event min-heap (time, priority, sequence)"

    def _build(self):
        g = copy.deepcopy(self.g)                       # events change the graph: never touch the shared one
        self.mgr = m = EventManager(g)
        es = list(g.edges)
        sc = [e.id for e in g.edges.values() if e.isShortcut]
        st = [v.id for v in g.vertices.values() if v.type == VertexType.FUEL_STATION]
        pk = [v.id for v in g.vertices.values() if v.type == VertexType.NITRO_PICKUP]
        m.schedule(ET.ROAD_BLOCKAGE, 5, es[0], 20)
        m.schedule(ET.OIL_SPILL, 5, es[1 % len(es)])
        m.schedule(ET.OIL_SPILL, 15, es[1 % len(es)])                        # overlaps the first spill
        m.schedule(ET.SPEED_RESTRICTION, 10, es[2 % len(es)])
        if sc:
            m.schedule(ET.SHORTCUT_TOGGLE, 12, sc[0], 15)
        if st:
            m.schedule(ET.STATION_AVAILABILITY, 12, st[0])
        if pk:
            m.schedule(ET.NITRO_BOOSTER, 20, pk[0])
        dead = m.schedule(ET.OIL_SPILL, 8, es[3 % len(es)])
        m.cancel(dead)                                                         # lazy deletion demo
        self.applied = 0

    def _advance(self):
        q = self.mgr.queue
        if len(q) > 0:
            self.applied += len(self.mgr.advance_to(q.peek().triggerTime))
        self.finished = len(q) == 0

    def counters(self):
        q = self.mgr.queue
        return {"pending": len(q), "applied": self.applied, "heap ops": q.heap_ops, "compares": q.compares,
                "lazy dropped": q.lazy_dropped, "time": self.mgr.now}

    def draw(self, surface, rect):
        _frame(surface, rect, self.title)
        x, y, w, h = rect
        text(surface, "heap array (key = time, priority, seq):", (x + 10, y + 36), DIM, 18)
        for r, (key, e) in enumerate(self.mgr.queue._h[:14]):
            col = DIM if e.cancelled else FG
            text(surface, "%s %s tgt %d%s" % (tuple(round(k, 1) for k in key), e.type.value, e.targetEdgeOrVertex,
                                               " [cancelled]" if e.cancelled else ""), (x + 10, y + 58 + r * 20), col, 18)
        text(surface, "event log:", (x + w // 2, y + 36), DIM, 18)
        for r, line in enumerate(self.mgr.log[-14:]):
            text(surface, line, (x + w // 2, y + 58 + r * 20), GREEN, 18)


class MSTPanel(_BPanel):
    title = "Kruskal MST on the road graph"

    def _build(self):
        g = self.g
        ids = sorted(g.vertices)
        pos = {v: i for i, v in enumerate(ids)}
        self.pts = [(g.vertices[v].x, g.vertices[v].y) for v in ids]
        seen, cand = set(), []
        for e in g.edges.values():
            k = (min(pos[e.from_], pos[e.to]), max(pos[e.from_], pos[e.to]))
            if k not in seen:
                seen.add(k)
                cand.append((k[0], k[1], e.distance))
        self.trace, self.msg = [], ""
        try:
            self.tree = mst_backbone(self.pts, cand, "kruskal", trace=self.trace)
        except ValueError as ex:
            self.tree, self.msg = [], str(ex)
        self.cand, self.finished = cand, bool(self.msg)

    def _advance(self):
        self.i += 1
        self.finished = self.i >= len(self.trace)

    def counters(self):
        acc = sum(1 for _, a in self.trace[:self.i] if a)
        return {"edges examined": self.i, "accepted": acc, "rejected": self.i - acc,
                "tree weight": round(sum(ed[2] for ed, a in self.trace[:self.i] if a), 1)}

    def draw(self, surface, rect):
        _frame(surface, rect, self.title)
        to = _mapper(rect)
        for u, v, _ in self.cand:
            pygame.draw.line(surface, (45, 52, 68), to(*self.pts[u]), to(*self.pts[v]), 1)
        for k, (ed, ok) in enumerate(self.trace[:self.i]):
            col = GREEN if ok else (110, 60, 60)
            if k == self.i - 1:
                col = YEL
            pygame.draw.line(surface, col, to(*self.pts[ed[0]]), to(*self.pts[ed[1]]), 3 if ok else 1)
        for p in self.pts:
            pygame.draw.circle(surface, FG, to(*p), 3)
        if self.msg:
            text(surface, self.msg, (rect[0] + 10, rect[1] + 36), RED, 20)


class BacktrackPanel(_BPanel):
    title = "Backtracking placement (checkpoints, stations, pickups)"
    _col = {"fin": RED, "cp": YEL, "fuel": GREEN, "nitro": BLUE}

    def _build(self):
        self.trace = []
        generate_track(12, 10, 1, trace=self.trace)      # seed 12: 108 steps, 43 undos
        self.placed = {}
        self.places = self.undos = 0

    def _advance(self):
        if self.i < len(self.trace):
            op, kind, idx, v, xy = self.trace[self.i]
            if op == "place":
                self.placed[v] = (kind, idx, xy)
                self.places += 1
            else:
                self.placed.pop(v, None)
                self.undos += 1
            self.i += 1
        self.finished = self.i >= len(self.trace)

    def counters(self):
        return {"steps": "%d/%d" % (self.i, len(self.trace)), "placements": self.places, "undos (backtracks)": self.undos,
                "placed now": len(self.placed)}

    def draw(self, surface, rect):
        _frame(surface, rect, self.title)
        to = _mapper(rect)
        for kind, idx, xy in self.placed.values():
            p = to(*xy)
            pygame.draw.circle(surface, self._col[kind], p, 6)
            if kind == "cp":
                text(surface, idx, (p[0] + 7, p[1] - 7), FG, 16)
        text(surface, "red finish, yellow checkpoint #, green fuel, blue nitro", (rect[0] + 10, rect[1] + 28), DIM, 16)


PANELS = [KnapsackPanel, RefuelPanel, EventHeapPanel, MSTPanel, BacktrackPanel]


def all_panels():
    """For lab.py: instances of every Person B panel."""
    return [p() for p in PANELS]
