"""PERSON B. CONTRACT (frozen). Uses A's routing.api.reachable_from / bfs_path for validation."""
from ..core.graph import Graph


def mst_backbone(points: list, candidate_edges: list, algo: str = "kruskal") -> list:
    """Undirected MST over a CONNECTED candidate graph (else raise ValueError). Returns chosen edges."""
    raise NotImplementedError


def generate_track(seed: int, n_checkpoints: int = 10, max_attempts: int = 50) -> tuple:
    """Returns (Graph or None, log: list[str]). log records rejected candidates and the reason."""
    raise NotImplementedError


def validate_track(g: Graph) -> list:
    """Return list of problems (empty = valid): ordered checkpoint reachability, lap return, >=2 alt routes,
    >=10 checkpoints, >=2 shortcuts, a cycle, a dead end, feasible fuel plan, geometry."""
    raise NotImplementedError
