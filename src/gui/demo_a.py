"""PERSON A. Stand-alone demo so you can see your screens without the rest of the game.
Run from the project root:   python -m src.gui.demo_a [tracks/circuit1.json]
F1 = Route Planner (keys shown at the bottom)   F2 = Algorithm Lab (1-4 choose panel, SPACE step, ENTER play/pause,
BACKSPACE replay, E run to end)   Esc in the planner / Q quits."""
import os
import sys
import pygame
from ..core.track_io import load_track
from .lab_a import PANELS_A
from .route_planner import RoutePlannerScreen
from .graph_draw import draw_text, BG, TEXT


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "..", "tracks", "circuit1.json")
    graph = load_track(path)
    pygame.init()
    screen = pygame.display.set_mode((1180, 760), pygame.RESIZABLE)
    pygame.display.set_caption("Person A demo - Route Planner and Algorithm Lab")
    clock = pygame.time.Clock()
    planner = RoutePlannerScreen()
    planner.on_enter(None, graph=graph)
    panels = [cls() for cls in PANELS_A]
    for p in panels:
        p.reset(graph)
    which, view, playing, timer = 3, "planner", False, 0.0
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                view = "planner"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                view = "lab"
            elif view == "planner":
                if planner.handle_event(event) == "main_menu":
                    running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    which = event.key - pygame.K_1
                    panels[which].rewind()
                elif event.key == pygame.K_SPACE:
                    panels[which].step()
                elif event.key == pygame.K_RETURN:
                    playing = not playing
                elif event.key == pygame.K_BACKSPACE:
                    panels[which].rewind()
                elif event.key == pygame.K_e:
                    panels[which].runner.step_to_end()
        if view == "lab" and playing:
            timer += dt
            while timer >= 0.12:
                timer -= 0.12
                panels[which].step()
        if view == "planner":
            planner.update(dt)
            planner.draw(screen)
        else:
            w, h = screen.get_size()
            screen.fill(BG)
            panels[which].draw(screen, (0, 30, w, h - 60))
            draw_text(screen, "Lab: 1 BFS  2 DFS  3 Dijkstra  4 A*  |  SPACE step  ENTER play/pause  BACKSPACE replay  "
                              "E run to end  |  F1 planner  Q quit", (8, h - 24), 18)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
