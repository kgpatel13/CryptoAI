from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.execution.live_control_center_service import LiveControlCenterService


class LiveControlCenterServiceTests(unittest.TestCase):
    def test_reports_blocked_readiness_without_live_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            service = LiveControlCenterService(data_dir=Path(tmp) / "data", report_dir=Path(tmp) / "reports")
            self._write_json(service.report_dir / "wallet_preflight.json", {"overall_status": "WALLET_PREP_READY", "wallet_preflight_allowed": True})
            self._write_json(service.report_dir / "live_readiness_checklist.json", {"overall_status": "LIVE_REVIEW_NOT_READY", "live_review_ready": False})
            self._write_json(service.report_dir / "transaction_simulation.json", {"overall_status": "TX_SIMULATION_ACTION", "transaction_simulation_passed": False})
            self._write_json(service.report_dir / "tiny_live_pilot.json", {"overall_status": "LIVE_PILOT_BLOCKED", "pilot_plan": {"usdc_balance": "449"}})

            payload = service.generate(refresh_plan=False)

        self.assertEqual(payload["overall_status"], "BLOCKED_LIVE_READINESS")
        self.assertIn("--live-loop", payload["continuous_live_trading_command"])
        self.assertEqual(payload["continuous_live_trading_status"], "NOT_AVAILABLE_UNTIL_LIVE_EXECUTOR")

    def test_ready_for_approval_when_all_gates_pass_and_allowance_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            service = LiveControlCenterService(data_dir=Path(tmp) / "data", report_dir=Path(tmp) / "reports")
            self._write_json(service.report_dir / "wallet_preflight.json", {"overall_status": "WALLET_PREP_READY", "wallet_preflight_allowed": True})
            self._write_json(service.report_dir / "live_readiness_checklist.json", {"overall_status": "LIVE_REVIEW_READY", "live_review_ready": True})
            self._write_json(service.report_dir / "transaction_simulation.json", {"overall_status": "TX_SIMULATION_READY", "transaction_simulation_passed": True})
            self._write_json(
                service.report_dir / "tiny_live_pilot.json",
                {
                    "overall_status": "LIVE_PILOT_READY",
                    "pilot_plan": {"allowance_sufficient": False, "approval_tx_available": True, "swap_tx_available": False},
                },
            )

            payload = service.generate(refresh_plan=False)

        self.assertEqual(payload["overall_status"], "READY_FOR_APPROVAL")
        self.assertIn("--mode approve", payload["next_command"])

    def test_loop_uses_read_only_generate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            service = LiveControlCenterService(data_dir=Path(tmp) / "data", report_dir=Path(tmp) / "reports")
            with patch.object(service, "generate", return_value={"generated_at": "now", "overall_status": "BLOCKED", "next_action": "wait", "wallet": {}}) as generate:
                result = service.run_loop(interval=0, max_cycles=2)

        self.assertEqual(result["status"], "STOPPED")
        self.assertEqual(result["cycles_completed"], 2)
        self.assertEqual(generate.call_count, 2)

    def test_live_loop_refuses_autonomous_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            service = LiveControlCenterService(data_dir=Path(tmp) / "data", report_dir=Path(tmp) / "reports")
            with patch.object(service, "generate", return_value={"generated_at": "now", "overall_status": "READY_FOR_TINY_SWAP", "next_action": "manual only", "continuous_live_trading_status": "NOT_AVAILABLE_UNTIL_LIVE_EXECUTOR", "continuous_monitor_command": "monitor"}) as generate:
                result = service.run_live_loop(interval=0, max_cycles=1)

        self.assertEqual(result["live_loop_status"], "REFUSED_AUTONOMOUS_EXECUTION")
        self.assertEqual(result["cycles_completed"], 1)
        self.assertEqual(generate.call_count, 1)

    @staticmethod
    def _write_json(path: Path, payload: dict) -> None:
        import json

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
