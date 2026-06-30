from __future__ import annotations

import json
import os
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

from app.execution.live_shadow_gate_service import LiveShadowGateService
from app.execution.paper_execution_service import PaperExecutionService
from app.risk.portfolio_risk_service import PortfolioRiskService


class LiveShadowGateServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.old_env = dict(os.environ)
        os.environ["CRYPTOAI_PAPER_INITIAL_CASH_USD"] = "500"
        os.environ["CRYPTOAI_DEFAULT_PAPER_NOTIONAL_USD"] = "20"
        os.environ["CRYPTOAI_MAX_PAPER_NOTIONAL_USD"] = "20"
        os.environ["CRYPTOAI_MIN_PAPER_NOTIONAL_USD"] = "20"
        os.environ["CRYPTOAI_PAPER_RISK_PER_TRADE_PCT"] = "4"
        os.environ["CRYPTOAI_PAPER_MAX_CASH_USAGE_PCT"] = "4"
        os.environ["CRYPTOAI_MAX_DAILY_PAPER_TRADES"] = "0"
        os.environ["CRYPTOAI_MAX_OPEN_POSITIONS"] = "1"
        os.environ["CRYPTOAI_TRADE_COOLDOWN_SECONDS"] = "0"
        os.environ["CRYPTOAI_DUPLICATE_SIGNAL_WINDOW_SECONDS"] = "0"
        os.environ["CRYPTOAI_BLOCK_SAME_PAIR_OPEN_POSITION"] = "true"
        os.environ["CRYPTOAI_PAPER_SIZING_MODE"] = "full_available_cash"

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self.old_env)

    def test_shadow_gate_marks_order_eligible_when_evidence_is_green(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            reports = root / "reports"
            data.mkdir()
            reports.mkdir()
            self._write_green_reports(reports)

            verdict = LiveShadowGateService(data_dir=data, report_dir=reports).evaluate_order(
                {
                    "order_id": "o1",
                    "status": "CLOSED",
                    "chain": "base",
                    "pair": "USDC/WETH",
                    "buy_source": "Uniswap V2",
                    "sell_source": "Uniswap V3",
                }
            )

            self.assertEqual(verdict["live_shadow_decision"], "SHADOW_ELIGIBLE")
            self.assertEqual(verdict["live_shadow_blockers"], [])

    def test_strict_paper_mode_skips_when_shadow_gate_is_not_eligible(self) -> None:
        os.environ["CRYPTOAI_PAPER_REQUIRE_LIVE_SHADOW_ELIGIBLE"] = "true"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            data.mkdir()
            self._write_buy_opportunity(data)
            portfolio = PortfolioRiskService(state_path=data / "paper_portfolio_state.json")
            service = PaperExecutionService(data_dir=data, portfolio_risk=portfolio)
            service._load_risk_assessments = lambda: [self._assessment()]  # type: ignore[method-assign]

            batch = service.run_once()
            orders = self._read_jsonl(data / "paper_orders.jsonl")

            self.assertEqual(batch.filled_orders, 0)
            self.assertEqual(orders[0]["status"], "SKIPPED")
            self.assertEqual(orders[0]["live_shadow_decision"], "PAPER_ONLY")
            self.assertIn("Live-shadow gate blocked paper fill", orders[0]["reason"])

    @staticmethod
    def _write_green_reports(reports: Path) -> None:
        (reports / "execution_realism.json").write_text(
            json.dumps(
                {
                    "opportunities": [
                        {
                            "chain": "base",
                            "pair": "USDC/WETH",
                            "buy_source": "Uniswap V2",
                            "sell_source": "Uniswap V3",
                            "realism_status": "SHADOW_READY",
                            "stress_net_edge_pct": "0.1200",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        (reports / "provider_monitor.json").write_text(json.dumps({"overall_status": "OK"}), encoding="utf-8")
        (reports / "execution_cost_evidence.json").write_text(json.dumps({"confidence": "HIGH"}), encoding="utf-8")

    @staticmethod
    def _assessment() -> SimpleNamespace:
        return SimpleNamespace(
            decision="APPROVED_FOR_PAPER",
            pair="USDC/WETH",
            expected_edge_pct=Decimal("0.35"),
            chain="base",
            strategy_name="DEX Arbitrage Strategy",
            max_allowed_notional_usd=Decimal("20"),
        )

    @staticmethod
    def _write_buy_opportunity(data: Path) -> None:
        row = {
            "timestamp": "2026-06-30T00:00:00Z",
            "chain": "base",
            "pair": "USDC/WETH",
            "buy_source": "Uniswap V2",
            "sell_source": "Uniswap V3",
            "buy_price": "0.00063",
            "sell_price": "0.000634",
            "gross_spread_pct": "0.6349",
            "total_cost_buffer_pct": "0.30",
            "estimated_net_edge_pct": "0.3349",
            "decision": "BUY",
        }
        (data / "opportunity_decisions.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    unittest.main()
