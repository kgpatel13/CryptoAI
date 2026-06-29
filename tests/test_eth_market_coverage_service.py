from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.research.eth_market_coverage_service import EthMarketCoverageService


class EthMarketCoverageServiceTests(unittest.TestCase):
    def test_scores_base_higher_than_unconfigured_optimism_without_fake_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data, reports = self._dirs(tmp)
            self._write_inputs(data, reports)

            payload = EthMarketCoverageService(data_dir=data, report_dir=reports).generate()

            by_chain = {row["chain"]: row for row in payload["chains"]}
            self.assertGreater(by_chain["base"]["coverage_score"], by_chain["optimism"]["coverage_score"])
            self.assertTrue(by_chain["base"]["registry_chain_configured"])
            self.assertFalse(by_chain["optimism"]["registry_chain_configured"])
            self.assertEqual(by_chain["optimism"]["coverage_status"], "TARGET_ONLY")
            self.assertIn("Uniswap V3", by_chain["base"]["target_dexes"])
            self.assertIn("Uniswap V3", by_chain["base"]["configured_target_dexes"])
            self.assertTrue((reports / "eth_market_coverage.json").exists())
            self.assertTrue((reports / "eth_market_coverage.md").exists())

    def test_requires_two_dex_quotes_for_quote_ready_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data, reports = self._dirs(tmp)
            self._write_inputs(data, reports)

            payload = EthMarketCoverageService(data_dir=data, report_dir=reports).generate()

            base = next(row for row in payload["chains"] if row["chain"] == "base")
            self.assertIn("WETH/USDC", base["quote_ready_routes"])
            self.assertNotIn("USDC/WETH", base["quote_ready_routes"])

    @staticmethod
    def _dirs(tmp: str) -> tuple[Path, Path]:
        root = Path(tmp)
        data = root / "data"
        reports = root / "reports"
        data.mkdir()
        reports.mkdir()
        return data, reports

    @staticmethod
    def _write_inputs(data: Path, reports: Path) -> None:
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
        (data / "provider_health.json").write_text(
            json.dumps(
                {
                    "providers": [
                        {"chain": "base", "provider_type": "dex", "name": "Uniswap V2", "score": 100},
                        {"chain": "base", "provider_type": "dex", "name": "Aerodrome", "score": 80},
                    ]
                }
            ),
            encoding="utf-8",
        )
        (reports / "quote_coverage_evidence.json").write_text(
            json.dumps({"pair_coverage": [{"chain": "base", "pair": "WETH/USDC", "status": "ACTIVE_QUOTED"}]}),
            encoding="utf-8",
        )
        (reports / "eth_route_architecture.json").write_text(
            json.dumps({"route_architecture_decision": "KEEP_0_30_PRODUCTION_RESEARCH_0_20"}),
            encoding="utf-8",
        )
        (reports / "execution_cost_evidence.json").write_text(
            json.dumps({"confidence": "LOW"}),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
