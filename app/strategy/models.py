from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class StrategyAction(str, Enum):
    WATCH = "WATCH"
    SKIP = "SKIP"
    READY_FOR_PAPER = "READY_FOR_PAPER"
    DISABLED = "DISABLED"


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
