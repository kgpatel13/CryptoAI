from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.reporting.paper_run_review import PaperRunReviewService


class PaperRunReviewServiceTests(unittest.TestCase):
    def test_profitable_paper_run_remains_blocked_without_depth_or_shadow_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            reports = root / "reports"
            data.mkdir()
            reports.mkdir()

            (data / "paper_portfolio_state.json").write_text(
                json.dumps(
                    {
                        "initial_cash_usd": "1000.00",
                        "cash_usd": "1066.4528",
                        "realized_pnl_usd": "66.4528",
                        "positions": [],
                    }
                ),
                encoding="utf-8",
            )
            (data / "paper_orders.jsonl").write_text(
                json.dumps(
                    {
                        "order_id": "o1",
                        "timestamp": "2026-06-30T07:35:00Z",
                        "status": "CLOSED",
                        "pair": "WETH/USDC",
                        "realized_pnl_usd": "66.4528",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (reports / "paper_report.json").write_text(
                json.dumps({"pnl_reconciliation": {"status": "RECONCILED"}}),
                encoding="utf-8",
            )
            (reports / "portfolio_analytics.json").write_text(
                json.dumps({"pnl_reconciliation": {"status": "RECONCILED"}}),
                encoding="utf-8",
            )
            (reports / "provider_monitor.json").write_text(
                json.dumps({"overall_status": "OK"}),
                encoding="utf-8",
            )
            (reports / "pool_depth_ladder.json").write_text(
                json.dumps({"overall_status": "DEPTH_EVIDENCE_WATCH", "depth_ready_route_count": 0}),
                encoding="utf-8",
            )
            (reports / "execution_realism.json").write_text(
                json.dumps({"overall_status": "NOT_SHADOW_READY", "confidence": "NONE", "shadow_ready_count": 0, "live_ready_count": 0}),
                encoding="utf-8",
            )
            (reports / "report_audit.json").write_text(
                json.dumps({"finding_count": 0}),
                encoding="utf-8",
            )

            review = PaperRunReviewService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(review["overall_status"], "PAPER_PROFIT_NOT_SHADOW_READY")
            self.assertEqual(review["shadow_decision"], "BLOCKED")
            self.assertEqual(review["live_decision"], "BLOCKED")
            self.assertEqual(review["closed_trade_count"], 1)
            self.assertEqual(review["losing_trade_count"], 0)
            blocked = {gate["name"] for gate in review["gates"] if gate["status"] == "BLOCK"}
            self.assertIn("pool_depth_ready", blocked)
            self.assertIn("execution_shadow_ready", blocked)
            self.assertTrue((reports / "paper_run_review.json").exists())
            self.assertTrue((reports / "paper_run_review.md").exists())

    def test_losing_trade_blocks_review_and_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            reports = root / "reports"
            data.mkdir()
            reports.mkdir()

            (data / "paper_portfolio_state.json").write_text(
                json.dumps({"initial_cash_usd": "1000", "cash_usd": "995", "realized_pnl_usd": "-5", "positions": []}),
                encoding="utf-8",
            )
            (data / "paper_orders.jsonl").write_text(
                json.dumps({"order_id": "loss1", "timestamp": "2026-06-30T07:35:00Z", "status": "CLOSED", "realized_pnl_usd": "-5"})
                + "\n",
                encoding="utf-8",
            )
            (reports / "paper_report.json").write_text(json.dumps({"pnl_reconciliation": {"status": "RECONCILED"}}), encoding="utf-8")
            (reports / "portfolio_analytics.json").write_text(json.dumps({"pnl_reconciliation": {"status": "RECONCILED"}}), encoding="utf-8")
            (reports / "provider_monitor.json").write_text(json.dumps({"overall_status": "OK"}), encoding="utf-8")
            (reports / "pool_depth_ladder.json").write_text(json.dumps({"depth_ready_route_count": 1}), encoding="utf-8")
            (reports / "execution_realism.json").write_text(json.dumps({"shadow_ready_count": 1, "confidence": "MEDIUM"}), encoding="utf-8")
            (reports / "report_audit.json").write_text(json.dumps({"finding_count": 0}), encoding="utf-8")

            review = PaperRunReviewService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(review["overall_status"], "PAPER_LOSS_REVIEW")
            self.assertEqual(review["shadow_decision"], "BLOCKED")
            self.assertEqual(review["losing_trade_count"], 1)
            self.assertTrue(any("negative realized PnL" in finding["message"] for finding in review["findings"]))

    def test_stale_research_audit_findings_do_not_block_shadow_review_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            reports = root / "reports"
            data.mkdir()
            reports.mkdir()

            (data / "paper_portfolio_state.json").write_text(
                json.dumps({"initial_cash_usd": "500", "cash_usd": "510", "realized_pnl_usd": "10", "positions": []}),
                encoding="utf-8",
            )
            (data / "paper_orders.jsonl").write_text(
                json.dumps({"order_id": "win1", "timestamp": "2026-06-30T07:35:00Z", "status": "CLOSED", "realized_pnl_usd": "10"})
                + "\n",
                encoding="utf-8",
            )
            (reports / "paper_report.json").write_text(json.dumps({"pnl_reconciliation": {"status": "RECONCILED"}}), encoding="utf-8")
            (reports / "portfolio_analytics.json").write_text(json.dumps({"pnl_reconciliation": {"status": "RECONCILED"}}), encoding="utf-8")
            (reports / "provider_monitor.json").write_text(json.dumps({"overall_status": "OK"}), encoding="utf-8")
            (reports / "pool_depth_ladder.json").write_text(json.dumps({"depth_ready_route_count": 1, "overall_status": "DEPTH_EVIDENCE_READY"}), encoding="utf-8")
            (reports / "execution_realism.json").write_text(json.dumps({"shadow_ready_count": 1, "live_ready_count": 0, "confidence": "MEDIUM"}), encoding="utf-8")
            (reports / "report_audit.json").write_text(
                json.dumps(
                    {
                        "finding_count": 5,
                        "blocking_finding_count": 0,
                        "operational_finding_count": 0,
                        "research_finding_count": 5,
                    }
                ),
                encoding="utf-8",
            )

            review = PaperRunReviewService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(review["overall_status"], "SHADOW_REVIEW_CANDIDATE")
            self.assertEqual(review["shadow_decision"], "REVIEW_READY")
            self.assertEqual(review["report_audit_blocking_findings"], 0)
            self.assertTrue(any("paper runtime gates are not blocked" in finding["message"] for finding in review["findings"]))


if __name__ == "__main__":
    unittest.main()
