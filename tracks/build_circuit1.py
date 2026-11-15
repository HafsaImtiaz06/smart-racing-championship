"""Builds tracks/circuit1.json (Person A). Run from the project root:  python tracks/build_circuit1.py
Edit the tables below, rerun, then run  python -m unittest discover tests  to re-validate the circuit.

Road kinds (seconds per unit distance, fuel per unit distance):
  hw    highway   fast, thirsty          rd   normal road          rough  slow dirt road, thrifty
  sc    shortcut  fastest, thirstiest, high difficulty
Lap rule used by this circuit: a lap = checkpoints 1..10 in order, then crossing the Finish vertex (the lap boundary).
Racers start at Start; after crossing Finish they drive Finish -> Start -> checkpoint 1 for the next lap."""
import json, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.track_io import load_track
from src.routing.api import dijkstra

KIND = {"hw": (0.022, 0.055), "rd": (0.033, 0.040), "rough": (0.050, 0.035), "sc": (0.020, 0.060)}

# id: (name, x, y, type, checkpointOrder)
V = {
    0: ("Start", 225, 640, "Start", None),
    1: ("Finish", 140, 620, "Finish", None),
    2: ("CP1", 300, 625, "Checkpoint", 1),
    3: ("R1", 450, 600, "Intersection", None),
    4: ("CP2", 610, 625, "Checkpoint", 2),
    5: ("FuelA", 740, 605, "FuelStation", None),
    6: ("CP3", 880, 565, "Checkpoint", 3),
    7: ("R2", 990, 620, "Intersection", None),
    8: ("CP4", 975, 330, "Checkpoint", 4),
    9: ("FuelE", 890, 170, "FuelStation", None),
    10: ("CP5", 760, 75, "Checkpoint", 5),
    11: ("NitroA", 610, 45, "NitroPickup", None),
    12: ("CP6", 460, 70, "Checkpoint", 6),
    13: ("FuelD", 320, 50, "FuelStation", None),
    14: ("CP7", 180, 115, "Checkpoint", 7),
    15: ("R5", 30, 170, "Intersection", None),
    16: ("CP8", 60, 310, "Checkpoint", 8),
    17: ("FuelB", 50, 400, "FuelStation", None),
    18: ("CP9", 75, 480, "Checkpoint", 9),
    19: ("CP10", 105, 550, "Checkpoint", 10),
    20: ("I1", 330, 480, "Intersection", None),
    21: ("I2", 520, 440, "Intersection", None),
    22: ("I3", 700, 430, "Intersection", None),
    23: ("I4", 800, 300, "Intersection", None),
    24: ("I5", 620, 260, "Intersection", None),
    25: ("I6", 430, 270, "Intersection", None),
    26: ("I7", 250, 300, "Intersection", None),
    27: ("I8", 200, 430, "Intersection", None),
    28: ("DeadEnd1", 1010, 90, "DeadEnd", None),
    29: ("NitroB", 250, 200, "NitroPickup", None),      # risky pickup at the end of a spur
    30: ("FuelC", 560, 350, "FuelStation", None),       # inner station between I2 and I5
    31: ("Back1", 850, 200, "Intersection", None),      # backroad CP4 -> CP5 (slow, thrifty, easy)
    32: ("Back2", 745, 545, "Intersection", None),      # backroad CP2 -> CP3 (skips FuelA)
}

