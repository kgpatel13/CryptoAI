from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class TradeDecision(str, Enum):
    BUY = "BUY"
    WATCH = "WATCH"
    SKIP = "SKIP"


@dataclass(frozen=True)
class OpportunityDecision:
    opportunity_id: str
    chain: str
    pair: str
    buy_source: str
    sell_source: str
    buy_price: Decimal | None
    sell_price: Decimal | None
    gross_spread_pct: Decimal | None
    gas_buffer_pct: Decimal
    fee_slippage_buffer_pct: Decimal
    total_cost_buffer_pct: Decimal
    estimated_net_edge_pct: Decimal | None
    readiness_score: int
    decision: TradeDecision
    reason: str
