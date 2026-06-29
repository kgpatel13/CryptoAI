from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.market_intelligence.market_intelligence_service import MarketIntelligenceService


class MarketIntelligenceTests(unittest.TestCase):
    def test_generates_pair_candidates_and_readiness_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            report_dir = root / "reports"
            data_dir.mkdir()
            (data_dir / "provider_health.json").write_text(
                json.dumps(
                    {
                        "providers": [
                            {"name": "base-rpc", "provider_type": "rpc", "chain": "base", "score": 90},
                            {"name": "uniswap", "provider_type": "dex", "chain": "base", "score": 80},
                            {"name": "polygon-rpc", "provider_type": "rpc", "chain": "polygon", "score": 60},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            payload = MarketIntelligenceService(data_dir=data_dir, report_dir=report_dir).generate()

            self.assertEqual(payload["mode"], "paper")
            self.assertGreaterEqual(payload["chain_count"], 4)
            self.assertGreaterEqual(payload["pair_candidate_count"], 8)
            self.assertGreaterEqual(payload["configured_pair_count"], 8)

            base = next(row for row in payload["chains"] if row["chain"] == "base")
            self.assertEqual(base["provider_count"], 2)
            self.assertEqual(base["provider_score"], 85)
            self.assertEqual(base["readiness_status"], "READY_FOR_PAPER")

            pairs = {row["pair"]: row for row in payload["pair_candidates"] if row["chain"] == "base"}
            self.assertTrue(pairs["WETH/USDC"]["configured"])
            self.assertTrue(pairs["cbBTC/USDC"]["configured"])

            self.assertTrue((report_dir / "market_intelligence.json").exists())
            self.assertTrue((report_dir / "market_intelligence.md").exists())

    def test_missing_provider_health_keeps_readiness_conservative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = MarketIntelligenceService(
                data_dir=root / "data",
                report_dir=root / "reports",
            ).generate()

            self.assertEqual(payload["provider_summary"]["provider_count"], 0)
            base = next(row for row in payload["chains"] if row["chain"] == "base")
            self.assertEqual(base["provider_score"], 40)
            self.assertIn("No provider health observations yet.", base["notes"])
            self.assertNotEqual(base["readiness_status"], "READY_FOR_PAPER")


if __name__ == "__main__":
    unittest.main()
