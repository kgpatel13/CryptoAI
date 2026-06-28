from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class BacktestTrade:
    timestamp: str
    strategy_name: str
    chain: str
    pair: str
    action: str
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
    winning_trades: int
    losing_trades: int
    total_simulated_profit_usd: Decimal
    win_rate_pct: Decimal
    notes: str
    trades: list[BacktestTrade]


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"
