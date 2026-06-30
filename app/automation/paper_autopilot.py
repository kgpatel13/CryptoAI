from __future__ import annotations

import argparse
import os
import time
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

try:
    from app.scheduler.scheduler_service import SchedulerService
except Exception:
    SchedulerService = None

try:
    from app.opportunities.opportunity_explorer import OpportunityExplorerService
except Exception:
    OpportunityExplorerService = None

try:
    from app.events.event_service import EventBusService
    from app.events.models import EventType
except Exception:
    EventBusService = None
    EventType = None

try:
    from app.operations.runtime import OperationsRuntime
except Exception:
    OperationsRuntime = None

try:
    from app.market_intelligence.market_intelligence_service import MarketIntelligenceService
except Exception:
    MarketIntelligenceService = None

try:
    from app.operations.provider_monitor import ProviderMonitorService
except Exception:
    ProviderMonitorService = None

try:
    from app.operations.paper_settings_service import PaperSettingsService
except Exception:
    PaperSettingsService = None

try:
    from app.reporting.paper_report import PaperReportService
except Exception:
    PaperReportService = None

try:
    from app.reporting.report_audit import ReportAuditService
except Exception:
    ReportAuditService = None

try:
    from app.execution.execution_realism_service import ExecutionRealismService
except Exception:
    ExecutionRealismService = None

try:
    from app.research.pool_depth_ladder_service import PoolDepthLadderService
except Exception:
    PoolDepthLadderService = None


