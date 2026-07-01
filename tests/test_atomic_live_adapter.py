from __future__ import annotations

import json
import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from app.execution.atomic_live_adapter import AtomicLiveExecutionAdapter, is_valid_evm_address


class AtomicLiveExecutionAdapterTests(unittest.TestCase):
    def test_validates_evm_address_shape(self) -> None:
        self.assertTrue(is_valid_evm_address("0x1111111111111111111111111111111111111111"))
        self.assertFalse(is_valid_evm_address("0xabc"))
        self.assertFalse(is_valid_evm_address(""))

    def test_refuses_when_atomic_executor_is_not_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adapter = AtomicLiveExecutionAdapter(report_dir=Path(tmp))
            result = adapter.execute({"overall_status": "READY_FOR_CONTINUOUS_LIVE", "can_run_continuous_live": True})

        self.assertEqual(result["status"], "REFUSED_ATOMIC_EXECUTOR_NOT_READY")
        self.assertFalse(result["transaction_sent"])

    def test_refuses_when_configured_but_atomic_send_flag_is_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_dir = Path(tmp)
            (report_dir / "live_pilot_reconciliation.json").write_text(
                json.dumps({"overall_status": "LIVE_PILOT_RECONCILED"}),
                encoding="utf-8",
            )
            adapter = AtomicLiveExecutionAdapter(report_dir=report_dir)
            with self._env(
                {
                    "CRYPTOAI_ATOMIC_EXECUTOR_ENABLED": "true",
                    "CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS": "0x1111111111111111111111111111111111111111",
                    "CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED": "true",
                    "CRYPTOAI_LIVE_EXECUTION_ADAPTER": "atomic",
                    "CRYPTOAI_PRIVATE_KEY": "test-key",
                }
            ):
                with patch(
                    "app.execution.atomic_live_adapter.AtomicArbitrageExecutionService.generate",
                    return_value={"overall_status": "ATOMIC_ROUTE_SIMULATION_PASSED", "atomic_route_simulation_passed": True},
                ):
                    result = adapter.execute(
                        {
                            "overall_status": "READY_FOR_CONTINUOUS_LIVE",
                            "can_run_continuous_live": True,
                            "gates": {"transaction_simulation_passed": True},
                        }
                    )

        self.assertEqual(result["status"], "REFUSED_ATOMIC_SEND_FLAG_DISABLED")
        self.assertFalse(result["transaction_sent"])

    @contextmanager
    def _env(self, values: dict[str, str]):
        keys = set(values)
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
