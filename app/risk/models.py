from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class RiskDecision(str, Enum):
    APPROVED_FOR_PAPER = "APPROVED_FOR_PAPER"
    WATCHLIST = "WATCHLIST"
    BLOCKED = "BLOCKED"
    DISABLED = "DISABLED"


@dataclass(frozen=True)
class RiskPolicy:
    max_paper_trade_usd: Decimal = Decimal("1000")
    min_ai_score_for_paper: int = 70
    min_expected_edge_pct: Decimal = Decimal("0.20")
    max_expected_edge_pct: Decimal = Decimal("5.00")
    allowed_chains: tuple[str, ...] = ("base", "arbitrum", "polygon", "ethereum")
    live_trading_enabled: bool = False


@dataclass(frozen=True)
class RiskAssessment:
    strategy_name: str
    chain: str
    pair: str
    ai_score: int
    expected_edge_pct: Decimal | None
    recommendation: str
    decision: RiskDecision
    max_allowed_notional_usd: Decimal
    reason: str
