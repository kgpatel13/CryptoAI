from __future__ import annotations

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from app.backtesting.optimization_service import OptimizationService


class OptimizationServiceTests(unittest.TestCase):
    def test_optimization_excludes_synthetic_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir, report_dir = self._dirs(tmp)
            (data_dir / "multi_dex_opportunities.jsonl").write_text(
                json.dumps(
                    {
                        "timestamp": "2026-06-29T00:00:00Z",
                        "mode": "PAPER_SIMULATED",
                        "pair": "WETH/USDC",
                        "buy_dex": "Uniswap V2",
                        "sell_dex": "SyntheticPaperVenue",
                        "gross_edge_pct": "0.90",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            payload = OptimizationService(data_dir=data_dir, report_dir=report_dir).run(
                cost_buffers=[Decimal("0.30")],
                min_net_edges=[Decimal("0.10")],
                notionals=[Decimal("1000")],
            )

            best = payload["best_scenario"]
            self.assertEqual(best["considered_signals"], 0)
            self.assertEqual(best["trade_count"], 0)
            self.assertEqual(best["skipped_synthetic"], 1)

    def test_optimization_ranks_real_profitable_scenario(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir, report_dir = self._dirs(tmp)
            (data_dir / "multi_dex_opportunities.jsonl").write_text(
                json.dumps(
                    {
                        "timestamp": "2026-06-29T00:00:00Z",
                        "mode": "REAL",
                        "pair": "WETH/USDC",
                        "buy_dex": "Uniswap V2",
                        "sell_dex": "Aerodrome",
                        "gross_edge_pct": "0.60",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            payload = OptimizationService(data_dir=data_dir, report_dir=report_dir).run(
                cost_buffers=[Decimal("0.20"), Decimal("0.50")],
                min_net_edges=[Decimal("0.05")],
                notionals=[Decimal("1000")],
            )

            best = payload["best_scenario"]
            self.assertEqual(best["cost_buffer_pct"], "0.20")
            self.assertEqual(best["trade_count"], 1)
            self.assertEqual(best["total_pnl_usd"], "4.0000")
            self.assertTrue((report_dir / "optimization_report.json").exists())
            self.assertTrue((report_dir / "optimization_report.md").exists())

    def test_duplicate_opportunities_count_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir, report_dir = self._dirs(tmp)
            row = {
                "timestamp": "2026-06-29T00:00:00Z",
                "mode": "REAL",
                "chain": "base",
                "pair": "WETH/USDC",
                "buy_dex": "Uniswap V2",
                "sell_dex": "Aerodrome",
                "gross_edge_pct": "0.60",
                "cost_buffer_pct": "0.30",
                "net_edge_pct": "0.30",
                "decision": "BUY",
            }
            (data_dir / "multi_dex_opportunities.jsonl").write_text(
                "\n".join(json.dumps(row) for _ in range(2)) + "\n",
                encoding="utf-8",
            )

            payload = OptimizationService(data_dir=data_dir, report_dir=report_dir).run(
                cost_buffers=[Decimal("0.20")],
                min_net_edges=[Decimal("0.05")],
                notionals=[Decimal("1000")],
            )

            best = payload["best_scenario"]
            self.assertEqual(payload["input_row_count"], 2)
            self.assertEqual(payload["deduped_row_count"], 1)
            self.assertEqual(best["considered_signals"], 1)
            self.assertEqual(best["trade_count"], 1)
            self.assertEqual(best["total_pnl_usd"], "4.0000")

    @staticmethod
    def _dirs(tmp: str) -> tuple[Path, Path]:
        root = Path(tmp)
        data_dir = root / "data"
        report_dir = root / "reports"
        data_dir.mkdir()
        report_dir.mkdir()
        return data_dir, report_dir


if __name__ == "__main__":
    unittest.main()
