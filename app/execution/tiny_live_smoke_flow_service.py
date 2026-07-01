from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from app.execution.live_readiness_checklist_service import LiveReadinessChecklistService
from app.execution.tiny_live_pilot_service import TinyLivePilotService
from app.execution.transaction_simulation_service import TransactionSimulationService
from app.execution.wallet_preflight_service import WalletPreflightService


ReportRunner = Callable[[], dict[str, Any]]
PilotFactory = Callable[[], TinyLivePilotService]


class TinyLiveSmokeFlowService:
    """One-command wrapper for the manual tiny live smoke sequence.

    This orchestrates the existing gated services. It does not enable
    autonomous arbitrage and still requires one explicit confirmation phrase.
    """

    CONFIRM_PHRASE = "LIVE_SMOKE_FLOW_APPROVED"

    def __init__(
        self,
        report_dir: Path | str = "reports",
        pilot_factory: PilotFactory | None = None,
        safe_report_runner: ReportRunner | None = None,
    ) -> None:
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.output_json = self.report_dir / "tiny_live_smoke_flow.json"
        self.output_md = self.report_dir / "tiny_live_smoke_flow.md"
        self.pilot_factory = pilot_factory or TinyLivePilotService
        self.safe_report_runner = safe_report_runner or self._run_safe_reports

    def generate(self, *, mode: str = "plan", confirm: str = "") -> dict[str, Any]:
        mode = mode.strip().lower()
        if mode not in {"plan", "run"}:
            raise ValueError("mode must be plan or run")

        steps: list[dict[str, Any]] = []
        safe_before = self.safe_report_runner()
        steps.append(self._step("safe_reports_before", safe_before))

        pilot = self.pilot_factory()
        plan_before = pilot.generate(mode="plan")
        steps.append(self._step("plan_before", plan_before))

        blockers: list[str] = []
        send_attempted = False
        approve_payload: dict[str, Any] | None = None
        swap_payload: dict[str, Any] | None = None
        safe_after_approval: dict[str, Any] | None = None

        if plan_before.get("overall_status") != "LIVE_PILOT_READY":
            blockers.append("Tiny live pilot plan is not ready.")
        if mode == "run" and confirm != self.CONFIRM_PHRASE:
            blockers.append(f"Pass --confirm {self.CONFIRM_PHRASE} to run the live smoke flow.")

        if mode == "run" and not blockers:
            approval_needed = not bool(plan_before.get("pilot_plan", {}).get("allowance_sufficient"))
            if approval_needed:
                approve_payload = pilot.generate(mode="approve", confirm=TinyLivePilotService.CONFIRM_PHRASE)
                send_attempted = send_attempted or bool(approve_payload.get("send_attempted"))
                steps.append(self._step("approve", approve_payload))
                if approve_payload.get("overall_status") != "LIVE_PILOT_SENT":
                    blockers.append("Approval transaction was not sent successfully.")

            if not blockers:
                safe_after_approval = self.safe_report_runner()
                steps.append(self._step("safe_reports_after_approval", safe_after_approval))
                tx_report = safe_after_approval.get("transaction_simulation", {})
                if tx_report.get("transaction_simulation_passed") is not True:
                    blockers.append("Transaction simulation did not pass after approval.")

            if not blockers:
                swap_payload = pilot.generate(mode="swap", confirm=TinyLivePilotService.CONFIRM_PHRASE)
                send_attempted = send_attempted or bool(swap_payload.get("send_attempted"))
                steps.append(self._step("swap", swap_payload))
                if swap_payload.get("overall_status") != "LIVE_PILOT_SENT":
                    blockers.append("Smoke swap transaction was not sent successfully.")

        status = "LIVE_SMOKE_FLOW_SENT" if mode == "run" and not blockers and swap_payload else ("LIVE_SMOKE_FLOW_READY" if not blockers else "LIVE_SMOKE_FLOW_BLOCKED")
        payload = {
            "generated_at": self._utc_now(),
            "mode": mode,
            "overall_status": status,
            "send_attempted": send_attempted,
            "blocked_check_count": len(blockers),
            "blockers": blockers,
            "steps": steps,
            "notes": [
                "Tiny Live Smoke Flow is a capped one-leg smoke test only.",
                "It does not enable autonomous live arbitrage or continuous trading.",
                "One explicit confirmation phrase is required before any real-money send.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _run_safe_reports(self) -> dict[str, Any]:
        original = {
            "CRYPTOAI_PRIVATE_KEY": os.environ.get("CRYPTOAI_PRIVATE_KEY"),
            "CRYPTOAI_LIVE_TRADING_ENABLED": os.environ.get("CRYPTOAI_LIVE_TRADING_ENABLED"),
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": os.environ.get("CRYPTOAI_LIVE_KILL_SWITCH_ENABLED"),
        }
        try:
            os.environ.pop("CRYPTOAI_PRIVATE_KEY", None)
            os.environ["CRYPTOAI_LIVE_TRADING_ENABLED"] = "false"
            os.environ["CRYPTOAI_LIVE_KILL_SWITCH_ENABLED"] = "true"
            wallet = WalletPreflightService(report_dir=self.report_dir).generate()
            simulation = TransactionSimulationService(report_dir=self.report_dir).generate()
            readiness = LiveReadinessChecklistService(report_dir=self.report_dir).generate()
            return {
                "wallet_preflight": wallet,
                "transaction_simulation": simulation,
                "live_readiness": readiness,
            }
        finally:
            for key, value in original.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    @staticmethod
    def _step(name: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": name,
            "overall_status": payload.get("overall_status"),
            "send_attempted": payload.get("send_attempted", False),
            "blocked_check_count": payload.get("blocked_check_count"),
            "action_count": payload.get("action_count"),
        }

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# Tiny Live Smoke Flow",
            "",
            f"Generated: `{payload['generated_at']}`",
            f"- Mode: `{payload['mode']}`",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Send attempted: `{payload['send_attempted']}`",
            f"- Blockers: `{payload['blocked_check_count']}`",
            "",
            "## Steps",
            "",
            "| Step | Status | Send attempted |",
            "|---|---|---|",
        ]
        for step in payload["steps"]:
            lines.append(f"| {step['name']} | {step.get('overall_status')} | {step.get('send_attempted')} |")
        if payload["blockers"]:
            lines.extend(["", "## Blockers", ""])
            lines.extend(f"- {row}" for row in payload["blockers"])
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="CryptoAI tiny live smoke flow")
    parser.add_argument("--mode", choices=["plan", "run"], default="plan")
    parser.add_argument("--confirm", default="")
    args = parser.parse_args()
    payload = TinyLiveSmokeFlowService().generate(mode=args.mode, confirm=args.confirm)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
