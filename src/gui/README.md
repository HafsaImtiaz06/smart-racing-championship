Screen ownership (one file per screen):
- main_menu.py, dashboard.py, racing_screen.py, lab.py (screen that hosts panels) .... Person C
- route_planner.py, lab_a.py (BFS/DFS/Dijkstra/A* panels) ........................ Person A
- racing_overlays.py (fuel/nitro/event log drawn on the racing screen), lab_b.py ... Person B
- lab_c.py (sorting / top-k panels) ............................................... Person C
lab.py imports the three lab_*.py modules; that import list is the only shared edit (Person C owns the file).
