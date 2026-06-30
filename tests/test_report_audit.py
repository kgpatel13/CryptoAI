from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime
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

    def test_stale_research_reports_are_non_blocking_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reports = Path(tmp)
            self._write_all_expected_reports(reports)
            stale_at = "2020-01-01T00:00:00Z"
            (reports / "backtest_report.json").write_text(json.dumps({"generated_at": stale_at}), encoding="utf-8")
            (reports / "backtest_report.md").write_text(f"# Backtest\n\nGenerated: `{stale_at}`\n", encoding="utf-8")

            payload = ReportAuditService(report_dir=reports, stale_after_minutes=30).generate()

            self.assertEqual(payload["blocking_finding_count"], 0)
            self.assertEqual(payload["operational_finding_count"], 0)
            self.assertEqual(payload["research_finding_count"], 2)
            self.assertTrue(all(not finding["blocks_shadow_review"] for finding in payload["findings"]))

    def test_stale_operational_reports_remain_blocking_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reports = Path(tmp)
            self._write_all_expected_reports(reports)
            stale_at = "2020-01-01T00:00:00Z"
            (reports / "paper_report.json").write_text(json.dumps({"generated_at": stale_at}), encoding="utf-8")

            payload = ReportAuditService(report_dir=reports, stale_after_minutes=30).generate()

            self.assertEqual(payload["blocking_finding_count"], 1)
            self.assertEqual(payload["operational_finding_count"], 1)
            self.assertEqual(payload["research_finding_count"], 0)
            self.assertTrue(payload["findings"][0]["blocks_shadow_review"])

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

    def test_paper_report_counts_closed_arbitrage_and_matches_state_open_positions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            reports = root / "reports"
            data.mkdir()
            reports.mkdir()
            (data / "paper_orders.jsonl").write_text(
                json.dumps(
                    {
                        "order_id": "arb1",
                        "timestamp": "2026-06-29T00:00:00Z",
                        "pair": "USDC/WETH",
                        "status": "CLOSED",
                        "execution_type": "ARBITRAGE_ROUND_TRIP",
                        "buy_source": "Uniswap V2",
                        "sell_source": "Uniswap V3",
                        "notional_usd": "10000.0000",
                        "filled_notional_usd": "10000.0000",
                        "simulated_fill_price_usd": "0.000626",
                        "simulated_quantity": "15974440.89456869",
                        "realized_pnl_usd": "35.0000",
                        "gross_edge_pct": "0.65",
                        "cost_buffer_pct": "0.30",
                        "net_edge_pct": "0.35",
                        "reason": "closed",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (data / "paper_portfolio_state.json").write_text(
                json.dumps(
                    {
                        "initial_cash_usd": "10000",
                        "cash_usd": "10035.0000",
                        "realized_pnl_usd": "35.0000",
                        "unrealized_pnl_usd": "0.0000",
                        "positions": [],
                    }
                ),
                encoding="utf-8",
            )

            report = PaperReportService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(report["filled_orders"], 1)
            self.assertEqual(report["total_realized_pnl_usd"], "35.0000")
            self.assertEqual(report["portfolio"]["open_positions"], 0)
            self.assertEqual(report["portfolio_analytics"]["open_positions"], 0)
            self.assertEqual(report["portfolio_analytics"]["cash_usd"], "10035.0000")
            self.assertEqual(report["legacy_accounting_warning_count"], 0)

    def test_paper_report_reconciles_pnl_to_active_portfolio_state(self) -> None:
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
                                "order_id": "old1",
                                "timestamp": "2026-06-29T00:00:00Z",
                                "pair": "WETH/USDC",
                                "status": "CLOSED",
                                "execution_type": "ARBITRAGE_ROUND_TRIP",
                                "notional_usd": "1000.0000",
                                "realized_pnl_usd": "100.0000",
                            }
                        ),
                        json.dumps(
                            {
                                "order_id": "active1",
                                "timestamp": "2026-06-30T00:00:00Z",
                                "pair": "WETH/USDC",
                                "status": "CLOSED",
                                "execution_type": "ARBITRAGE_ROUND_TRIP",
                                "notional_usd": "1000.0000",
                                "realized_pnl_usd": "30.0000",
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (data / "paper_portfolio_state.json").write_text(
                json.dumps(
                    {
                        "initial_cash_usd": "1000",
                        "cash_usd": "1030.0000",
                        "realized_pnl_usd": "30.0000",
                        "daily_realized_pnl_usd": "30.0000",
                        "positions": [],
                    }
                ),
                encoding="utf-8",
            )

            report = PaperReportService(data_dir=data, report_dir=reports).generate()

            self.assertEqual(report["total_realized_pnl_usd"], "30.0000")
            self.assertEqual(report["portfolio_realized_pnl_usd"], "30.0000")
            self.assertEqual(report["order_file_realized_pnl_usd"], "130.0000")
            self.assertEqual(
                report["pnl_reconciliation"]["status"],
                "ORDER_HISTORY_DIFFERS_FROM_PORTFOLIO_STATE",
            )

    def _write_all_expected_reports(self, reports: Path) -> None:
        generated_at = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
        for name in ReportAuditService.EXPECTED_REPORTS:
            path = reports / name
            if path.suffix == ".json":
                path.write_text(json.dumps({"generated_at": generated_at}), encoding="utf-8")
            else:
                path.write_text(f"# {name}\n\nGenerated: `{generated_at}`\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
