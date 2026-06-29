from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.execution.execution_cost_evidence_service import ExecutionCostEvidenceService


class ExecutionCostEvidenceServiceTests(unittest.TestCase):
    def test_measures_lower_bound_cost_without_changing_production_buffer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            reports = root / "reports"
            data.mkdir()
            reports.mkdir()
            (data / "paper_orders.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-06-29T00:00:00Z",
                                "status": "FILLED",
                                "filled_notional_usd": "100",
                                "slippage_bps": "5",
                                "latency_ms": 250,
                                "execution_quality": "GOOD",
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-06-29T00:01:00Z",
                                "status": "FILLED",
                                "filled_notional_usd": "100",
                                "slippage_bps": "5",
                                "latency_ms": 250,
                                "execution_quality": "GOOD",
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (data / "opportunity_decisions.jsonl").write_text(
                json.dumps(
                    {
                        "timestamp": "2026-06-29T00:00:00Z",
                        "gas_buffer_pct": "0.08",
                        "fee_slippage_buffer_pct": "0.22",
                        "total_cost_buffer_pct": "0.30",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (data / "multi_dex_opportunities.jsonl").write_text(
                "\n".join(
                    [
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
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-06-29T00:01:00Z",
                                "mode": "REAL",
                                "chain": "base",
                                "pair": "WETH/USDC",
                                "buy_dex": "Uniswap V2",
                                "sell_dex": "Aerodrome",
                                "gross_edge_pct": "0.26",
                                "cost_buffer_pct": "0.30",
                                "net_edge_pct": "-0.04",
                                "decision": "SKIP",
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (data / "quote_diagnostics.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps({"status": "OK", "dex": "Uniswap V2", "latency_ms": 100}),
                        json.dumps({"status": "OK", "dex": "Aerodrome", "latency_ms": 110}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (data / "provider_health.json").write_text(
                json.dumps(
                    {
                        "providers": [
                            {"name": "Uniswap V2", "provider_type": "dex", "chain": "base", "success_rate_pct": 100, "avg_latency_ms": 100, "score": 100, "consecutive_failures": 0},
                            {"name": "Aerodrome", "provider_type": "dex", "chain": "base", "success_rate_pct": 100, "avg_latency_ms": 110, "score": 100, "consecutive_failures": 0},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            payload = ExecutionCostEvidenceService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(payload["production_cost_buffer_pct"], "0.30")
            self.assertEqual(payload["assessment"]["buffer_status"], "CONSERVATIVE")
            self.assertEqual(payload["assessment"]["observed_total_cost_lower_bound_pct"], "0.1300")
            self.assertEqual(payload["replay_cost_evidence"]["production_trade_count"], 0)
            self.assertEqual(payload["replay_cost_evidence"]["observed_lower_bound_trade_count"], 2)
            self.assertTrue((reports / "execution_cost_evidence.json").exists())
            self.assertTrue((reports / "execution_cost_evidence.md").exists())

    def test_missing_paper_execution_sample_is_insufficient(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            reports = Path(tmp) / "reports"
            data.mkdir()
            reports.mkdir()

            payload = ExecutionCostEvidenceService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(payload["assessment"]["buffer_status"], "INSUFFICIENT_EVIDENCE")
            self.assertEqual(payload["assessment"]["confidence"], "INSUFFICIENT")

    def test_high_confidence_lower_bound_can_identify_too_high_buffer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            reports = Path(tmp) / "reports"
            data.mkdir()
            reports.mkdir()

            orders = [
                {
                    "timestamp": f"2026-06-29T00:{minute:02d}:00Z",
                    "status": "FILLED",
                    "filled_notional_usd": "100",
                    "slippage_bps": "5",
                    "latency_ms": 250,
                    "execution_quality": "GOOD",
                }
                for minute in range(30)
            ]
            (data / "paper_orders.jsonl").write_text(
                "\n".join(json.dumps(row) for row in orders) + "\n",
                encoding="utf-8",
            )
            (data / "opportunity_decisions.jsonl").write_text(
                json.dumps(
                    {
                        "timestamp": "2026-06-29T00:00:00Z",
                        "gas_buffer_pct": "0.08",
                        "fee_slippage_buffer_pct": "0.22",
                        "total_cost_buffer_pct": "0.30",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (data / "multi_dex_opportunities.jsonl").write_text(
                "\n".join(
                    json.dumps(
                        {
                            "timestamp": f"2026-06-29T01:{minute:02d}:00Z",
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
                    for minute in range(3)
                )
                + "\n",
                encoding="utf-8",
            )
            (data / "quote_diagnostics.jsonl").write_text(
                "\n".join(
                    json.dumps({"status": "OK", "dex": "Uniswap V2", "latency_ms": 100})
                    for _ in range(30)
                )
                + "\n",
                encoding="utf-8",
            )

            payload = ExecutionCostEvidenceService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(payload["assessment"]["confidence"], "HIGH")
            self.assertEqual(payload["assessment"]["buffer_status"], "TOO_HIGH")
            self.assertEqual(payload["production_cost_buffer_pct"], "0.30")


if __name__ == "__main__":
    unittest.main()
