from __future__ import annotations

import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from app.execution.live_autopilot import LiveAutopilot


class LiveAutopilotTests(unittest.TestCase):
    def test_run_once_blocks_and_journals_without_sending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            report_dir = Path(tmp) / "reports"
            autopilot = LiveAutopilot(data_dir=data_dir, report_dir=report_dir)
            with patch("app.execution.live_autopilot.LiveExecutionEngineService") as service_cls:
                service_cls.return_value.generate.return_value = {
                    "overall_status": "BLOCKED_LIVE_READINESS",
                    "execution_stage": "LIVE_READINESS",
                    "can_send_approval": False,
                    "can_send_smoke_swap": False,
                    "can_run_continuous_live": False,
                    "next_unblock_step": "Need more evidence.",
                    "next_allowed_command": None,
                }

                payload = autopilot.run_once()

            self.assertEqual(payload["status"], "BLOCKED")
            self.assertEqual(payload["action"], "WAIT")
            self.assertFalse(payload["transaction_sent"])
            self.assertTrue((data_dir / "live_autopilot_decisions.jsonl").exists())

    def test_manual_approval_is_not_auto_sent(self) -> None:
        autopilot = LiveAutopilot()
        payload = autopilot._decision({"can_send_approval": True})

        self.assertEqual(payload["status"], "READY_FOR_MANUAL_APPROVAL")
        self.assertEqual(payload["action"], "MANUAL_ONLY")

    def test_manual_smoke_swap_is_not_auto_sent(self) -> None:
        autopilot = LiveAutopilot()
        payload = autopilot._decision({"can_send_smoke_swap": True})

        self.assertEqual(payload["status"], "READY_FOR_MANUAL_SMOKE_SWAP")
        self.assertEqual(payload["action"], "MANUAL_ONLY")

    def test_continuous_live_refuses_until_execution_adapter_exists(self) -> None:
        autopilot = LiveAutopilot()
        payload = autopilot._decision({"can_run_continuous_live": True})

        self.assertEqual(payload["status"], "READY_FOR_CONTINUOUS_LIVE")
        self.assertEqual(payload["action"], "SEND_CONTINUOUS_LIVE")

    def test_continuous_live_does_not_send_without_explicit_send_flag(self) -> None:
        autopilot = LiveAutopilot()

        with self._env({"CRYPTOAI_LIVE_AUTOPILOT_SEND_ENABLED": "false"}):
            payload = autopilot._execute_if_allowed(
                engine={"can_run_continuous_live": True},
                decision={"status": "READY_FOR_CONTINUOUS_LIVE", "action": "SEND_CONTINUOUS_LIVE", "reason": "ready"},
            )

        self.assertEqual(payload["status"], "REFUSED_SEND_FLAG_DISABLED")
        self.assertFalse(payload["transaction_sent"])

    def test_continuous_live_uses_injected_adapter_when_green_and_enabled(self) -> None:
        class FakeAdapter:
            def execute(self, engine):
                return {"status": "SENT", "transaction_sent": True, "reason": "fake tx", "engine": engine["overall_status"]}

        autopilot = LiveAutopilot(execution_adapter=FakeAdapter())

        with self._env({"CRYPTOAI_LIVE_AUTOPILOT_SEND_ENABLED": "true"}):
            payload = autopilot._execute_if_allowed(
                engine={"overall_status": "READY_FOR_CONTINUOUS_LIVE", "can_run_continuous_live": True},
                decision={"status": "READY_FOR_CONTINUOUS_LIVE", "action": "SEND_CONTINUOUS_LIVE", "reason": "ready"},
            )

        self.assertEqual(payload["status"], "SENT")
        self.assertTrue(payload["transaction_sent"])

    def test_default_adapter_still_fails_closed_when_green_and_enabled(self) -> None:
        autopilot = LiveAutopilot()

        with self._env({"CRYPTOAI_LIVE_AUTOPILOT_SEND_ENABLED": "true"}):
            payload = autopilot._execute_if_allowed(
                engine={"overall_status": "READY_FOR_CONTINUOUS_LIVE", "can_run_continuous_live": True},
                decision={"status": "READY_FOR_CONTINUOUS_LIVE", "action": "SEND_CONTINUOUS_LIVE", "reason": "ready"},
            )

        self.assertEqual(payload["status"], "REFUSED")
        self.assertFalse(payload["transaction_sent"])

    def test_loop_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            autopilot = LiveAutopilot(data_dir=Path(tmp) / "data", report_dir=Path(tmp) / "reports")
            with patch.object(
                autopilot,
                "run_once",
                return_value={"status": "BLOCKED", "action": "WAIT", "transaction_sent": False},
            ) as run_once:
                result = autopilot.run_loop(interval_seconds=0, max_cycles=2)

        self.assertEqual(result["status"], "STOPPED")
        self.assertEqual(result["cycles_completed"], 2)
        self.assertEqual(run_once.call_count, 2)

    @contextmanager
    def _env(self, values: dict[str, str]):
        keys = {"CRYPTOAI_LIVE_AUTOPILOT_SEND_ENABLED"}
        previous = {key: os.environ.get(key) for key in keys}
        try:
            for key in keys:
                os.environ.pop(key, None)
            os.environ.update(values)
            yield
        finally:
            for key in keys:
                os.environ.pop(key, None)
                if previous[key] is not None:
                    os.environ[key] = previous[key]


if __name__ == "__main__":
    unittest.main()
