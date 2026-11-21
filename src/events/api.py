"""PERSON B. CONTRACT (frozen). Min-heap keyed by Event.key() = (triggerTime, priority, insertionSequence); lazy deletion.
EventQueue: push, pop (skips cancelled), peek, cancel(event_id), len(), counters heap_ops/compares/swaps/lazy_dropped.
EventManager(graph): schedule(etype, trigger_time, target, duration=None) -> eventId;
                     advance_to(t) -> list of applied Events (empty list = no graph change = no replanning);
                     extras: cancel(event_id), notify_collected(vertex_id), log (list[str]) for the racing screen."""
from .queue import EventQueue
from .manager import EventManager
