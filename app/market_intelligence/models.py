from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class PairCandidate:
    chain: str
    pair: str
    base_symbol: str
    quote_symbol: str
    configured: bool
    priority: int
    token_ready: bool
    dex_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChainReadiness:
    chain: str
    name: str
    token_count: int
    dex_count: int
    configured_pair_count: int
    generated_pair_count: int
    provider_count: int
    provider_score: int
    registry_score: int
    readiness_score: int
    readiness_status: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

