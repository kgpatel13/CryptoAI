from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.backtesting.experiment_service import ExperimentService


class ExperimentServiceTests(unittest.TestCase):
    def test_experiment_records_research_only_when_gates_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir, report_dir = self._dirs(tmp)
            self._write_json(
                report_dir / "backtest_report.json",
                {"generated_at": "2026-06-29T00:00:00Z", "simulated_trades": 0, "total_simulated_profit_usd": "0.0000"},
            )
            self._write_json(
                report_dir / "optimization_report.json",
                {"generated_at": "2026-06-29T00:00:00Z", "best_scenario": {"trade_count": 8, "total_pnl_usd": "1.0000"}},
            )
            self._write_json(
                report_dir / "provider_monitor.json",
                {"generated_at": "2026-06-29T00:00:00Z", "overall_status": "CRITICAL", "alert_count": 2},
            )
            self._write_json(
                report_dir / "paper_report.json",
                {"generated_at": "2026-06-29T00:00:00Z", "portfolio_analytics": {"total_pnl_usd": "0.1000"}},
            )
            self._write_json(report_dir / "report_audit.json", {"generated_at": "2026-06-29T00:00:00Z", "finding_count": 1})

            payload = ExperimentService(data_dir=data_dir, report_dir=report_dir).run(
                run_backtest=False,
                run_optimization=False,
            )

            latest = payload["latest_experiment"]
            self.assertEqual(latest["status"], "RESEARCH_ONLY")
            self.assertFalse(latest["promotion_allowed"])
            self.assertGreaterEqual(latest["fail_count"], 1)
            self.assertTrue((data_dir / "experiments.jsonl").exists())
            self.assertTrue((report_dir / "experiment_report.json").exists())
            self.assertTrue((report_dir / "experiment_report.md").exists())

    def test_experiment_candidate_still_does_not_allow_live_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir, report_dir = self._dirs(tmp)
            self._write_json(
                report_dir / "backtest_report.json",
                {"generated_at": "2026-06-29T00:00:00Z", "simulated_trades": 2, "total_simulated_profit_usd": "1.5000"},
            )
            self._write_json(
                report_dir / "optimization_report.json",
                {
                    "generated_at": "2026-06-29T00:00:00Z",
                    "scenario_count": 2,
                    "best_scenario": {"trade_count": 6, "total_pnl_usd": "2.0000", "cost_buffer_pct": "0.30"},
                },
            )
            self._write_json(
                report_dir / "provider_monitor.json",
                {"generated_at": "2026-06-29T00:00:00Z", "overall_status": "OK", "alert_count": 0},
            )
            self._write_json(
                report_dir / "paper_report.json",
                {"generated_at": "2026-06-29T00:00:00Z", "portfolio_analytics": {"total_pnl_usd": "0.1000"}},
            )
            self._write_json(report_dir / "report_audit.json", {"generated_at": "2026-06-29T00:00:00Z", "finding_count": 0})

            payload = ExperimentService(data_dir=data_dir, report_dir=report_dir).run(
                run_backtest=False,
                run_optimization=False,
            )

            latest = payload["latest_experiment"]
            self.assertEqual(latest["status"], "PAPER_EVIDENCE_CANDIDATE")
            self.assertFalse(latest["promotion_allowed"])
            self.assertEqual(latest["fail_count"], 0)
            self.assertEqual(latest["warn_count"], 0)

    def test_provider_watch_status_keeps_experiment_on_watchlist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir, report_dir = self._dirs(tmp)
            self._write_json(
                report_dir / "backtest_report.json",
                {"generated_at": "2026-06-29T00:00:00Z", "simulated_trades": 2, "total_simulated_profit_usd": "1.5000"},
            )
            self._write_json(
                report_dir / "optimization_report.json",
                {
                    "generated_at": "2026-06-29T00:00:00Z",
                    "scenario_count": 2,
                    "best_scenario": {"trade_count": 6, "total_pnl_usd": "2.0000", "cost_buffer_pct": "0.30"},
                },
            )
            self._write_json(
                report_dir / "provider_monitor.json",
                {"generated_at": "2026-06-29T00:00:00Z", "overall_status": "WATCH", "alert_count": 1},
            )
            self._write_json(
                report_dir / "paper_report.json",
                {"generated_at": "2026-06-29T00:00:00Z", "portfolio_analytics": {"total_pnl_usd": "0.1000"}},
            )
            self._write_json(report_dir / "report_audit.json", {"generated_at": "2026-06-29T00:00:00Z", "finding_count": 0})

            payload = ExperimentService(data_dir=data_dir, report_dir=report_dir).run(
                run_backtest=False,
                run_optimization=False,
            )

            latest = payload["latest_experiment"]
            self.assertEqual(latest["status"], "WATCHLIST")
            self.assertEqual(latest["fail_count"], 0)
            self.assertEqual(latest["warn_count"], 1)
            provider_gate = [gate for gate in latest["gates"] if gate["name"] == "provider_health_not_critical"][0]
            self.assertEqual(provider_gate["status"], "WARN")

    def test_stale_downstream_reports_do_not_block_experiment_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir, report_dir = self._dirs(tmp)
            self._write_json(
                report_dir / "backtest_report.json",
                {"generated_at": "2026-06-29T00:00:00Z", "simulated_trades": 2, "total_simulated_profit_usd": "1.5000"},
            )
            self._write_json(
                report_dir / "optimization_report.json",
                {
                    "generated_at": "2026-06-29T00:00:00Z",
                    "scenario_count": 2,
                    "best_scenario": {"trade_count": 6, "total_pnl_usd": "2.0000", "cost_buffer_pct": "0.30"},
                },
            )
            self._write_json(
                report_dir / "provider_monitor.json",
                {"generated_at": "2026-06-29T00:00:00Z", "overall_status": "OK", "alert_count": 0},
            )
            self._write_json(
                report_dir / "paper_report.json",
                {"generated_at": "2026-06-29T00:00:00Z", "portfolio_analytics": {"total_pnl_usd": "0.1000"}},
            )
            self._write_json(
                report_dir / "report_audit.json",
                {
                    "generated_at": "2026-06-29T00:00:00Z",
                    "finding_count": 2,
                    "findings": [
                        {
                            "severity": "WATCH",
                            "report": "experiment_report.json",
                            "message": "Report is older than freshness window.",
                        },
                        {
                            "severity": "WATCH",
                            "report": "strategy_intelligence.json",
                            "message": "Report is older than freshness window.",
                        },
                    ],
                },
            )

            payload = ExperimentService(data_dir=data_dir, report_dir=report_dir).run(
                run_backtest=False,
                run_optimization=False,
            )

            latest = payload["latest_experiment"]
            self.assertEqual(latest["summary"]["audit_finding_count"], 0)
            audit_gate = [gate for gate in latest["gates"] if gate["name"] == "report_audit_has_no_findings"][0]
            self.assertEqual(audit_gate["status"], "PASS")

    @staticmethod
    def _dirs(tmp: str) -> tuple[Path, Path]:
        root = Path(tmp)
        data_dir = root / "data"
        report_dir = root / "reports"
        data_dir.mkdir()
        report_dir.mkdir()
        return data_dir, report_dir

    @staticmethod
    def _write_json(path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
