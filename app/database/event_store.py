from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from app.database.db import get_connection, initialize_database


class EventStore:
    """Small SQLite-backed event store."""

    def __init__(self) -> None:
        initialize_database()

    def record_event(self, event_type: str, source: str, payload: Any) -> None:
        created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        payload_json = json.dumps(self._serialize(payload))

        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO events (created_at, event_type, source, payload_json)
                VALUES (?, ?, ?, ?)
                """,
                (created_at, event_type, source, payload_json),
            )
            conn.commit()

    def recent_events(self, limit: int = 100) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT created_at, event_type, source, payload_json
                FROM events
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        output = []
        for row in rows:
            try:
                payload = json.loads(row["payload_json"])
            except Exception:
                payload = row["payload_json"]

            output.append(
                {
                    "created_at": row["created_at"],
                    "event_type": row["event_type"],
                    "source": row["source"],
                    "payload": payload,
                }
            )

        return output

    @classmethod
    def _serialize(cls, value: Any) -> Any:
        if is_dataclass(value):
            return cls._serialize(asdict(value))
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, dict):
            return {str(k): cls._serialize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [cls._serialize(v) for v in value]
        if isinstance(value, tuple):
            return [cls._serialize(v) for v in value]
        return value
