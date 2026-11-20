Screen ownership (one file per screen):
- main_menu.py, dashboard.py, racing_screen.py, lab.py (screen that hosts panels) .... Person C
- route_planner.py (Route Planner screen), lab_a.py (BFS/DFS/Dijkstra/A* panels) ..... Person A
    helpers by A: route_view.py (decisions, no pygame), lab_trace.py (step replay, no pygame),
                  graph_draw.py (pygame drawing helpers), demo_a.py (stand-alone demo)
- racing_overlays.py (fuel/nitro/event log drawn on the racing screen), lab_b.py ... Person B
- lab_c.py (sorting / top-k panels) ............................................... Person C
lab.py imports the three lab_*.py modules; that import list is the only shared edit (Person C owns the file).

Person A demo (no other screens needed):   python -m src.gui.demo_a
Lab host contract (Person C): panel = PanelClass(); panel.reset(graph); panel.step(); panel.draw(surface, (x, y, w, h));
panel.counters() -> dict; panel.finished -> bool; panel.rewind().   Screens: on_enter(app, graph=...) or app.graph;
handle_event returns the NAME of the next screen or None.
