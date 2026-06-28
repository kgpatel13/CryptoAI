from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from enum import Enum
from typing import Any

from app.events.event_bus import event_bus
from app.events.models import CryptoAiEvent, EventType, create_event

try:
    from app.database.event_store import EventStore
except Exception:
    EventStore = None


class EventBusService:
    """Application service for publishing and reading events."""

    def publish(
        self,
        event_type: EventType,
        source: str,
        payload: dict[str, Any] | None = None,
        persist: bool = True,
    ) -> CryptoAiEvent:
        event = create_event(
            event_type=event_type,
            source=source,
            payload=self._serialize(payload or {}),
        )
        event_bus.publish(event)

        if persist and EventStore is not None:
            try:
                EventStore().record_event(event_type.value, source, asdict(event))
            except Exception:
                pass

        return event

    def publish_system_event(self, source: str, message: str) -> CryptoAiEvent:
        return self.publish(
            event_type=EventType.SYSTEM,
            source=source,
            payload={"message": message},
        )

    def recent_events(self, limit: int = 100) -> list[dict]:
        rows = []
        for event in event_bus.recent(limit):
            rows.append(
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "source": event.source,
                    "created_at": event.created_at,
                    "payload": event.payload,
                }
            )
        return rows

    @classmethod
    def _serialize(cls, value: Any) -> Any:
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, dict):
            return {str(k): cls._serialize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [cls._serialize(v) for v in value]
        if hasattr(value, "__dict__"):
            return cls._serialize(value.__dict__)
        return value
