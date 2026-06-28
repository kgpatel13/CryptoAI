from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterator

from web3 import Web3

from app.resilience.circuit_breaker import CircuitBreaker
from app.resilience.provider_health import provider_health_registry


@dataclass(frozen=True)
class RpcEndpoint:
    chain: str
    url: str
    index: int

    @property
    def name(self) -> str:
        redacted = self.url.split("?")[0].rstrip("/")
        return f"{self.chain}:rpc{self.index}:{redacted}"


class RpcProviderPool:
    """Latency-aware RPC failover pool with circuit breakers."""

    def __init__(self, chain: str, urls: list[str], timeout_seconds: int = 10, failure_threshold: int = 2, cooldown_seconds: int = 60) -> None:
        if not urls:
            raise ValueError(f"No RPC URLs configured for {chain}")
        self.chain = chain
        self.timeout_seconds = timeout_seconds
        self.endpoints = [RpcEndpoint(chain=chain, url=url, index=i + 1) for i, url in enumerate(urls)]
        self.breakers = {ep.name: CircuitBreaker(ep.name, failure_threshold=failure_threshold, recovery_timeout_seconds=cooldown_seconds) for ep in self.endpoints}

    def candidates(self) -> Iterator[tuple[RpcEndpoint, Web3]]:
        ranked = sorted(self.endpoints, key=self._rank)
        for endpoint in ranked:
            breaker = self.breakers[endpoint.name]
            if breaker.allow_request():
                yield endpoint, Web3(Web3.HTTPProvider(endpoint.url, request_kwargs={"timeout": self.timeout_seconds}))

    def record_success(self, endpoint: RpcEndpoint, latency_ms: float) -> None:
        self.breakers[endpoint.name].record_success()
        provider_health_registry.record_success(endpoint.name, "rpc", latency_ms, chain=self.chain, url=self._safe_url(endpoint.url), circuit_state=self.breakers[endpoint.name].state.value)

    def record_failure(self, endpoint: RpcEndpoint, error: str, latency_ms: float | None = None) -> None:
        self.breakers[endpoint.name].record_failure(error)
        provider_health_registry.record_failure(endpoint.name, "rpc", error, latency_ms, chain=self.chain, url=self._safe_url(endpoint.url), circuit_state=self.breakers[endpoint.name].state.value)

    def health_rows(self) -> list[dict]:
        rows = []
        for ep in self.endpoints:
            breaker = self.breakers[ep.name]
            rows.append({"chain": self.chain, "rpc": ep.name, "url": self._safe_url(ep.url), **breaker.snapshot()})
        return rows

    def _rank(self, endpoint: RpcEndpoint) -> tuple[int, int, str]:
        breaker = self.breakers[endpoint.name]
        open_penalty = 1 if not breaker.allow_request() else 0
        return (open_penalty, breaker.failure_count, endpoint.url)

    @staticmethod
    def _safe_url(url: str) -> str:
        if "@" in url:
            return url.split("@", 1)[-1]
        if len(url) > 80:
            return url[:77] + "..."
        return url
