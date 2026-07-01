from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.execution.live_execution_engine_service import LiveExecutionEngineService


class LiveExecutionEngineServiceTests(unittest.TestCase):
    def test_blocks_when_live_readiness_is_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            service = LiveExecutionEngineService(data_dir=Path(tmp) / "data", report_dir=Path(tmp) / "reports")
            self._write_ready_wallet(service)
            self._write_json(service.report_dir / "live_readiness_checklist.json", {"live_review_ready": False, "checks": []})
            self._write_json(service.report_dir / "transaction_simulation.json", {"transaction_simulation_passed": False, "checks": []})
            self._write_json(service.report_dir / "provider_monitor.json", {"overall_status": "OK"})
            self._write_json(service.report_dir / "report_audit.json", {"blocking_finding_count": 0})
            self._write_json(service.report_dir / "tiny_live_pilot.json", {"overall_status": "LIVE_PILOT_BLOCKED", "pilot_plan": {}})

            payload = service.generate(refresh_control=False)

        self.assertEqual(payload["overall_status"], "BLOCKED_LIVE_READINESS")
        self.assertFalse(payload["can_send_approval"])
        self.assertFalse(payload["can_send_smoke_swap"])
        self.assertFalse(payload["can_run_continuous_live"])
        self.assertIsNone(payload["commands"]["approval"])

    def test_ready_for_manual_approval_when_all_gates_pass_and_allowance_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            service = LiveExecutionEngineService(data_dir=Path(tmp) / "data", report_dir=Path(tmp) / "reports")
            self._write_all_green(service, allowance_sufficient=False, swap_available=False)

            payload = service.generate(refresh_control=False)

        self.assertEqual(payload["overall_status"], "READY_FOR_MANUAL_APPROVAL")
        self.assertTrue(payload["can_send_approval"])
        self.assertFalse(payload["can_send_smoke_swap"])
        self.assertIn("--mode approve", payload["commands"]["approval"])
        self.assertIsNone(payload["commands"]["smoke_swap"])
        self.assertFalse(payload["can_run_continuous_live"])

    def test_ready_for_manual_smoke_swap_but_not_continuous_without_atomic_executor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            service = LiveExecutionEngineService(data_dir=Path(tmp) / "data", report_dir=Path(tmp) / "reports")
            self._write_all_green(service, allowance_sufficient=True, swap_available=True)

            payload = service.generate(refresh_control=False)

        self.assertEqual(payload["overall_status"], "READY_FOR_MANUAL_SMOKE_SWAP")
        self.assertFalse(payload["can_send_approval"])
        self.assertTrue(payload["can_send_smoke_swap"])
        self.assertFalse(payload["can_run_continuous_live"])
        self.assertIn("atomic_live_arbitrage_executor", {row["component"] for row in payload["missing_components"]})

    def test_continuous_live_requires_reviewed_atomic_executor_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            service = LiveExecutionEngineService(data_dir=Path(tmp) / "data", report_dir=Path(tmp) / "reports")
            self._write_all_green(service, allowance_sufficient=True, swap_available=True)
            self._write_json(service.report_dir / "atomic_live_arbitrage.json", {"atomic_route_simulation_passed": True})
            with patch.dict(
                "os.environ",
                {
                    "CRYPTOAI_ATOMIC_EXECUTOR_ENABLED": "true",
                    "CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS": "0x1111111111111111111111111111111111111111",
                    "CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED": "true",
                    "CRYPTOAI_LIVE_EXECUTION_ADAPTER": "atomic",
                },
                clear=False,
            ):
                payload = service.generate(refresh_control=False)

        self.assertEqual(payload["overall_status"], "READY_FOR_CONTINUOUS_LIVE")
        self.assertTrue(payload["can_run_continuous_live"])
        self.assertTrue(payload["atomic_executor"]["ready"])

    def test_continuous_live_blocks_invalid_atomic_executor_address(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            service = LiveExecutionEngineService(data_dir=Path(tmp) / "data", report_dir=Path(tmp) / "reports")
            self._write_all_green(service, allowance_sufficient=True, swap_available=True)
            with patch.dict(
                "os.environ",
                {
                    "CRYPTOAI_ATOMIC_EXECUTOR_ENABLED": "true",
                    "CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS": "0xabc",
                    "CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED": "true",
                    "CRYPTOAI_LIVE_EXECUTION_ADAPTER": "atomic",
                },
                clear=False,
            ):
                payload = service.generate(refresh_control=False)

        self.assertEqual(payload["overall_status"], "READY_FOR_MANUAL_SMOKE_SWAP")
        self.assertFalse(payload["can_run_continuous_live"])
        self.assertFalse(payload["atomic_executor"]["address_valid"])

    def test_loop_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            service = LiveExecutionEngineService(data_dir=Path(tmp) / "data", report_dir=Path(tmp) / "reports")
            with patch.object(service, "generate", return_value={"generated_at": "now", "overall_status": "BLOCKED", "execution_stage": "TEST"}) as generate:
                result = service.run_loop(interval=0, max_cycles=2)

        self.assertEqual(result["status"], "STOPPED")
        self.assertEqual(result["cycles_completed"], 2)
        self.assertEqual(generate.call_count, 2)

    def _write_all_green(self, service: LiveExecutionEngineService, *, allowance_sufficient: bool, swap_available: bool) -> None:
        self._write_ready_wallet(service)
        self._write_json(service.report_dir / "live_readiness_checklist.json", {"live_review_ready": True, "checks": []})
        self._write_json(service.report_dir / "transaction_simulation.json", {"transaction_simulation_passed": True, "checks": []})
        self._write_json(service.report_dir / "provider_monitor.json", {"overall_status": "OK"})
        self._write_json(service.report_dir / "report_audit.json", {"blocking_finding_count": 0})
        self._write_json(service.report_dir / "live_safety.json", {"overall_status": "LIVE_BLOCKED"})
        self._write_json(
            service.report_dir / "tiny_live_pilot.json",
            {
                "overall_status": "LIVE_PILOT_READY",
                "checks": [],
                "pilot_plan": {
                    "allowance_sufficient": allowance_sufficient,
                    "approval_tx_available": True,
                    "swap_tx_available": swap_available,
                },
            },
        )

    def _write_ready_wallet(self, service: LiveExecutionEngineService) -> None:
        self._write_json(service.report_dir / "wallet_preflight.json", {"wallet_preflight_allowed": True})

    @staticmethod
    def _write_json(path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
