"""FROZEN GUI pattern. Each screen is a class in its OWN file, so GUI work never conflicts.
Navigation: a screen returns the NAME of the next screen from handle_event/update, or None to stay."""


class Screen:
    name = "base"
    def on_enter(self, app, **kwargs): pass
    def handle_event(self, event): return None
    def update(self, dt): return None
    def draw(self, surface): pass


class LabPanel:
    """Algorithm Lab panel. Each person writes panels for THEIR algorithms in gui/lab_<a|b|c>.py.
    Must call the same functions as gameplay (e.g. routing.api.dijkstra), never a copy."""
    title = "panel"
    def reset(self, graph): pass
    def step(self): pass            # advance visualization one step
    def counters(self) -> dict: return {}
    def draw(self, surface, rect): pass
