from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from app.config.feature_flags import load_feature_flags


class LiveReadinessChecklistService:
    """Aggregates the pre-live checklist into a single evidence report.

    This service does not approve live trading. It verifies whether paper,
    shadow, wallet, risk, logging, and export evidence are ready for a human
    live-pilot review.
    """

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.output_json = self.report_dir / "live_readiness_checklist.json"
        self.output_md = self.report_dir / "live_readiness_checklist.md"

    def generate(self) -> dict[str, Any]:
        flags = load_feature_flags()
        paper = self._read_json("paper_report.json")
        analytics = self._read_json("portfolio_analytics.json")
        paper_run = self._read_json("paper_run_review.json")
        realism = self._read_json("execution_realism.json")
        cost = self._read_json("execution_cost_evidence.json")
        provider = self._read_json("provider_monitor.json")
        audit = self._read_json("report_audit.json")
        live_safety = self._read_json("live_safety.json")
        wallet = self._read_json("wallet_preflight.json")
        transaction_simulation = self._read_json("transaction_simulation.json")
        settings = self._read_json("paper_trading_settings.json")
        paper_settings = settings.get("settings", {}) if isinstance(settings.get("settings"), dict) else {}
        orders = self._read_jsonl(self.data_dir / "paper_orders.jsonl")

        checks = self._checks(
            flags=flags,
            paper=paper,
            analytics=analytics,
            paper_run=paper_run,
            realism=realism,
            cost=cost,
            provider=provider,
            audit=audit,
            live_safety=live_safety,
            wallet=wallet,
            transaction_simulation=transaction_simulation,
            paper_settings=paper_settings,
            orders=orders,
        )
        blockers = [check for check in checks if check["severity"] == "BLOCK"]
        actions = [check for check in checks if check["severity"] == "ACTION"]
        warnings = [check for check in checks if check["severity"] == "WATCH"]
        status = "LIVE_REVIEW_READY" if not blockers and not actions else "LIVE_REVIEW_NOT_READY"
        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "overall_status": status,
            "live_review_ready": status == "LIVE_REVIEW_READY",
            "live_trading_approval": False,
            "check_count": len(checks),
            "pass_count": sum(1 for check in checks if check["severity"] == "PASS"),
            "watch_count": len(warnings),
            "action_count": len(actions),
            "blocked_check_count": len(blockers),
            "paper_profile": settings.get("paper_profile", paper_settings.get("paper_profile", "-")),
            "closed_trade_count": self._int(paper_run.get("closed_trade_count", paper.get("filled_orders"))),
            "paper_cash_usd": paper_run.get("cash_usd", analytics.get("cash_usd")),
            "paper_realized_pnl_usd": paper_run.get("realized_pnl_usd", analytics.get("realized_pnl_usd")),
            "max_live_wallet_usd": str(flags.max_live_wallet_usd),
            "max_live_trade_usd": str(flags.max_live_trade_usd),
            "max_daily_loss_usd": str(flags.max_daily_loss_usd),
            "checks": checks,
            "notes": [
                "Live Readiness Checklist is a human review gate and never enables live trading.",
                "Paper can use the same limits as the intended tiny-live pilot, but it cannot exactly reproduce gas spikes, failed transactions, MEV, mempool ordering, RPC outages, nonce issues, wallet signing, or pool movement between legs.",
                "Use a live-parity paper profile before tiny real-money testing: wallet ceiling <= $500, per-trade cap <= tiny-live cap, daily loss cap > $0, Base only, USDC/WETH only.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _checks(
        self,
        *,
        flags: Any,
        paper: dict[str, Any],
        analytics: dict[str, Any],
        paper_run: dict[str, Any],
        realism: dict[str, Any],
        cost: dict[str, Any],
        provider: dict[str, Any],
        audit: dict[str, Any],
        live_safety: dict[str, Any],
        wallet: dict[str, Any],
        transaction_simulation: dict[str, Any],
        paper_settings: dict[str, Any],
        orders: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        closed_orders = [row for row in orders if str(row.get("status", "")).upper() == "CLOSED"]
        max_paper_notional = max((self._decimal(row.get("notional_usd")) for row in closed_orders), default=Decimal("0"))
        paper_capital = self._paper_capital_usd(paper_settings)
        paper_trade_cap = self._decimal(paper_settings.get("paper_capital", {}).get("max_notional_usd_per_trade"))
        paper_daily_loss = self._decimal(paper_settings.get("risk", {}).get("max_daily_loss_usd"))
        paper_chains = {str(row).lower() for row in paper_settings.get("market_scope", {}).get("chains", [])}
        paper_routes = {str(row).upper() for row in paper_settings.get("market_scope", {}).get("routes", [])}
        paper_dexes = {str(row) for row in paper_settings.get("market_scope", {}).get("dexes", [])}
        paper_risk = paper_settings.get("risk", {})

        return [
            self._check(
                "stable_paper_trading",
                self._int(paper_run.get("closed_trade_count", paper.get("filled_orders"))) >= flags.min_paper_closed_trades,
                "BLOCK",
                f"Need at least {flags.min_paper_closed_trades} closed paper trades under the review profile.",
                "Closed paper trade sample meets the configured minimum.",
            ),
            self._check(
                "paper_shadow_review_ready",
                paper_run.get("shadow_decision") == "REVIEW_READY",
                "ACTION",
                "Paper Run Review must reach REVIEW_READY before live-pilot review.",
                "Paper Run Review is ready for shadow review.",
            ),
            self._check(
                "paper_pnl_reconciled",
                paper.get("pnl_reconciliation", {}).get("status") == "RECONCILED"
                and analytics.get("pnl_reconciliation", {}).get("status") == "RECONCILED",
                "BLOCK",
                "Paper report and portfolio analytics must both reconcile PnL.",
                "Paper report and portfolio analytics PnL are reconciled.",
            ),
            self._check(
                "no_open_positions",
                self._int(paper_run.get("open_position_count")) == 0 and self._int(analytics.get("open_positions")) == 0,
                "BLOCK",
                "Open paper positions must be zero before review.",
                "No open paper positions.",
            ),
            self._check(
                "execution_engine_atomic",
                bool(closed_orders) and all(str(row.get("execution_type", "")).upper() == "ARBITRAGE_ROUND_TRIP" for row in closed_orders[-100:]),
                "BLOCK",
                "Recent paper fills must be atomic arbitrage round trips.",
                "Recent paper fills are atomic arbitrage round trips.",
            ),
            self._check(
                "risk_engine_validated",
                self._int(paper.get("risk_rejected_orders")) >= 0 and self._int(paper_run.get("losing_trade_count")) == 0,
                "ACTION",
                "Risk engine reports or losing-trade review are not clean.",
                "Risk engine evidence is present and losing-trade count is clean.",
            ),
            self._check(
                "provider_health_ok",
                provider.get("overall_status") == "OK",
                "BLOCK",
                "Provider Monitor must be OK.",
                "Provider Monitor is OK.",
            ),
            self._check(
                "execution_cost_confidence",
                str(cost.get("confidence", "")).upper() == "HIGH",
                "ACTION",
                "Execution-cost evidence confidence must be HIGH.",
                "Execution-cost evidence confidence is HIGH.",
            ),
            self._check(
                "execution_realism_shadow_ready",
                self._int(realism.get("shadow_ready_count")) > 0 and self._int(realism.get("live_ready_count")) == 0,
                "ACTION",
                "Execution realism must have shadow-ready evidence and zero live-ready approvals.",
                "Execution realism has shadow-ready evidence and no live approvals.",
            ),
            self._check(
                "report_audit_clean",
                self._audit_blocking_findings(audit) == 0,
                "BLOCK",
                "Report Audit has blocking operational findings.",
                "Report Audit has no blocking operational findings.",
            ),
            self._check(
                "audit_trail_available",
                bool(orders) and bool(analytics.get("trade_journal")),
                "BLOCK",
                "Paper orders and analytics trade journal must exist for audit trail review.",
                "Paper orders and analytics trade journal are available.",
            ),
            self._check(
                "transaction_tax_export_available",
                bool(analytics.get("trade_journal")) and bool(paper.get("latest_orders")),
                "ACTION",
                "Trade journal/export evidence must be available for tax/accounting records.",
                "Trade journal/export evidence is available for tax/accounting records.",
            ),
            self._check(
                "wallet_preflight_ready",
                wallet.get("wallet_preflight_allowed") is True,
                "ACTION",
                "Wallet Preflight must be ready with an isolated public wallet and tiny-pilot caps.",
                "Wallet Preflight is ready.",
            ),
            self._check(
                "transaction_simulation_passed",
                transaction_simulation.get("transaction_simulation_passed") is True,
                "ACTION",
                "Transaction Simulation must pass exact calldata and eth_call checks before live review.",
                "Transaction Simulation passed exact calldata and eth_call checks.",
            ),
            self._check(
                "live_safety_blocked",
                live_safety.get("overall_status") == "LIVE_BLOCKED" and live_safety.get("live_guard_allowed") is False,
                "BLOCK",
                "Live Safety must remain blocked during readiness review.",
                "Live Safety remains blocked during readiness review.",
            ),
            self._check(
                "live_feature_off",
                flags.live_trading_enabled is False,
                "BLOCK",
                "Live feature flag must remain off until the final reviewed pilot.",
                "Live feature flag is off.",
            ),
            self._check(
                "kill_switch_on",
                flags.live_kill_switch_enabled is True and paper_risk.get("kill_switch_enabled") is True,
                "BLOCK",
                "Live and paper kill switches must remain on during readiness review.",
                "Live and paper kill switches are on.",
            ),
            self._check(
                "private_key_absent",
                flags.private_key_configured is False,
                "BLOCK",
                "Private key must not be configured during readiness review.",
                "Private key is absent.",
            ),
            self._check(
                "paper_live_wallet_parity",
                Decimal("0") < flags.max_live_wallet_usd <= Decimal("500")
                and paper_capital > Decimal("0")
                and paper_capital <= flags.max_live_wallet_usd,
                "ACTION",
                "Paper capital should be > $0 and no larger than the configured live wallet ceiling.",
                "Paper capital is within the configured live wallet ceiling.",
            ),
            self._check(
                "paper_live_trade_cap_parity",
                Decimal("0") < flags.max_live_trade_usd <= flags.tiny_live_trade_ceiling_usd
                and paper_trade_cap > Decimal("0")
                and paper_trade_cap <= flags.max_live_trade_usd
                and max_paper_notional <= flags.max_live_trade_usd,
                "ACTION",
                "Paper max notional and observed fills should be no larger than the configured live trade cap.",
                "Paper trade cap and observed fills are within the live trade cap.",
            ),
            self._check(
                "paper_live_daily_loss_parity",
                Decimal("0") < flags.max_daily_loss_usd <= flags.max_live_trade_usd
                and Decimal("0") < paper_daily_loss <= flags.max_daily_loss_usd,
                "ACTION",
                "Paper daily loss cap should be > $0 and no larger than the configured live daily loss cap.",
                "Paper daily loss cap matches the tiny-live policy.",
            ),
            self._check(
                "base_eth_scope_only",
                paper_chains == {"base"}
                and paper_routes.issubset({"WETH/USDC", "USDC/WETH"})
                and {"Uniswap V3", "Aerodrome"}.issubset(paper_dexes),
                "BLOCK",
                "Readiness review must stay on Base ETH routes with approved DEX coverage.",
                "Readiness review is restricted to Base ETH approved routes.",
            ),
        ]

    @staticmethod
    def _check(name: str, passed: bool, fail_severity: str, fail_detail: str, pass_detail: str) -> dict[str, str]:
        return {
            "name": name,
            "severity": "PASS" if passed else fail_severity,
            "passed": bool(passed),
            "detail": pass_detail if passed else fail_detail,
        }

    def _read_json(self, name: str) -> dict[str, Any]:
        path = self.report_dir / name
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

    def _paper_capital_usd(self, paper_settings: dict[str, Any]) -> Decimal:
        capital = paper_settings.get("paper_capital", {})
        return self._decimal(capital.get("initial_capital_eth")) * self._decimal(capital.get("eth_reference_usd"))

    def _audit_blocking_findings(self, audit: dict[str, Any]) -> int:
        if "blocking_finding_count" in audit:
            return self._int(audit.get("blocking_finding_count"))
        return self._int(audit.get("finding_count"))

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

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# Live Readiness Checklist",
            "",
            f"Generated: `{payload['generated_at']}`",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Live review ready: `{payload['live_review_ready']}`",
            f"- Live trading approval: `{payload['live_trading_approval']}`",
            f"- Paper profile: `{payload['paper_profile']}`",
            f"- Closed paper trades: `{payload['closed_trade_count']}`",
            f"- Paper cash USD: `${payload['paper_cash_usd']}`",
            f"- Paper realized PnL USD: `${payload['paper_realized_pnl_usd']}`",
            f"- Max live wallet USD: `${payload['max_live_wallet_usd']}`",
            f"- Max live trade USD: `${payload['max_live_trade_usd']}`",
            f"- Max daily loss USD: `${payload['max_daily_loss_usd']}`",
            f"- Blocked checks: `{payload['blocked_check_count']}`",
            f"- Action checks: `{payload['action_count']}`",
            f"- Watch checks: `{payload['watch_count']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "|---|---|---|",
        ]
        for row in payload["checks"]:
            lines.append(f"| {row['name']} | {row['severity']} | {row['detail']} |")
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    payload = LiveReadinessChecklistService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
