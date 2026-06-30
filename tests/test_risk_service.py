from __future__ import annotations

import os
import unittest
from decimal import Decimal
from types import SimpleNamespace

from app.risk.risk_service import RiskService


class RiskServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.old_env = dict(os.environ)
        os.environ["CRYPTOAI_LIVE_TRADING_ENABLED"] = "false"
        os.environ["CRYPTOAI_MIN_AI_SCORE_FOR_PAPER"] = "50"
        os.environ["CRYPTOAI_MIN_EDGE_FOR_PAPER_PCT"] = "0.30"
        os.environ["CRYPTOAI_DEFAULT_PAPER_NOTIONAL_USD"] = "100"
        os.environ["CRYPTOAI_MAX_PAPER_NOTIONAL_USD"] = "100000"

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self.old_env)

    def test_full_available_cash_sizing_requests_max_paper_notional(self) -> None:
        os.environ["CRYPTOAI_PAPER_SIZING_MODE"] = "full_available_cash"
        signal = SimpleNamespace(
            strategy_name="DEX Arbitrage Strategy",
            chain="base",
            pair="WETH/USDC",
            ai_score=80,
            expected_edge_pct=Decimal("0.35"),
            recommendation="PAPER_TRADE_CANDIDATE",
            source_action="READY_FOR_PAPER",
        )

        assessment = RiskService()._assess_one(signal)

        self.assertEqual(str(assessment.decision), "RiskDecision.APPROVED_FOR_PAPER")
        self.assertEqual(assessment.max_allowed_notional_usd, Decimal("100000"))

    def test_edge_scaled_sizing_keeps_existing_notional_behavior(self) -> None:
        os.environ["CRYPTOAI_PAPER_SIZING_MODE"] = "edge_scaled"
        signal = SimpleNamespace(
            strategy_name="DEX Arbitrage Strategy",
            chain="base",
            pair="WETH/USDC",
            ai_score=80,
            expected_edge_pct=Decimal("0.35"),
            recommendation="PAPER_TRADE_CANDIDATE",
            source_action="READY_FOR_PAPER",
        )

        assessment = RiskService()._assess_one(signal)

        self.assertEqual(assessment.max_allowed_notional_usd, Decimal("105.00"))


if __name__ == "__main__":
    unittest.main()
