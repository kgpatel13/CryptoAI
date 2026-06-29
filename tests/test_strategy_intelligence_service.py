from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.ai.strategy_intelligence_service import StrategyIntelligenceService


class StrategyIntelligenceServiceTests(unittest.TestCase):
    def test_clean_evidence_can_mark_strategy_as_paper_optimize_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reports = Path(tmp) / "reports"
            reports.mkdir()
            self._write_base_reports(reports, experiment_fail_count=0, experiment_warn_count=0, closed_positions=12)

            payload = StrategyIntelligenceService(data_dir=Path(tmp) / "data", report_dir=reports).generate()

            self.assertEqual(payload["strategy_count"], 1)
            row = payload["strategies"][0]
            self.assertEqual(row["recommendation"], "PAPER_OPTIMIZE_CANDIDATE")
            self.assertFalse(payload["promotion_allowed"])
            self.assertTrue((reports / "strategy_intelligence.json").exists())
            self.assertTrue((reports / "strategy_intelligence.md").exists())

    def test_experiment_failure_keeps_strategy_in_research(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reports = Path(tmp) / "reports"
            reports.mkdir()
            self._write_base_reports(reports, experiment_fail_count=1, experiment_warn_count=1, closed_positions=12)

            payload = StrategyIntelligenceService(data_dir=Path(tmp) / "data", report_dir=reports).generate()

            row = payload["strategies"][0]
            self.assertEqual(row["recommendation"], "CONTINUE_RESEARCH")
            self.assertIn("Experiment evidence has 1 failing gate(s).", row["blockers"])

    @staticmethod
    def _write_base_reports(
        reports: Path,
        *,
        experiment_fail_count: int,
        experiment_warn_count: int,
        closed_positions: int,
    ) -> None:
        (reports / "strategy_center.json").write_text(
            json.dumps(
                {
                    "generated_at": "2026-06-29T00:00:00Z",
                    "mode": "paper",
                    "strategies": [
                        {
                            "strategy_id": "arbitrage",
                            "strategy_name": "DEX Arbitrage Strategy",
                            "enabled": True,
                            "health": "ACTIVE",
                            "orders": 20,
                            "filled_orders": 12,
                            "closed_positions": closed_positions,
                            "risk_rejected_orders": 1,
                            "realized_pnl_usd": "6.0000",
                            "win_rate_pct": "66.0000",
                            "avg_slippage_bps": "5.0000",
                            "avg_latency_ms": "250.0000",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (reports / "feature_store.json").write_text(
            json.dumps({"generated_at": "2026-06-29T00:00:00Z", "feature_count": 500, "tradeable_or_filled_count": 100}),
            encoding="utf-8",
        )
        (reports / "optimization_report.json").write_text(
            json.dumps(
                {
                    "generated_at": "2026-06-29T00:00:00Z",
                    "best_scenario": {"trade_count": 12, "total_pnl_usd": "8.0000", "cost_buffer_pct": "0.20"},
                }
            ),
            encoding="utf-8",
        )
        (reports / "experiment_report.json").write_text(
            json.dumps(
                {
                    "generated_at": "2026-06-29T00:00:00Z",
                    "latest_experiment": {
                        "status": "PAPER_EVIDENCE_CANDIDATE",
                        "fail_count": experiment_fail_count,
                        "warn_count": experiment_warn_count,
                    },
                }
            ),
            encoding="utf-8",
        )
        (reports / "provider_monitor.json").write_text(
            json.dumps({"generated_at": "2026-06-29T00:00:00Z", "overall_status": "OK", "alert_count": 0}),
            encoding="utf-8",
        )
        (reports / "paper_report.json").write_text(
            json.dumps(
                {
                    "generated_at": "2026-06-29T00:00:00Z",
                    "filled_orders": 12,
                    "portfolio_analytics": {"total_pnl_usd": "6.0000", "total_return_pct": "0.0600"},
                }
            ),
            encoding="utf-8",
        )
        (reports / "report_audit.json").write_text(
            json.dumps({"generated_at": "2026-06-29T00:00:00Z", "finding_count": 0}),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
