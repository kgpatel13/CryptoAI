from __future__ import annotations

import argparse
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.execution.atomic_live_adapter import is_valid_evm_address, reviewed_atomic_adapter_selected
from app.execution.live_control_center_service import LiveControlCenterService
from app.execution.atomic_arbitrage_execution_service import AtomicArbitrageExecutionService


class LiveExecutionEngineService:
    """State machine for live execution readiness.

    The engine intentionally does not sign or send transactions. It converts the
    scattered live readiness reports into one execution workflow so the operator
    can see whether approval, a smoke swap, or continuous live arbitrage is
    allowed. Continuous live sends remain blocked until a reviewed atomic live
    arbitrage executor exists and every real-money gate is green.
    """

    MONITOR_COMMAND = "python -m app.execution.live_execution_engine_service --loop --interval 30"
    CONTROL_COMMAND = "python -m app.execution.live_control_center_service --loop --interval 30"
    APPROVE_COMMAND = "python -m app.execution.tiny_live_pilot_service --mode approve --confirm LIVE_PILOT_APPROVED"
    SMOKE_SWAP_COMMAND = "python -m app.execution.tiny_live_pilot_service --mode swap --confirm LIVE_PILOT_APPROVED"
    CONTINUOUS_LIVE_COMMAND = "python -m app.execution.live_autopilot --loop --interval-seconds 0"

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.output_json = self.report_dir / "live_execution_engine.json"
        self.output_md = self.report_dir / "live_execution_engine.md"

    def generate(self, refresh_control: bool = True) -> dict[str, Any]:
        refresh_errors: list[str] = []
        if refresh_control:
            try:
                LiveControlCenterService(data_dir=self.data_dir, report_dir=self.report_dir).generate(refresh_plan=True)
            except Exception as exc:
                refresh_errors.append(f"live_control_center: {type(exc).__name__}: {exc}")
            try:
                AtomicArbitrageExecutionService(data_dir=self.data_dir, report_dir=self.report_dir).generate()
            except Exception as exc:
                refresh_errors.append(f"atomic_live_arbitrage: {type(exc).__name__}: {exc}")

        control = self._read_json("live_control_center.json")
        wallet = self._read_json("wallet_preflight.json")
        readiness = self._read_json("live_readiness_checklist.json")
        tx_sim = self._read_json("transaction_simulation.json")
        pilot = self._read_json("tiny_live_pilot.json")
        provider = self._read_json("provider_monitor.json")
        audit = self._read_json("report_audit.json")
        safety = self._read_json("live_safety.json")
        atomic = self._read_json("atomic_live_arbitrage.json")

        state = self._state(
            control=control,
            wallet=wallet,
            readiness=readiness,
            tx_sim=tx_sim,
            pilot=pilot,
            provider=provider,
            audit=audit,
            safety=safety,
            atomic=atomic,
        )
        payload = {
            "generated_at": self._utc_now(),
            "mode": "live_execution_engine",
            "overall_status": state["overall_status"],
            "execution_stage": state["execution_stage"],
            "can_send_approval": state["can_send_approval"],
            "can_send_smoke_swap": state["can_send_smoke_swap"],
            "can_run_continuous_live": state["can_run_continuous_live"],
            "next_unblock_step": state["next_unblock_step"],
            "next_allowed_command": state["next_allowed_command"],
            "commands": {
                "safe_live_monitor": self.CONTROL_COMMAND,
                "live_execution_monitor": self.MONITOR_COMMAND,
                "approval": self.APPROVE_COMMAND if state["can_send_approval"] else None,
                "smoke_swap": self.SMOKE_SWAP_COMMAND if state["can_send_smoke_swap"] else None,
                "continuous_live": self.CONTINUOUS_LIVE_COMMAND if state["can_run_continuous_live"] else None,
            },
            "refresh_errors": refresh_errors,
            "gates": state["gates"],
            "atomic_executor": state["atomic_executor"],
            "blockers": state["blockers"],
            "missing_components": state["missing_components"],
            "unblock_path": self._unblock_path(),
            "wallet": control.get("wallet", {}) if isinstance(control.get("wallet"), dict) else {},
            "notes": [
                "This engine is an execution-readiness state machine. It never signs, approves, swaps, or runs autonomous live arbitrage.",
                "Manual approval and manual smoke-swap commands appear only when all prerequisite reports permit them.",
                "Continuous live arbitrage requires a reviewed atomic executor path plus the live autopilot send flag; the current tiny pilot is one-leg smoke testing only.",
                "Paper profits do not guarantee live profits because live execution can fail from gas, slippage, MEV, reverts, nonce issues, and pool movement.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def run_loop(self, interval: int = 30, max_cycles: int | None = None) -> dict[str, Any]:
        cycles = 0
        last_payload: dict[str, Any] = {}
        print(f"CryptoAI live execution engine monitor started. Interval: {interval}s")
        print("Read-only execution state machine. It will not send live transactions.")
        try:
            while True:
                cycles += 1
                last_payload = self.generate(refresh_control=True)
                print(
                    json.dumps(
                        {
                            "cycle": cycles,
                            "generated_at": last_payload.get("generated_at"),
                            "overall_status": last_payload.get("overall_status"),
                            "execution_stage": last_payload.get("execution_stage"),
                            "can_send_approval": last_payload.get("can_send_approval"),
                            "can_send_smoke_swap": last_payload.get("can_send_smoke_swap"),
                            "can_run_continuous_live": last_payload.get("can_run_continuous_live"),
                            "next_unblock_step": last_payload.get("next_unblock_step"),
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

    def _state(
        self,
        *,
        control: dict[str, Any],
        wallet: dict[str, Any],
        readiness: dict[str, Any],
        tx_sim: dict[str, Any],
        pilot: dict[str, Any],
        provider: dict[str, Any],
        audit: dict[str, Any],
        safety: dict[str, Any],
        atomic: dict[str, Any],
    ) -> dict[str, Any]:
        pilot_plan = pilot.get("pilot_plan", {}) if isinstance(pilot.get("pilot_plan"), dict) else {}
        gates = {
            "wallet_preflight_allowed": wallet.get("wallet_preflight_allowed") is True,
            "live_review_ready": readiness.get("live_review_ready") is True,
            "transaction_simulation_passed": tx_sim.get("transaction_simulation_passed") is True,
            "provider_monitor_ok": provider.get("overall_status") == "OK",
            "report_audit_clean": self._int(audit.get("blocking_finding_count", audit.get("finding_count"))) == 0,
            "tiny_live_pilot_ready": pilot.get("overall_status") == "LIVE_PILOT_READY",
            "allowance_sufficient": pilot_plan.get("allowance_sufficient") is True,
            "approval_tx_available": pilot_plan.get("approval_tx_available") is True,
            "swap_tx_available": pilot_plan.get("swap_tx_available") is True,
            "live_safety_report_present": bool(safety),
            "live_control_center_present": bool(control),
            "atomic_executor_ready": self._atomic_executor_details()["ready"],
            "atomic_route_simulation_passed": atomic.get("atomic_route_simulation_passed") is True,
        }
        blockers = self._blockers(
            control=control,
            readiness=readiness,
            tx_sim=tx_sim,
            pilot=pilot,
            gates=gates,
            atomic=atomic,
        )
        missing_components = self._missing_components(gates)
        atomic_attempted = atomic.get("overall_status") == "ATOMIC_ROUTE_ACTION" and bool(atomic.get("atomic_route"))
        atomic_profit_blocked = atomic_attempted and atomic.get("atomic_route_simulation_passed") is not True

        prerequisite_ready = (
            gates["wallet_preflight_allowed"]
            and gates["live_review_ready"]
            and (gates["transaction_simulation_passed"] or gates["atomic_route_simulation_passed"])
            and gates["provider_monitor_ok"]
            and gates["report_audit_clean"]
            and gates["tiny_live_pilot_ready"]
        )
        can_send_approval = prerequisite_ready and gates["approval_tx_available"] and not gates["allowance_sufficient"]
        can_send_smoke_swap = prerequisite_ready and gates["allowance_sufficient"] and gates["swap_tx_available"]
        can_run_continuous_live = prerequisite_ready and gates["atomic_executor_ready"] and gates["atomic_route_simulation_passed"] and can_send_smoke_swap

        if can_run_continuous_live:
            status = "READY_FOR_CONTINUOUS_LIVE"
            stage = "CONTINUOUS_LIVE_READY"
        elif can_send_smoke_swap:
            status = "READY_FOR_MANUAL_SMOKE_SWAP"
            stage = "TINY_LIVE_SMOKE_SWAP"
        elif can_send_approval:
            status = "READY_FOR_MANUAL_APPROVAL"
            stage = "TOKEN_ALLOWANCE_APPROVAL"
        elif atomic_profit_blocked:
            status = "BLOCKED_ATOMIC_ROUTE_SIMULATION"
            stage = "ATOMIC_ARBITRAGE_ETH_CALL"
        elif not gates["wallet_preflight_allowed"]:
            status = "BLOCKED_PREFLIGHT"
            stage = "WALLET_PREFLIGHT"
        elif not gates["live_review_ready"]:
            status = "BLOCKED_LIVE_READINESS"
            stage = "LIVE_READINESS"
        elif not gates["transaction_simulation_passed"] and not gates["atomic_route_simulation_passed"]:
            status = "BLOCKED_TRANSACTION_SIMULATION"
            stage = "EXACT_CALLDATA_ETH_CALL"
        elif not gates["tiny_live_pilot_ready"]:
            status = "BLOCKED_TINY_LIVE_PILOT"
            stage = "TINY_LIVE_PLAN"
        elif not gates["atomic_executor_ready"]:
            status = "BLOCKED_ATOMIC_EXECUTOR_MISSING"
            stage = "ATOMIC_ARBITRAGE_EXECUTOR"
        elif not gates["atomic_route_simulation_passed"]:
            status = "BLOCKED_ATOMIC_ROUTE_SIMULATION"
            stage = "ATOMIC_ARBITRAGE_ETH_CALL"
        else:
            status = "BLOCKED_LIVE_AUTOMATION"
            stage = "LIVE_AUTOMATION_REVIEW"

        next_command = None
        if can_send_approval:
            next_command = self.APPROVE_COMMAND
        elif can_send_smoke_swap:
            next_command = self.SMOKE_SWAP_COMMAND

        return {
            "overall_status": status,
            "execution_stage": stage,
            "can_send_approval": can_send_approval,
            "can_send_smoke_swap": can_send_smoke_swap,
            "can_run_continuous_live": can_run_continuous_live,
            "next_unblock_step": blockers[0]["detail"] if blockers else ("Manual tiny smoke swap is the next reviewed step." if can_send_smoke_swap else "No blocker detected."),
            "next_allowed_command": next_command,
            "gates": gates,
            "atomic_executor": self._atomic_executor_details(),
            "blockers": blockers,
            "missing_components": missing_components,
        }

    def _blockers(
        self,
        *,
        control: dict[str, Any],
        readiness: dict[str, Any],
        tx_sim: dict[str, Any],
        pilot: dict[str, Any],
        gates: dict[str, bool],
        atomic: dict[str, Any],
    ) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        atomic_route = atomic.get("atomic_route", {}) if isinstance(atomic.get("atomic_route"), dict) else {}
        decoded_error = atomic_route.get("eth_call_decoded_error", {}) if isinstance(atomic_route.get("eth_call_decoded_error"), dict) else {}
        reconciliation = atomic.get("profit_reconciliation", {}) if isinstance(atomic.get("profit_reconciliation"), dict) else {}
        if atomic.get("overall_status") == "ATOMIC_ROUTE_ACTION" and atomic.get("atomic_route_simulation_passed") is not True:
            detail = "Atomic executor eth_call did not pass."
            if decoded_error.get("name") == "ProfitTooLow":
                detail = (
                    "Atomic executor rejected the route as ProfitTooLow: "
                    f"simulated output {decoded_error.get('amount_out_usdc')} USDC, "
                    f"required {decoded_error.get('required_out_usdc')} USDC."
                )
            elif reconciliation.get("status"):
                detail = f"Atomic route reconciliation status: {reconciliation.get('status')}."
            rows.append(
                {
                    "source": "atomic_live_arbitrage",
                    "name": "atomic_route_simulation_passed",
                    "severity": "BLOCK",
                    "detail": detail,
                }
            )
        gate_details = [
            ("wallet_preflight_allowed", "Wallet preflight is not ready for the isolated Base wallet."),
            ("live_review_ready", "Live readiness is not ready: paper/live caps, cost confidence, realism, or audit evidence still need work."),
            ("provider_monitor_ok", "Provider monitor must be OK before any live send."),
            ("report_audit_clean", "Report audit still has blocking findings."),
            ("tiny_live_pilot_ready", "Tiny live pilot plan is blocked."),
        ]
        for name, detail in gate_details:
            if not gates[name]:
                rows.append({"source": "live_execution_engine", "name": name, "severity": "BLOCK", "detail": detail})
        if not gates["transaction_simulation_passed"] and not gates.get("atomic_route_simulation_passed", False):
            rows.append(
                {
                    "source": "live_execution_engine",
                    "name": "transaction_or_atomic_simulation_passed",
                    "severity": "BLOCK",
                    "detail": "Either standalone transaction simulation or atomic executor eth_call simulation must pass.",
                }
            )

        for source_name, payload, key in [
            ("live_control_center", control, "blocking_checks"),
            ("live_readiness", readiness, "checks"),
            ("transaction_simulation", tx_sim, "checks"),
            ("tiny_live_pilot", pilot, "checks"),
        ]:
            raw_rows = payload.get(key, [])
            if not isinstance(raw_rows, list):
                continue
            for row in raw_rows:
                severity = str(row.get("severity", ""))
                passed = row.get("passed")
                if severity in {"BLOCK", "ACTION"} or passed is False:
                    rows.append(
                        {
                            "source": source_name,
                            "name": str(row.get("name", "-")),
                            "severity": severity or "ACTION",
                            "detail": str(row.get("detail", "-")),
                        }
                    )
        if not gates["atomic_executor_ready"]:
            rows.append(
                {
                    "source": "live_execution_engine",
                    "name": "atomic_executor_ready",
                    "severity": "ACTION",
                    "detail": "Continuous live arbitrage is blocked until an atomic route executor is deployed, reviewed, selected as the live adapter, and backed by reviewed calldata.",
                }
            )
        if not gates.get("atomic_route_simulation_passed", False):
            rows.append(
                {
                    "source": "live_execution_engine",
                    "name": "atomic_route_simulation_passed",
                    "severity": "ACTION",
                    "detail": "Run python -m app.execution.atomic_arbitrage_execution_service --generate until the atomic executor calldata eth_call passes.",
                }
            )
        return rows[:50]

    @staticmethod
    def _missing_components(gates: dict[str, bool]) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        if not gates["atomic_executor_ready"]:
            rows.append(
                {
                    "component": "atomic_live_arbitrage_executor",
                    "status": "MISSING",
                    "detail": "Required before continuous live arbitrage; manual tiny smoke swap is only one-leg execution.",
                }
            )
        if not gates["transaction_simulation_passed"] and not gates.get("atomic_route_simulation_passed", False):
            rows.append(
                {
                    "component": "exact_calldata_eth_call_pass",
                    "status": "ACTION",
                    "detail": "Need a SHADOW_READY Base USDC/WETH opportunity with exact calldata built and eth_call PASS.",
                }
            )
        if not gates.get("atomic_route_simulation_passed", False):
            rows.append(
                {
                    "component": "atomic_executor_eth_call_pass",
                    "status": "ACTION",
                    "detail": "Need one passing eth_call for the exact atomic executor transaction before continuous live can run.",
                }
            )
        return rows

    @staticmethod
    def _unblock_path() -> list[dict[str, str]]:
        return [
            {"step": "1", "name": "Live-parity paper profile", "detail": "Paper max trade and observed fills must stay at or below the live cap, e.g. $20 for the tiny pilot."},
            {"step": "2", "name": "Execution evidence", "detail": "Execution-cost confidence must reach HIGH and execution realism must produce SHADOW_READY opportunities."},
            {"step": "3", "name": "Transaction simulation", "detail": "Build exact Base calldata and pass eth_call for the selected USDC/WETH route."},
            {"step": "4", "name": "Manual tiny live pilot", "detail": "Run approval and one tiny smoke swap only when the engine shows READY_FOR_MANUAL_APPROVAL or READY_FOR_MANUAL_SMOKE_SWAP."},
            {"step": "5", "name": "Atomic live executor", "detail": "Deploy/review the single-transaction arbitrage executor, approve USDC to that executor, and pass the atomic executor eth_call report before continuous live trading is allowed."},
        ]

    @staticmethod
    def _atomic_executor_ready() -> bool:
        return LiveExecutionEngineService._atomic_executor_details()["ready"]

    @staticmethod
    def _atomic_executor_details() -> dict[str, Any]:
        enabled = os.getenv("CRYPTOAI_ATOMIC_EXECUTOR_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}
        reviewed = os.getenv("CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED", "").strip().lower() in {"1", "true", "yes", "on"}
        address = os.getenv("CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS", "").strip()
        address_valid = is_valid_evm_address(address)
        adapter_selected = reviewed_atomic_adapter_selected()
        return {
            "enabled": enabled,
            "address": address or None,
            "address_valid": address_valid,
            "reviewed": reviewed,
            "adapter_selected": adapter_selected,
            "ready": enabled and address_valid and reviewed and adapter_selected,
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

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# Live Execution Engine",
            "",
            f"Generated: `{payload['generated_at']}`",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Execution stage: `{payload['execution_stage']}`",
            f"- Can send approval: `{payload['can_send_approval']}`",
            f"- Can send smoke swap: `{payload['can_send_smoke_swap']}`",
            f"- Can run continuous live: `{payload['can_run_continuous_live']}`",
            f"- Next unblock step: `{payload['next_unblock_step']}`",
            "",
            "## Commands",
            "",
            "```json",
            json.dumps(payload["commands"], indent=2),
            "```",
            "",
            "## Gates",
            "",
            "```json",
            json.dumps(payload["gates"], indent=2),
            "```",
            "",
            "## Atomic Executor",
            "",
            "```json",
            json.dumps(payload["atomic_executor"], indent=2),
            "```",
            "",
            "## Blockers",
            "",
            "| Source | Check | Severity | Detail |",
            "|---|---|---|---|",
        ]
        if payload["blockers"]:
            for row in payload["blockers"][:30]:
                lines.append(f"| {row.get('source', '-')} | {row.get('name', '-')} | {row.get('severity', '-')} | {row.get('detail', '-')} |")
        else:
            lines.append("| - | - | PASS | No blockers. |")
        lines.extend(["", "## Unblock Path", "", "| Step | Name | Detail |", "|---|---|---|"])
        for row in payload["unblock_path"]:
            lines.append(f"| {row['step']} | {row['name']} | {row['detail']} |")
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _int(value: Any) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="CryptoAI live execution engine monitor")
    parser.add_argument("--loop", action="store_true", help="Continuously refresh read-only live execution status.")
    parser.add_argument("--interval", type=int, default=30, help="Loop interval in seconds.")
    parser.add_argument("--max-cycles", type=int, default=None, help="Optional cycle limit for tests/manual checks.")
    parser.add_argument("--no-refresh-control", action="store_true", help="Do not refresh live control reports before summarizing.")
    args = parser.parse_args()

    service = LiveExecutionEngineService()
    if args.loop:
        result = service.run_loop(interval=max(5, args.interval), max_cycles=args.max_cycles)
        print(json.dumps(result, indent=2))
    else:
        payload = service.generate(refresh_control=not args.no_refresh_control)
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
