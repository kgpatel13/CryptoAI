from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class PaperOrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class PaperOrderStatus(str, Enum):
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    SKIPPED = "SKIPPED"
    RISK_REJECTED = "RISK_REJECTED"


@dataclass(frozen=True)
class PaperOrder:
    order_id: str
    timestamp: str
    strategy_name: str
    chain: str
    pair: str
    side: PaperOrderSide
    notional_usd: Decimal
    estimated_edge_pct: Decimal | None
    simulated_fill_price_usd: Decimal | None
    simulated_quantity: Decimal | None
    status: PaperOrderStatus
    reason: str


@dataclass(frozen=True)
class PaperExecutionBatch:
    timestamp: str
    total_candidates: int
    filled_orders: int
    rejected_orders: int
    skipped_orders: int
    total_notional_usd: Decimal
    orders: list[PaperOrder]
