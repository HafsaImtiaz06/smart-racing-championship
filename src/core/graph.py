"""FROZEN graph API (adjacency lists). Everyone calls the graph ONLY through these methods.
Dynamic updates never rebuild the graph. `version` increases on every change, so planners know when to replan."""
from typing import Dict, List, Tuple
from .models import Vertex, Edge, Effect, EdgeStatus, VertexType
from . import constants as K


class Graph:
    def __init__(self, name: str = ""):
        self.name = name
        self.vertices: Dict[int, Vertex] = {}
        self.edges: Dict[int, Edge] = {}
        self._adj: Dict[int, List[Tuple[int, int]]] = {}   # vertex id -> [(edge id, neighbour id)]
        self._effects: Dict[int, Dict[int, Effect]] = {}   # edge id -> {effect id: Effect}
        self.d_ref = self.t_ref = self.f_ref = 1.0          # normalization references (set by finalize)
        self.version = 0
        self._ratio_cache: Dict[str, float] = {}

    # ---------- building ----------
    def add_vertex(self, v: Vertex):
        self.vertices[v.id] = v
        self._adj.setdefault(v.id, [])

    def add_edge(self, e: Edge):
        self.edges[e.id] = e
        self._adj.setdefault(e.from_, []).append((e.id, e.to))
        if not e.directed:
            self._adj.setdefault(e.to, []).append((e.id, e.from_))

    def finalize(self):
        """Compute normalization references: D_ref=max distance, T_ref=max baseTime, F_ref=max base fuel (x worst multiplier)."""
        es = list(self.edges.values())
        self.d_ref = max([e.distance for e in es] + [1e-9]) or 1.0
        self.t_ref = max([e.baseTime for e in es] + [1e-9]) or 1.0
        self.f_ref = max([e.fuelCost * K.difficulty_multiplier(e.difficulty) for e in es] + [1e-9]) or 1.0
        self._ratio_cache.clear()
        self.version += 1

    # ---------- queries ----------
    def neighbors(self, vid: int) -> List[Tuple[Edge, int]]:
        """Traversable (non-Blocked) out-edges of vid as (edge, neighbour_id). Blocked edges are excluded (spec 3.1)."""
        return [(self.edges[eid], nb) for eid, nb in self._adj.get(vid, [])
                if self.edges[eid].status != EdgeStatus.BLOCKED]

    def all_neighbors(self, vid: int) -> List[Tuple[Edge, int]]:
        """Including Blocked edges (for drawing / generation / validation)."""
        return [(self.edges[eid], nb) for eid, nb in self._adj.get(vid, [])]

    def checkpoints_in_order(self) -> List[int]:
        cps = [v for v in self.vertices.values() if v.checkpointOrder is not None]
        return [v.id for v in sorted(cps, key=lambda v: v.checkpointOrder)]

    def start_vertex(self) -> int:
        return next(v.id for v in self.vertices.values() if v.type == VertexType.START)

    def finish_vertex(self) -> int:
        return next(v.id for v in self.vertices.values() if v.type == VertexType.FINISH)

    def is_service_available(self, vid: int) -> bool:
        return self.vertices[vid].active

    # ---------- dynamic updates ----------
    def _changed(self):
        self.version += 1

    def block_edge(self, eid: int):
        self.edges[eid].status = EdgeStatus.BLOCKED; self._changed()

    def unblock_edge(self, eid: int):
        self.edges[eid].status = EdgeStatus.OPEN; self._changed()

    def set_status(self, eid: int, status: EdgeStatus):
        self.edges[eid].status = status; self._changed()

    def set_station_active(self, vid: int, active: bool):
        self.vertices[vid].active = active; self._changed()

    def add_effect(self, eid: int, effect: Effect):
        """Overlapping effects are stored independently; removing one never removes another."""
        self._effects.setdefault(eid, {})[effect.effect_id] = effect; self._changed()

    def remove_effect(self, eid: int, effect_id: int):
        self._effects.get(eid, {}).pop(effect_id, None); self._changed()

    def effects_on(self, eid: int) -> List[Effect]:
        return list(self._effects.get(eid, {}).values())

    # ---------- effective edge attributes (documented order: strictest active effect wins) ----------
    def effective_difficulty(self, e: Edge) -> int:
        add = max([f.value for f in self.effects_on(e.id) if f.kind == "oil"] + [0])
        return min(5, e.difficulty + int(add))

    def speed_factor(self, e: Edge) -> float:
        caps = [f.value for f in self.effects_on(e.id) if f.kind == "speed_cap"]
        if any(f.kind == "oil" for f in self.effects_on(e.id)):
            caps.append(K.OIL_SPEED_FACTOR)
        return min(caps + [1.0])                           # strictest cap

    def effective_time(self, e: Edge) -> float:
        t = e.baseTime / self.speed_factor(e)
        return t * K.RESTRICTED_TIME_FACTOR if e.status == EdgeStatus.RESTRICTED else t

    def effective_fuel(self, e: Edge, nitro: bool = False) -> float:
        f = e.fuelCost * K.difficulty_multiplier(self.effective_difficulty(e))
        return f * K.NITRO_FUEL_FACTOR if nitro else f

    def obstacle_penalty(self, e: Edge) -> float:
        o = 1.0 if any(f.kind == "oil" for f in self.effects_on(e.id)) else 0.0
        if e.status == EdgeStatus.RESTRICTED:
            o = max(o, K.RESTRICTED_OBSTACLE)
        return o

    # ---------- cost (spec 3.3) ----------
    def edge_cost(self, e: Edge, preset: str = K.DEFAULT_PRESET) -> float:
        """cost(e) = w_d*D + w_t*T + w_f*F + w_r*R + w_o*O, all terms normalized to ~[0,1+].
        THIS is the only cost function. Displayed cost == optimized cost."""
        wd, wt, wf, wr, wo = K.PRESETS[preset]
        D = e.distance / self.d_ref
        T = self.effective_time(e) / self.t_ref
        F = self.effective_fuel(e) / self.f_ref
        R = (self.effective_difficulty(e) - 1) / 4.0
        O = self.obstacle_penalty(e)
        return wd * D + wt * T + wf * F + wr * R + wo * O

    def heuristic_ratio(self, preset: str = K.DEFAULT_PRESET) -> float:
        """Lower bound of (edge cost / edge distance) over BASE edges (no effects, status Open).
        A* heuristic: h(v) = ratio * euclid(v, target). Admissible if every edge distance >= straight-line distance
        (checked by validate_geometry) because effects/restrictions only ever INCREASE cost."""
        if preset in self._ratio_cache:
            return self._ratio_cache[preset]
        wd, wt, wf, wr, wo = K.PRESETS[preset]
        best = None
        for e in self.edges.values():
            if e.distance <= 0:
                continue
            base = (wd * e.distance / self.d_ref + wt * e.baseTime / self.t_ref
                    + wf * e.fuelCost * K.difficulty_multiplier(e.difficulty) / self.f_ref
                    + wr * (e.difficulty - 1) / 4.0)
            r = base / e.distance
            best = r if best is None else min(best, r)
        self._ratio_cache[preset] = best or 0.0
        return self._ratio_cache[preset]

    def euclid(self, a: int, b: int) -> float:
        va, vb = self.vertices[a], self.vertices[b]
        return ((va.x - vb.x) ** 2 + (va.y - vb.y) ** 2) ** 0.5

    def validate_geometry(self) -> List[int]:
        """Edge ids whose distance is SHORTER than straight-line (would break A* admissibility). Should be []."""
        return [e.id for e in self.edges.values() if e.distance + 1e-9 < self.euclid(e.from_, e.to)]
