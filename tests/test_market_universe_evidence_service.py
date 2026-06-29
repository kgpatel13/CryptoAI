from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.research.market_universe_evidence_service import MarketUniverseEvidenceService


class MarketUniverseEvidenceServiceTests(unittest.TestCase):
    def test_ranks_base_weth_as_active_focus_and_keeps_settings_research_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data, reports = self._dirs(tmp)
            self._write_market_intelligence(reports)
            self._write_support_reports(reports)
            (data / "quote_diagnostics.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps({"chain": "base", "pair": "WETH/USDC", "dex": "Uniswap V2", "status": "OK"}),
                        json.dumps({"chain": "base", "pair": "WETH/USDC", "dex": "Aerodrome", "status": "OK"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (data / "multi_dex_opportunities.jsonl").write_text(
                json.dumps(
                    {
                        "timestamp": "2026-06-29T00:00:00Z",
                        "mode": "REAL",
                        "chain": "base",
                        "pair": "WETH/USDC",
                        "buy_dex": "Uniswap V2",
                        "sell_dex": "Aerodrome",
                        "gross_edge_pct": "0.20",
                        "cost_buffer_pct": "0.30",
                        "net_edge_pct": "-0.10",
                        "decision": "SKIP",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            payload = MarketUniverseEvidenceService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(payload["primary_focus"]["chain"], "base")
            self.assertEqual(payload["primary_focus"]["pair"], "WETH/USDC")
            focus = payload["universe"][0]
            self.assertEqual(focus["classification"], "ACTIVE_FOCUS")
            self.assertEqual(focus["lower_bound_trade_count"], 1)
            self.assertIn("keep production unchanged", payload["settings_evidence"]["recommendation"])
            self.assertTrue((reports / "market_universe_evidence.json").exists())
            self.assertTrue((reports / "market_universe_evidence.md").exists())

    def test_configured_pair_without_quotes_is_blocked_for_provider_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data, reports = self._dirs(tmp)
            self._write_market_intelligence(reports)
            self._write_support_reports(reports)

            payload = MarketUniverseEvidenceService(data_dir=data, report_dir=reports).generate()

            by_pair = {(row["chain"], row["pair"]): row for row in payload["universe"]}
            self.assertEqual(by_pair[("base", "WETH/USDC")]["classification"], "BLOCKED_NEEDS_QUOTES")
            self.assertEqual(by_pair[("arbitrum", "WETH/USDC")]["classification"], "BLOCKED_NEEDS_QUOTES")
            self.assertGreaterEqual(payload["blocked_count"], 2)

    @staticmethod
    def _dirs(tmp: str) -> tuple[Path, Path]:
        root = Path(tmp)
        data = root / "data"
        reports = root / "reports"
        data.mkdir()
        reports.mkdir()
        return data, reports

    @staticmethod
    def _write_market_intelligence(reports: Path) -> None:
        (reports / "market_intelligence.json").write_text(
            json.dumps(
                {
                    "generated_at": "2026-06-29T00:00:00Z",
                    "mode": "paper",
                    "chains": [
                        {"chain": "base", "readiness_status": "READY_FOR_PAPER", "readiness_score": 90},
                        {"chain": "arbitrum", "readiness_status": "WATCH", "readiness_score": 70},
                    ],
                    "pair_candidates": [
                        {"chain": "base", "pair": "WETH/USDC", "configured": True, "priority": 1, "dex_count": 3},
                        {"chain": "base", "pair": "cbBTC/USDC", "configured": True, "priority": 2, "dex_count": 3},
                        {"chain": "arbitrum", "pair": "WETH/USDC", "configured": True, "priority": 1, "dex_count": 3},
                    ],
                }
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _write_support_reports(reports: Path) -> None:
        (reports / "provider_monitor.json").write_text(
            json.dumps({"generated_at": "2026-06-29T00:00:00Z", "overall_status": "WATCH", "alert_count": 1}),
            encoding="utf-8",
        )
        (reports / "execution_cost_evidence.json").write_text(
            json.dumps(
                {
                    "generated_at": "2026-06-29T00:00:00Z",
                    "production_cost_buffer_pct": "0.30",
                    "buffer_status": "CONSERVATIVE",
                    "confidence": "LOW",
                    "observed_total_cost_lower_bound_pct": "0.13",
                }
            ),
            encoding="utf-8",
        )
        (reports / "optimization_report.json").write_text(
            json.dumps(
                {
                    "generated_at": "2026-06-29T00:00:00Z",
                    "best_scenario": {
                        "cost_buffer_pct": "0.20",
                        "min_net_edge_pct": "0.00",
                        "notional_usd": "1000",
                        "trade_count": 8,
                        "total_pnl_usd": "4.0000",
                        "avg_net_edge_pct": "0.0500",
                        "max_drawdown_usd": "0.0000",
                    },
                    "scenarios": [
                        {
                            "cost_buffer_pct": "0.20",
                            "min_net_edge_pct": "0.00",
                            "notional_usd": "1000",
                            "trade_count": 8,
                            "total_pnl_usd": "4.0000",
                            "avg_net_edge_pct": "0.0500",
                            "max_drawdown_usd": "0.0000",
                        },
                        {
                            "cost_buffer_pct": "0.30",
                            "min_net_edge_pct": "0.00",
                            "notional_usd": "1000",
                            "trade_count": 0,
                            "total_pnl_usd": "0.0000",
                            "avg_net_edge_pct": "0.0000",
                            "max_drawdown_usd": "0.0000",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
