import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.research.feature_store import FeatureStoreService
from app.research.models import FeatureVector
from app.explainability.decision_explainer import DecisionExplainer


class FeatureStoreTests(unittest.TestCase):
    def test_feature_vector_from_opportunity_labels_paper_simulated(self):
        vector = FeatureVector.from_opportunity(
            {
                "timestamp": "2026-01-01T01:02:03Z",
                "chain": "base",
                "pair": "WETH/USDC",
                "buy_source": "Uniswap V2",
                "sell_source": "SyntheticPaperVenue",
                "estimated_net_edge_pct": "0.3500",
                "readiness_score": 70,
                "decision": "BUY",
                "reason": "PAPER_SIMULATED: Not live-tradeable.",
            }
        )
        self.assertEqual(vector.pair, "WETH/USDC")
        self.assertEqual(vector.confidence_score, 70)
        self.assertIn("paper_simulated", vector.tags)
        self.assertIn("not_live_tradeable", vector.tags)

    def test_decision_explainer_blocks_live_for_synthetic(self):
        explanation = DecisionExplainer().explain(
            {
                "decision": "BUY",
                "estimated_net_edge_pct": "0.35",
                "reason": "PAPER_SIMULATED: Not live-tradeable.",
            }
        )
        self.assertTrue(explanation["accepted_for_paper"])
        self.assertFalse(explanation["accepted_for_live"])
        self.assertTrue(any(c["name"] == "live_tradeable" and not c["passed"] for c in explanation["checks"]))

    def test_feature_store_builds_runtime_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            (root / "reports").mkdir()
            (root / "data" / "opportunity_decisions.jsonl").write_text(
                json.dumps({
                    "timestamp": "2026-01-01T01:02:03Z",
                    "chain": "base",
                    "pair": "WETH/USDC",
                    "buy_source": "Uniswap V2",
                    "sell_source": "SyntheticPaperVenue",
                    "estimated_net_edge_pct": "0.3500",
                    "readiness_score": 70,
                    "decision": "BUY",
                    "reason": "PAPER_SIMULATED: Not live-tradeable.",
                }) + "\n",
                encoding="utf-8",
            )
            (root / "data" / "paper_orders.jsonl").write_text(
                json.dumps({
                    "timestamp": "2026-01-01T01:03:03Z",
                    "chain": "base",
                    "pair": "WETH/USDC",
                    "status": "RISK_REJECTED",
                    "estimated_edge_pct": "0.3500",
                    "reason": "Portfolio risk rejected: duplicate exposure.",
                }) + "\n",
                encoding="utf-8",
            )
            with patch("app.database.db.DB_PATH", root / "data" / "cryptoai.db"):
                old = Path.cwd()
                try:
                    import os
                    os.chdir(root)
                    summary = FeatureStoreService().build_from_runtime()
                finally:
                    os.chdir(old)
            self.assertGreaterEqual(summary["feature_count"], 2)
            self.assertTrue((root / "data" / "feature_vectors.jsonl").exists())
            self.assertTrue((root / "data" / "feature_vectors.csv").exists())
            self.assertTrue((root / "reports" / "feature_store.md").exists())


if __name__ == "__main__":
    unittest.main()
