"""PERSON A. Pure Python (no pygame). Runs the REAL algorithm once with a trace callback, then lets the
Algorithm Lab replay the recorded events one step at a time. Gameplay and Lab therefore use the same code."""
from ..routing.api import bfs_path, dijkstra, astar, dfs_order
from .route_view import default_endpoints

ALGORITHMS = ("bfs", "dfs", "dijkstra", "astar")


class TraceRunner:
    def __init__(self, graph, algo, source=None, target=None, preset="Balanced"):
        if algo not in ALGORITHMS:
            raise ValueError("unknown algorithm %r" % (algo,))
        self.g = graph
        self.algo = algo
        self.preset = preset
        d_source, d_target = default_endpoints(graph)
        self.source = d_source if source is None else source
        self.target = d_target if target is None else target
        self.events = []
        self.result = None          # PathResult (bfs/dijkstra/astar) or the DFS order list
        self._run()
        self.reset_playback()

    def _run(self):
        cb = self.events.append
        if self.algo == "bfs":
            self.result = bfs_path(self.g, self.source, self.target, trace=cb)
        elif self.algo == "dfs":
            self.result = dfs_order(self.g, self.source, trace=cb)[0]
        elif self.algo == "dijkstra":
            self.result = dijkstra(self.g, self.source, self.target, self.preset, trace=cb)
        else:
            self.result = astar(self.g, self.source, self.target, self.preset, trace=cb)

    # ---------- playback ----------
    def reset_playback(self):
        self.pos = 0
        self.expanded_order = []        # vertices in the order they were expanded
        self.expanded = set()
        self.relaxed_edges = []         # edge ids examined so far
        self.improved_edges = set()     # edges whose examination improved or discovered something
        self.current = None             # vertex expanded by the latest step
        self.last_relax = None          # (u, v, edge id, improved) of the latest examined road
        self.cost_so_far = None

    @property
    def finished(self):
        return self.pos >= len(self.events)

    def step(self):
        """Apply the next recorded event. Returns False when there is nothing left."""
        if self.finished:
            return False
        ev = self.events[self.pos]
        self.pos += 1
        if ev[0] == "expand":
            self.current = ev[1]
            self.expanded.add(ev[1])
            self.expanded_order.append(ev[1])
            if len(ev) > 2:
                self.cost_so_far = ev[2]
        else:
            _, u, v, eid, improved = ev
            self.last_relax = (u, v, eid, improved)
            self.relaxed_edges.append(eid)
            if improved:
                self.improved_edges.add(eid)
        return True

    def step_to_end(self):
        while self.step():
            pass

    def rewind(self):
        self.reset_playback()

    # ---------- results ----------
    def path_vertices(self):
        """Final route (only for the path algorithms, and only once playback has finished)."""
        if self.algo == "dfs" or not self.finished or not getattr(self.result, "found", False):
            return []
        return list(self.result.vertices)

    def counters(self):
        total_expand = sum(1 for e in self.events if e[0] == "expand")
        total_relax = len(self.events) - total_expand
        out = {"step": self.pos, "steps": len(self.events), "expanded": len(self.expanded_order),
               "relaxed": len(self.relaxed_edges), "expanded_total": total_expand, "relaxed_total": total_relax}
        if self.cost_so_far is not None:
            out["cost_so_far"] = round(self.cost_so_far, 4)
        if self.finished and self.algo != "dfs":
            out["found"] = bool(self.result.found)
            if self.result.found:
                out["path_edges"] = len(self.result.edges)
                out["path_cost"] = round(self.result.cost, 4)
        return out
