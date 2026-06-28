from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class CircuitBreaker:
    """Small dependency-free circuit breaker for external providers."""

    name: str
    failure_threshold: int = 3
    recovery_timeout_seconds: float = 60.0
    half_open_success_threshold: int = 1
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    half_open_success_count: int = 0
    opened_at: float | None = None
    last_error: str | None = None

    def allow_request(self, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.HALF_OPEN:
            return True
        if self.opened_at is None or now - self.opened_at >= self.recovery_timeout_seconds:
            self.state = CircuitState.HALF_OPEN
            self.half_open_success_count = 0
            return True
        return False

    def record_success(self) -> None:
        self.failure_count = 0
        self.last_error = None
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_success_count += 1
            if self.half_open_success_count >= self.half_open_success_threshold:
                self.state = CircuitState.CLOSED
                self.opened_at = None
                self.half_open_success_count = 0
        elif self.state == CircuitState.OPEN:
            self.state = CircuitState.HALF_OPEN

    def record_failure(self, error: str, now: float | None = None) -> None:
        now = time.time() if now is None else now
        self.last_error = error[:500]
        self.failure_count += 1
        if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.opened_at = now
            self.half_open_success_count = 0

    def snapshot(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "opened_at": self.opened_at,
            "last_error": self.last_error,
            "recovery_timeout_seconds": self.recovery_timeout_seconds,
        }
