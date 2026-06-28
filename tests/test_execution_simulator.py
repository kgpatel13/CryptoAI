from __future__ import annotations

import os
import unittest
from decimal import Decimal

from app.execution.execution_simulator import ExecutionSimulator
from app.execution.models import PaperOrderStatus


class ExecutionSimulatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.old_env = dict(os.environ)
        os.environ["CRYPTOAI_PAPER_SLIPPAGE_BPS"] = "5"
        os.environ["CRYPTOAI_PAPER_PARTIAL_FILL_RATIO"] = "1.00"

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self.old_env)

    def test_full_fill_lifecycle_has_expected_events(self) -> None:
        result = ExecutionSimulator().simulate_entry_order(
            timestamp="2026-06-28T00:00:00Z",
            pair="WETH/USDC",
            side="BUY",
            requested_notional_usd=Decimal("100"),
            reference_price_usd=Decimal("2000"),
            expected_edge_pct=Decimal("0.35"),
        )
        self.assertEqual(result.status, PaperOrderStatus.FILLED)
        self.assertEqual(result.filled_notional_usd, Decimal("100.0000"))
        self.assertEqual(result.execution_quality, "GOOD")
        self.assertEqual([event["status"] for event in result.lifecycle_events][:4], ["NEW", "VALIDATED", "SUBMITTED", "PENDING"])

    def test_partial_fill_ratio_creates_partial_fill(self) -> None:
        os.environ["CRYPTOAI_PAPER_PARTIAL_FILL_RATIO"] = "0.50"
        result = ExecutionSimulator().simulate_entry_order(
            timestamp="2026-06-28T00:00:00Z",
            pair="WETH/USDC",
            side="BUY",
            requested_notional_usd=Decimal("100"),
            reference_price_usd=Decimal("2000"),
            expected_edge_pct=Decimal("0.35"),
        )
        self.assertEqual(result.status, PaperOrderStatus.PARTIAL_FILL)
        self.assertEqual(result.filled_notional_usd, Decimal("50.0000"))
        self.assertEqual(result.execution_quality, "PARTIAL")


if __name__ == "__main__":
    unittest.main()
