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
        self.report_dir.mkdir(exist_ok=True)

    def generate(self) -> dict:
        orders = self._read_jsonl(self.paper_orders_file)
        opportunities = self._read_jsonl(self.opportunity_file)

        filled = [o for o in orders if str(o.get("status", "")).upper() == "FILLED"]
        skipped = [o for o in orders if str(o.get("status", "")).upper() == "SKIPPED"]
        rejected = [o for o in orders if str(o.get("status", "")).upper() == "REJECTED"]

        total_notional = sum(self._decimal(o.get("notional_usd", "0")) for o in filled)

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
            "total_filled_notional_usd": str(total_notional),
            "skip_reasons": skip_reasons,
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
            f"- Total filled notional USD: `${report['total_filled_notional_usd']}`",
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
            lines.append("| Time | Pair | Status | Notional | Edge % | Reason |")
            lines.append("|---|---|---|---:|---:|---|")
            for order in orders:
                reason = str(order.get("reason", "-")).replace("|", "/")
                lines.append(
                    f"| {order.get('timestamp', '-')} | {order.get('pair', '-')} | "
                    f"{order.get('status', '-')} | {order.get('notional_usd', '-')} | "
                    f"{order.get('estimated_edge_pct', '-')} | {reason} |"
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
