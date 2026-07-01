from __future__ import annotations

import json
import os
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

from app.execution.models import PaperOrderStatus
from app.execution.paper_execution_service import PaperExecutionService
from app.risk.portfolio_risk_service import PortfolioRiskService


class ArbitrageExecutionEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.old_env = dict(os.environ)
        os.environ["CRYPTOAI_PAPER_INITIAL_CASH_USD"] = "10000"
        os.environ["CRYPTOAI_DEFAULT_PAPER_NOTIONAL_USD"] = "10000"
        os.environ["CRYPTOAI_MAX_PAPER_NOTIONAL_USD"] = "1000000"
        os.environ["CRYPTOAI_MIN_PAPER_NOTIONAL_USD"] = "25"
        os.environ["CRYPTOAI_PAPER_RISK_PER_TRADE_PCT"] = "100"
        os.environ["CRYPTOAI_PAPER_MAX_CASH_USAGE_PCT"] = "100"
        os.environ["CRYPTOAI_MAX_TOKEN_EXPOSURE_PCT"] = "100"
        os.environ["CRYPTOAI_MAX_CHAIN_EXPOSURE_PCT"] = "100"
        os.environ["CRYPTOAI_MAX_DAILY_PAPER_TRADES"] = "0"
        os.environ["CRYPTOAI_MAX_OPEN_POSITIONS"] = "1"
        os.environ["CRYPTOAI_TRADE_COOLDOWN_SECONDS"] = "0"
        os.environ["CRYPTOAI_DUPLICATE_SIGNAL_WINDOW_SECONDS"] = "0"
        os.environ["CRYPTOAI_BLOCK_SAME_PAIR_OPEN_POSITION"] = "true"
        os.environ["CRYPTOAI_PAPER_SIZING_MODE"] = "full_available_cash"
        os.environ["CRYPTOAI_PAPER_SLIPPAGE_BPS"] = "5"
        os.environ["CRYPTOAI_PAPER_PARTIAL_FILL_RATIO"] = "1.00"

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self.old_env)

    def test_paper_arbitrage_closes_immediately_and_reconciles_cash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            data.mkdir()
            self._write_buy_opportunity(data)
            portfolio = PortfolioRiskService(state_path=data / "paper_portfolio_state.json")
            service = PaperExecutionService(data_dir=data, portfolio_risk=portfolio)
            service._load_risk_assessments = lambda: [self._assessment()]  # type: ignore[method-assign]

            batch = service.run_once()
            state = portfolio.load_state()
            orders = self._read_jsonl(data / "paper_orders.jsonl")

            self.assertEqual(batch.filled_orders, 1)
            self.assertEqual(orders[0]["status"], PaperOrderStatus.CLOSED.value)
            self.assertEqual(orders[0]["execution_type"], "ARBITRAGE_ROUND_TRIP")
            self.assertEqual(orders[0]["buy_source"], "Uniswap V2")
            self.assertEqual(orders[0]["sell_source"], "Uniswap V3")
            self.assertEqual(Decimal(orders[0]["notional_usd"]), Decimal("10000.0000"))
            self.assertEqual(Decimal(orders[0]["realized_pnl_usd"]), Decimal("35.0000"))
            self.assertEqual(state["positions"], [])
            self.assertEqual(len(state["arbitrage_trades"]), 1)
            self.assertEqual(Decimal(state["cash_usd"]), Decimal("10035.0000"))
            self.assertEqual(Decimal(state["realized_pnl_usd"]), Decimal("35.0000"))

    def test_multiple_full_cash_arbitrage_trades_do_not_create_open_exposure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            data.mkdir()
            self._write_buy_opportunity(data)
            portfolio = PortfolioRiskService(state_path=data / "paper_portfolio_state.json")
            service = PaperExecutionService(data_dir=data, portfolio_risk=portfolio)
            service._load_risk_assessments = lambda: [self._assessment(), self._assessment()]  # type: ignore[method-assign]

            batch = service.run_once()
            state = portfolio.load_state()
            orders = self._read_jsonl(data / "paper_orders.jsonl")

            self.assertEqual(batch.filled_orders, 2)
            self.assertTrue(all(row["status"] == "CLOSED" for row in orders))
            self.assertEqual(state["positions"], [])
            self.assertEqual(len(state["arbitrage_trades"]), 2)
            expected_cash = Decimal("10000") + Decimal(orders[0]["realized_pnl_usd"]) + Decimal(orders[1]["realized_pnl_usd"])
            self.assertEqual(Decimal(state["cash_usd"]), expected_cash.quantize(Decimal("0.0000")))

    def test_duplicate_arbitrage_signal_fingerprint_blocks_second_identical_trade(self) -> None:
        os.environ["CRYPTOAI_ARBITRAGE_SIGNAL_FINGERPRINT_WINDOW_SECONDS"] = "60"
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            data.mkdir()
            self._write_buy_opportunity(data)
            portfolio = PortfolioRiskService(state_path=data / "paper_portfolio_state.json")
            service = PaperExecutionService(data_dir=data, portfolio_risk=portfolio)
            service._load_risk_assessments = lambda: [self._assessment(), self._assessment()]  # type: ignore[method-assign]

            batch = service.run_once()
            orders = self._read_jsonl(data / "paper_orders.jsonl")

            self.assertEqual(batch.filled_orders, 1)
            self.assertEqual(orders[0]["status"], "CLOSED")
            self.assertEqual(orders[1]["status"], "RISK_REJECTED")
            self.assertEqual(orders[0]["signal_fingerprint"], orders[1]["signal_fingerprint"])
            self.assertEqual(orders[0]["signal_timestamp"], "2026-06-29T00:00:00Z")
            self.assertIn("duplicate arbitrage signal fingerprint", orders[1]["reason"].lower())

    @staticmethod
    def _assessment() -> SimpleNamespace:
        return SimpleNamespace(
            decision="APPROVED_FOR_PAPER",
            pair="WETH/USDC",
            expected_edge_pct=Decimal("0.35"),
            chain="base",
            strategy_name="DEX Arbitrage Strategy",
            max_allowed_notional_usd=Decimal("1000000"),
        )

    @staticmethod
    def _write_buy_opportunity(data: Path) -> None:
        row = {
            "timestamp": "2026-06-29T00:00:00Z",
            "opportunity_id": "opp1",
            "chain": "base",
            "pair": "WETH/USDC",
            "buy_source": "Uniswap V2",
            "sell_source": "Uniswap V3",
            "buy_price": "2000",
            "sell_price": "2013",
            "gross_spread_pct": "0.65",
            "total_cost_buffer_pct": "0.30",
            "estimated_net_edge_pct": "0.35",
            "decision": "BUY",
            "reason": "test opportunity",
        }
        (data / "opportunity_decisions.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    unittest.main()
