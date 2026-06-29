from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.reporting.paper_report import PaperReportService
from app.reporting.report_audit import ReportAuditService


class ReportAuditTests(unittest.TestCase):
    def test_report_audit_flags_provider_critical_and_paper_simulated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reports = Path(tmp)
            (reports / "provider_monitor.json").write_text(
                json.dumps(
                    {
                        "generated_at": "2026-06-29T02:00:00Z",
                        "overall_status": "CRITICAL",
                        "alert_count": 2,
                    }
                ),
                encoding="utf-8",
            )
            (reports / "paper_report.json").write_text(
                json.dumps(
                    {
                        "generated_at": "2026-06-29T02:00:00Z",
                        "opportunity_decision_counts": {"BUY": 2},
                        "legacy_accounting_warning_count": 1,
                    }
                ),
                encoding="utf-8",
            )
            (reports / "opportunity_explorer.md").write_text(
                "# CryptoAI Opportunity Explorer\n\nGenerated: `2026-06-29T02:00:00Z`\n\nPAPER_SIMULATED\n",
                encoding="utf-8",
            )
            (reports / "quote_diagnostics.md").write_text(
                "# CryptoAI Quote Diagnostics\n\n"
                "Generated: `2026-06-29T02:00:00Z`\n\n"
                "## Summary\n\n"
                "- Error: `2`\n"
                "- Invalid: `1`\n",
                encoding="utf-8",
            )

            payload = ReportAuditService(report_dir=reports, stale_after_minutes=999999).generate()

            messages = [finding["message"] for finding in payload["findings"]]
            self.assertTrue(any("Provider Monitor status is CRITICAL" in message for message in messages))
            self.assertTrue(any("Quote Diagnostics has 2 error row(s)" in message for message in messages))
            self.assertTrue(any("legacy inverse-pair" in message for message in messages))
            self.assertTrue(any("paper-simulated" in message for message in messages))
            self.assertTrue((reports / "report_audit.json").exists())
            self.assertTrue((reports / "report_audit.md").exists())

    def test_paper_report_annotates_legacy_inverse_pair_orders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            reports = root / "reports"
            data.mkdir()
            reports.mkdir()
            (data / "paper_orders.jsonl").write_text(
                json.dumps(
                    {
                        "order_id": "legacy1",
                        "timestamp": "2026-06-28T00:00:00Z",
                        "pair": "USDC/WETH",
                        "status": "FILLED",
                        "notional_usd": "100",
                        "simulated_fill_price_usd": "0.00063",
                        "simulated_quantity": "158000",
                        "estimated_edge_pct": "0.35",
                        "reason": "legacy",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            report = PaperReportService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(report["legacy_accounting_warning_count"], 1)
            self.assertIn("legacy_accounting_warning", report["latest_orders"][0])


if __name__ == "__main__":
    unittest.main()
