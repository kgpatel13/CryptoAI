from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class RuntimeStatus(str, Enum):
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class Heartbeat:
    service_name: str
    status: RuntimeStatus
    emitted_at: str
    run_id: str
    cycle_count: int
    uptime_seconds: float
    message: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload


@dataclass(frozen=True)
class RuntimeState:
    service_name: str
    status: RuntimeStatus
    run_id: str
    started_at: str
    updated_at: str
    uptime_seconds: float
    cycle_count: int
    last_cycle_started_at: str | None = None
    last_cycle_completed_at: str | None = None
    last_cycle_status: str | None = None
    last_error: str | None = None
    stop_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload


@dataclass(frozen=True)
class OperationalMetrics:
    service_name: str
    run_id: str
    uptime_seconds: float
    cycles_completed: int
    cycles_failed: int
    heartbeats_emitted: int
    last_cycle_latency_ms: float
    average_cycle_latency_ms: float
    scheduler_status_counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MissionSummary:
    service_name: str
    run_id: str
    status: RuntimeStatus
    mode: str
    started_at: str
    updated_at: str
    uptime_seconds: float
    cycles_completed: int
    cycles_failed: int
    last_cycle_status: str | None
    last_error: str | None
    live_trading_enabled: bool
    stop_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload

