from __future__ import annotations

import json
from pathlib import Path
from decimal import Decimal

from app.backtesting.models import BacktestResult, BacktestTrade, utc_now_iso

try:
    from app.strategy.strategy_service import StrategyService
except Exception:
    StrategyService = None


class BacktestService:
    """First version of the read-only backtesting engine.

    v1.1 supports:
    - replay from saved scan history if available
    - fallback synthetic backtest from live strategy signals

    This is intentionally conservative. It does not claim real profitability.
    """

    def __init__(self) -> None:
        self.data_dir = Path("data")
        self.scan_file = self.data_dir / "scan_history.jsonl"

    def run_default_backtest(self, notional_usd: Decimal = Decimal("1000")) -> BacktestResult:
        started = utc_now_iso()
        rows = self._read_scan_history()

        if rows:
            result = self._backtest_scan_history(rows, notional_usd, started)
        else:
            result = self._backtest_live_strategy_snapshot(notional_usd, started)

        return result

    def _backtest_scan_history(
        self,
        rows: list[dict],
        notional_usd: Decimal,
        started: str,
    ) -> BacktestResult:
        trades: list[BacktestTrade] = []

        for row in rows[-500:]:
            spread = self._extract_spread(row)
            if spread is None:
                continue

            # Conservative rough cost model until full execution simulator exists.
            estimated_cost_pct = Decimal("0.20")
            net_edge = spread - estimated_cost_pct

            if net_edge <= 0:
                continue

            profit = notional_usd * (net_edge / Decimal("100"))

            trades.append(
                BacktestTrade(
                    timestamp=str(row.get("timestamp") or row.get("created_at") or "-"),
                    strategy_name="Historical Gross Arbitrage Replay",
                    chain=str(row.get("chain", "base")),
                    pair=str(row.get("pair", "-")),
                    action="SIMULATED_TRADE",
                    estimated_edge_pct=net_edge,
                    simulated_profit_usd=profit,
                    reason="Historical scan spread exceeded rough cost model.",
                )
            )

        return self._build_result(
            strategy_name="Historical Gross Arbitrage Replay",
            started=started,
            trades=trades,
            total_signals=len(rows),
            notes="Replay used saved scan_history.jsonl with a rough 0.20% cost model.",
        )

    def _backtest_live_strategy_snapshot(
        self,
        notional_usd: Decimal,
        started: str,
    ) -> BacktestResult:
        trades: list[BacktestTrade] = []
        total_signals = 0

        if StrategyService is None:
            return self._build_result(
                strategy_name="Live Strategy Snapshot",
                started=started,
                trades=[],
                total_signals=0,
                notes="StrategyService not available.",
            )

        try:
            signals = StrategyService().get_all_signals()
        except Exception as exc:
            return self._build_result(
                strategy_name="Live Strategy Snapshot",
                started=started,
                trades=[],
                total_signals=0,
                notes=f"StrategyService failed: {exc}",
            )

        total_signals = len(signals)

        for signal in signals:
            edge = getattr(signal, "expected_edge_pct", None)
            action = getattr(signal, "action", "")

            if edge is None:
                continue

            edge = Decimal(str(edge))
            action_value = action.value if hasattr(action, "value") else str(action)

            if action_value != "READY_FOR_PAPER":
                continue

            estimated_cost_pct = Decimal("0.20")
            net_edge = edge - estimated_cost_pct

            if net_edge <= 0:
                continue

            profit = notional_usd * (net_edge / Decimal("100"))

            trades.append(
                BacktestTrade(
                    timestamp=utc_now_iso(),
                    strategy_name=str(getattr(signal, "strategy_name", "Strategy")),
                    chain=str(getattr(signal, "chain", "base")),
                    pair=str(getattr(signal, "pair", "-")),
                    action="SIMULATED_TRADE",
                    estimated_edge_pct=net_edge,
                    simulated_profit_usd=profit,
                    reason="Live strategy signal was READY_FOR_PAPER and passed rough cost model.",
                )
            )

        return self._build_result(
            strategy_name="Live Strategy Snapshot",
            started=started,
            trades=trades,
            total_signals=total_signals,
            notes=(
                "No saved scan history found. Used current live strategy snapshot. "
                "This is a framework test, not a real historical backtest."
            ),
        )

    def _build_result(
        self,
        strategy_name: str,
        started: str,
        trades: list[BacktestTrade],
        total_signals: int,
        notes: str,
    ) -> BacktestResult:
        winning = sum(1 for t in trades if t.simulated_profit_usd > 0)
        losing = sum(1 for t in trades if t.simulated_profit_usd < 0)
        total_profit = sum((t.simulated_profit_usd for t in trades), Decimal("0"))
        win_rate = Decimal(winning) / Decimal(len(trades)) * Decimal("100") if trades else Decimal("0")

        return BacktestResult(
            strategy_name=strategy_name,
            started_at=started,
            completed_at=utc_now_iso(),
            total_signals=total_signals,
            simulated_trades=len(trades),
            winning_trades=winning,
            losing_trades=losing,
            total_simulated_profit_usd=total_profit,
            win_rate_pct=win_rate,
            notes=notes,
            trades=trades,
        )

    def _read_scan_history(self) -> list[dict]:
        if not self.scan_file.exists():
            return []

        rows: list[dict] = []
        try:
            for line in self.scan_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        except Exception:
            return []

        return rows

    @staticmethod
    def _extract_spread(row: dict) -> Decimal | None:
        candidates = [
            "gross_spread_pct",
            "Gross Spread %",
            "spread_pct",
            "edge_pct",
        ]

        for key in candidates:
            if key in row:
                try:
                    return Decimal(str(row[key]))
                except Exception:
                    return None

        return None
