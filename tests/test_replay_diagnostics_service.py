from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.backtesting.replay_diagnostics_service import ReplayDiagnosticsService


class ReplayDiagnosticsServiceTests(unittest.TestCase):
    def test_explains_when_lower_cost_buffer_has_trades_but_production_does_not(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            reports = root / "reports"
            data.mkdir()
            reports.mkdir()
            rows = [
                {
                    "timestamp": "2026-06-29T00:00:00Z",
                    "mode": "REAL",
                    "chain": "base",
                    "pair": "WETH/USDC",
                    "buy_dex": "Uniswap V2",
                    "sell_dex": "Aerodrome",
                    "gross_edge_pct": "0.25",
                    "cost_buffer_pct": "0.30",
                    "net_edge_pct": "-0.05",
                    "decision": "SKIP",
                },
                {
                    "timestamp": "2026-06-29T00:01:00Z",
                    "mode": "PAPER_SIMULATED",
                    "chain": "base",
                    "pair": "WETH/USDC",
                    "buy_dex": "Uniswap V2",
                    "sell_dex": "SyntheticPaperVenue",
                    "gross_edge_pct": "0.80",
                    "cost_buffer_pct": "0.30",
                    "net_edge_pct": "0.50",
                    "decision": "BUY",
                },
            ]
            (data / "multi_dex_opportunities.jsonl").write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n",
                encoding="utf-8",
            )

            payload = ReplayDiagnosticsService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(payload["production_trade_count"], 0)
            self.assertEqual(payload["best_profitable_cost_buffer_pct"], "0.20")
            self.assertEqual(payload["best_profitable_trade_count"], 1)
            self.assertEqual(payload["synthetic_signal_count"], 1)
            self.assertIn("Production buffer", payload["findings"][0]["message"])
            self.assertTrue((reports / "replay_diagnostics.json").exists())
            self.assertTrue((reports / "replay_diagnostics.md").exists())


if __name__ == "__main__":
    unittest.main()
