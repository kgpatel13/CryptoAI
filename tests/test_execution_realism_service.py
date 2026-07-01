from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.execution.execution_realism_service import ExecutionRealismService


class ExecutionRealismServiceTests(unittest.TestCase):
    def test_buy_opportunity_is_shadow_only_without_pool_depth_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data, reports = self._dirs(tmp)
            self._write_settings(reports)
            self._write_portfolio(data)
            self._write_quotes(
                data,
                [
                    {"timestamp": "2026-06-30T00:00:00Z", "chain": "base", "dex": "Uniswap V2", "pair": "WETH/USDC", "amount_in": "1", "price": "1000", "status": "OK"},
                    {"timestamp": "2026-06-30T00:00:00Z", "chain": "base", "dex": "Uniswap V3", "pair": "WETH/USDC", "amount_in": "1", "price": "1008", "status": "OK"},
                ],
            )
            self._write_opportunities(
                data,
                [
                    {
                        "timestamp": "2026-06-30T00:00:01Z",
                        "chain": "base",
                        "pair": "WETH/USDC",
                        "buy_source": "Uniswap V2",
                        "sell_source": "Uniswap V3",
                        "gross_spread_pct": "0.80",
                        "total_cost_buffer_pct": "0.30",
                        "estimated_net_edge_pct": "0.50",
                        "decision": "BUY",
                    }
                ],
            )

            payload = ExecutionRealismService(data_dir=data, report_dir=reports).generate()

            row = payload["opportunities"][0]
            self.assertEqual(payload["paper_capital_usd"], "1000.0000")
            self.assertEqual(payload["requested_notional_usd"], "1000.0000")
            self.assertEqual(row["max_executable_notional_usd"], "1000.0000")
            self.assertEqual(row["realism_status"], "SHADOW_ONLY")
            self.assertEqual(row["confidence"], "LOW")
            self.assertEqual(payload["overall_status"], "PAPER_ONLY_NEEDS_DEPTH")
            self.assertTrue((reports / "execution_realism.json").exists())
            self.assertTrue((reports / "execution_realism.md").exists())

    def test_single_route_quote_is_not_executable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data, reports = self._dirs(tmp)
            self._write_settings(reports)
            self._write_portfolio(data)
            self._write_quotes(
                data,
                [
                    {"timestamp": "2026-06-30T00:00:00Z", "chain": "base", "dex": "Uniswap V2", "pair": "WETH/USDC", "amount_in": "1", "price": "1000", "status": "OK"},
                ],
            )
            self._write_opportunities(
                data,
                [
                    {
                        "timestamp": "2026-06-30T00:00:01Z",
                        "chain": "base",
                        "pair": "WETH/USDC",
                        "buy_source": "Uniswap V2",
                        "sell_source": "Uniswap V3",
                        "gross_spread_pct": "0.80",
                        "total_cost_buffer_pct": "0.30",
                        "estimated_net_edge_pct": "0.50",
                        "decision": "BUY",
                    }
                ],
            )

            payload = ExecutionRealismService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(payload["opportunities"][0]["realism_status"], "NOT_EXECUTABLE")
            self.assertEqual(payload["opportunities"][0]["confidence"], "NONE")
            self.assertEqual(payload["overall_status"], "NOT_SHADOW_READY")

    def test_quote_snapshot_fallback_proves_route_when_diagnostics_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data, reports = self._dirs(tmp)
            self._write_settings(reports)
            self._write_portfolio(data)
            self._write_quote_snapshot(
                data,
                [
                    {"chain": "base", "dex": "Uniswap V2", "token_in": "WETH", "token_out": "USDC", "amount_in": "1", "amount_out": "1000", "price": "1000", "error": None},
                    {"chain": "base", "dex": "Uniswap V3", "token_in": "WETH", "token_out": "USDC", "amount_in": "1", "amount_out": "1008", "price": "1008", "error": None},
                ],
            )
            self._write_opportunities(
                data,
                [
                    {
                        "timestamp": "2026-06-30T00:00:01Z",
                        "chain": "base",
                        "pair": "WETH/USDC",
                        "buy_source": "Uniswap V2",
                        "sell_source": "Uniswap V3",
                        "gross_spread_pct": "0.80",
                        "total_cost_buffer_pct": "0.30",
                        "estimated_net_edge_pct": "0.50",
                        "decision": "BUY",
                    }
                ],
            )

            payload = ExecutionRealismService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(payload["quote_evidence"]["healthy_dex_count"], 2)
            self.assertEqual(payload["opportunities"][0]["realism_status"], "SHADOW_ONLY")
            self.assertNotIn("healthy route DEXes=0", payload["opportunities"][0]["reason"])

    def test_pool_depth_ladder_can_promote_buy_to_shadow_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data, reports = self._dirs(tmp)
            self._write_settings(reports)
            self._write_portfolio(data)
            self._write_pool_depth(reports)
            self._write_quotes(
                data,
                [
                    {"timestamp": "2026-06-30T00:00:00Z", "chain": "base", "dex": "Uniswap V2", "pair": "WETH/USDC", "amount_in": "1", "price": "1000", "status": "OK"},
                    {"timestamp": "2026-06-30T00:00:00Z", "chain": "base", "dex": "Uniswap V3", "pair": "WETH/USDC", "amount_in": "1", "price": "1008", "status": "OK"},
                ],
            )
            self._write_opportunities(
                data,
                [
                    {
                        "timestamp": "2026-06-30T00:00:01Z",
                        "chain": "base",
                        "pair": "WETH/USDC",
                        "buy_source": "Uniswap V2",
                        "sell_source": "Uniswap V3",
                        "gross_spread_pct": "0.80",
                        "total_cost_buffer_pct": "0.30",
                        "estimated_net_edge_pct": "0.50",
                        "decision": "BUY",
                    }
                ],
            )

            payload = ExecutionRealismService(data_dir=data, report_dir=reports).generate()

            row = payload["opportunities"][0]
            self.assertEqual(row["depth_model"], "POOL_DEPTH_LADDER")
            self.assertEqual(row["confidence"], "MEDIUM")
            self.assertEqual(row["realism_status"], "SHADOW_READY")
            self.assertEqual(payload["overall_status"], "SHADOW_REVIEW_READY")
            self.assertEqual(payload["live_ready_count"], 0)

    @staticmethod
    def _dirs(tmp: str) -> tuple[Path, Path]:
        root = Path(tmp)
        data = root / "data"
        reports = root / "reports"
        data.mkdir()
        reports.mkdir()
        return data, reports

    @staticmethod
    def _write_settings(reports: Path) -> None:
        (reports / "paper_trading_settings.json").write_text(
            json.dumps(
                {
                    "paper_capital_usd": "1000.00",
                    "settings": {
                        "paper_capital": {
                            "max_notional_usd_per_trade": "1000",
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _write_portfolio(data: Path) -> None:
        (data / "paper_portfolio_state.json").write_text(
            json.dumps({"initial_cash_usd": "1000.00", "cash_usd": "1000.00", "positions": []}),
            encoding="utf-8",
        )

    @staticmethod
    def _write_pool_depth(reports: Path) -> None:
        (reports / "pool_depth_ladder.json").write_text(
            json.dumps(
                {
                    "overall_status": "DEPTH_EVIDENCE_READY",
                    "confidence": "MEDIUM",
                    "routes": [
                        {
                            "chain": "base",
                            "pair": "WETH/USDC",
                            "status": "DEPTH_READY",
                            "confidence": "MEDIUM",
                            "max_usable_notional_usd": "1000.0000",
                            "worst_price_impact_pct": "0.0500",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _write_quotes(data: Path, rows: list[dict]) -> None:
        (data / "quote_diagnostics.jsonl").write_text(
            "\n".join(json.dumps(row) for row in rows) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _write_quote_snapshot(data: Path, rows: list[dict]) -> None:
        (data / "quote_snapshot.json").write_text(
            json.dumps({"saved_at": 1782867545.0, "quotes": rows}),
            encoding="utf-8",
        )

    @staticmethod
    def _write_opportunities(data: Path, rows: list[dict]) -> None:
        (data / "opportunity_decisions.jsonl").write_text(
            "\n".join(json.dumps(row) for row in rows) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
