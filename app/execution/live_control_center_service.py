from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.execution.tiny_live_pilot_service import TinyLivePilotService


class LiveControlCenterService:
    """Single operational view for the manual live pilot.

    The control center is intentionally read-only. It can refresh the tiny-live
    plan and readiness reports, but it never approves, swaps, or starts an
    autonomous live trading loop.
    """

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.output_json = self.report_dir / "live_control_center.json"
        self.output_md = self.report_dir / "live_control_center.md"

    def generate(self, refresh_plan: bool = True) -> dict[str, Any]:
        refresh_errors: list[str] = []
        if refresh_plan:
            refresh_errors.extend(self._refresh_safe_reports())
            try:
                TinyLivePilotService(data_dir=self.data_dir, report_dir=self.report_dir).generate(mode="plan")
            except Exception as exc:
                refresh_errors.append(f"tiny_live_pilot: {type(exc).__name__}: {exc}")

        wallet = self._read_json("wallet_preflight.json")
        readiness = self._read_json("live_readiness_checklist.json")
        tx_sim = self._read_json("transaction_simulation.json")
        pilot = self._read_json("tiny_live_pilot.json")
        provider = self._read_json("provider_monitor.json")
        audit = self._read_json("report_audit.json")
        live_safety = self._read_json("live_safety.json")
        live_orders = self._read_jsonl(self.data_dir / "live_pilot_orders.jsonl", limit=20)

        pilot_plan = pilot.get("pilot_plan", {}) if isinstance(pilot.get("pilot_plan"), dict) else {}
        blocking_checks = [
            {
                "source": "tiny_live_pilot",
                "name": row.get("name", "-"),
                "severity": row.get("severity", "-"),
                "detail": row.get("detail", "-"),
            }
            for row in pilot.get("checks", [])
            if row.get("severity") == "BLOCK" or row.get("passed") is False
        ]
        readiness_actions = [
            {
                "source": "live_readiness",
                "name": row.get("name", "-"),
                "severity": row.get("severity", "-"),
                "detail": row.get("detail", "-"),
            }
            for row in readiness.get("checks", [])
            if row.get("severity") != "PASS" or row.get("passed") is False
        ]
        tx_actions = [
            {
                "source": "transaction_simulation",
                "name": row.get("name", "-"),
                "severity": row.get("severity", "-"),
                "detail": row.get("detail", "-"),
            }
            for row in tx_sim.get("checks", [])
            if row.get("severity") != "PASS" or row.get("passed") is False
        ]

        status, next_action, next_command = self._decision(
            wallet=wallet,
            readiness=readiness,
            tx_sim=tx_sim,
            pilot=pilot,
            pilot_plan=pilot_plan,
        )

        payload = {
            "generated_at": self._utc_now(),
            "mode": "live_control_center",
            "overall_status": status,
            "next_action": next_action,
            "next_command": next_command,
            "continuous_monitor_command": "python -m app.execution.live_control_center_service --loop --interval 30",
            "continuous_live_trading_command": "python -m app.execution.live_control_center_service --live-loop --interval 30",
            "continuous_live_trading_status": "NOT_AVAILABLE_UNTIL_LIVE_EXECUTOR",
            "refresh_errors": refresh_errors,
            "wallet": {
                "address": pilot_plan.get("wallet_address", ""),
                "chain": "base",
                "usdc_balance": pilot_plan.get("usdc_balance", "0"),
                "eth_balance": pilot_plan.get("eth_balance", "0"),
                "allowance_sufficient": pilot_plan.get("allowance_sufficient", False),
                "approval_tx_available": pilot_plan.get("approval_tx_available", False),
                "swap_tx_available": pilot_plan.get("swap_tx_available", False),
                "smoke_usd": pilot_plan.get("smoke_usd", "-"),
                "dex": pilot_plan.get("dex", "-"),
                "router_address": pilot_plan.get("router_address", "-"),
                "latest_block": pilot_plan.get("latest_block", "-"),
            },
            "gates": {
                "wallet_preflight": wallet.get("overall_status", "-"),
                "wallet_preflight_allowed": wallet.get("wallet_preflight_allowed", False),
                "live_readiness": readiness.get("overall_status", "-"),
                "live_review_ready": readiness.get("live_review_ready", False),
                "transaction_simulation": tx_sim.get("overall_status", "-"),
                "transaction_simulation_passed": tx_sim.get("transaction_simulation_passed", False),
                "tiny_live_pilot": pilot.get("overall_status", "-"),
                "tiny_live_blocked_checks": pilot.get("blocked_check_count", "-"),
                "provider_monitor": provider.get("overall_status", "-"),
                "report_audit_blocking_findings": audit.get("blocking_finding_count", "-"),
                "live_safety": live_safety.get("overall_status", "-"),
            },
            "blocking_checks": blocking_checks[:20],
            "readiness_actions": readiness_actions[:20],
            "transaction_simulation_actions": tx_actions[:20],
            "recent_live_pilot_orders": live_orders,
            "notes": [
                "This control center is read-only and never sends live transactions.",
                "Refreshing safe reports can update wallet, provider, readiness, and simulation evidence, but cannot approve or swap.",
                "The live-loop command exists as the future continuous entrypoint, but currently refuses autonomous execution.",
                "Continuous live arbitrage is not available until exact transaction simulation, live readiness, and a real live arbitrage executor pass review.",
                "The current live-capable path is a manual tiny smoke pilot only.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def run_loop(self, interval: int = 30, max_cycles: int | None = None) -> dict[str, Any]:
        cycles = 0
        last_payload: dict[str, Any] = {}
        print(f"CryptoAI live control center monitor started. Interval: {interval}s")
        print("Read-only monitor. It will not approve, swap, or trade continuously.")
        try:
            while True:
                cycles += 1
                last_payload = self.generate(refresh_plan=True)
                print(
                    json.dumps(
                        {
                            "cycle": cycles,
                            "generated_at": last_payload.get("generated_at"),
                            "overall_status": last_payload.get("overall_status"),
                            "next_action": last_payload.get("next_action"),
                            "wallet": last_payload.get("wallet", {}),
                        },
                        indent=2,
                    )
                )
                if max_cycles is not None and cycles >= max_cycles:
                    break
                time.sleep(interval)
        except KeyboardInterrupt:
            pass
        return {"status": "STOPPED", "cycles_completed": cycles, "last_payload": last_payload}

    def run_live_loop(self, interval: int = 30, max_cycles: int | None = None) -> dict[str, Any]:
        """Future continuous live entrypoint.

        This loop deliberately does not send transactions. It gives the user one
        command to run when they think live is close, but keeps the actual
        execution path blocked until the project has a reviewed continuous live
        arbitrage executor.
        """
        cycles = 0
        last_payload: dict[str, Any] = {}
        print(f"CryptoAI continuous live loop requested. Interval: {interval}s")
        print("Autonomous live execution is not available yet. This loop will monitor and refuse sends.")
        try:
            while True:
                cycles += 1
                last_payload = self.generate(refresh_plan=True)
                status = last_payload.get("overall_status")
                summary = {
                    "cycle": cycles,
                    "generated_at": last_payload.get("generated_at"),
                    "live_loop_status": "REFUSED_AUTONOMOUS_EXECUTION",
                    "readiness_status": status,
                    "continuous_live_trading_status": last_payload.get("continuous_live_trading_status"),
                    "next_action": last_payload.get("next_action"),
                    "safe_monitor_command": last_payload.get("continuous_monitor_command"),
                }
                print(json.dumps(summary, indent=2))
                if max_cycles is not None and cycles >= max_cycles:
                    break
                time.sleep(interval)
        except KeyboardInterrupt:
            pass
        return {
            "status": "STOPPED",
            "live_loop_status": "REFUSED_AUTONOMOUS_EXECUTION",
            "cycles_completed": cycles,
            "last_payload": last_payload,
        }

    def _decision(
        self,
        *,
        wallet: dict[str, Any],
        readiness: dict[str, Any],
        tx_sim: dict[str, Any],
        pilot: dict[str, Any],
        pilot_plan: dict[str, Any],
    ) -> tuple[str, str, str | None]:
        if wallet.get("wallet_preflight_allowed") is not True:
            return (
                "BLOCKED_WALLET_PREFLIGHT",
                "Run wallet preflight in safe mode until it is WALLET_PREP_READY.",
                "python -m app.execution.wallet_preflight_service",
            )
        if readiness.get("live_review_ready") is not True:
            return (
                "BLOCKED_LIVE_READINESS",
                "Continue paper/live-parity evidence; live readiness is not ready.",
                "python -m app.execution.live_readiness_checklist_service",
            )
        if tx_sim.get("transaction_simulation_passed") is not True:
            return (
                "BLOCKED_TRANSACTION_SIMULATION",
                "Transaction simulation must pass exact calldata and eth_call before any live send.",
                "python -m app.execution.transaction_simulation_service",
            )
        if pilot.get("overall_status") == "LIVE_PILOT_READY":
            if pilot_plan.get("allowance_sufficient") is True:
                return (
                    "READY_FOR_TINY_SWAP",
                    "Manual tiny one-leg smoke swap is ready; this is not continuous arbitrage.",
                    "python -m app.execution.tiny_live_pilot_service --mode swap --confirm LIVE_PILOT_APPROVED",
                )
            return (
                "READY_FOR_APPROVAL",
                "Manual USDC allowance approval is ready.",
                "python -m app.execution.tiny_live_pilot_service --mode approve --confirm LIVE_PILOT_APPROVED",
            )
        return (
            "BLOCKED_TINY_LIVE_PILOT",
            "Tiny live pilot is still blocked; review blocking checks.",
            "python -m app.execution.tiny_live_pilot_service --mode plan",
        )

    def _refresh_safe_reports(self) -> list[str]:
        errors: list[str] = []
        tasks = [
            ("provider_monitor", "app.operations.provider_monitor", "ProviderMonitorService"),
            ("wallet_preflight", "app.execution.wallet_preflight_service", "WalletPreflightService"),
            ("live_readiness", "app.execution.live_readiness_checklist_service", "LiveReadinessChecklistService"),
            ("transaction_simulation", "app.execution.transaction_simulation_service", "TransactionSimulationService"),
            ("live_readiness", "app.execution.live_readiness_checklist_service", "LiveReadinessChecklistService"),
            ("report_audit", "app.reporting.report_audit", "ReportAuditService"),
        ]
        for label, module_name, class_name in tasks:
            try:
                module = __import__(module_name, fromlist=[class_name])
                service_cls = getattr(module, class_name)
                service_cls(data_dir=self.data_dir, report_dir=self.report_dir).generate()
            except TypeError:
                try:
                    service_cls().generate()
                except Exception as exc:
                    errors.append(f"{label}: {type(exc).__name__}: {exc}")
            except Exception as exc:
                errors.append(f"{label}: {type(exc).__name__}: {exc}")
        return errors

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
    def _read_jsonl(path: Path, limit: int = 20) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                row = {"raw": line}
            rows.append(row)
        return rows[-limit:]

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# Live Control Center",
            "",
            f"Generated: `{payload['generated_at']}`",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Next action: `{payload['next_action']}`",
            f"- Next command: `{payload['next_command'] or '-'}`",
            f"- Continuous monitor: `{payload['continuous_monitor_command']}`",
            f"- Continuous live command: `{payload['continuous_live_trading_command']}`",
            f"- Continuous live status: `{payload['continuous_live_trading_status']}`",
            "",
            "## Wallet",
            "",
            "```json",
            json.dumps(payload["wallet"], indent=2),
            "```",
            "",
            "## Gates",
            "",
            "```json",
            json.dumps(payload["gates"], indent=2),
            "```",
            "",
            "## Blocking Checks",
            "",
            "| Source | Check | Severity | Detail |",
            "|---|---|---|---|",
        ]
        rows = payload["blocking_checks"] or payload["readiness_actions"] or payload["transaction_simulation_actions"]
        if rows:
            for row in rows[:20]:
                lines.append(f"| {row.get('source', '-')} | {row.get('name', '-')} | {row.get('severity', '-')} | {row.get('detail', '-')} |")
        else:
            lines.append("| - | - | PASS | No blocking checks. |")
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="CryptoAI live control center monitor")
    parser.add_argument("--loop", action="store_true", help="Continuously refresh read-only live control status.")
    parser.add_argument("--live-loop", action="store_true", help="Future continuous live entrypoint; currently monitors and refuses autonomous sends.")
    parser.add_argument("--interval", type=int, default=30, help="Loop interval in seconds.")
    parser.add_argument("--max-cycles", type=int, default=None, help="Optional cycle limit for tests/manual checks.")
    parser.add_argument("--no-refresh-plan", action="store_true", help="Do not refresh tiny_live_pilot plan before summarizing.")
    args = parser.parse_args()

    service = LiveControlCenterService()
    if args.live_loop:
        result = service.run_live_loop(interval=max(5, args.interval), max_cycles=args.max_cycles)
        print(json.dumps(result, indent=2))
    elif args.loop:
        result = service.run_loop(interval=max(5, args.interval), max_cycles=args.max_cycles)
        print(json.dumps(result, indent=2))
    else:
        payload = service.generate(refresh_plan=not args.no_refresh_plan)
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
