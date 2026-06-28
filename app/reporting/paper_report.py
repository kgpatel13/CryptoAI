from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from decimal import Decimal


class PaperReportService:
    def __init__(self) -> None:
        self.data_dir = Path("data")
        self.report_dir = Path("reports")
        self.paper_orders_file = self.data_dir / "paper_orders.jsonl"
        self.opportunity_file = self.data_dir / "opportunity_decisions.jsonl"
        self.portfolio_state_file = self.data_dir / "paper_portfolio_state.json"
        self.report_dir.mkdir(exist_ok=True)

    def generate(self) -> dict:
        orders = self._read_jsonl(self.paper_orders_file)
        opportunities = self._read_jsonl(self.opportunity_file)

        filled = [o for o in orders if str(o.get("status", "")).upper() in {"FILLED", "PARTIAL_FILL"}]
        skipped = [o for o in orders if str(o.get("status", "")).upper() == "SKIPPED"]
        rejected = [o for o in orders if str(o.get("status", "")).upper() in {"REJECTED", "CANCELLED", "EXPIRED"}]
        risk_rejected = [o for o in orders if str(o.get("status", "")).upper() == "RISK_REJECTED"]

        total_notional = sum(self._decimal(o.get("notional_usd", "0")) for o in filled)
        portfolio_state = self._read_json(self.portfolio_state_file)
        portfolio_summary = self._portfolio_summary(portfolio_state)

        decision_counts = {}
        for row in opportunities:
            decision = str(row.get("decision", "UNKNOWN"))
            decision_counts[decision] = decision_counts.get(decision, 0) + 1

        skip_reasons = {}
        for order in skipped:
            reason = str(order.get("reason", "UNKNOWN"))
            skip_reasons[reason] = skip_reasons.get(reason, 0) + 1

        report = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "live_trading": "disabled",
            "total_opportunity_decisions": len(opportunities),
            "opportunity_decision_counts": decision_counts,
            "total_orders": len(orders),
            "filled_orders": len(filled),
            "skipped_orders": len(skipped),
            "rejected_orders": len(rejected),
            "risk_rejected_orders": len(risk_rejected),
            "total_filled_notional_usd": str(total_notional),
            "skip_reasons": skip_reasons,
            "risk_rejection_reasons": self._reason_counts(risk_rejected),
            "execution_quality_counts": self._value_counts(filled, "execution_quality"),
            "avg_slippage_bps": self._avg_decimal(filled, "slippage_bps"),
            "avg_latency_ms": self._avg_decimal(filled, "latency_ms"),
            "portfolio": portfolio_summary,
            "latest_opportunities": opportunities[-20:],
            "latest_orders": orders[-20:],
            "notes": [
                "This is simulated paper-trading output only.",
                "No real wallet or exchange order was used.",
                "If filled_orders is zero, inspect opportunity_decision_counts and skip_reasons.",
            ],
        }

        self._write_json(report)
        self._write_markdown(report)
        return report

    def _write_json(self, report: dict) -> None:
        (self.report_dir / "paper_report.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )

    def _write_markdown(self, report: dict) -> None:
        lines = [
            "# CryptoAI Paper Trading Report",
            "",
            f"Generated: `{report['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Mode: `{report['mode']}`",
            f"- Live trading: `{report['live_trading']}`",
            f"- Opportunity decisions: `{report['total_opportunity_decisions']}`",
            f"- Total orders: `{report['total_orders']}`",
            f"- Filled orders: `{report['filled_orders']}`",
            f"- Skipped orders: `{report['skipped_orders']}`",
            f"- Rejected orders: `{report['rejected_orders']}`",
            f"- Portfolio risk rejections: `{report['risk_rejected_orders']}`",
            f"- Total filled notional USD: `${report['total_filled_notional_usd']}`",
            f"- Paper portfolio cash USD: `${report['portfolio'].get('cash_usd', '-')}`",
            f"- Open paper positions: `{report['portfolio'].get('open_positions', 0)}`",
            f"- Closed paper positions: `{report['portfolio'].get('closed_positions', 0)}`",
            f"- Avg execution slippage bps: `{report.get('avg_slippage_bps', "-")}`",
            f"- Avg execution latency ms: `{report.get('avg_latency_ms', "-")}`",
            "",
            "## Opportunity Decision Counts",
            "",
        ]

        if report["opportunity_decision_counts"]:
            for decision, count in report["opportunity_decision_counts"].items():
                lines.append(f"- `{decision}`: {count}")
        else:
            lines.append("- No opportunity decisions found.")

        lines += ["", "## Skip Reasons", ""]
        if report["skip_reasons"]:
            for reason, count in report["skip_reasons"].items():
                lines.append(f"- `{reason}`: {count}")
        else:
            lines.append("- No skipped orders.")


        lines += ["", "## Portfolio Risk Rejection Reasons", ""]
        if report["risk_rejection_reasons"]:
            for reason, count in report["risk_rejection_reasons"].items():
                lines.append(f"- `{reason}`: {count}")
        else:
            lines.append("- No portfolio risk rejections.")

        lines += ["", "## Execution Quality", ""]
        if report.get("execution_quality_counts"):
            for quality, count in report["execution_quality_counts"].items():
                lines.append(f"- `{quality}`: {count}")
        else:
            lines.append("- No filled execution-quality records yet.")

        lines += ["", "## Paper Portfolio", ""]
        portfolio = report.get("portfolio", {})
        lines.append(f"- Cash USD: `${portfolio.get('cash_usd', '-')}`")
        lines.append(f"- Initial cash USD: `${portfolio.get('initial_cash_usd', '-')}`")
        lines.append(f"- Open positions: `{portfolio.get('open_positions', 0)}`")
        lines.append(f"- Closed positions: `{portfolio.get('closed_positions', 0)}`")
        lines.append(f"- Daily realized PnL USD: `${portfolio.get('daily_realized_pnl_usd', 0)}`")
        lines.append(f"- Unrealized PnL USD: `${portfolio.get('unrealized_pnl_usd', 0)}`")
        lines.append(f"- Daily filled trades: `{portfolio.get('daily_filled_trades', 0)}`")
        lines.append(f"- Exposure by chain: `{portfolio.get('exposure_by_chain', {})}`")
        lines.append(f"- Exposure by token: `{portfolio.get('exposure_by_token', {})}`")

        lines += ["", "## Latest Opportunities", ""]
        opps = report["latest_opportunities"]
        if opps:
            lines.append("| Pair | Net % | Score | Decision | Reason |")
            lines.append("|---|---:|---:|---|---|")
            for opp in opps:
                reason = str(opp.get("reason", "-")).replace("|", "/")
                lines.append(
                    f"| {opp.get('pair', '-')} | {opp.get('estimated_net_edge_pct', '-')} | "
                    f"{opp.get('readiness_score', '-')} | {opp.get('decision', '-')} | {reason} |"
                )
        else:
            lines.append("No opportunity rows found.")

        lines += ["", "## Latest Orders", ""]
        orders = report["latest_orders"]
        if orders:
            lines.append("| Time | Pair | Status | Notional | Edge % | Slip bps | Quality | Reason |")
            lines.append("|---|---|---|---:|---:|---:|---|---|")
            for order in orders:
                reason = str(order.get("reason", "-")).replace("|", "/")
                lines.append(
                    f"| {order.get('timestamp', '-')} | {order.get('pair', '-')} | "
                    f"{order.get('status', '-')} | {order.get('notional_usd', '-')} | "
                    f"{order.get('estimated_edge_pct', '-')} | {order.get('slippage_bps', '-')} | "
                    f"{order.get('execution_quality', '-')} | {reason} |"
                )
        else:
            lines.append("No paper orders saved yet.")

        lines += ["", "## Notes", ""]
        for note in report["notes"]:
            lines.append(f"- {note}")

        (self.report_dir / "paper_report.md").write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict]:
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
    def _read_json(path: Path) -> dict:
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def _reason_counts(rows: list[dict]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in rows:
            reason = str(row.get("reason", "UNKNOWN"))
            counts[reason] = counts.get(reason, 0) + 1
        return counts

    @staticmethod
    def _value_counts(rows: list[dict], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in rows:
            value = str(row.get(key) or "UNKNOWN")
            counts[value] = counts.get(value, 0) + 1
        return counts

    @staticmethod
    def _avg_decimal(rows: list[dict], key: str) -> str:
        values = [PaperReportService._decimal(row.get(key)) for row in rows if row.get(key) is not None]
        if not values:
            return "-"
        return str((sum(values, Decimal("0")) / Decimal(len(values))).quantize(Decimal("0.0001")))

    @staticmethod
    def _portfolio_summary(state: dict) -> dict:
        if not state:
            return {"cash_usd": "-", "initial_cash_usd": "-", "open_positions": 0, "daily_filled_trades": 0, "exposure_by_chain": {}, "exposure_by_token": {}}
        positions = [p for p in state.get("positions", []) if str(p.get("status", "OPEN")).upper() == "OPEN"]
        exposure_by_chain: dict[str, str] = {}
        exposure_by_token: dict[str, str] = {}
        for pos in positions:
            notional = PaperReportService._decimal(pos.get("notional_usd", "0"))
            chain = str(pos.get("chain", "-"))
            token = str(pos.get("base_symbol", "-"))
            exposure_by_chain[chain] = str(PaperReportService._decimal(exposure_by_chain.get(chain, "0")) + notional)
            exposure_by_token[token] = str(PaperReportService._decimal(exposure_by_token.get(token, "0")) + notional)
        closed_positions = [p for p in state.get("positions", []) if str(p.get("status", "")).upper() == "CLOSED"]
        unrealized = Decimal("0")
        for pos in positions:
            qty = PaperReportService._decimal(pos.get("quantity", "0"))
            cur = PaperReportService._decimal(pos.get("current_price_usd", pos.get("entry_price_usd", "0")))
            notional = PaperReportService._decimal(pos.get("notional_usd", "0"))
            unrealized += (qty * cur) - notional
        return {
            "cash_usd": state.get("cash_usd", "-"),
            "initial_cash_usd": state.get("initial_cash_usd", "-"),
            "open_positions": len(positions),
            "closed_positions": len(closed_positions),
            "daily_filled_trades": state.get("daily_filled_trades", 0),
            "daily_realized_pnl_usd": state.get("daily_realized_pnl_usd", "0"),
            "realized_pnl_usd": state.get("realized_pnl_usd", "0"),
            "unrealized_pnl_usd": str(unrealized.quantize(Decimal("0.0001"))),
            "exposure_by_chain": exposure_by_chain,
            "exposure_by_token": exposure_by_token,
            "updated_at": state.get("updated_at"),
        }

    @staticmethod
    def _decimal(value) -> Decimal:
        try:
            return Decimal(str(value))
        except Exception:
            return Decimal("0")

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    report = PaperReportService().generate()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
