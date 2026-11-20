"""PERSON A. Algorithm Lab panels for BFS, DFS, Dijkstra and A*. Each panel replays a trace of the REAL algorithm
(see lab_trace.TraceRunner), so what the Lab shows is exactly what gameplay runs.
Contract for the Lab host (Person C's lab.py):   panel = PanelClass(); panel.reset(graph[, source, target, preset]);
panel.step() on each key press / timer tick; panel.draw(surface, (x, y, w, h)); panel.counters() -> dict;
panel.finished -> bool; panel.rewind() to replay."""
import pygame
from .base import LabPanel
from .graph_draw import (BG, GREEN, RED, BLUE, ORANGE, draw_graph, draw_route, draw_text)
from .lab_trace import TraceRunner
from .route_view import Viewport, vertex_label

LIGHT_BLUE = (140, 190, 235)


class _TracePanel(LabPanel):
    algo = None
    title = ""

    def reset(self, graph, source=None, target=None, preset="Balanced"):
        self.runner = TraceRunner(graph, self.algo, source, target, preset)

    def rewind(self):
        self.runner.rewind()

    def step(self):
        self.runner.step()

    @property
    def finished(self):
        return self.runner.finished

    def counters(self):
        return self.runner.counters()

    def draw(self, surface, rect):
        x, y, w, h = tuple(rect)
        r, g = self.runner, self.runner.g
        pygame.draw.rect(surface, BG, (x, y, w, h))
        vp = Viewport(g, (x, y, w, h - 70))
        edge_styles = {eid: (LIGHT_BLUE, 3) for eid in r.relaxed_edges}
        if r.last_relax:
            edge_styles[r.last_relax[2]] = (ORANGE, 5)
        fill = {v: BLUE for v in r.expanded}
        if r.current is not None:
            fill[r.current] = RED
        draw_graph(surface, g, vp, edge_styles, fill, {r.source: GREEN, r.target: (20, 20, 20)} if r.algo != "dfs"
                   else {r.source: GREEN}, labels=True)
        if r.finished and r.path_vertices():
            draw_route(surface, vp, r.path_vertices(), GREEN, 6)
        c = r.counters()
        yy = y + h - 66
        yy += draw_text(surface, "%s  (%s -> %s)" % (self.title, vertex_label(g, r.source),
                                                     "all" if r.algo == "dfs" else vertex_label(g, r.target)),
                        (x + 8, yy), 24) + 2
        line = "step %d/%d   expanded %d   examined roads %d" % (c["step"], c["steps"], c["expanded"], c["relaxed"])
        if "path_cost" in c:
            line += "   path cost %.3f (%d roads)" % (c["path_cost"], c["path_edges"])
        elif c.get("found") is False:
            line += "   NO PATH"
        yy += draw_text(surface, line, (x + 8, yy), 20) + 2
        draw_text(surface, "blue = expanded, red = current, orange = road just examined, green = final route",
                  (x + 8, yy), 17)


class BfsPanel(_TracePanel):
    algo, title = "bfs", "BFS (fewest roads)"


class DfsPanel(_TracePanel):
    algo, title = "dfs", "DFS (depth-first traversal)"


class DijkstraPanel(_TracePanel):
    algo, title = "dijkstra", "Dijkstra (least cost)"


class AStarPanel(_TracePanel):
    algo, title = "astar", "A* (least cost, guided)"


PANELS_A = [BfsPanel, DfsPanel, DijkstraPanel, AStarPanel]