class PaperAutopilot:
    """Safe paper-trading autopilot.

    It now also runs Opportunity Explorer so reports explain skipped trades.
    """

    def __init__(self, enable_paper_execution: bool = True) -> None:
        self.enable_paper_execution = enable_paper_execution

    def run_once(self) -> dict:
        self._publish("Paper autopilot cycle started.")

        opportunity_count = 0
        if OpportunityExplorerService is not None:
            try:
                decisions = OpportunityExplorerService().scan()
                opportunity_count = len(decisions)
            except Exception:
                opportunity_count = 0

        if SchedulerService is None:
            provider_monitor_status, market_readiness_score = self._generate_operations_reports()
            return {
                "status": "FAILED",
                "message": "SchedulerService is not available.",
                "provider_monitor_status": provider_monitor_status,
                "market_readiness_score": market_readiness_score,
                "opportunity_decisions": opportunity_count,
                "timestamp": self._utc_now(),
            }

        result = SchedulerService().run_once(
            enable_paper_execution=self.enable_paper_execution
        )
        provider_monitor_status, market_readiness_score = self._generate_operations_reports()

        payload = {
            "status": result.status.value if hasattr(result.status, "value") else str(result.status),
            "run_id": result.run_id,
            "paper_execution_enabled": result.paper_execution_enabled,
            "provider_monitor_status": provider_monitor_status,
            "market_readiness_score": market_readiness_score,
            "opportunity_decisions": opportunity_count,
            "total_latency_ms": result.total_latency_ms,
            "steps": [
                {
                    "step": step.step_name,
                    "status": step.status.value if hasattr(step.status, "value") else str(step.status),
                    "items": step.items_processed,
                    "latency_ms": step.latency_ms,
                    "message": step.message,
                }
                for step in result.steps
            ],
            "timestamp": self._utc_now(),
        }

        self._publish("Paper autopilot cycle completed.", payload)
        return payload

    @staticmethod
    def _generate_operations_reports() -> tuple[str | None, int | None]:
        if PaperReportService is not None:
            try:
                PaperReportService().generate()
            except Exception:
                pass

        provider_monitor_status = None
        if ProviderMonitorService is not None:
            try:
                provider_monitor = ProviderMonitorService().generate()
                provider_monitor_status = provider_monitor.get("overall_status")
            except Exception:
                provider_monitor_status = None

        market_readiness_score = None
        if MarketIntelligenceService is not None:
            try:
                market_intelligence = MarketIntelligenceService().generate()
                market_readiness_score = market_intelligence.get("overall_readiness_score")
            except Exception:
                market_readiness_score = None

        if PoolDepthLadderService is not None and PaperAutopilot._report_missing_or_stale("pool_depth_ladder.json", max_age_seconds=900):
            try:
                PoolDepthLadderService().generate()
            except Exception:
                pass

        if ExecutionRealismService is not None:
            try:
                ExecutionRealismService().generate()
            except Exception:
                pass

        if ReportAuditService is not None:
            try:
                ReportAuditService().generate()
            except Exception:
                pass

        return provider_monitor_status, market_readiness_score

    @staticmethod
    def _report_missing_or_stale(name: str, max_age_seconds: int) -> bool:
        path = Path("reports") / name
        if not path.exists():
            return True
        try:
            return time.time() - path.stat().st_mtime > max_age_seconds
        except Exception:
            return True

    def run_loop(
        self,
        interval_seconds: int,
        max_cycles: int | None = None,
        heartbeat_interval_seconds: int = 60,
    ) -> dict:
        interval_label = "continuous" if interval_seconds == 0 else f"{interval_seconds}s"
        print(f"CryptoAI paper autopilot started. Interval: {interval_label}")
        print("Live trading is disabled. Press Ctrl+C to stop.")

        if OperationsRuntime is not None:
            runtime = OperationsRuntime(
                service_name="paper_autopilot",
                interval_seconds=interval_seconds,
                heartbeat_interval_seconds=heartbeat_interval_seconds,
                max_cycles=max_cycles,
            )
            runtime.install_signal_handlers()
            summary = runtime.run(self.run_once)
            payload = summary.to_dict()
            print(payload)
            return payload

        cycle = 0
        while True:
            try:
                cycle += 1
                result = self.run_once()
                print(result)

                if max_cycles is not None and cycle >= max_cycles:
                    print(f"Paper autopilot completed {max_cycles} cycle(s).")
                    return result

            except KeyboardInterrupt:
                print("Paper autopilot stopped.")
                return {
                    "status": "STOPPED",
                    "message": "Paper autopilot stopped.",
                    "timestamp": self._utc_now(),
                }
            except Exception as exc:
                print(
                    {
                        "status": "FAILED",
                        "message": str(exc),
                        "timestamp": self._utc_now(),
                    }
                )

            time.sleep(interval_seconds)

    @staticmethod
    def _publish(message: str, payload: dict | None = None) -> None:
        if EventBusService is None or EventType is None:
            return
        try:
            EventBusService().publish(
                event_type=EventType.SYSTEM,
                source="paper_autopilot",
                payload={"message": message, **(payload or {})},
            )
        except Exception:
            return

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="CryptoAI paper autopilot")
    parser.add_argument("--once", action="store_true", help="Run one paper cycle")
    parser.add_argument("--loop", action="store_true", help="Run continuous paper cycles")
    parser.add_argument(
        "--interval-seconds",
        type=int,
        default=int(os.getenv("CRYPTOAI_AUTOPILOT_INTERVAL_SECONDS", "300")),
    )
    parser.add_argument(
        "--heartbeat-interval-seconds",
        type=int,
        default=int(os.getenv("CRYPTOAI_HEARTBEAT_INTERVAL_SECONDS", "60")),
    )
    parser.add_argument("--max-cycles", type=int, default=None)
    parser.add_argument("--disable-paper-execution", action="store_true")
    parser.add_argument("--use-settings", action="store_true", help="Load validated 24/7 paper settings from config.")
    parser.add_argument(
        "--settings-file",
        default="config/paper_trading_settings.json",
        help="Paper settings JSON path used with --use-settings.",
    )

    args = parser.parse_args()

    live_enabled = os.getenv("CRYPTOAI_LIVE_TRADING_ENABLED", "false").lower() in {
        "1", "true", "yes", "on",
    }

    if live_enabled:
        raise RuntimeError("Refusing to start because live trading is enabled.")

    cli_max_cycles = args.max_cycles
    if args.use_settings:
        if PaperSettingsService is None:
            raise RuntimeError("PaperSettingsService is not available.")
        settings_service = PaperSettingsService(settings_path=args.settings_file)
        settings = settings_service.load()
        validation = settings_service.generate_report(settings)
        if validation["status"] != "VALID":
            raise RuntimeError(
                "Refusing to start because paper settings are invalid: "
                + "; ".join(row["message"] for row in validation["findings"])
            )
        settings_service.apply_runtime_environment(validation["settings"])
        operations = validation["settings"]["operations"]
        args.interval_seconds = int(operations["loop_interval_seconds"])
        args.heartbeat_interval_seconds = int(operations["heartbeat_interval_seconds"])
        args.max_cycles = cli_max_cycles if cli_max_cycles is not None else operations.get("max_cycles")

    autopilot = PaperAutopilot(enable_paper_execution=not args.disable_paper_execution)

    if args.loop:
        autopilot.run_loop(
            interval_seconds=max(0, args.interval_seconds),
            max_cycles=args.max_cycles,
            heartbeat_interval_seconds=max(1, args.heartbeat_interval_seconds),
        )
    else:
        print(autopilot.run_once())


if __name__ == "__main__":
    main()
