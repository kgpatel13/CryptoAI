from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from app.backtesting.models import BacktestResult, BacktestTrade, utc_now_iso

try:
    from app.strategy.strategy_service import StrategyService
except Exception:
    StrategyService = None


class BacktestService:
    """First version of the read-only backtesting engine.

    v1.1 supports:
    - replay from saved multi-DEX opportunity history
    - replay from saved scan history if available
    - fallback synthetic backtest from live strategy signals

    This is intentionally conservative. It does not claim real profitability.
    """

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.report_dir.mkdir(exist_ok=True)
        self.scan_file = self.data_dir / "scan_history.jsonl"
        self.multi_dex_file = self.data_dir / "multi_dex_opportunities.jsonl"
        self.report_json = self.report_dir / "backtest_report.json"
        self.report_md = self.report_dir / "backtest_report.md"

    def run_default_backtest(self, notional_usd: Decimal = Decimal("1000"), include_synthetic: bool = False) -> BacktestResult:
        started = utc_now_iso()
        multi_dex_rows = self._read_jsonl(self.multi_dex_file)

        if multi_dex_rows:
            result = self._backtest_multi_dex_history(self._dedupe_opportunity_rows(multi_dex_rows), notional_usd, started, include_synthetic)
        else:
            rows = self._read_jsonl(self.scan_file)
            if rows:
                result = self._backtest_scan_history(rows, notional_usd, started)
            else:
                result = self._backtest_live_strategy_snapshot(notional_usd, started)

        self._write_reports(result)
        return result

    def _backtest_multi_dex_history(
        self,
        rows: list[dict],
        notional_usd: Decimal,
        started: str,
        include_synthetic: bool,
    ) -> BacktestResult:
        trades: list[BacktestTrade] = []
        considered = []
        for row in rows[-1000:]:
            mode = str(row.get("mode", "REAL"))
            if mode != "REAL" and not include_synthetic:
                continue
            considered.append(row)
            if str(row.get("decision")) != "BUY":
                continue
            net_edge = self._to_decimal(row.get("net_edge_pct"))
            gross_edge = self._to_decimal(row.get("gross_edge_pct"))
            cost = self._to_decimal(row.get("cost_buffer_pct")) or Decimal("0")
            if net_edge is None or gross_edge is None or net_edge <= 0:
                continue
            profit = (notional_usd * net_edge / Decimal("100")).quantize(Decimal("0.0001"))
            trades.append(
                BacktestTrade(
                    timestamp=str(row.get("timestamp") or "-"),
                    strategy_name="Multi-DEX Opportunity Replay",
                    chain=str(row.get("chain", "base")),
                    pair=str(row.get("pair", "-")),
                    action="SIMULATED_TRADE",
                    mode=mode,
                    buy_source=str(row.get("buy_dex", "-")),
                    sell_source=str(row.get("sell_dex", "-")),
                    notional_usd=notional_usd,
                    gross_edge_pct=gross_edge,
                    cost_pct=cost,
                    estimated_edge_pct=net_edge,
                    simulated_profit_usd=profit,
                    reason="Recorded opportunity had BUY decision and positive net edge.",
                )
            )

        notes = "Replay used multi_dex_opportunities.jsonl. Synthetic paper opportunities were excluded."
        if include_synthetic:
            notes = "Replay used multi_dex_opportunities.jsonl. Synthetic paper opportunities were included by explicit request."
        return self._build_result(
            strategy_name="Multi-DEX Opportunity Replay",
            started=started,
            trades=trades,
            total_signals=len(considered),
            source_file=str(self.multi_dex_file),
            notes=notes,
        )

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

            profit = (notional_usd * (net_edge / Decimal("100"))).quantize(Decimal("0.0001"))

            trades.append(
                BacktestTrade(
                    timestamp=str(row.get("timestamp") or row.get("created_at") or "-"),
                    strategy_name="Historical Gross Arbitrage Replay",
                    chain=str(row.get("chain", "base")),
                    pair=str(row.get("pair", "-")),
                    action="SIMULATED_TRADE",
                    mode="REAL",
                    buy_source=str(row.get("buy_dex") or row.get("source_buy") or "-"),
                    sell_source=str(row.get("sell_dex") or row.get("source_sell") or "-"),
                    notional_usd=notional_usd,
                    gross_edge_pct=spread,
                    cost_pct=estimated_cost_pct,
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
            source_file=str(self.scan_file),
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
                source_file="StrategyService",
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
                source_file="StrategyService",
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

            profit = (notional_usd * (net_edge / Decimal("100"))).quantize(Decimal("0.0001"))

            trades.append(
                BacktestTrade(
                    timestamp=utc_now_iso(),
                    strategy_name=str(getattr(signal, "strategy_name", "Strategy")),
                    chain=str(getattr(signal, "chain", "base")),
                    pair=str(getattr(signal, "pair", "-")),
                    action="SIMULATED_TRADE",
                    mode="REAL",
                    buy_source="-",
                    sell_source="-",
                    notional_usd=notional_usd,
                    gross_edge_pct=edge,
                    cost_pct=estimated_cost_pct,
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
            source_file="StrategyService",
            notes=(
                "No saved replay history found. Used current live strategy snapshot. "
                "This is a framework test, not a real historical backtest."
            ),
        )

    def _build_result(
        self,
        strategy_name: str,
        started: str,
        trades: list[BacktestTrade],
        total_signals: int,
        source_file: str,
        notes: str,
    ) -> BacktestResult:
        winning = sum(1 for t in trades if t.simulated_profit_usd > 0)
        losing = sum(1 for t in trades if t.simulated_profit_usd < 0)
        breakeven = sum(1 for t in trades if t.simulated_profit_usd == 0)
        total_profit = sum((t.simulated_profit_usd for t in trades), Decimal("0")).quantize(Decimal("0.0001"))
        avg_profit = (total_profit / Decimal(len(trades))).quantize(Decimal("0.0001")) if trades else Decimal("0.0000")
        avg_edge = (sum((t.estimated_edge_pct for t in trades), Decimal("0")) / Decimal(len(trades))).quantize(Decimal("0.0001")) if trades else Decimal("0.0000")
        win_rate = (Decimal(winning) / Decimal(len(trades)) * Decimal("100")).quantize(Decimal("0.0001")) if trades else Decimal("0.0000")

        running = Decimal("0")
        peak = Decimal("0")
        max_drawdown = Decimal("0")
        for trade in trades:
            running += trade.simulated_profit_usd
            peak = max(peak, running)
            max_drawdown = max(max_drawdown, peak - running)

        return BacktestResult(
            strategy_name=strategy_name,
            started_at=started,
            completed_at=utc_now_iso(),
            total_signals=total_signals,
            simulated_trades=len(trades),
            skipped_signals=max(0, total_signals - len(trades)),
            winning_trades=winning,
            losing_trades=losing,
            breakeven_trades=breakeven,
            total_simulated_profit_usd=total_profit,
            average_profit_usd=avg_profit,
            average_net_edge_pct=avg_edge,
            max_drawdown_usd=max_drawdown.quantize(Decimal("0.0001")),
            win_rate_pct=win_rate,
            source_file=source_file,
            notes=notes,
            trades=trades,
        )

    def _write_reports(self, result: BacktestResult) -> None:
        payload = self._serialize_result(result)
        self.report_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.report_md.write_text(self._markdown(result), encoding="utf-8")

    def _markdown(self, result: BacktestResult) -> str:
        lines = [
            "# CryptoAI Backtest Report",
            "",
            f"Generated: `{result.completed_at}`",
            "",
            "## Summary",
            "",
            f"- Strategy: `{result.strategy_name}`",
            f"- Source: `{result.source_file}`",
            f"- Total signals: `{result.total_signals}`",
            f"- Simulated trades: `{result.simulated_trades}`",
            f"- Skipped signals: `{result.skipped_signals}`",
            f"- Total simulated PnL: `{result.total_simulated_profit_usd}`",
            f"- Average net edge %: `{result.average_net_edge_pct}`",
            f"- Win rate %: `{result.win_rate_pct}`",
            f"- Max drawdown: `{result.max_drawdown_usd}`",
            "",
            "## Trades",
            "",
            "| Time | Mode | Pair | Buy | Sell | Net % | PnL | Reason |",
            "|---|---|---|---|---|---:|---:|---|",
        ]
        for trade in result.trades[-50:]:
            lines.append(
                f"| {trade.timestamp} | {trade.mode} | {trade.pair} | {trade.buy_source} | {trade.sell_source} | "
                f"{trade.estimated_edge_pct} | {trade.simulated_profit_usd} | {trade.reason.replace('|', '/')} |"
            )
        if not result.trades:
            lines.append("| - | - | - | - | - | - | - | No simulated trades met the replay threshold. |")
        lines += ["", "## Notes", "", f"- {result.notes}", "- Backtests are research evidence only and are not live-trading approval."]
        return "\n".join(lines) + "\n"

    @staticmethod
    def _serialize_result(result: BacktestResult) -> dict:
        payload = {
            "generated_at": result.completed_at,
            "strategy_name": result.strategy_name,
            "started_at": result.started_at,
            "completed_at": result.completed_at,
            "total_signals": result.total_signals,
            "simulated_trades": result.simulated_trades,
            "skipped_signals": result.skipped_signals,
            "winning_trades": result.winning_trades,
            "losing_trades": result.losing_trades,
            "breakeven_trades": result.breakeven_trades,
            "total_simulated_profit_usd": str(result.total_simulated_profit_usd),
            "average_profit_usd": str(result.average_profit_usd),
            "average_net_edge_pct": str(result.average_net_edge_pct),
            "max_drawdown_usd": str(result.max_drawdown_usd),
            "win_rate_pct": str(result.win_rate_pct),
            "source_file": result.source_file,
            "notes": result.notes,
            "trades": [],
        }
        for trade in result.trades:
            payload["trades"].append(
                {
                    "timestamp": trade.timestamp,
                    "strategy_name": trade.strategy_name,
                    "chain": trade.chain,
                    "pair": trade.pair,
                    "action": trade.action,
                    "mode": trade.mode,
                    "buy_source": trade.buy_source,
                    "sell_source": trade.sell_source,
                    "notional_usd": str(trade.notional_usd),
                    "gross_edge_pct": str(trade.gross_edge_pct),
                    "cost_pct": str(trade.cost_pct),
                    "estimated_edge_pct": str(trade.estimated_edge_pct),
                    "simulated_profit_usd": str(trade.simulated_profit_usd),
                    "reason": trade.reason,
                }
            )
        return payload

    def _read_jsonl(self, path: Path) -> list[dict]:
        if not path.exists():
            return []

        rows: list[dict] = []
        try:
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
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
    def _dedupe_opportunity_rows(rows: list[dict]) -> list[dict]:
        seen = set()
        deduped = []
        for row in rows:
            key = (
                row.get("timestamp"),
                row.get("mode"),
                row.get("chain"),
                row.get("pair"),
                row.get("buy_dex"),
                row.get("sell_dex"),
                row.get("gross_edge_pct"),
                row.get("cost_buffer_pct"),
                row.get("net_edge_pct"),
                row.get("decision"),
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(row)
        return deduped

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

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


def main() -> None:
    result = BacktestService().run_default_backtest()
    print(json.dumps(BacktestService._serialize_result(result), indent=2))


if __name__ == "__main__":
    main()
