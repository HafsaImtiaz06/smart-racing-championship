"""PERSON B. CONTRACT (frozen). Uses A's routing.api.reachable_from / bfs_path for validation.
mst_backbone(points, candidate_edges, algo="kruskal") -> chosen edges (ValueError if candidate graph is disconnected)
generate_track(seed, n_checkpoints=10, max_attempts=50) -> (Graph or None, log: list[str])   [optional params=, trace=]
validate_track(g) -> list of problems (empty = valid)
export_extras(g) -> dict for core.track_io.save_track(extra=...): lap_boundary, main_route, fixed_detour"""
from .mst import mst_backbone
from .track import generate_track, validate_track, export_extras
