from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.research.eth_route_architecture_service import EthRouteArchitectureService


class EthRouteArchitectureServiceTests(unittest.TestCase):
    def test_keeps_020_buffer_research_only_when_cost_confidence_is_low(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data, reports = self._dirs(tmp)
            self._write_route_inputs(data, reports, confidence="LOW", paper_samples=6, quote_ok_rate="64.0")

            payload = EthRouteArchitectureService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(payload["focus_chain"], "base")
            self.assertEqual(payload["production_buffer_pct"], "0.30")
            self.assertEqual(payload["candidate_buffer_pct"], "0.20")
            self.assertEqual(payload["route_architecture_decision"], "KEEP_0_30_PRODUCTION_RESEARCH_0_20")
            self.assertTrue(payload["combined_buffer_scenarios"]["candidate_0_20"]["positive_after_buffer_count"] > 0)
            self.assertTrue(payload["combined_buffer_scenarios"]["production_0_30"]["positive_after_buffer_count"] == 0)
            self.assertTrue((reports / "eth_route_architecture.json").exists())
            self.assertTrue((reports / "eth_route_architecture.md").exists())

    def test_can_mark_candidate_ready_for_separate_paper_review_when_all_gates_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data, reports = self._dirs(tmp)
            self._write_route_inputs(data, reports, confidence="HIGH", paper_samples=35, quote_ok_rate="95.0", signal_count=35)

            payload = EthRouteArchitectureService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(payload["route_architecture_decision"], "READY_FOR_SEPARATE_PAPER_BUFFER_REVIEW")
            self.assertEqual(payload["buffer_promotion"]["passed_gate_count"], payload["buffer_promotion"]["gate_count"])

    def test_route_readiness_requires_two_dex_quotes_per_direction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data, reports = self._dirs(tmp)
            self._write_route_inputs(data, reports, confidence="LOW", paper_samples=6, quote_ok_rate="64.0")

            payload = EthRouteArchitectureService(data_dir=data, report_dir=reports).generate()

            by_route = {row["route"]: row for row in payload["route_evidence"]}
            self.assertTrue(by_route["WETH/USDC"]["two_dex_quote_ready"])
            self.assertFalse(by_route["USDC/WETH"]["two_dex_quote_ready"])

    @staticmethod
    def _dirs(tmp: str) -> tuple[Path, Path]:
        root = Path(tmp)
        data = root / "data"
        reports = root / "reports"
        data.mkdir()
        reports.mkdir()
        return data, reports

    @staticmethod
    def _write_route_inputs(
        data: Path,
        reports: Path,
        *,
        confidence: str,
        paper_samples: int,
        quote_ok_rate: str,
        signal_count: int = 3,
    ) -> None:
        (data / "quote_diagnostics.jsonl").write_text(
            "\n".join(
                [
                    json.dumps({"chain": "base", "dex": "Uniswap V2", "pair": "WETH/USDC", "status": "OK"}),
                    json.dumps({"chain": "base", "dex": "Aerodrome", "pair": "WETH/USDC", "status": "OK"}),
                    json.dumps({"chain": "base", "dex": "Uniswap V2", "pair": "USDC/WETH", "status": "OK"}),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        rows = []
        for idx in range(signal_count):
            rows.append(
                {
                    "timestamp": f"2026-06-29T00:{idx:02d}:00Z",
                    "mode": "REAL",
                    "chain": "base",
                    "pair": "WETH/USDC" if idx % 2 == 0 else "USDC/WETH",
                    "buy_dex": "Uniswap V2",
                    "sell_dex": "Aerodrome",
                    "gross_edge_pct": "0.24",
                }
            )
        (data / "multi_dex_opportunities.jsonl").write_text(
            "\n".join(json.dumps(row) for row in rows) + "\n",
            encoding="utf-8",
        )
        (reports / "quote_coverage_evidence.json").write_text(
            json.dumps(
                {
                    "active_pair_count": 1,
                    "pair_coverage": [
                        {"chain": "base", "pair": "WETH/USDC", "status": "ACTIVE_QUOTED"},
                    ],
                }
            ),
            encoding="utf-8",
        )
        (reports / "execution_cost_evidence.json").write_text(
            json.dumps(
                {
                    "confidence": confidence,
                    "paper_execution_evidence": {"sample_count": paper_samples},
                    "quote_evidence": {"ok_rate_pct": quote_ok_rate},
                }
            ),
            encoding="utf-8",
        )
        (reports / "provider_monitor.json").write_text(
            json.dumps({"overall_status": "WATCH"}),
            encoding="utf-8",
        )
        (reports / "report_audit.json").write_text(
            json.dumps({"finding_count": 0}),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
