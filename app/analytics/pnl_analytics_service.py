from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TradeJournalEntry:
    order_id: str
    timestamp: str
    date: str
    pair: str
    side: str
    status: str
    notional_usd: Decimal
    realized_pnl_usd: Decimal
    slippage_bps: Decimal | None
    latency_ms: Decimal | None
    execution_quality: str
    reason: str
    buy_source: str = "-"
    sell_source: str = "-"
    gross_edge_pct: Decimal | None = None
    cost_buffer_pct: Decimal | None = None
    net_edge_pct: Decimal | None = None

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        for key, value in list(row.items()):
            if isinstance(value, Decimal):
                row[key] = str(value)
        return row


class PnLAnalyticsService:
    """Portfolio analytics for paper-trading output.

    The service is intentionally ledger/report driven. It reads the same runtime
    files used by the dashboard and report generator, so it can run locally,
    in GitHub Actions, or from the Streamlit dashboard without needing live
    providers.
    """

    def __init__(self, data_dir: str | Path = "data", report_dir: str | Path = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.paper_orders_file = self.data_dir / "paper_orders.jsonl"
        self.portfolio_state_file = self.data_dir / "paper_portfolio_state.json"
        self.analytics_json_file = self.report_dir / "portfolio_analytics.json"
        self.analytics_md_file = self.report_dir / "portfolio_analytics.md"
        self.report_dir.mkdir(exist_ok=True)

    def generate(self) -> dict[str, Any]:
        orders = self._read_jsonl(self.paper_orders_file)
        state = self._read_json(self.portfolio_state_file)
        journal = self.build_trade_journal(orders, state)
        analytics = self.compute_analytics(journal, state)
        self._write_json(analytics)
        self._write_markdown(analytics)
        return analytics

    def build_trade_journal(self, orders: list[dict[str, Any]], state: dict[str, Any]) -> list[TradeJournalEntry]:
        position_pnl_by_pair = self._closed_position_pnl_by_pair(state)
        journal: list[TradeJournalEntry] = []

        for order in orders:
            status = str(order.get("status", "UNKNOWN")).upper()
            if status not in {"FILLED", "PARTIAL_FILL", "CLOSED"}:
                continue

            timestamp = str(order.get("timestamp") or "")
            pair = str(order.get("pair") or "-")
            notional = self._decimal(order.get("filled_notional_usd", order.get("notional_usd", "0")))
            if notional <= 0:
                notional = self._decimal(order.get("notional_usd", "0"))

            # Prefer explicit order-level realized PnL. If absent, allocate known
            # closed-position PnL to the first matching filled row so historical
            # files from earlier releases remain analyzable.
            pnl = self._decimal(order.get("realized_pnl_usd", "0"))
            if pnl == 0 and pair in position_pnl_by_pair and position_pnl_by_pair[pair]:
                pnl = position_pnl_by_pair[pair].pop(0)

            journal.append(
                TradeJournalEntry(
                    order_id=str(order.get("order_id", "-")),
                    timestamp=timestamp,
                    date=self._date_key(timestamp),
                    pair=pair,
                    side=str(order.get("side", "-")),
                    status=status,
                    notional_usd=self._q(notional),
                    realized_pnl_usd=self._q(pnl),
                    slippage_bps=self._optional_decimal(order.get("slippage_bps")),
                    latency_ms=self._optional_decimal(order.get("latency_ms")),
                    execution_quality=str(order.get("execution_quality") or "UNKNOWN"),
                    reason=str(order.get("reason", "")),
                    buy_source=str(order.get("buy_source") or "-"),
                    sell_source=str(order.get("sell_source") or "-"),
                    gross_edge_pct=self._optional_decimal(order.get("gross_edge_pct")),
                    cost_buffer_pct=self._optional_decimal(order.get("cost_buffer_pct")),
                    net_edge_pct=self._optional_decimal(order.get("net_edge_pct")),
                )
            )

        return journal

    def compute_analytics(self, journal: list[TradeJournalEntry], state: dict[str, Any]) -> dict[str, Any]:
        initial_cash = self._decimal(state.get("initial_cash_usd", "10000"))
        cash = self._decimal(state.get("cash_usd", initial_cash))
        realized = self._decimal(state.get("realized_pnl_usd", state.get("daily_realized_pnl_usd", "0")))
        unrealized = self._unrealized_from_state(state)
        open_notional = self._open_notional_from_state(state)
        equity = self._q(cash + open_notional + unrealized)
        total_pnl = self._q(realized + unrealized)
        total_return_pct = self._pct(total_pnl, initial_cash)
        journal_realized = self._q(sum((t.realized_pnl_usd for t in journal), Decimal("0")))
        pnl_reconciliation = self._pnl_reconciliation(
            portfolio_realized_pnl=realized,
            journal_realized_pnl=journal_realized,
            state=state,
            journal_count=len(journal),
        )

        closed_or_pnl_trades = [t for t in journal if t.realized_pnl_usd != 0]
        wins = [t for t in closed_or_pnl_trades if t.realized_pnl_usd > 0]
        losses = [t for t in closed_or_pnl_trades if t.realized_pnl_usd < 0]
        breakeven = [t for t in journal if t.realized_pnl_usd == 0]

        gross_profit = sum((t.realized_pnl_usd for t in wins), Decimal("0"))
        gross_loss = sum((abs(t.realized_pnl_usd) for t in losses), Decimal("0"))
        journal_gross_profit = gross_profit
        journal_gross_loss = gross_loss
        if pnl_reconciliation["status"] != "RECONCILED":
            gross_profit = realized if realized > 0 else Decimal("0")
            gross_loss = abs(realized) if realized < 0 else Decimal("0")
            expectancy_count = int(state.get("daily_filled_trades", len(closed_or_pnl_trades)) or 0)
            expectancy = realized / Decimal(expectancy_count) if expectancy_count > 0 else Decimal("0")
        else:
            expectancy = (sum((t.realized_pnl_usd for t in closed_or_pnl_trades), Decimal("0")) / Decimal(len(closed_or_pnl_trades))) if closed_or_pnl_trades else Decimal("0")
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else None

        if pnl_reconciliation["status"] == "RECONCILED":
            daily = self._daily_pnl(journal, initial_cash)
            by_pair = self._by_pair(journal)
        else:
            daily = self._daily_pnl_from_state(state, journal, initial_cash)
            by_pair = self._by_pair_allocated_to_portfolio_state(journal, realized)
        equity_curve = self._equity_curve(daily, initial_cash)
        max_drawdown = self._max_drawdown(equity_curve)

        return {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "initial_cash_usd": str(self._q(initial_cash)),
            "cash_usd": str(self._q(cash)),
            "open_position_notional_usd": str(self._q(open_notional)),
            "equity_usd": str(equity),
            "realized_pnl_usd": str(self._q(realized)),
            "journal_realized_pnl_usd": str(journal_realized),
            "unrealized_pnl_usd": str(self._q(unrealized)),
            "total_pnl_usd": str(total_pnl),
            "total_return_pct": str(total_return_pct),
            "pnl_reconciliation": pnl_reconciliation,
            "trade_count": len(journal),
            "closed_trade_count": len([t for t in journal if t.status == "CLOSED"]),
            "open_positions": len([p for p in state.get("positions", []) if str(p.get("status", "OPEN")).upper() == "OPEN"]),
            "closed_positions": len([p for p in state.get("positions", []) if str(p.get("status", "")).upper() == "CLOSED"]),
            "win_count": len(wins),
            "loss_count": len(losses),
            "breakeven_or_open_trade_count": len(breakeven),
            "win_rate_pct": str(self._pct(Decimal(len(wins)), Decimal(len(closed_or_pnl_trades))) if closed_or_pnl_trades else Decimal("0.0000")),
            "gross_profit_usd": str(self._q(gross_profit)),
            "gross_loss_usd": str(self._q(gross_loss)),
            "journal_gross_profit_usd": str(self._q(journal_gross_profit)),
            "journal_gross_loss_usd": str(self._q(journal_gross_loss)),
            "profit_factor": str(self._q(profit_factor)) if profit_factor is not None else "N/A",
            "expectancy_usd": str(self._q(expectancy)),
            "max_drawdown_usd": str(self._q(max_drawdown["drawdown_usd"])),
            "max_drawdown_pct": str(max_drawdown["drawdown_pct"]),
            "avg_slippage_bps": self._avg_optional(journal, "slippage_bps"),
            "avg_latency_ms": self._avg_optional(journal, "latency_ms"),
            "daily_pnl": daily,
            "equity_curve": equity_curve,
            "performance_by_pair": by_pair,
            "trade_journal": [t.to_dict() for t in journal[-100:]],
            "notes": [
                "Paper analytics are for simulated trading only.",
                "Cash, equity, total PnL, Daily PnL, and the equity curve are reconciled to paper_portfolio_state.json.",
                "The recent trade journal is execution evidence from paper_orders.jsonl and can include rows from earlier paper sessions.",
                "Closed-trade metrics are meaningful after positions have entry and exit records.",
                "Live trading remains disabled unless explicitly enabled elsewhere and gated by live safety checks.",
            ],
        }

    def _daily_pnl(self, journal: list[TradeJournalEntry], initial_cash: Decimal) -> list[dict[str, str]]:
        buckets: dict[str, dict[str, Decimal]] = defaultdict(lambda: {"realized": Decimal("0"), "notional": Decimal("0"), "trades": Decimal("0")})
        for trade in journal:
            bucket = buckets[trade.date]
            bucket["realized"] += trade.realized_pnl_usd
            bucket["notional"] += trade.notional_usd
            bucket["trades"] += Decimal("1")

        rows = []
        cumulative = Decimal("0")
        for date in sorted(buckets):
            realized = buckets[date]["realized"]
            cumulative += realized
            rows.append(
                {
                    "date": date,
                    "trades": str(int(buckets[date]["trades"])),
                    "filled_notional_usd": str(self._q(buckets[date]["notional"])),
                    "realized_pnl_usd": str(self._q(realized)),
                    "cumulative_realized_pnl_usd": str(self._q(cumulative)),
                    "daily_return_pct": str(self._pct(realized, initial_cash)),
                }
            )
        return rows

    def _daily_pnl_from_state(
        self,
        state: dict[str, Any],
        journal: list[TradeJournalEntry],
        initial_cash: Decimal,
    ) -> list[dict[str, str]]:
        date = str(state.get("daily_date") or state.get("updated_at") or self._utc_now())[:10]
        realized = self._q(self._decimal(state.get("daily_realized_pnl_usd", state.get("realized_pnl_usd", "0"))))
        trades = int(state.get("daily_filled_trades", len(journal) if journal else 0) or 0)
        return [
            {
                "date": date,
                "trades": str(trades),
                "filled_notional_usd": str(self._q(self._state_day_notional(journal, date))),
                "realized_pnl_usd": str(realized),
                "cumulative_realized_pnl_usd": str(realized),
                "daily_return_pct": str(self._pct(realized, initial_cash)),
                "pnl_basis": "paper_portfolio_state",
            }
        ]

    def _equity_curve(self, daily_rows: list[dict[str, str]], initial_cash: Decimal) -> list[dict[str, str]]:
        rows = []
        equity = initial_cash
        for row in daily_rows:
            equity += self._decimal(row.get("realized_pnl_usd", "0"))
            rows.append(
                {
                    "date": row["date"],
                    "equity_usd": str(self._q(equity)),
                    "return_from_start_pct": str(self._pct(equity - initial_cash, initial_cash)),
                }
            )
        return rows

    def _max_drawdown(self, equity_curve: list[dict[str, str]]) -> dict[str, Decimal]:
        peak: Decimal | None = None
        max_dd = Decimal("0")
        max_dd_pct = Decimal("0")
        for row in equity_curve:
            equity = self._decimal(row.get("equity_usd", "0"))
            if peak is None or equity > peak:
                peak = equity
            if peak and peak > 0:
                dd = peak - equity
                dd_pct = dd / peak * Decimal("100")
                if dd > max_dd:
                    max_dd = dd
                    max_dd_pct = dd_pct
        return {"drawdown_usd": max_dd, "drawdown_pct": self._q(max_dd_pct)}

    def _by_pair(self, journal: list[TradeJournalEntry]) -> list[dict[str, str]]:
        buckets: dict[str, dict[str, Decimal]] = defaultdict(lambda: {"trades": Decimal("0"), "notional": Decimal("0"), "pnl": Decimal("0"), "wins": Decimal("0"), "losses": Decimal("0")})
        for trade in journal:
            pair = trade.pair
            buckets[pair]["trades"] += Decimal("1")
            buckets[pair]["notional"] += trade.notional_usd
            buckets[pair]["pnl"] += trade.realized_pnl_usd
            if trade.realized_pnl_usd > 0:
                buckets[pair]["wins"] += Decimal("1")
            if trade.realized_pnl_usd < 0:
                buckets[pair]["losses"] += Decimal("1")

        rows = []
        for pair, bucket in sorted(buckets.items()):
            rows.append(
                {
                    "pair": pair,
                    "trades": str(int(bucket["trades"])),
                    "filled_notional_usd": str(self._q(bucket["notional"])),
                    "realized_pnl_usd": str(self._q(bucket["pnl"])),
                    "win_rate_pct": str(self._pct(bucket["wins"], bucket["wins"] + bucket["losses"]) if (bucket["wins"] + bucket["losses"]) > 0 else Decimal("0.0000")),
                }
            )
        return rows

    def _by_pair_allocated_to_portfolio_state(
        self,
        journal: list[TradeJournalEntry],
        portfolio_realized_pnl: Decimal,
    ) -> list[dict[str, str]]:
        raw_rows = self._by_pair(journal)
        total_positive_pnl = sum(
            (self._decimal(row.get("realized_pnl_usd", "0")) for row in raw_rows if self._decimal(row.get("realized_pnl_usd", "0")) > 0),
            Decimal("0"),
        )
        if not raw_rows:
            return []
        if total_positive_pnl <= 0:
            pair = raw_rows[0]["pair"]
            return [
                {
                    "pair": pair,
                    "trades": raw_rows[0]["trades"],
                    "filled_notional_usd": raw_rows[0]["filled_notional_usd"],
                    "realized_pnl_usd": str(self._q(portfolio_realized_pnl)),
                    "win_rate_pct": raw_rows[0]["win_rate_pct"],
                    "pnl_basis": "paper_portfolio_state",
                }
            ]
        allocated = []
        remaining = self._q(portfolio_realized_pnl)
        positive_rows = [row for row in raw_rows if self._decimal(row.get("realized_pnl_usd", "0")) > 0]
        for row in raw_rows:
            pnl = self._decimal(row.get("realized_pnl_usd", "0"))
            if pnl <= 0:
                allocated_pnl = Decimal("0.0000")
            elif row is positive_rows[-1]:
                allocated_pnl = remaining
            else:
                allocated_pnl = self._q(portfolio_realized_pnl * pnl / total_positive_pnl)
                remaining -= allocated_pnl
            allocated.append(
                {
                    **row,
                    "realized_pnl_usd": str(self._q(allocated_pnl)),
                    "pnl_basis": "allocated_to_paper_portfolio_state",
                }
            )
        return allocated

    def _state_day_notional(self, journal: list[TradeJournalEntry], date: str) -> Decimal:
        return sum((trade.notional_usd for trade in journal if trade.date == date), Decimal("0"))

    def _pnl_reconciliation(
        self,
        *,
        portfolio_realized_pnl: Decimal,
        journal_realized_pnl: Decimal,
        state: dict[str, Any],
        journal_count: int,
    ) -> dict[str, Any]:
        difference = self._q(journal_realized_pnl - portfolio_realized_pnl)
        if abs(difference) <= Decimal("0.0001"):
            status = "RECONCILED"
            reason = "The paper-order journal and active portfolio ledger agree."
        else:
            status = "ORDER_HISTORY_DIFFERS_FROM_PORTFOLIO_STATE"
            reason = (
                "Cash and total PnL use the active portfolio ledger. "
                "The paper-order journal is retained as historical execution evidence and can include rows from earlier paper sessions."
            )
        return {
            "source_of_truth": "paper_portfolio_state.json",
            "status": status,
            "portfolio_realized_pnl_usd": str(self._q(portfolio_realized_pnl)),
            "journal_realized_pnl_usd": str(journal_realized_pnl),
            "difference_usd": str(difference),
            "journal_trade_count": journal_count,
            "state_daily_filled_trades": state.get("daily_filled_trades", 0),
            "state_updated_at": state.get("updated_at"),
            "reason": reason,
        }

    def _closed_position_pnl_by_pair(self, state: dict[str, Any]) -> dict[str, list[Decimal]]:
        rows: dict[str, list[Decimal]] = defaultdict(list)
        for pos in state.get("positions", []):
            if str(pos.get("status", "")).upper() != "CLOSED":
                continue
            pnl = self._decimal(pos.get("realized_pnl_usd", pos.get("pnl_usd", "0")))
            if pnl == 0:
                notional = self._decimal(pos.get("notional_usd", "0"))
                exit_value = self._decimal(pos.get("exit_value_usd", "0"))
                if exit_value:
                    pnl = exit_value - notional
            rows[str(pos.get("pair", "-"))].append(self._q(pnl))
        return rows

    def _unrealized_from_state(self, state: dict[str, Any]) -> Decimal:
        if "unrealized_pnl_usd" in state:
            return self._decimal(state.get("unrealized_pnl_usd"))
        total = Decimal("0")
        for pos in state.get("positions", []):
            if str(pos.get("status", "OPEN")).upper() != "OPEN":
                continue
            qty = self._decimal(pos.get("quantity", "0"))
            cur = self._decimal(pos.get("current_price_usd", pos.get("entry_price_usd", "0")))
            notional = self._decimal(pos.get("notional_usd", "0"))
            total += (qty * cur) - notional
        return self._q(total)

    def _open_notional_from_state(self, state: dict[str, Any]) -> Decimal:
        total = Decimal("0")
        for pos in state.get("positions", []):
            if str(pos.get("status", "OPEN")).upper() == "OPEN":
                total += self._decimal(pos.get("notional_usd", "0"))
        return self._q(total)

    def _write_json(self, analytics: dict[str, Any]) -> None:
        self.analytics_json_file.write_text(json.dumps(analytics, indent=2), encoding="utf-8")

    def _write_markdown(self, analytics: dict[str, Any]) -> None:
        lines = [
            "# CryptoAI Portfolio Analytics Report",
            "",
            f"Generated: `{analytics['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Mode: `{analytics['mode']}`",
            f"- Initial cash USD: `${analytics['initial_cash_usd']}`",
            f"- Cash USD: `${analytics['cash_usd']}`",
            f"- Equity USD: `${analytics['equity_usd']}`",
            f"- Realized PnL USD: `${analytics['realized_pnl_usd']}`",
            f"- Unrealized PnL USD: `${analytics['unrealized_pnl_usd']}`",
            f"- Total PnL USD: `${analytics['total_pnl_usd']}`",
            f"- Total return %: `{analytics['total_return_pct']}`",
            f"- PnL reconciliation: `{analytics.get('pnl_reconciliation', {}).get('status', '-')}`",
            f"- Journal realized PnL USD: `${analytics.get('journal_realized_pnl_usd', '-')}`",
            f"- Trade count: `{analytics['trade_count']}`",
            f"- Closed/PnL trade count: `{analytics['closed_trade_count']}`",
            f"- Win rate %: `{analytics['win_rate_pct']}`",
            f"- Profit factor: `{analytics['profit_factor']}`",
            f"- Expectancy USD: `${analytics['expectancy_usd']}`",
            f"- Max drawdown USD: `${analytics['max_drawdown_usd']}`",
            f"- Max drawdown %: `{analytics['max_drawdown_pct']}`",
            f"- Avg slippage bps: `{analytics['avg_slippage_bps']}`",
            f"- Avg latency ms: `{analytics['avg_latency_ms']}`",
            "",
            "## Daily PnL",
            "",
        ]
        daily = analytics.get("daily_pnl", [])
        if daily:
            lines.append("| Date | Trades | Filled Notional | Realized PnL | Cumulative PnL | Daily Return % |")
            lines.append("|---|---:|---:|---:|---:|---:|")
            for row in daily:
                lines.append(f"| {row['date']} | {row['trades']} | {row['filled_notional_usd']} | {row['realized_pnl_usd']} | {row['cumulative_realized_pnl_usd']} | {row['daily_return_pct']} |")
        else:
            lines.append("No filled paper trades yet.")

        reconciliation = analytics.get("pnl_reconciliation", {})
        lines += ["", "## PnL Reconciliation", ""]
        if reconciliation:
            lines.append(f"- Source of truth: `{reconciliation.get('source_of_truth', '-')}`")
            lines.append(f"- Status: `{reconciliation.get('status', '-')}`")
            lines.append(f"- Portfolio realized PnL USD: `${reconciliation.get('portfolio_realized_pnl_usd', '-')}`")
            lines.append(f"- Journal realized PnL USD: `${reconciliation.get('journal_realized_pnl_usd', '-')}`")
            lines.append(f"- Difference USD: `${reconciliation.get('difference_usd', '-')}`")
            lines.append(f"- Note: {reconciliation.get('reason', '-')}")
        else:
            lines.append("No PnL reconciliation data available.")

        lines += ["", "## Performance by Pair", ""]
        by_pair = analytics.get("performance_by_pair", [])
        if by_pair:
            lines.append("| Pair | Trades | Filled Notional | Realized PnL | Win Rate % |")
            lines.append("|---|---:|---:|---:|---:|")
            for row in by_pair:
                lines.append(f"| {row['pair']} | {row['trades']} | {row['filled_notional_usd']} | {row['realized_pnl_usd']} | {row['win_rate_pct']} |")
        else:
            lines.append("No pair-level performance yet.")

        lines += ["", "## Recent Trade Journal", ""]
        journal = analytics.get("trade_journal", [])[-20:]
        if journal:
            lines.append("| Time | Pair | Buy | Sell | Status | Notional | Net % | Realized PnL | Quality | Reason |")
            lines.append("|---|---|---|---|---|---:|---:|---:|---|---|")
            for row in journal:
                reason = str(row.get("reason", "")).replace("|", "/")
                lines.append(
                    f"| {row.get('timestamp', '-')} | {row.get('pair', '-')} | "
                    f"{row.get('buy_source', '-')} | {row.get('sell_source', '-')} | "
                    f"{row.get('status', '-')} | {row.get('notional_usd', '-')} | "
                    f"{row.get('net_edge_pct', '-')} | {row.get('realized_pnl_usd', '-')} | "
                    f"{row.get('execution_quality', '-')} | {reason} |"
                )
        else:
            lines.append("No trade journal rows yet.")

        lines += ["", "## Notes", ""]
        for note in analytics.get("notes", []):
            lines.append(f"- {note}")

        self.analytics_md_file.write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return rows

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def _date_key(timestamp: str) -> str:
        if not timestamp:
            return "unknown"
        return timestamp[:10]

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except Exception:
            return Decimal("0")

    @classmethod
    def _optional_decimal(cls, value: Any) -> Decimal | None:
        if value is None:
            return None
        parsed = cls._decimal(value)
        return parsed

    @staticmethod
    def _q(value: Decimal | None) -> Decimal:
        if value is None:
            return Decimal("0.0000")
        return Decimal(value).quantize(Decimal("0.0000"))

    @classmethod
    def _pct(cls, numerator: Decimal, denominator: Decimal) -> Decimal:
        if denominator == 0:
            return Decimal("0.0000")
        return cls._q(numerator / denominator * Decimal("100"))

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")

    def _avg_optional(self, journal: list[TradeJournalEntry], attr: str) -> str:
        values = [getattr(t, attr) for t in journal if getattr(t, attr) is not None]
        if not values:
            return "-"
        return str(self._q(sum(values, Decimal("0")) / Decimal(len(values))))


def main() -> None:
    analytics = PnLAnalyticsService().generate()
    print(json.dumps(analytics, indent=2))


if __name__ == "__main__":
    main()
