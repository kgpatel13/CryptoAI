from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class OpportunityType(str, Enum):
    DEX_ARBITRAGE = "DEX_ARBITRAGE"
    CEX_DEX_ARBITRAGE = "CEX_DEX_ARBITRAGE"
    CROSS_CHAIN_ARBITRAGE = "CROSS_CHAIN_ARBITRAGE"
    TREND = "TREND"
    UNKNOWN = "UNKNOWN"


class OpportunityStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    WATCH = "WATCH"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class OpportunityCandidate:
    opportunity_id: str
    opportunity_type: OpportunityType
    chain: str
    pair: str
    source_buy: str
    source_sell: str
    buy_price: Decimal | None
    sell_price: Decimal | None
    gross_spread_pct: Decimal | None
    estimated_cost_pct: Decimal
    estimated_net_edge_pct: Decimal | None
    latency_sensitivity: str
    liquidity_status: str
    status: OpportunityStatus
    reason: str
