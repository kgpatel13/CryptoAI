from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo


EASTERN_TZ = ZoneInfo("America/New_York")
ISO_DATETIME_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?\b")
TIME_FIELD_HINTS = ("timestamp", "generated_at", "updated_at", "started_at", "completed_at", "emitted_at", "created_at", "closed_at", "date_time")


def format_eastern_datetime(value: Any) -> str:
    if value in (None, ""):
        return "-"
    raw = str(value).strip()
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return raw
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    eastern = parsed.astimezone(EASTERN_TZ)
    hour = eastern.hour % 12 or 12
    return f"{eastern.day:02d}-{eastern:%b-%Y} {hour}:{eastern:%M} {eastern:%p}"


def localize_timestamps_in_text(text: str) -> str:
    return ISO_DATETIME_PATTERN.sub(lambda match: format_eastern_datetime(match.group(0)), text)


def localize_timestamps(value: Any, key_hint: str = "") -> Any:
    if isinstance(value, dict):
        return {key: localize_timestamps(item, str(key)) for key, item in value.items()}
    if isinstance(value, list):
        return [localize_timestamps(item, key_hint) for item in value]
    if isinstance(value, str):
        lower_key = key_hint.lower()
        if any(hint in lower_key for hint in TIME_FIELD_HINTS) or ISO_DATETIME_PATTERN.fullmatch(value.strip()):
            return localize_timestamps_in_text(value)
    return value
