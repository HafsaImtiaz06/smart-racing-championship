"""Person B racing-screen overlays: fuel bar, nitro charges, event log, planner recommendations.
Usage (Person C's racing_screen.py):  overlays.draw(surface, state, rect, recommended=ids, to_screen=fn)
state is core.models.RaceState; recommended = list of vertex ids from planning.api.recommend_pickups."""
import pygame
from ..core import constants as K
from .lab_b import font, text, BG, FG, DIM, GREEN, RED, YEL, BLUE, ORG


def draw_fuel_nitro(surface, racer, rect):
    x, y, w, h = rect
    frac = max(0.0, min(1.0, racer.fuel / K.MAX_FUEL))
    col = GREEN if frac > K.REFUEL_THRESHOLD else RED
    text(surface, "Fuel %.0f / %.0f" % (racer.fuel, K.MAX_FUEL), (x, y), FG, 20)
    pygame.draw.rect(surface, (40, 46, 60), (x, y + 22, w, 16))
    pygame.draw.rect(surface, col, (x, y + 22, int(w * frac), 16))
    mark = x + int(w * K.REFUEL_THRESHOLD)
    pygame.draw.line(surface, YEL, (mark, y + 20), (mark, y + 40), 2)
    text(surface, "Nitro", (x, y + 46), FG, 20)
    for i in range(K.MAX_NITRO):
        c = ORG if i < racer.nitroCharges else (50, 55, 70)
        pygame.draw.circle(surface, c, (x + 60 + i * 26, y + 55), 9)
    return y + 74


def draw_event_log(surface, log, rect, lines=6):
    x, y, w, h = rect
    text(surface, "Race events", (x, y), YEL, 20)
    for r, s in enumerate(log[-lines:]):
        text(surface, s[:int(w / 7)], (x, y + 22 + r * 18), FG, 17)
    if not log:
        text(surface, "no events yet", (x, y + 22), DIM, 17)


def draw_recommendations(surface, graph, ids, to_screen):
    """Rings around recommended nitro pickups on the map; to_screen maps (x, y) to screen pixels."""
    for vid in ids:
        v = graph.vertices[vid]
        pygame.draw.circle(surface, ORG, to_screen(v.x, v.y), 13, 3)


class RacingOverlays:
    def draw(self, surface, state, rect, recommended=None, to_screen=None):
        x, y, w, h = rect
        pygame.draw.rect(surface, BG, rect)
        human = next((r for r in state.racers if r.isHuman), state.racers[0] if state.racers else None)
        if human is None:
            return
        text(surface, "%s  lap %d  cp %d  t=%.1fs" % (human.name, human.lap, human.nextCheckpoint, state.time), (x + 8, y + 6), FG, 20)
        yy = draw_fuel_nitro(surface, human, (x + 8, y + 32, w - 16, 0))
        if recommended is not None:
            text(surface, "Recommended pickups: " + (", ".join("N%d" % v for v in recommended) or "none"), (x + 8, yy + 4), ORG, 18)
            yy += 24
            if to_screen is not None:
                draw_recommendations(surface, state.graph, recommended, to_screen)
        draw_event_log(surface, state.event_log, (x + 8, yy + 6, w - 16, h - (yy - y) - 8))
