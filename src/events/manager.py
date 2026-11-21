"""EventManager: schedules events, applies them to the Graph (only through Graph's update methods), expires them.
Effect rules: blocked if ANY blockage / shortcut closure is active; oil = strongest (Graph takes max); speed = strictest cap
(Graph takes min); a station is off if ANY off-effect is active, else on if any on-effect is active, else its base state.
Each effect keeps its own id, so expiry of one never removes another."""
from ..core import constants as K
from ..core.models import Event, EventType, Effect, EdgeStatus, VertexType
from .queue import EventQueue

_EDGE_TYPES = (EventType.ROAD_BLOCKAGE, EventType.SHORTCUT_TOGGLE, EventType.OIL_SPILL, EventType.SPEED_RESTRICTION)


class EventManager:
    def __init__(self, graph):
        self.g = graph
        self.queue = EventQueue()
        self.now = 0.0
        self.log = []                 # list[str], newest last (shown on the racing screen)
        self._next_id = 1
        self._seq = 0
        self._expiry_of = {}          # expiry event id -> origin event id
        self._applied = {}            # origin event id -> record of the live effect
        self._blocks = {}             # edge id -> set of origin ids holding it blocked
        self._prior = {}              # edge id -> status it had before WE blocked it (restored when the last block ends)
        self._sc_close = {}           # shortcut edge id -> origin id of its active closure
        self._off, self._on, self._base = {}, {}, {}

    # ---------- scheduling ----------
    def _new(self, etype, t, target, duration):
        e = Event(self._next_id, etype, t, K.EVENT_PRIORITY[etype.value], self._seq, target, duration)
        self._next_id += 1
        self._seq += 1
        return e

    def _validate(self, etype, t, target):
        if t < self.now:
            raise ValueError("trigger time %.2f is in the past (now %.2f)" % (t, self.now))
        g = self.g
        if etype in _EDGE_TYPES:
            if target not in g.edges:
                raise ValueError("edge %r does not exist" % (target,))
            if etype == EventType.SHORTCUT_TOGGLE and not g.edges[target].isShortcut:
                raise ValueError("edge %r is not a shortcut" % (target,))
        else:
            if target not in g.vertices:
                raise ValueError("vertex %r does not exist" % (target,))
            want = VertexType.FUEL_STATION if etype == EventType.STATION_AVAILABILITY else VertexType.NITRO_PICKUP
            if g.vertices[target].type != want:
                raise ValueError("vertex %r is not a %s" % (target, want.value))

    def schedule(self, etype, trigger_time, target, duration=None):
        """duration None = default from K.EVENT_DURATION (None there = until reversed); float('inf') = never expires."""
        etype = EventType(etype)
        self._validate(etype, trigger_time, target)
        if duration is None:
            duration = K.EVENT_DURATION[etype.value]
        if duration is not None and duration < 0:
            raise ValueError("duration must be >= 0")
        e = self._new(etype, trigger_time, target, duration)
        self.queue.push(e)
        return e.eventId

    def cancel(self, event_id):
        """Pending event: lazy-delete it. Already applied: undo its effect now (and cancel its expiry)."""
        if self.queue.cancel(event_id):
            return True
        return self._remove(event_id)

    def notify_collected(self, vid):
        """Race engine calls this when a booster pickup is taken: its temporary activation ends."""
        for origin in [o for o, r in self._applied.items() if r["kind"] == "on" and r["target"] == vid]:
            self._remove(origin)

    # ---------- running ----------
    def advance_to(self, t):
        """Apply ALL events with triggerTime <= t in heap order. Returns the Events that changed the graph."""
        applied = []
        while len(self.queue) > 0 and self.queue.peek().triggerTime <= t:
            e = self.queue.pop()
            self.now = max(self.now, e.triggerTime)
            if self._apply(e):
                applied.append(e)
        self.now = max(self.now, t)
        return applied

    def _expiry(self, origin, e):
        if e.duration is None or e.duration == float("inf"):
            return
        x = self._new(e.type, e.triggerTime + e.duration, e.targetEdgeOrVertex, None)
        self.queue.push(x)
        self._expiry_of[x.eventId] = origin
        self._applied[origin]["expiry"] = x.eventId

    def _say(self, e, what):
        self.log.append("t=%.1f %s %s target=%d" % (e.triggerTime, e.type.value, what, e.targetEdgeOrVertex))

    def _apply(self, e):
        if e.eventId in self._expiry_of:
            ok = self._remove(self._expiry_of.pop(e.eventId), expired=True)
            if ok:
                self._say(e, "expired")
            return ok
        g, t, tg, i = self.g, e.type, e.targetEdgeOrVertex, e.eventId
        if t == EventType.ROAD_BLOCKAGE:
            self._applied[i] = {"kind": "block", "target": tg}
            self._blocks.setdefault(tg, set()).add(i)
            self._sync_edge(tg)
        elif t == EventType.SHORTCUT_TOGGLE:
            if tg in self._sc_close:                      # reverses an earlier closure
                self._remove(self._sc_close[tg])
                self._say(e, "reopened")
                return True
            self._applied[i] = {"kind": "block", "target": tg, "sc": True}
            self._blocks.setdefault(tg, set()).add(i)
            self._sc_close[tg] = i
            self._sync_edge(tg)
        elif t == EventType.OIL_SPILL:
            self._applied[i] = {"kind": "effect", "target": tg}
            g.add_effect(tg, Effect(i, "oil", K.OIL_DIFFICULTY_ADD))
        elif t == EventType.SPEED_RESTRICTION:
            self._applied[i] = {"kind": "effect", "target": tg}
            g.add_effect(tg, Effect(i, "speed_cap", K.SPEED_RESTRICTION_FACTOR))
        else:                                              # station availability / nitro booster
            self._base.setdefault(tg, g.vertices[tg].active)
            to_off = (t == EventType.STATION_AVAILABILITY and g.vertices[tg].active)
            self._applied[i] = {"kind": "off" if to_off else "on", "target": tg}
            (self._off if to_off else self._on).setdefault(tg, set()).add(i)
            self._sync_vertex(tg)
        self._expiry(i, e)
        self._say(e, "applied")
        return True

    def _remove(self, origin, expired=False):
        r = self._applied.pop(origin, None)
        if r is None:
            return False
        tg, k = r["target"], r["kind"]
        if "expiry" in r and not expired:
            self.queue.cancel(r["expiry"])
        if k == "block":
            self._blocks[tg].discard(origin)
            if r.get("sc"):
                self._sc_close.pop(tg, None)
            self._sync_edge(tg)
        elif k == "effect":
            self.g.remove_effect(tg, origin)
        else:
            (self._off if k == "off" else self._on)[tg].discard(origin)
            self._sync_vertex(tg)
        return True

    def _sync_edge(self, eid):
        edge, held = self.g.edges[eid], bool(self._blocks.get(eid))
        if held and edge.status != EdgeStatus.BLOCKED:
            self._prior[eid] = edge.status               # remembered once; overlapping blockages share it
            self.g.block_edge(eid)
        elif not held and eid in self._prior:
            prior = self._prior.pop(eid)
            if edge.status == EdgeStatus.BLOCKED:
                self.g.set_status(eid, prior)            # RESTRICTED stays RESTRICTED (unblock_edge would force OPEN)

    def _sync_vertex(self, vid):
        want = self._base[vid]
        if self._off.get(vid):
            want = False
        elif self._on.get(vid):
            want = True
        if self.g.vertices[vid].active != want:
            self.g.set_station_active(vid, want)
