from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SchedulerStepStatus(str, Enum):
    OK = "OK"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class SchedulerStepResult:
    step_name: str
    status: SchedulerStepStatus
    items_processed: int
    latency_ms: float
    message: str


@dataclass(frozen=True)
class SchedulerRunResult:
    run_id: str
    started_at: str
    completed_at: str
    status: SchedulerStepStatus
    paper_execution_enabled: bool
    total_latency_ms: float
    steps: list[SchedulerStepResult]
