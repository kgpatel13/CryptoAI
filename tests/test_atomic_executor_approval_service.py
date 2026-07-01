from __future__ import annotations

import os
import tempfile
import unittest
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from app.execution.atomic_executor_approval_service import AtomicApprovalPlan, AtomicExecutorApprovalService


class AtomicExecutorApprovalServiceTests(unittest.TestCase):
    def test_plan_is_read_only_and_blocks_without_executor_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            service = AtomicExecutorApprovalService(data_dir=Path(tmp) / "data", report_dir=Path(tmp) / "reports")
            with patch.object(
                service,
                "_prepare",
                return_value=AtomicApprovalPlan(
                    wallet_address="0x1111111111111111111111111111111111111111",
                    executor_address="0x2222222222222222222222222222222222222222",
                    approval_usd=Decimal("20"),
                    amount_units=20000000,
                    usdc_balance_units=100000000,
                    executor_code_bytes=1,
                ),
            ):
                payload = service.generate(mode="plan")

        self.assertEqual(payload["overall_status"], "ATOMIC_APPROVAL_BLOCKED")
        self.assertFalse(payload["send_attempted"])

    def test_approve_sends_when_explicitly_confirmed_and_green(self) -> None:
        sent_rows: list[dict] = []

        def fake_sender(tx, private_key):
            sent_rows.append({"tx": tx, "private_key": private_key})
            return {"tx_hash": "0xabc", "receipt_status": 1, "block_number": 123, "gas_used": 456}

        plan = AtomicApprovalPlan(
            wallet_address="0x1111111111111111111111111111111111111111",
            executor_address="0x2222222222222222222222222222222222222222",
            approval_usd=Decimal("20"),
            amount_units=20000000,
            usdc_balance_units=100000000,
            allowance_units=0,
            chain_id=8453,
            executor_code_bytes=1,
            approval_tx={"to": "0x3333333333333333333333333333333333333333", "data": "0x"},
        )

        env = {
            "CRYPTOAI_ENABLE_ATOMIC_EXECUTOR_APPROVAL": "true",
            "CRYPTOAI_LIVE_TRADING_ENABLED": "true",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": "false",
            "CRYPTOAI_ATOMIC_EXECUTOR_ENABLED": "true",
            "CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED": "true",
            "CRYPTOAI_PRIVATE_KEY": "test-key",
            "CRYPTOAI_LIVE_WALLET_ADDRESS": plan.wallet_address,
            "CRYPTOAI_MAX_LIVE_TRADE_USD": "20",
        }
        with tempfile.TemporaryDirectory() as tmp, self._env(env):
            service = AtomicExecutorApprovalService(data_dir=Path(tmp) / "data", report_dir=Path(tmp) / "reports", tx_sender=fake_sender)
            with patch.object(service, "_prepare", return_value=plan), patch.object(service, "_private_key_address", return_value=plan.wallet_address):
                payload = service.generate(mode="approve", confirm="ATOMIC_EXECUTOR_APPROVED")

        self.assertEqual(payload["overall_status"], "ATOMIC_APPROVAL_SENT")
        self.assertTrue(payload["send_attempted"])
        self.assertEqual(len(sent_rows), 1)

    @contextmanager
    def _env(self, values: dict[str, str]):
        keys = {
            "CRYPTOAI_ENABLE_ATOMIC_EXECUTOR_APPROVAL",
            "CRYPTOAI_LIVE_TRADING_ENABLED",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED",
            "CRYPTOAI_ATOMIC_EXECUTOR_ENABLED",
            "CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED",
            "CRYPTOAI_PRIVATE_KEY",
            "CRYPTOAI_LIVE_WALLET_ADDRESS",
            "CRYPTOAI_MAX_LIVE_TRADE_USD",
        }
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
