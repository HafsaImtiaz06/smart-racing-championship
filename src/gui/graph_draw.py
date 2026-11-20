"""PERSON A. Pygame drawing helpers shared by the Route Planner screen and the Algorithm Lab panels.
All geometry comes from route_view.Viewport; nothing here makes decisions."""
import math
import pygame
from ..core.models import EdgeStatus, VertexType

BG = (250, 250, 247)
PANEL_BG = (238, 240, 245)
TEXT = (30, 30, 30)
GREY = (150, 150, 150)
BLUE = (31, 119, 180)
RED = (214, 39, 40)
GREEN = (44, 160, 44)
ORANGE = (255, 127, 14)
AMBER = (230, 170, 30)
BLOCKED = (200, 60, 60)
VERTEX_COLORS = {VertexType.START: (44, 160, 44), VertexType.FINISH: (20, 20, 20), VertexType.CHECKPOINT: (255, 127, 14),
                 VertexType.INTERSECTION: (170, 170, 170), VertexType.FUEL_STATION: (148, 103, 189),
                 VertexType.NITRO_PICKUP: (23, 190, 207), VertexType.DEAD_END: (140, 86, 75)}
_fonts = {}


def get_font(size):
    if not pygame.font.get_init():
        pygame.font.init()
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(None, size)
    return _fonts[size]


def draw_text(surface, text, pos, size=20, color=TEXT):
    """Draws one line of text at pos=(x, y). Returns the line height so callers can stack lines."""
    font = get_font(size)
    surface.blit(font.render(text, True, color), pos)
    return font.get_height()


def draw_dashed(surface, color, a, b, width=2, dash=8):
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    if length == 0:
        return
    n = max(int(length // dash), 1)
    for i in range(0, n, 2):
        p0 = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
        p1 = (a[0] + (b[0] - a[0]) * min(i + 1, n) / n, a[1] + (b[1] - a[1]) * min(i + 1, n) / n)
        pygame.draw.line(surface, color, p0, p1, width)


def draw_arrow_head(surface, color, a, b, size=9):
    """Arrow head 70% of the way from a to b (marks one-way roads)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    tip = (a[0] + dx * 0.7, a[1] + dy * 0.7)
    left = (tip[0] - ux * size - uy * size / 2, tip[1] - uy * size + ux * size / 2)
    right = (tip[0] - ux * size + uy * size / 2, tip[1] - uy * size - ux * size / 2)
    pygame.draw.polygon(surface, color, [tip, left, right])


def draw_graph(surface, g, vp, edge_styles=None, vertex_fill=None, vertex_ring=None, labels=True):
    """edge_styles: {edge id: (color, width)}; vertex_fill: {vertex id: color}; vertex_ring: {vertex id: color}."""
    edge_styles = edge_styles or {}
    vertex_fill = vertex_fill or {}
    vertex_ring = vertex_ring or {}
    for e in g.edges.values():
        a, b = vp.vertex_pos(e.from_), vp.vertex_pos(e.to)
        if e.id in edge_styles:
            color, width = edge_styles[e.id]
        elif e.status == EdgeStatus.BLOCKED:
            color, width = BLOCKED, 2
        elif e.status == EdgeStatus.RESTRICTED:
            color, width = AMBER, 2
        elif e.isShortcut:
            color, width = (230, 120, 120), 3
        else:
            color, width = GREY, 2
        if e.status == EdgeStatus.BLOCKED and e.id not in edge_styles:
            draw_dashed(surface, color, a, b, width)
        else:
            pygame.draw.line(surface, color, a, b, width)
        if e.directed:
            draw_arrow_head(surface, color, a, b)
    for v in g.vertices.values():
        pos = vp.vertex_pos(v.id)
        radius = 8 if v.type != VertexType.INTERSECTION else 6
        pygame.draw.circle(surface, vertex_fill.get(v.id, VERTEX_COLORS[v.type]), pos, radius)
        pygame.draw.circle(surface, (255, 255, 255), pos, radius, 1)
        if v.id in vertex_ring:
            pygame.draw.circle(surface, vertex_ring[v.id], pos, radius + 5, 3)
        if labels and v.type != VertexType.INTERSECTION:
            from .route_view import vertex_label
            draw_text(surface, vertex_label(g, v.id), (pos[0] + 9, pos[1] - 14), 17)


def draw_route(surface, vp, vertices, color, width=5):
    points = [vp.vertex_pos(v) for v in vertices]
    if len(points) >= 2:
        pygame.draw.lines(surface, color, False, points, width)
    for p in points:
        pygame.draw.circle(surface, color, p, max(width // 2, 2))
