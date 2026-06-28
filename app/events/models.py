from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4
from typing import Any


class EventType(str, Enum):
    SYSTEM = "SYSTEM"
    QUOTE_REFRESH_STARTED = "QUOTE_REFRESH_STARTED"
    QUOTE_REFRESH_COMPLETED = "QUOTE_REFRESH_COMPLETED"
    STRATEGY_SIGNALS_GENERATED = "STRATEGY_SIGNALS_GENERATED"
    AI_RANKING_COMPLETED = "AI_RANKING_COMPLETED"
    RISK_ASSESSMENT_COMPLETED = "RISK_ASSESSMENT_COMPLETED"
    PAPER_EXECUTION_COMPLETED = "PAPER_EXECUTION_COMPLETED"
    SCHEDULER_RUN_STARTED = "SCHEDULER_RUN_STARTED"
    SCHEDULER_RUN_COMPLETED = "SCHEDULER_RUN_COMPLETED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class CryptoAiEvent:
    event_id: str
    event_type: EventType
    source: str
    created_at: str
    payload: dict[str, Any] = field(default_factory=dict)


def create_event(
    event_type: EventType,
    source: str,
    payload: dict[str, Any] | None = None,
) -> CryptoAiEvent:
    return CryptoAiEvent(
        event_id=str(uuid4())[:12],
        event_type=event_type,
        source=source,
        created_at=datetime.utcnow().isoformat(timespec="seconds") + "Z",
        payload=payload or {},
    )
