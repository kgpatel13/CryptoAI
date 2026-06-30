from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.automation.paper_autopilot import PaperAutopilot, SingleInstanceLock
from app.operations.models import RuntimeStatus
from app.operations.runtime import OperationsRuntime


class OperationsRuntimeTests(unittest.TestCase):
    def test_single_instance_lock_blocks_second_active_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / "paper_autopilot.lock"
            first = SingleInstanceLock(lock_path)
            first.acquire()
            try:
                with self.assertRaisesRegex(RuntimeError, "already running"):
                    SingleInstanceLock(lock_path).acquire()
            finally:
                first.release()

            self.assertFalse(lock_path.exists())

    def test_single_instance_lock_removes_stale_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / "paper_autopilot.lock"
            lock_path.write_text("pid=0\nstarted_at=old\n", encoding="utf-8")

            lock = SingleInstanceLock(lock_path)
            try:
                lock.acquire()
                self.assertTrue(lock_path.exists())
                self.assertIn(f"pid=", lock_path.read_text(encoding="utf-8"))
            finally:
                lock.release()

    def test_runtime_writes_heartbeat_state_metrics_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            calls = 0

            def run_cycle() -> dict:
                nonlocal calls
                calls += 1
                return {"status": "OK", "run_id": f"cycle-{calls}"}

            runtime = OperationsRuntime(
                service_name="paper_autopilot",
                interval_seconds=0,
                heartbeat_interval_seconds=1,
                max_cycles=2,
                data_dir=root / "data",
                report_dir=root / "reports",
            )

            summary = runtime.run(run_cycle)

            self.assertEqual(summary.status, RuntimeStatus.STOPPED)
            self.assertEqual(summary.cycles_completed, 2)
            self.assertEqual(summary.stop_reason, "max_cycles_reached")

            heartbeat = json.loads((root / "data" / "heartbeat.json").read_text(encoding="utf-8"))
            state = json.loads((root / "data" / "runtime_state.json").read_text(encoding="utf-8"))
            metrics = json.loads((root / "reports" / "operational_metrics.json").read_text(encoding="utf-8"))
            mission = json.loads((root / "reports" / "mission_summary.json").read_text(encoding="utf-8"))

            self.assertEqual(heartbeat["status"], "STOPPED")
            self.assertEqual(state["status"], "STOPPED")
            self.assertEqual(metrics["cycles_completed"], 2)
            self.assertEqual(metrics["scheduler_status_counts"], {"OK": 2})
            self.assertEqual(mission["mode"], "PAPER")
            self.assertFalse(mission["live_trading_enabled"])
            self.assertTrue((root / "reports" / "mission_summary.md").exists())

    def test_runtime_records_failed_cycles_without_enabling_live_trading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def run_cycle() -> dict:
                raise RuntimeError("simulated cycle failure")

            runtime = OperationsRuntime(
                service_name="paper_autopilot",
                interval_seconds=0,
                heartbeat_interval_seconds=1,
                max_cycles=1,
                data_dir=root / "data",
                report_dir=root / "reports",
            )

            summary = runtime.run(run_cycle)

            self.assertEqual(summary.status, RuntimeStatus.STOPPED)
            self.assertEqual(summary.cycles_completed, 1)
            self.assertEqual(summary.cycles_failed, 1)
            self.assertEqual(summary.last_cycle_status, "FAILED")
            self.assertEqual(summary.last_error, "simulated cycle failure")

    def test_autopilot_loop_uses_operations_runtime(self) -> None:
        class FakeRuntime:
            def __init__(self, **kwargs) -> None:
                self.kwargs = kwargs
                captured["kwargs"] = kwargs

            def install_signal_handlers(self) -> None:
                captured["installed"] = True

            def run(self, cycle_runner):
                captured["cycle"] = cycle_runner()
                return RuntimeStatusSummary()

        class RuntimeStatusSummary:
            def to_dict(self) -> dict:
                return {"status": "STOPPED", "cycles_completed": 1}

        captured: dict = {}
        autopilot = PaperAutopilot()

        with patch.object(autopilot, "run_once", return_value={"status": "OK"}):
            with patch("app.automation.paper_autopilot.OperationsRuntime", FakeRuntime):
                result = autopilot.run_loop(
                    interval_seconds=60,
                    max_cycles=1,
                    heartbeat_interval_seconds=5,
                )

        self.assertEqual(result["status"], "STOPPED")
        self.assertTrue(captured["installed"])
        self.assertEqual(captured["cycle"], {"status": "OK"})
        self.assertEqual(captured["kwargs"]["service_name"], "paper_autopilot")
        self.assertEqual(captured["kwargs"]["heartbeat_interval_seconds"], 5)

    def test_autopilot_generates_provider_monitor_after_cycle_refresh(self) -> None:
        calls: list[str] = []

        class FakeOpportunityExplorer:
            def scan(self) -> list:
                calls.append("opportunity")
                return [{"id": "decision-1"}]

        class FakeScheduler:
            def run_once(self, enable_paper_execution: bool = False):
                calls.append("scheduler")
                return SchedulerResult()

        class SchedulerResult:
            status = "OK"
            run_id = "run-1"
            paper_execution_enabled = True
            total_latency_ms = 1.0
            steps = []

        class FakeProviderMonitor:
            def generate(self) -> dict:
                calls.append("provider")
                return {"overall_status": "WATCH"}

        class FakePaperReport:
            def generate(self) -> dict:
                calls.append("paper")
                return {"status": "OK"}

        class FakeReportAudit:
            def generate(self) -> dict:
                calls.append("audit")
                return {"finding_count": 0}

        class FakePaperRunReview:
            def generate(self) -> dict:
                calls.append("run_review")
                return {"overall_status": "PAPER_PROFIT_NOT_SHADOW_READY"}

        class FakeExecutionRealism:
            def generate(self) -> dict:
                calls.append("realism")
                return {"overall_status": "PAPER_ONLY_NEEDS_DEPTH"}

        class FakeExecutionCostEvidence:
            def generate(self) -> dict:
                calls.append("cost")
                return {"confidence": "LOW"}

        class FakeWalletPreflight:
            def generate(self) -> dict:
                calls.append("wallet")
                return {"overall_status": "WALLET_PREP_READY"}

        class FakeLiveSafety:
            def generate(self) -> dict:
                calls.append("live_safety")
                return {"overall_status": "LIVE_BLOCKED"}

        class FakeTransactionSimulation:
            def generate(self) -> dict:
                calls.append("tx_sim")
                return {"overall_status": "TX_SIMULATION_ACTION"}

        class FakeLiveReadiness:
            def generate(self) -> dict:
                calls.append("live_readiness")
                return {"overall_status": "LIVE_REVIEW_NOT_READY"}

        class FakePoolDepthLadder:
            def generate(self) -> dict:
                calls.append("pool_depth")
                return {"overall_status": "DEPTH_EVIDENCE_READY"}

        class FakeMarketIntelligence:
            def generate(self) -> dict:
                calls.append("market")
                return {"overall_readiness_score": 77}

        with (
            patch("app.automation.paper_autopilot.OpportunityExplorerService", FakeOpportunityExplorer),
            patch("app.automation.paper_autopilot.SchedulerService", FakeScheduler),
            patch("app.automation.paper_autopilot.ProviderMonitorService", FakeProviderMonitor),
            patch("app.automation.paper_autopilot.PaperReportService", FakePaperReport),
            patch("app.automation.paper_autopilot.ReportAuditService", FakeReportAudit),
            patch("app.automation.paper_autopilot.PaperRunReviewService", FakePaperRunReview),
            patch("app.automation.paper_autopilot.MarketIntelligenceService", FakeMarketIntelligence),
            patch("app.automation.paper_autopilot.ExecutionRealismService", FakeExecutionRealism),
            patch("app.automation.paper_autopilot.ExecutionCostEvidenceService", FakeExecutionCostEvidence),
            patch("app.automation.paper_autopilot.WalletPreflightService", FakeWalletPreflight),
            patch("app.automation.paper_autopilot.LiveSafetyReportService", FakeLiveSafety),
            patch("app.automation.paper_autopilot.TransactionSimulationService", FakeTransactionSimulation),
            patch("app.automation.paper_autopilot.LiveReadinessChecklistService", FakeLiveReadiness),
            patch("app.automation.paper_autopilot.PoolDepthLadderService", FakePoolDepthLadder),
            patch("app.automation.paper_autopilot.PaperAutopilot._report_missing_or_stale", return_value=True),
        ):
            result = PaperAutopilot().run_once()

        self.assertEqual(
            calls,
            [
                "opportunity",
                "scheduler",
                "paper",
                "provider",
                "market",
                "pool_depth",
                "cost",
                "realism",
                "wallet",
                "live_safety",
                "tx_sim",
                "audit",
                "run_review",
                "live_readiness",
                "audit",
            ],
        )
        self.assertEqual(result["provider_monitor_status"], "WATCH")
        self.assertEqual(result["market_readiness_score"], 77)
        self.assertEqual(result["opportunity_decisions"], 1)


if __name__ == "__main__":
    unittest.main()
