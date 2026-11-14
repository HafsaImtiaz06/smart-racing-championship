"""PERSON B. CONTRACT (frozen). Min-heap keyed by Event.key() = (triggerTime, priority, insertionSequence); lazy deletion."""
from ..core.graph import Graph
from ..core.models import Event, EventType


class EventQueue:
    def push(self, e: Event) -> None: raise NotImplementedError
    def pop(self) -> Event: raise NotImplementedError          # skips cancelled events
    def peek(self) -> Event: raise NotImplementedError
    def cancel(self, event_id: int) -> bool: raise NotImplementedError
    def __len__(self) -> int: raise NotImplementedError
    # counters for Experiment 4
    heap_ops: int = 0


class EventManager:
    """Owns the EventQueue and applies effects to the Graph (only via Graph's dynamic-update methods)."""
    def __init__(self, graph: Graph): raise NotImplementedError

    def schedule(self, etype: EventType, trigger_time: float, target: int, duration=None) -> int:
        """Validate target exists, assign priority from K.EVENT_PRIORITY, insertionSequence, schedule expiry event. Returns eventId."""
        raise NotImplementedError

    def advance_to(self, t: float) -> list:
        """Apply ALL events with triggerTime <= t in heap order. Return list of applied Event objects
        (empty list => no graph change => no replanning needed). Race engine replans when list is non-empty."""
        raise NotImplementedError
