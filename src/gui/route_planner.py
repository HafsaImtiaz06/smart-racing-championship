"""PERSON A. Route Planner screen (spec screen 2): graph view, reachable checkpoints, alternative routes, cost comparison.
Drawing and input only; the decisions live in route_view.PlannerModel (tested without pygame)."""
import pygame
from ..core import constants as K
from .base import Screen
from .graph_draw import (BG, PANEL_BG, TEXT, GREEN, ORANGE, BLUE, draw_graph, draw_route, draw_text)
from .route_view import PlannerModel, Viewport

HELP = ("Click: source then target | 1-4: preset | A: A*/Dijkstra | C: checkpoint route | "
        "N/P: alternatives | X: block road mode | R: reset | Esc: menu")
PRESET_KEYS = {pygame.K_1: "Balanced", pygame.K_2: "Speed", pygame.K_3: "Economy", pygame.K_4: "Safety"}


class RoutePlannerScreen(Screen):
    name = "route_planner"

    def on_enter(self, app, **kwargs):
        graph = kwargs.get("graph") or getattr(app, "graph", None)
        if graph is None:
            raise ValueError("RoutePlannerScreen needs a graph: on_enter(app, graph=...) or app.graph")
        self.app = app
        self.model = PlannerModel(graph)
        self.block_mode = False
        self.vp = None
        self._size = None

    def _layout(self, surface):
        w, h = surface.get_size()
        if self._size != (w, h) or self.vp is None:
            self._size = (w, h)
            self.map_w = int(w * 0.66)
            self.vp = Viewport(self.model.g, (0, 0, self.map_w, h - 34))
        return w, h

    def handle_event(self, event):
        if self.vp is None:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            if self.vp.contains(x, y):
                if self.block_mode:
                    eid = self.vp.edge_at(x, y)
                    if eid is not None:
                        self.model.toggle_block(eid)
                else:
                    vid = self.vp.vertex_at(x, y)
                    if vid is not None:
                        self.model.click_vertex(vid)
        elif event.type == pygame.KEYDOWN:
            if event.key in PRESET_KEYS:
                self.model.set_preset(PRESET_KEYS[event.key])
            elif event.key == pygame.K_a:
                self.model.cycle_algo()
            elif event.key == pygame.K_c:
                self.model.toggle_mode()
            elif event.key == pygame.K_x:
                self.block_mode = not self.block_mode
            elif event.key in (pygame.K_n, pygame.K_RIGHT):
                self.model.step_alternative(1)
            elif event.key in (pygame.K_p, pygame.K_LEFT):
                self.model.step_alternative(-1)
            elif event.key == pygame.K_r:
                self.model.reset_endpoints()
            elif event.key == pygame.K_ESCAPE:
                return "main_menu"
        return None

    def update(self, dt):
        return None

    def draw(self, surface):
        w, h = self._layout(surface)
        m, g, r = self.model, self.model.g, self.model.result()
        surface.fill(BG)
        pygame.draw.rect(surface, PANEL_BG, (self.map_w, 0, w - self.map_w, h - 34))
        draw_graph(surface, g, self.vp)
        if r.alternatives:                                          # selected alternative under the main route
            draw_route(surface, self.vp, r.alternatives[m.selected_alt][0], ORANGE, 8)
        if r.found:
            draw_route(surface, self.vp, r.vertices, GREEN, 4)
        s, t = self.vp.vertex_pos(m.source), self.vp.vertex_pos(m.target)
        pygame.draw.circle(surface, GREEN, s, 14, 3)
        if r.mode == "point":
            pygame.draw.circle(surface, BLUE, t, 14, 3)
        y = 10
        for line in m.info_lines():
            y += draw_text(surface, line, (self.map_w + 10, y), 20) + 2
        if self.block_mode:
            draw_text(surface, "BLOCK MODE: click a road to block / reopen it", (10, 8), 24, (200, 60, 60))
        draw_text(surface, "Next click sets: %s" % m.next_click, (10, h - 56), 18)
        draw_text(surface, HELP, (8, h - 26), 18)
