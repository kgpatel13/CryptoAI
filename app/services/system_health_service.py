from __future__ import annotations

from dataclasses import dataclass

from app.cache.quote_cache import quote_cache
from app.metrics.metrics import metrics


@dataclass(frozen=True)
class LatencyBudget:
    stage: str
    target_ms: int
    current_ms: float | None
    status: str


class SystemHealthService:
    """Central place for latency and readiness status.

    For future live trading, the full signal-to-execution pipeline must be
    consistently fast. This service tracks early building blocks.
    """

    def get_cache_stats(self) -> dict:
        return quote_cache.stats()

    def get_metric_rows(self) -> list[dict]:
        return [
            {
                "Component": item.name,
                "Calls": item.calls,
                "Successes": item.successes,
                "Failures": item.failures,
                "Avg Latency ms": item.avg_latency_ms,
                "Max Latency ms": item.max_latency_ms,
            }
            for item in metrics.snapshots()
        ]

    def get_latency_budget(self) -> list[LatencyBudget]:
        snapshots = {s.name: s for s in metrics.snapshots()}

        quote_avg = snapshots.get("quote_service.get_base_quotes").avg_latency_ms if snapshots.get("quote_service.get_base_quotes") else None
        chain_avg = snapshots.get("chain_health.check_all").avg_latency_ms if snapshots.get("chain_health.check_all") else None

        return [
            self._budget("Chain health read", 1000, chain_avg),
            self._budget("Quote refresh", 1500, quote_avg),
            self._budget("Scanner decision path", 2500, quote_avg),
            self._budget("Future execution path", 1000, None),
        ]

    @staticmethod
    def _budget(stage: str, target_ms: int, current_ms: float | None) -> LatencyBudget:
        if current_ms is None:
            status = "Not measured"
        elif current_ms <= target_ms:
            status = "✅ OK"
        else:
            status = "⚠️ Slow"

        return LatencyBudget(stage, target_ms, current_ms, status)
