"""FROZEN circuit JSON format. See tracks/FORMAT.md."""
import json
from .graph import Graph
from .models import Vertex, Edge, VertexType, EdgeStatus


def load_track(path: str) -> Graph:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    g = Graph(data.get("name", path))
    for v in data["vertices"]:
        g.add_vertex(Vertex(id=v["id"], x=v["x"], y=v["y"], type=VertexType(v["type"]),
                            checkpointOrder=v.get("checkpointOrder"), active=v.get("active", True)))
    for e in data["edges"]:
        g.add_edge(Edge(id=e["id"], from_=e["from"], to=e["to"], distance=e["distance"],
                        baseTime=e["baseTime"], fuelCost=e["fuelCost"], difficulty=e.get("difficulty", 1),
                        status=EdgeStatus(e.get("status", "Open")), isShortcut=e.get("isShortcut", False),
                        directed=e.get("directed", False)))
    g.finalize()
    return g


def save_track(g: Graph, path: str, extra: dict = None):
    data = {"name": g.name,
            "vertices": [{"id": v.id, "x": v.x, "y": v.y, "type": v.type.value,
                          "checkpointOrder": v.checkpointOrder, "active": v.active} for v in g.vertices.values()],
            "edges": [{"id": e.id, "from": e.from_, "to": e.to, "distance": e.distance, "baseTime": e.baseTime,
                       "fuelCost": e.fuelCost, "difficulty": e.difficulty, "status": e.status.value,
                       "isShortcut": e.isShortcut, "directed": e.directed} for e in g.edges.values()]}
    if extra:
        data.update(extra)   # e.g. "main_route": [...] for Opponent 1, "events": [...] scripted race events
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
