from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProviderHealthStats:
    name: str
    provider_type: str
    chain: str = "base"
    success_count: int = 0
    failure_count: int = 0
    consecutive_failures: int = 0
    total_latency_ms: float = 0.0
    last_latency_ms: float | None = None
    last_success_at: float | None = None
    last_failure_at: float | None = None
    last_error: str | None = None
    metadata: dict = field(default_factory=dict)

    @property
    def total_count(self) -> int:
        return self.success_count + self.failure_count

    @property
    def success_rate(self) -> float:
        if self.total_count == 0:
            return 1.0
        return self.success_count / self.total_count

    @property
    def avg_latency_ms(self) -> float | None:
        if self.success_count == 0:
            return None
        return self.total_latency_ms / self.success_count

    @property
    def score(self) -> int:
        base = self.success_rate * 100
        penalty = min(40, self.consecutive_failures * 10)
        latency_penalty = 0
        avg = self.avg_latency_ms
        if avg is not None:
            latency_penalty = min(30, max(0, (avg - 750) / 100))
        return int(max(0, min(100, base - penalty - latency_penalty)))

    def record_success(self, latency_ms: float) -> None:
        self.success_count += 1
        self.consecutive_failures = 0
        self.total_latency_ms += latency_ms
        self.last_latency_ms = latency_ms
        self.last_success_at = time.time()
        self.last_error = None

    def record_failure(self, error: str, latency_ms: float | None = None) -> None:
        self.failure_count += 1
        self.consecutive_failures += 1
        self.last_failure_at = time.time()
        self.last_error = error[:500]
        if latency_ms is not None:
            self.last_latency_ms = latency_ms

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "provider_type": self.provider_type,
            "chain": self.chain,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate_pct": round(self.success_rate * 100, 2),
            "consecutive_failures": self.consecutive_failures,
            "avg_latency_ms": round(self.avg_latency_ms, 2) if self.avg_latency_ms is not None else None,
            "last_latency_ms": round(self.last_latency_ms, 2) if self.last_latency_ms is not None else None,
            "last_success_at": self.last_success_at,
            "last_failure_at": self.last_failure_at,
            "last_error": self.last_error,
            "score": self.score,
            "metadata": self.metadata,
        }


class ProviderHealthRegistry:
    def __init__(self, output_path: Path | str = "data/provider_health.json") -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(exist_ok=True)
        self._stats: dict[str, ProviderHealthStats] = {}

    def get(self, name: str, provider_type: str, chain: str = "base") -> ProviderHealthStats:
        normalized_chain = self._normalize_chain(chain)
        key = self._key(provider_type, normalized_chain, name)
        if key not in self._stats:
            self._stats[key] = ProviderHealthStats(name=name, provider_type=provider_type, chain=normalized_chain)
        return self._stats[key]

    def record_success(self, name: str, provider_type: str, latency_ms: float, chain: str = "base", **metadata) -> None:
        stats = self.get(name, provider_type, chain)
        stats.metadata.update(metadata)
        stats.record_success(latency_ms)
        self.persist()

    def record_failure(self, name: str, provider_type: str, error: str, latency_ms: float | None = None, chain: str = "base", **metadata) -> None:
        stats = self.get(name, provider_type, chain)
        stats.metadata.update(metadata)
        stats.record_failure(error, latency_ms)
        self.persist()

    def snapshot(self) -> list[dict]:
        return sorted((s.to_dict() for s in self._stats.values()), key=lambda row: (row["provider_type"], row["chain"], -row["score"], row["name"]))

    def persist(self) -> None:
        payload = {"generated_at": time.time(), "providers": self.snapshot()}
        self.output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @staticmethod
    def _key(provider_type: str, chain: str, name: str) -> str:
        return f"{provider_type.lower()}|{chain.lower()}|{name.lower()}"

    @staticmethod
    def _normalize_chain(chain: str) -> str:
        normalized = str(chain).strip().lower()
        aliases = {
            "base": "base",
            "ethereum": "ethereum",
            "ethereum mainnet": "ethereum",
            "arbitrum one": "arbitrum",
            "arbitrum": "arbitrum",
            "polygon": "polygon",
        }
        return aliases.get(normalized, normalized)


provider_health_registry = ProviderHealthRegistry()
