from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any


class StrategyAction(str, Enum):
    WATCH = "WATCH"
    SKIP = "SKIP"
    READY_FOR_PAPER = "READY_FOR_PAPER"
    DISABLED = "DISABLED"


class StrategyHealth(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    DEGRADED = "DEGRADED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class StrategySignal:
    strategy_name: str
    chain: str
    pair: str
    action: StrategyAction
    confidence_score: int
    expected_edge_pct: Decimal | None
    reason: str
    source: str = "scanner"
    signal_id: str | None = None
    rank_score: int = 0
    features: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategyConfig:
    strategy_id: str
    name: str
    enabled: bool = True
    weight: Decimal = Decimal("1.0")
    min_confidence: int = 0
    max_signals_per_cycle: int = 10
    mode: str = "paper"
    notes: str = ""


@dataclass(frozen=True)
class StrategyDescriptor:
    strategy_id: str
    name: str
    enabled: bool
    health: StrategyHealth
    weight: Decimal
    class_name: str
    reason: str = ""


@dataclass(frozen=True)
class RankedStrategySignal:
    rank: int
    strategy_id: str
    strategy_name: str
    chain: str
    pair: str
    action: StrategyAction
    confidence_score: int
    expected_edge_pct: Decimal | None
    rank_score: int
    reason: str
    source: str = "strategy_manager"
    features: dict[str, Any] = field(default_factory=dict)