# (from, to, kind, difficulty, directed, isShortcut)   distance = straight line x curve factor
E = [
    # outer ring: Finish - Start - CP1 - ... - CP10 - Finish (Start and Finish sit side by side on the start/finish straight)
    (0, 1, "rd", 1, False, False),
    (0, 2, "hw", 2, False, False), (2, 3, "hw", 2, False, False), (3, 4, "hw", 2, False, False),
    (4, 5, "hw", 2, False, False), (5, 6, "hw", 2, False, False), (6, 7, "hw", 3, False, False),
    (7, 8, "hw", 3, False, False), (8, 9, "hw", 3, False, False), (9, 10, "hw", 2, False, False),
    (10, 11, "hw", 2, False, False), (11, 12, "hw", 2, False, False), (12, 13, "hw", 2, False, False),
    (13, 14, "hw", 3, False, False), (14, 15, "hw", 3, False, False), (15, 16, "hw", 3, False, False),
    (16, 17, "hw", 2, False, False), (17, 18, "hw", 2, False, False), (18, 19, "hw", 2, False, False),
    (19, 1, "hw", 2, False, False),
    # inner roads (alternatives, gentler)
    (2, 20, "rd", 1, False, False), (20, 21, "rd", 1, False, False), (21, 4, "rough", 1, False, False),
    (21, 3, "rd", 1, False, False), (21, 22, "rd", 1, False, False), (22, 6, "rd", 2, False, False),
    (22, 5, "rd", 1, False, False), (22, 23, "rd", 1, False, False), (23, 8, "rd", 1, False, False),
    (23, 7, "rough", 2, False, False), (23, 24, "rd", 1, False, False), (24, 11, "rough", 2, False, False),
    (24, 25, "rd", 1, False, False), (25, 12, "rd", 1, False, False), (25, 26, "rd", 1, False, False),
    (26, 14, "rough", 2, False, False), (26, 16, "rd", 1, False, False), (26, 27, "rd", 1, False, False),
    (27, 20, "rd", 1, False, False), (27, 18, "rd", 1, False, False), (27, 19, "rd", 2, False, False),
    (21, 30, "rd", 1, False, False), (30, 24, "rd", 1, False, False),
    # backroads: same distance as the highway, slower, thriftier, easier
    (8, 31, "rough", 1, False, False), (31, 10, "rough", 1, False, False),
    (4, 32, "rough", 1, False, False), (32, 6, "rough", 1, False, False),
    # spurs (dead ends)
    (9, 28, "rough", 2, False, False), (26, 29, "rough", 3, False, False),
    # shortcuts
    (6, 8, "sc", 4, False, True),        # SC1: CP3 -> CP4 straight across the bottom-right corner
    (14, 16, "sc", 5, True, True),       # SC2: CP7 -> CP8 one-way, steep, across the top-left corner
]

ONE_LAP_MAIN_ROUTE = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 1]   # Opponent 1: Start -> CP1..CP10 -> Finish; later laps repeat from Finish via Start


def build():
    vertices = [{"id": i, "x": x, "y": y, "type": t, "checkpointOrder": c, "active": True, "name": n}
                for i, (n, x, y, t, c) in V.items()]
    edges = []
    for k, (a, b, kind, diff, directed, sc) in enumerate(E):
        (_, xa, ya, _, _), (_, xb, yb, _, _) = V[a], V[b]
        straight = math.hypot(xa - xb, ya - yb)
        curve = 1.0 if sc else 1.12 if kind == "hw" else 1.06
        dist = round(straight * curve, 1)
        sec_per_unit, fuel_per_unit = KIND[kind]
        edges.append({"id": k, "from": a, "to": b, "distance": dist, "baseTime": round(dist * sec_per_unit, 2),
                      "fuelCost": round(dist * fuel_per_unit, 2), "difficulty": diff, "status": "Open",
                      "isShortcut": sc, "directed": directed})
    return {"name": "Circuit 1 - Coastal Loop", "vertices": vertices, "edges": edges,
            "lap_boundary": 1, "laps_note": "A lap = checkpoints 1..10 in order, then crossing the Finish vertex (id 1). Later laps run Finish -> Start -> CP1.",
            "main_route": ONE_LAP_MAIN_ROUTE}


def add_fixed_detours(path):
    """Opponent 1 detour table: for each road on the main route, the vertex path (computed once with Dijkstra,
    Balanced preset, that road blocked) that replaces it. Stored so the behaviour is fixed and documented."""
    g = load_track(path)
    by_pair = {}
    for e in g.edges.values():
        by_pair.setdefault(frozenset((e.from_, e.to)), []).append(e.id)
    detours = {}
    for a, b in zip(ONE_LAP_MAIN_ROUTE, ONE_LAP_MAIN_ROUTE[1:] + [ONE_LAP_MAIN_ROUTE[0]]):
        eid = by_pair[frozenset((a, b))][0]
        g.block_edge(eid)
        r = dijkstra(g, a, b, "Balanced")
        g.unblock_edge(eid)
        if r.found:
            detours[str(eid)] = r.vertices
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["fixed_detour"] = detours
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "circuit1.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(build(), f, indent=1)
    add_fixed_detours(out)
    print("wrote", out)
