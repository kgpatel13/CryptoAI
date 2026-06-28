from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 2
    base_delay_seconds: float = 0.20
    max_delay_seconds: float = 2.0
    jitter_seconds: float = 0.10

    def sleep_seconds(self, attempt_index: int) -> float:
        exponential = self.base_delay_seconds * (2 ** max(0, attempt_index - 1))
        return min(self.max_delay_seconds, exponential) + random.uniform(0, self.jitter_seconds)

    def run(self, fn: Callable[[], T]) -> T:
        last_exc: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return fn()
            except Exception as exc:  # noqa: PERF203 - clarity over micro-optimization
                last_exc = exc
                if attempt >= self.max_attempts:
                    break
                time.sleep(self.sleep_seconds(attempt))
        assert last_exc is not None
        raise last_exc
