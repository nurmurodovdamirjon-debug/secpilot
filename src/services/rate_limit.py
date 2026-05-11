"""Small in-process rate limiter for defensive API actions."""

from collections import defaultdict, deque
from time import monotonic


class RateLimitExceededError(RuntimeError):
    """Raised when an actor exceeds the configured request budget."""


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, *, limit: int, window_seconds: float = 60.0) -> None:
        now = monotonic()
        events = self._events[key]
        while events and now - events[0] > window_seconds:
            events.popleft()
        if len(events) >= limit:
            raise RateLimitExceededError("rate_limit_exceeded")
        events.append(now)


rate_limiter = InMemoryRateLimiter()
