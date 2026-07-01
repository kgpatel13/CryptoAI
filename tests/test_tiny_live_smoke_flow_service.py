from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.execution.tiny_live_smoke_flow_service import TinyLiveSmokeFlowService


class FakePilotService:
    def __init__(self, *, allowance: bool = False) -> None:
        self.allowance = allowance
        self.calls: list[str] = []

    def generate(self, mode: str = "plan", confirm: str = "") -> dict:
        self.calls.append(mode)
        if mode == "plan":
            return {
                "overall_status": "LIVE_PILOT_READY",
                "send_attempted": False,
                "blocked_check_count": 0,
                "pilot_plan": {"allowance_sufficient": self.allowance},
            }
        if mode == "approve":
            self.allowance = True
            return {"overall_status": "LIVE_PILOT_SENT", "send_attempted": True, "blocked_check_count": 0}
        if mode == "swap":
            return {"overall_status": "LIVE_PILOT_SENT", "send_attempted": True, "blocked_check_count": 0}
        raise AssertionError(mode)


class TinyLiveSmokeFlowServiceTests(unittest.TestCase):
    def test_plan_mode_never_sends(self) -> None:
        pilot = FakePilotService(allowance=False)
        with tempfile.TemporaryDirectory() as tmp:
            payload = TinyLiveSmokeFlowService(
                report_dir=Path(tmp),
                pilot_factory=lambda: pilot,
                safe_report_runner=self._safe_reports,
            ).generate(mode="plan")

        self.assertEqual(payload["overall_status"], "LIVE_SMOKE_FLOW_READY")
        self.assertFalse(payload["send_attempted"])
        self.assertEqual(pilot.calls, ["plan"])

    def test_run_requires_confirmation(self) -> None:
        pilot = FakePilotService(allowance=False)
        with tempfile.TemporaryDirectory() as tmp:
            payload = TinyLiveSmokeFlowService(
                report_dir=Path(tmp),
                pilot_factory=lambda: pilot,
                safe_report_runner=self._safe_reports,
            ).generate(mode="run", confirm="")

        self.assertEqual(payload["overall_status"], "LIVE_SMOKE_FLOW_BLOCKED")
        self.assertFalse(payload["send_attempted"])
        self.assertIn("Pass --confirm LIVE_SMOKE_FLOW_APPROVED", payload["blockers"][0])

    def test_run_approves_resimulates_and_swaps(self) -> None:
        pilot = FakePilotService(allowance=False)
        with tempfile.TemporaryDirectory() as tmp:
            payload = TinyLiveSmokeFlowService(
                report_dir=Path(tmp),
                pilot_factory=lambda: pilot,
                safe_report_runner=self._safe_reports,
            ).generate(mode="run", confirm=TinyLiveSmokeFlowService.CONFIRM_PHRASE)

        self.assertEqual(payload["overall_status"], "LIVE_SMOKE_FLOW_SENT")
        self.assertTrue(payload["send_attempted"])
        self.assertEqual(pilot.calls, ["plan", "approve", "swap"])

    @staticmethod
    def _safe_reports() -> dict:
        return {
            "wallet_preflight": {"overall_status": "WALLET_PREP_READY", "wallet_preflight_allowed": True},
            "transaction_simulation": {"overall_status": "TX_SIMULATION_READY", "transaction_simulation_passed": True},
            "live_readiness": {"overall_status": "LIVE_REVIEW_NOT_READY", "blocked_check_count": 0},
        }


if __name__ == "__main__":
    unittest.main()
