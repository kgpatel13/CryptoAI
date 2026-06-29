from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.quotes.aerodrome_quote_provider import AERODROME_ROUTER
from app.quotes.uniswap_v3_quote_provider import UNISWAP_V3_BASE_SWAP_ROUTER_02
from app.registry.dexes import get_dexes_for_chain
from app.research.quote_coverage_evidence_service import QuoteCoverageEvidenceService


class QuoteCoverageEvidenceServiceTests(unittest.TestCase):
    def test_classifies_active_base_pair_and_provider_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data, reports = self._dirs(tmp)
            (data / "quote_diagnostics.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps({"chain": "base", "dex": "Uniswap V2", "pair": "WETH/USDC", "status": "OK"}),
                        json.dumps({"chain": "base", "dex": "Aerodrome", "pair": "WETH/USDC", "status": "OK"}),
                        json.dumps({"chain": "base", "dex": "Uniswap V3", "pair": "WETH/USDC", "status": "OK"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (reports / "provider_monitor.json").write_text(
                json.dumps({"overall_status": "WATCH", "alert_count": 2}),
                encoding="utf-8",
            )

            payload = QuoteCoverageEvidenceService(data_dir=data, report_dir=reports).generate()

            by_pair = {(row["chain"], row["pair"]): row for row in payload["pair_coverage"]}
            self.assertEqual(by_pair[("base", "WETH/USDC")]["status"], "ACTIVE_QUOTED")
            self.assertEqual(by_pair[("base", "CBBTC/USDC")]["status"], "NEEDS_QUOTE_TEST")
            self.assertEqual(by_pair[("arbitrum", "WETH/USDC")]["status"], "ROUTER_OR_PROVIDER_GAP")
            self.assertEqual(payload["active_pair_count"], 1)
            self.assertEqual(payload["implemented_provider_count"], 3)
            self.assertGreaterEqual(payload["provider_gap_count"], 1)
            self.assertTrue((reports / "quote_coverage_evidence.json").exists())
            self.assertTrue((reports / "quote_coverage_evidence.md").exists())

    def test_registry_aerodrome_router_matches_provider_constant(self) -> None:
        aerodrome = next(row for row in get_dexes_for_chain("base") if row.name == "Aerodrome")

        self.assertEqual(str(aerodrome.router_address).lower(), AERODROME_ROUTER.lower())

    def test_registry_uniswap_v3_router_matches_provider_constant(self) -> None:
        uniswap_v3 = next(row for row in get_dexes_for_chain("base") if row.name == "Uniswap V3")

        self.assertEqual(str(uniswap_v3.router_address).lower(), UNISWAP_V3_BASE_SWAP_ROUTER_02.lower())

    @staticmethod
    def _dirs(tmp: str) -> tuple[Path, Path]:
        root = Path(tmp)
        data = root / "data"
        reports = root / "reports"
        data.mkdir()
        reports.mkdir()
        return data, reports


if __name__ == "__main__":
    unittest.main()
