from __future__ import annotations

import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class MetricSnapshot:
    name: str
    calls: int
    successes: int
    failures: int
    avg_latency_ms: float
    max_latency_ms: float


class MetricsRegistry:
    """In-memory performance metrics for the running dashboard process."""

    def __init__(self) -> None:
        self._calls: dict[str, int] = defaultdict(int)
        self._successes: dict[str, int] = defaultdict(int)
        self._failures: dict[str, int] = defaultdict(int)
        self._latencies: dict[str, list[float]] = defaultdict(list)

    def record(self, name: str, latency_ms: float, success: bool) -> None:
        self._calls[name] += 1
        if success:
            self._successes[name] += 1
        else:
            self._failures[name] += 1
        self._latencies[name].append(latency_ms)

    @contextmanager
    def timer(self, name: str):
        start = time.perf_counter()
        success = False
        try:
            yield
            success = True
        finally:
            latency_ms = (time.perf_counter() - start) * 1000
            self.record(name, latency_ms, success)

    def snapshots(self) -> list[MetricSnapshot]:
        rows: list[MetricSnapshot] = []
        for name in sorted(self._calls.keys()):
            latencies = self._latencies[name]
            avg = sum(latencies) / len(latencies) if latencies else 0.0
            mx = max(latencies) if latencies else 0.0
            rows.append(
                MetricSnapshot(
                    name=name,
                    calls=self._calls[name],
                    successes=self._successes[name],
                    failures=self._failures[name],
                    avg_latency_ms=round(avg, 2),
                    max_latency_ms=round(mx, 2),
                )
            )
        return rows

    def reset(self) -> None:
        self._calls.clear()
        self._successes.clear()
        self._failures.clear()
        self._latencies.clear()


metrics = MetricsRegistry()
