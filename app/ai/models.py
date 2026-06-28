from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class AiRecommendation(str, Enum):
    IGNORE = "IGNORE"
    WATCH = "WATCH"
    PAPER_TRADE_CANDIDATE = "PAPER_TRADE_CANDIDATE"
    NEEDS_MORE_DATA = "NEEDS_MORE_DATA"


@dataclass(frozen=True)
class AiRankedSignal:
    strategy_name: str
    chain: str
    pair: str
    source_action: str
    confidence_score: int
    expected_edge_pct: Decimal | None
    ai_score: int
    recommendation: AiRecommendation
    reasoning: str
