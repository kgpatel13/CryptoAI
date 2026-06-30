from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


class PaperRunReviewService:
    """Summarizes fresh 24/7 paper performance against shadow-readiness evidence."""

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.output_json = self.report_dir / "paper_run_review.json"
        self.output_md = self.report_dir / "paper_run_review.md"

    def generate(self) -> dict[str, Any]:
        state = self._read_json(self.data_dir / "paper_portfolio_state.json")
        orders = self._read_jsonl(self.data_dir / "paper_orders.jsonl")
        paper = self._read_json(self.report_dir / "paper_report.json")
        analytics = self._read_json(self.report_dir / "portfolio_analytics.json")
        pool_depth = self._read_json(self.report_dir / "pool_depth_ladder.json")
        execution_realism = self._read_json(self.report_dir / "execution_realism.json")
        provider_monitor = self._read_json(self.report_dir / "provider_monitor.json")
        report_audit = self._read_json(self.report_dir / "report_audit.json")
        settings = self._read_json(self.report_dir / "paper_trading_settings.json")

        closed_orders = [row for row in orders if str(row.get("status", "")).upper() == "CLOSED"]
        losing_orders = [row for row in closed_orders if self._decimal(row.get("realized_pnl_usd")) < 0]
        open_positions = [
            row for row in state.get("positions", [])
            if str(row.get("status", "OPEN")).upper() == "OPEN"
        ]

        initial_cash = self._decimal(state.get("initial_cash_usd", analytics.get("initial_cash_usd", "0")))
        cash = self._decimal(state.get("cash_usd", analytics.get("cash_usd", initial_cash)))
        realized = self._decimal(state.get("realized_pnl_usd", analytics.get("realized_pnl_usd", "0")))
        return_pct = self._pct(realized, initial_cash)
        first_trade_at, last_trade_at = self._trade_window(closed_orders)

        gates = self._gates(
            paper=paper,
            analytics=analytics,
            pool_depth=pool_depth,
            execution_realism=execution_realism,
            provider_monitor=provider_monitor,
            report_audit=report_audit,
            losing_orders=losing_orders,
            open_positions=open_positions,
        )
        readiness = self._readiness(gates=gates, realized=realized, closed_trade_count=len(closed_orders))
        findings = self._findings(
            gates=gates,
            realized=realized,
            return_pct=return_pct,
            closed_trade_count=len(closed_orders),
            losing_trade_count=len(losing_orders),
            pool_depth=pool_depth,
            execution_realism=execution_realism,
            report_audit=report_audit,
        )

        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "overall_status": readiness["overall_status"],
            "recommendation": readiness["recommendation"],
            "live_decision": "BLOCKED",
            "shadow_decision": readiness["shadow_decision"],
            "paper_profile": settings.get("paper_profile", settings.get("settings", {}).get("paper_profile", "-")),
            "initial_cash_usd": self._fmt_usd(initial_cash),
            "cash_usd": self._fmt_usd(cash),
            "realized_pnl_usd": self._fmt_usd(realized),
            "return_pct": self._fmt(return_pct),
            "closed_trade_count": len(closed_orders),
            "losing_trade_count": len(losing_orders),
            "open_position_count": len(open_positions),
            "first_trade_at": first_trade_at,
            "last_trade_at": last_trade_at,
            "provider_status": provider_monitor.get("overall_status", "UNKNOWN"),
            "pool_depth_status": pool_depth.get("overall_status", "MISSING"),
            "pool_depth_ready_route_count": self._int(pool_depth.get("depth_ready_route_count")),
            "execution_realism_status": execution_realism.get("overall_status", "MISSING"),
            "execution_realism_confidence": execution_realism.get("confidence", "UNKNOWN"),
            "shadow_ready_count": self._int(execution_realism.get("shadow_ready_count")),
            "live_ready_count": self._int(execution_realism.get("live_ready_count")),
            "report_audit_findings": self._int(report_audit.get("finding_count")),
            "gates": gates,
            "findings": findings,
            "notes": [
                "Paper Run Review is evidence-only and never enables live trading.",
                "Paper profit is useful only when execution realism and pool-depth evidence also improve.",
                "Live trading remains blocked until explicit live-readiness controls are implemented and evidence supports them.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _gates(
        self,
        *,
        paper: dict[str, Any],
        analytics: dict[str, Any],
        pool_depth: dict[str, Any],
        execution_realism: dict[str, Any],
        provider_monitor: dict[str, Any],
        report_audit: dict[str, Any],
        losing_orders: list[dict[str, Any]],
        open_positions: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        return [
            self._gate(
                "pnl_reconciled",
                paper.get("pnl_reconciliation", {}).get("status") == "RECONCILED"
                and analytics.get("pnl_reconciliation", {}).get("status") == "RECONCILED",
                f"paper={paper.get('pnl_reconciliation', {}).get('status', '-')}; analytics={analytics.get('pnl_reconciliation', {}).get('status', '-')}",
            ),
            self._gate("no_open_positions", len(open_positions) == 0, f"open_positions={len(open_positions)}"),
            self._gate("no_losing_closed_trades", len(losing_orders) == 0, f"losing_trades={len(losing_orders)}"),
            self._gate(
                "provider_ok",
                provider_monitor.get("overall_status") == "OK",
                f"provider_status={provider_monitor.get('overall_status', 'UNKNOWN')}",
            ),
            self._gate(
                "pool_depth_ready",
                self._int(pool_depth.get("depth_ready_route_count")) > 0,
                f"depth_ready_routes={self._int(pool_depth.get('depth_ready_route_count'))}; status={pool_depth.get('overall_status', 'MISSING')}",
            ),
            self._gate(
                "execution_shadow_ready",
                self._int(execution_realism.get("shadow_ready_count")) > 0,
                f"shadow_ready={self._int(execution_realism.get('shadow_ready_count'))}; status={execution_realism.get('overall_status', 'MISSING')}",
            ),
            self._gate(
                "report_audit_clean",
                self._int(report_audit.get("finding_count")) == 0,
                f"findings={self._int(report_audit.get('finding_count'))}",
            ),
        ]

    @staticmethod
    def _gate(name: str, passed: bool, message: str) -> dict[str, str]:
        return {"name": name, "status": "PASS" if passed else "BLOCK", "message": message}

    @staticmethod
    def _readiness(*, gates: list[dict[str, str]], realized: Decimal, closed_trade_count: int) -> dict[str, str]:
        blocked = {gate["name"] for gate in gates if gate["status"] != "PASS"}
        if "pnl_reconciled" in blocked or "no_open_positions" in blocked:
            return {
                "overall_status": "ACCOUNTING_REVIEW",
                "shadow_decision": "BLOCKED",
                "recommendation": "Fix accounting or open-position state before strategy interpretation.",
            }
        if "no_losing_closed_trades" in blocked:
            return {
                "overall_status": "PAPER_LOSS_REVIEW",
                "shadow_decision": "BLOCKED",
                "recommendation": "Review losing paper transactions before shadow review.",
            }
        if closed_trade_count == 0:
            return {
                "overall_status": "COLLECTING_PAPER_EVIDENCE",
                "shadow_decision": "BLOCKED",
                "recommendation": "Continue paper run until closed trade evidence exists.",
            }
        if "pool_depth_ready" in blocked or "execution_shadow_ready" in blocked:
            return {
                "overall_status": "PAPER_PROFIT_NOT_SHADOW_READY" if realized > 0 else "PAPER_ONLY_NOT_SHADOW_READY",
                "shadow_decision": "BLOCKED",
                "recommendation": "Continue paper trading and improve pool-depth/execution realism before shadow review.",
            }
        if "provider_ok" in blocked or "report_audit_clean" in blocked:
            return {
                "overall_status": "OPERATIONS_REVIEW",
                "shadow_decision": "BLOCKED",
                "recommendation": "Refresh operational evidence before shadow review.",
            }
        return {
            "overall_status": "SHADOW_REVIEW_CANDIDATE",
            "shadow_decision": "REVIEW_READY",
            "recommendation": "Review sustained paper evidence before any live-trading design decision.",
        }

    def _findings(
        self,
        *,
        gates: list[dict[str, str]],
        realized: Decimal,
        return_pct: Decimal,
        closed_trade_count: int,
        losing_trade_count: int,
        pool_depth: dict[str, Any],
        execution_realism: dict[str, Any],
        report_audit: dict[str, Any],
    ) -> list[dict[str, str]]:
        findings: list[dict[str, str]] = []
        if closed_trade_count == 0:
            findings.append({"severity": "WATCH", "message": "No closed paper trades yet after fresh reset."})
        if realized > 0 and closed_trade_count > 0:
            findings.append({"severity": "INFO", "message": f"Paper run is profitable so far: ${self._fmt_usd(realized)} across {closed_trade_count} closed trade(s)."})
        if losing_trade_count:
            findings.append({"severity": "ACTION", "message": f"{losing_trade_count} closed trade(s) have negative realized PnL."})
        if return_pct >= Decimal("5") and closed_trade_count < 100:
            findings.append({"severity": "WATCH", "message": "High early return with a small trade sample; treat as paper-only until more evidence accumulates."})
        if self._int(pool_depth.get("depth_ready_route_count")) == 0:
            findings.append({"severity": "ACTION", "message": "Pool-depth ladder has zero depth-ready routes; paper profit is not executable-size evidence yet."})
        if self._int(execution_realism.get("shadow_ready_count")) == 0:
            findings.append({"severity": "ACTION", "message": "Execution realism has zero shadow-ready opportunities; live trading remains blocked."})
        if self._int(report_audit.get("finding_count")):
            findings.append({"severity": "WATCH", "message": f"Report audit has {self._int(report_audit.get('finding_count'))} finding(s); refresh missing/stale research reports as needed."})
        blocked = [gate["name"] for gate in gates if gate["status"] != "PASS"]
        if blocked:
            findings.append({"severity": "SUMMARY", "message": "Blocked gates: " + ", ".join(blocked) + "."})
        return findings

    @staticmethod
    def _trade_window(rows: list[dict[str, Any]]) -> tuple[str | None, str | None]:
        timestamps = [str(row.get("timestamp")) for row in rows if row.get("timestamp")]
        if not timestamps:
            return None, None
        return min(timestamps), max(timestamps)

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
    def _read_jsonl(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
        return rows

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0")

    @staticmethod
    def _int(value: Any) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _pct(numerator: Decimal, denominator: Decimal) -> Decimal:
        if denominator == 0:
            return Decimal("0")
        return numerator / denominator * Decimal("100")

    @staticmethod
    def _fmt(value: Decimal) -> str:
        return str(value.quantize(Decimal("0.0000")))

    @staticmethod
    def _fmt_usd(value: Decimal) -> str:
        return str(value.quantize(Decimal("0.0000")))

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# CryptoAI Paper Run Review",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Recommendation: `{payload['recommendation']}`",
            f"- Shadow decision: `{payload['shadow_decision']}`",
            f"- Live decision: `{payload['live_decision']}`",
            f"- Initial cash USD: `${payload['initial_cash_usd']}`",
            f"- Cash USD: `${payload['cash_usd']}`",
            f"- Realized PnL USD: `${payload['realized_pnl_usd']}`",
            f"- Return %: `{payload['return_pct']}`",
            f"- Closed trades: `{payload['closed_trade_count']}`",
            f"- Losing trades: `{payload['losing_trade_count']}`",
            f"- Open positions: `{payload['open_position_count']}`",
            f"- Provider status: `{payload['provider_status']}`",
            f"- Pool depth status: `{payload['pool_depth_status']}`",
            f"- Execution realism: `{payload['execution_realism_status']}` / `{payload['execution_realism_confidence']}`",
            "",
            "## Gates",
            "",
            "| Gate | Status | Message |",
            "|---|---|---|",
        ]
        for gate in payload["gates"]:
            lines.append(f"| {gate['name']} | {gate['status']} | {gate['message']} |")
        lines += ["", "## Findings", "", "| Severity | Message |", "|---|---|"]
        for finding in payload["findings"]:
            lines.append(f"| {finding['severity']} | {finding['message']} |")
        if not payload["findings"]:
            lines.append("| OK | No findings. |")
        lines += ["", "## Notes", ""]
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    payload = PaperRunReviewService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
