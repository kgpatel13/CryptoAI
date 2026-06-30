from __future__ import annotations

import os
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from app.risk.portfolio_risk_service import PortfolioRiskService


class PortfolioRiskServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.state_path = Path(self.tmp.name) / "state.json"
        self.old_env = dict(os.environ)
        os.environ["CRYPTOAI_PAPER_INITIAL_CASH_USD"] = "1000"
        os.environ["CRYPTOAI_PAPER_RISK_PER_TRADE_PCT"] = "10"
        os.environ["CRYPTOAI_PAPER_MAX_CASH_USAGE_PCT"] = "50"
        os.environ["CRYPTOAI_MAX_PAPER_NOTIONAL_USD"] = "250"
        os.environ["CRYPTOAI_MIN_PAPER_NOTIONAL_USD"] = "25"
        os.environ["CRYPTOAI_TRADE_COOLDOWN_SECONDS"] = "900"
        os.environ["CRYPTOAI_DUPLICATE_SIGNAL_WINDOW_SECONDS"] = "900"
        os.environ["CRYPTOAI_MAX_DAILY_PAPER_TRADES"] = "2"
        os.environ["CRYPTOAI_MAX_OPEN_POSITIONS"] = "3"

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self.old_env)
        self.tmp.cleanup()

    def service(self) -> PortfolioRiskService:
        return PortfolioRiskService(state_path=self.state_path)

    def test_dynamic_position_size_is_capped_by_risk(self) -> None:
        svc = self.service()
        decision = svc.assess(chain="base", pair="WETH/USDC", side="BUY", requested_notional_usd=Decimal("250"), now="2026-06-28T00:00:00Z")
        self.assertTrue(decision.approved)
        self.assertEqual(decision.notional_usd, Decimal("100.0000"))

    def test_duplicate_open_position_is_rejected(self) -> None:
        svc = self.service()
        svc.record_filled_order(order_id="abc123", timestamp="2026-06-28T00:00:00Z", strategy_name="test", chain="base", pair="WETH/USDC", side="BUY", notional_usd=Decimal("100"), fill_price_usd=Decimal("2000"), quantity=Decimal("0.05"))
        decision = svc.assess(chain="base", pair="WETH/USDC", side="BUY", requested_notional_usd=Decimal("100"), now="2026-06-28T00:05:00Z")
        self.assertFalse(decision.approved)
        self.assertIn("duplicate", decision.reason.lower())

    def test_cooldown_blocks_recent_same_signal_after_position_closed(self) -> None:
        svc = self.service()
        svc.record_filled_order(order_id="abc123", timestamp="2026-06-28T00:00:00Z", strategy_name="test", chain="base", pair="WETH/USDC", side="BUY", notional_usd=Decimal("100"), fill_price_usd=Decimal("2000"), quantity=Decimal("0.05"))
        state = svc.load_state()
        state["positions"][0]["status"] = "CLOSED"
        svc.save_state(state)
        decision = svc.assess(chain="base", pair="WETH/USDC", side="BUY", requested_notional_usd=Decimal("100"), now="2026-06-28T00:05:00Z")
        self.assertFalse(decision.approved)
        self.assertIn("cooldown", decision.reason.lower())

    def test_daily_trade_limit_blocks_after_limit(self) -> None:
        svc = self.service()
        svc.record_filled_order(order_id="a", timestamp="2026-06-28T00:00:00Z", strategy_name="test", chain="base", pair="WETH/USDC", side="BUY", notional_usd=Decimal("100"), fill_price_usd=Decimal("2000"), quantity=Decimal("0.05"))
        svc.record_filled_order(order_id="b", timestamp="2026-06-28T00:10:00Z", strategy_name="test", chain="base", pair="USDC/WETH", side="BUY", notional_usd=Decimal("100"), fill_price_usd=Decimal("1"), quantity=Decimal("100"))
        decision = svc.assess(chain="base", pair="CBETH/USDC", side="BUY", requested_notional_usd=Decimal("100"), now="2026-06-28T00:20:00Z")
        self.assertFalse(decision.approved)
        self.assertIn("max daily", decision.reason.lower())

    def test_zero_limits_disable_paper_throttles(self) -> None:
        os.environ["CRYPTOAI_MAX_DAILY_PAPER_TRADES"] = "0"
        os.environ["CRYPTOAI_MAX_OPEN_POSITIONS"] = "0"
        os.environ["CRYPTOAI_TRADE_COOLDOWN_SECONDS"] = "0"
        os.environ["CRYPTOAI_DUPLICATE_SIGNAL_WINDOW_SECONDS"] = "0"
        os.environ["CRYPTOAI_BLOCK_SAME_PAIR_OPEN_POSITION"] = "false"
        os.environ["CRYPTOAI_PAPER_RISK_PER_TRADE_PCT"] = "100"
        os.environ["CRYPTOAI_PAPER_MAX_CASH_USAGE_PCT"] = "100"
        os.environ["CRYPTOAI_MAX_TOKEN_EXPOSURE_PCT"] = "100"
        os.environ["CRYPTOAI_MAX_CHAIN_EXPOSURE_PCT"] = "100"
        svc = self.service()
        svc.record_filled_order(order_id="a", timestamp="2026-06-28T00:00:00Z", strategy_name="test", chain="base", pair="WETH/USDC", side="BUY", notional_usd=Decimal("100"), fill_price_usd=Decimal("2000"), quantity=Decimal("0.05"))
        svc.record_filled_order(order_id="b", timestamp="2026-06-28T00:01:00Z", strategy_name="test", chain="base", pair="WETH/USDC", side="BUY", notional_usd=Decimal("100"), fill_price_usd=Decimal("2000"), quantity=Decimal("0.05"))

        decision = svc.assess(chain="base", pair="WETH/USDC", side="BUY", requested_notional_usd=Decimal("100"), now="2026-06-28T00:02:00Z")

        self.assertTrue(decision.approved, decision.reason)
        self.assertEqual(decision.notional_usd, Decimal("100.0000"))

    def test_monitor_positions_closes_take_profit(self) -> None:
        svc = self.service()
        svc.record_filled_order(order_id="tp1", timestamp="2026-06-28T00:00:00Z", strategy_name="test", chain="base", pair="WETH/USDC", side="BUY", notional_usd=Decimal("100"), fill_price_usd=Decimal("2000"), quantity=Decimal("0.05"))
        result = svc.monitor_positions(prices={"WETH/USDC": Decimal("2100")}, now="2026-06-28T00:01:00Z")
        self.assertEqual(result.closed_positions, 1)
        state = svc.load_state()
        self.assertEqual(state["positions"][0]["status"], "CLOSED")
        self.assertEqual(state["positions"][0]["exit_reason"], "TAKE_PROFIT")

    def test_inverse_pair_accounting_does_not_create_huge_quantity(self) -> None:
        svc = self.service()
        svc.record_filled_order(
            order_id="inv1",
            timestamp="2026-06-28T00:00:00Z",
            strategy_name="test",
            chain="base",
            pair="USDC/WETH",
            side="BUY",
            notional_usd=Decimal("100"),
            fill_price_usd=Decimal("0.0005"),
            quantity=Decimal("200000"),
            estimated_edge_pct=Decimal("0.35"),
        )
        state = svc.load_state()
        pos = state["positions"][0]
        self.assertEqual(Decimal(pos["entry_price_usd"]), Decimal("1"))
        self.assertEqual(Decimal(pos["quantity"]), Decimal("100"))
        result = svc.monitor_positions(prices={"USDC": Decimal("1")}, now="2026-06-28T00:01:00Z")
        self.assertEqual(result.closed_positions, 0)
        self.assertLess(Decimal(svc.load_state()["cash_usd"]), Decimal("1000"))

    def test_legacy_inverse_pair_state_is_repaired(self) -> None:
        svc = self.service()
        bad_state = svc._initial_state()
        bad_state["version"] = "3.4"
        bad_state["cash_usd"] = "157573.8665"
        bad_state["realized_pnl_usd"] = "157473.8665"
        bad_state["daily_realized_pnl_usd"] = "157473.8665"
        bad_state["positions"] = [
            {
                "position_id": "bad",
                "order_id": "bad",
                "strategy_name": "test",
                "chain": "base",
                "pair": "USDC/WETH",
                "side": "BUY",
                "base_symbol": "USDC",
                "quote_symbol": "WETH",
                "quantity": "157823.8966300458592473904105",
                "entry_price_usd": "0.000633617608836572183",
                "current_price_usd": "0.000633617608836572183",
                "notional_usd": "100",
                "estimated_edge_pct": "0.35",
                "status": "CLOSED",
                "realized_pnl_usd": "157473.8665",
                "exit_value_usd": "157573.8665",
                "closed_at": "2026-06-28T00:10:00Z",
            }
        ]
        svc.save_state(bad_state)
        repaired = svc.load_state()
        self.assertEqual(repaired["version"], "3.4.1")
        self.assertEqual(Decimal(repaired["cash_usd"]), Decimal("1000.3500"))
        self.assertEqual(Decimal(repaired["realized_pnl_usd"]), Decimal("0.3500"))
        self.assertEqual(Decimal(repaired["positions"][0]["quantity"]), Decimal("100"))


if __name__ == "__main__":
    unittest.main()
