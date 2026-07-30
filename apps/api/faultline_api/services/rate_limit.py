from __future__ import annotations

from collections import deque
from threading import Lock
from time import monotonic


class SlidingWindowLimiter:
    """Bounded process-local limiter for public demo write endpoints.

    A scaled production deployment should replace this with an edge or Redis-backed
    limiter so limits are shared across workers and instances.
    """

    def __init__(self, limit: int, window_seconds: int, max_keys: int = 2048) -> None:
        if limit <= 0 or window_seconds <= 0 or max_keys <= 0:
            raise ValueError("rate-limit settings must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self.max_keys = max_keys
        self._events: dict[str, deque[float]] = {}
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            stale_keys = [
                candidate
                for candidate, values in self._events.items()
                if not values or values[-1] < cutoff
            ]
            for candidate in stale_keys:
                self._events.pop(candidate, None)

            events = self._events.get(key)
            if events is None:
                if len(self._events) >= self.max_keys:
                    return False
                events = deque()
                self._events[key] = events

            while events and events[0] < cutoff:
                events.popleft()
            if len(events) >= self.limit:
                return False
            events.append(now)
            return True


UPLOAD_LIMITER = SlidingWindowLimiter(limit=12, window_seconds=60)
WRITE_LIMITER = SlidingWindowLimiter(limit=90, window_seconds=60)
