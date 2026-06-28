from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class PositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class Holding:
    chain: str
    symbol: str
    quantity: Decimal
    avg_cost_usd: Decimal
    current_price_usd: Decimal
    market_value_usd: Decimal
    unrealized_pnl_usd: Decimal
    unrealized_pnl_pct: Decimal


@dataclass(frozen=True)
class Position:
    position_id: str
    strategy_name: str
    chain: str
    pair: str
    base_symbol: str
    quote_symbol: str
    quantity: Decimal
    entry_price_usd: Decimal
    current_price_usd: Decimal
    notional_usd: Decimal
    unrealized_pnl_usd: Decimal
    unrealized_pnl_pct: Decimal
    status: PositionStatus
    opened_at: str


@dataclass(frozen=True)
class PortfolioSnapshot:
    portfolio_name: str
    cash_usd: Decimal
    holdings_value_usd: Decimal
    open_positions_value_usd: Decimal
    total_value_usd: Decimal
    realized_pnl_usd: Decimal
    unrealized_pnl_usd: Decimal
    total_pnl_usd: Decimal
    open_positions: int
    closed_positions: int
    holdings: list[Holding]
    positions: list[Position]
