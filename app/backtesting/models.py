from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal


@dataclass(frozen=True)
class BacktestTrade:
    timestamp: str
    strategy_name: str
    chain: str
    pair: str
    action: str
    mode: str
    buy_source: str
    sell_source: str
    notional_usd: Decimal
    gross_edge_pct: Decimal
    cost_pct: Decimal
    estimated_edge_pct: Decimal
    simulated_profit_usd: Decimal
    reason: str


@dataclass(frozen=True)
class BacktestResult:
    strategy_name: str
    started_at: str
    completed_at: str
    total_signals: int
    simulated_trades: int
    skipped_signals: int
    winning_trades: int
    losing_trades: int
    breakeven_trades: int
    total_simulated_profit_usd: Decimal
    average_profit_usd: Decimal
    average_net_edge_pct: Decimal
    max_drawdown_usd: Decimal
    win_rate_pct: Decimal
    source_file: str
    notes: str
    trades: list[BacktestTrade]


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
