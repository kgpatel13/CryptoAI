from __future__ import annotations

from collections import deque
from threading import Lock
from typing import Callable

from app.events.models import CryptoAiEvent


EventHandler = Callable[[CryptoAiEvent], None]


class EventBus:
    """Small in-memory event bus.

    This is intentionally lightweight for v2.0. Future versions can swap this
    for Redis Streams, Kafka, RabbitMQ, or another durable bus.
    """

    def __init__(self, max_events: int = 1000) -> None:
        self._events: deque[CryptoAiEvent] = deque(maxlen=max_events)
        self._subscribers: list[EventHandler] = []
        self._lock = Lock()

    def publish(self, event: CryptoAiEvent) -> None:
        with self._lock:
            self._events.appendleft(event)
            subscribers = list(self._subscribers)

        for handler in subscribers:
            try:
                handler(event)
            except Exception:
                # Subscribers should never break the event bus.
                continue

    def subscribe(self, handler: EventHandler) -> None:
        with self._lock:
            self._subscribers.append(handler)

    def recent(self, limit: int = 100) -> list[CryptoAiEvent]:
        with self._lock:
            return list(self._events)[:limit]

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


event_bus = EventBus()
