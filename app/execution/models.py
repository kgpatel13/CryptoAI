from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


class PaperOrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class PaperOrderStatus(str, Enum):
    NEW = "NEW"
    VALIDATED = "VALIDATED"
    SUBMITTED = "SUBMITTED"
    PENDING = "PENDING"
    PARTIAL_FILL = "PARTIAL_FILL"
    FILLED = "FILLED"
    EXIT_REQUESTED = "EXIT_REQUESTED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
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
    execution_type: str = "POSITION"
    buy_source: str | None = None
    sell_source: str | None = None
    buy_price_usd: Decimal | None = None
    sell_price_usd: Decimal | None = None
    gross_edge_pct: Decimal | None = None
    cost_buffer_pct: Decimal | None = None
    net_edge_pct: Decimal | None = None
    realized_pnl_usd: Decimal | None = None
    exit_value_usd: Decimal | None = None
    requested_notional_usd: Decimal | None = None
    filled_notional_usd: Decimal | None = None
    slippage_bps: Decimal | None = None
    latency_ms: int | None = None
    execution_quality: str | None = None
    lifecycle_events: list[dict] = field(default_factory=list)


@dataclass(frozen=True)
class PaperExecutionBatch:
    timestamp: str
    total_candidates: int
    filled_orders: int
    rejected_orders: int
    skipped_orders: int
    total_notional_usd: Decimal
    orders: list[PaperOrder]
    monitored_positions: int = 0
    closed_positions: int = 0
