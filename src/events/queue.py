"""Binary min-heap of Events keyed by Event.key() = (triggerTime, priority, insertionSequence). Lazy deletion."""
from ..core.models import Event


class EventQueue:
    def __init__(self):
        self._h = []              # list of (key, event)
        self._live = {}           # eventId -> event, for events still waiting
        self.heap_ops = 0         # pushes + pops (including pops that discard cancelled events)
        self.compares = 0
        self.swaps = 0
        self.lazy_dropped = 0

    def _less(self, a, b):
        self.compares += 1
        return a[0] < b[0]

    def push(self, e: Event) -> None:
        h = self._h
        h.append((e.key(), e))
        self._live[e.eventId] = e
        self.heap_ops += 1
        i = len(h) - 1
        while i > 0:
            p = (i - 1) // 2
            if not self._less(h[i], h[p]):
                break
            h[i], h[p] = h[p], h[i]
            self.swaps += 1
            i = p

    def _pop_raw(self):
        h = self._h
        top = h[0]
        last = h.pop()
        self.heap_ops += 1
        if h:
            h[0] = last
            i, n = 0, len(h)
            while True:
                l, r, m = 2 * i + 1, 2 * i + 2, i
                if l < n and self._less(h[l], h[m]):
                    m = l
                if r < n and self._less(h[r], h[m]):
                    m = r
                if m == i:
                    break
                h[i], h[m] = h[m], h[i]
                self.swaps += 1
                i = m
        return top[1]

    def _drop_cancelled(self):
        while self._h and self._h[0][1].cancelled:
            self._pop_raw()
            self.lazy_dropped += 1

    def pop(self) -> Event:
        self._drop_cancelled()
        if not self._h:
            raise IndexError("pop from empty EventQueue")
        e = self._pop_raw()
        self._live.pop(e.eventId, None)
        return e

    def peek(self) -> Event:
        self._drop_cancelled()
        if not self._h:
            raise IndexError("peek at empty EventQueue")
        return self._h[0][1]

    def cancel(self, event_id: int) -> bool:
        """Lazy deletion: only mark the event. It is discarded when it reaches the top (O(1) now, memory freed later)."""
        e = self._live.pop(event_id, None)
        if e is None or e.cancelled:
            return False
        e.cancelled = True
        return True

    def __len__(self) -> int:
        return len(self._live)
