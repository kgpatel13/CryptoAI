from __future__ import annotations

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from app.backtesting.backtest_service import BacktestService


class BacktestServiceTests(unittest.TestCase):
    def test_replays_real_multi_dex_history_and_excludes_synthetic_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            report_dir = root / "reports"
            data_dir.mkdir()
            report_dir.mkdir()
            rows = [
                {
                    "timestamp": "2026-06-29T00:00:00Z",
                    "mode": "PAPER_SIMULATED",
                    "chain": "base",
                    "pair": "WETH/USDC",
                    "buy_dex": "Uniswap V2",
                    "sell_dex": "SyntheticPaperVenue",
                    "gross_edge_pct": "0.6500",
                    "cost_buffer_pct": "0.30",
                    "net_edge_pct": "0.3500",
                    "decision": "BUY",
                },
                {
                    "timestamp": "2026-06-29T00:01:00Z",
                    "mode": "REAL",
                    "chain": "base",
                    "pair": "WETH/USDC",
                    "buy_dex": "Uniswap V2",
                    "sell_dex": "Aerodrome",
                    "gross_edge_pct": "0.50",
                    "cost_buffer_pct": "0.30",
                    "net_edge_pct": "0.20",
                    "decision": "BUY",
                },
                {
                    "timestamp": "2026-06-29T00:02:00Z",
                    "mode": "REAL",
                    "chain": "base",
                    "pair": "USDC/WETH",
                    "buy_dex": "Uniswap V2",
                    "sell_dex": "Aerodrome",
                    "gross_edge_pct": "0.10",
                    "cost_buffer_pct": "0.30",
                    "net_edge_pct": "-0.20",
                    "decision": "SKIP",
                },
            ]
            (data_dir / "multi_dex_opportunities.jsonl").write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n",
                encoding="utf-8",
            )

            result = BacktestService(data_dir=data_dir, report_dir=report_dir).run_default_backtest(
                notional_usd=Decimal("1000")
            )

            self.assertEqual(result.total_signals, 2)
            self.assertEqual(result.simulated_trades, 1)
            self.assertEqual(result.skipped_signals, 1)
            self.assertEqual(result.total_simulated_profit_usd, Decimal("2.0000"))
            self.assertEqual(result.trades[0].mode, "REAL")
            self.assertTrue((report_dir / "backtest_report.json").exists())
            self.assertTrue((report_dir / "backtest_report.md").exists())

    def test_can_include_synthetic_when_explicitly_requested(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            report_dir = root / "reports"
            data_dir.mkdir()
            report_dir.mkdir()
            (data_dir / "multi_dex_opportunities.jsonl").write_text(
                json.dumps(
                    {
                        "timestamp": "2026-06-29T00:00:00Z",
                        "mode": "PAPER_SIMULATED",
                        "chain": "base",
                        "pair": "WETH/USDC",
                        "buy_dex": "Uniswap V2",
                        "sell_dex": "SyntheticPaperVenue",
                        "gross_edge_pct": "0.6500",
                        "cost_buffer_pct": "0.30",
                        "net_edge_pct": "0.3500",
                        "decision": "BUY",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = BacktestService(data_dir=data_dir, report_dir=report_dir).run_default_backtest(
                notional_usd=Decimal("1000"),
                include_synthetic=True,
            )

            self.assertEqual(result.total_signals, 1)
            self.assertEqual(result.simulated_trades, 1)
            self.assertEqual(result.total_simulated_profit_usd, Decimal("3.5000"))
            self.assertEqual(result.trades[0].mode, "PAPER_SIMULATED")


if __name__ == "__main__":
    unittest.main()
