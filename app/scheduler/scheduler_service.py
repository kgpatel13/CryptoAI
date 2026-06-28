from __future__ import annotations

import time
from datetime import datetime
from uuid import uuid4

from app.scheduler.models import SchedulerRunResult, SchedulerStepResult, SchedulerStepStatus

try:
    from app.events.event_service import EventBusService
    from app.events.models import EventType
except Exception:
    EventBusService = None
    EventType = None

try:
    from app.database.db import get_connection, initialize_database
    from app.database.event_store import EventStore
except Exception:
    get_connection = None
    initialize_database = None
    EventStore = None

try:
    from app.quotes.quote_service import QuoteService
except Exception:
    QuoteService = None

try:
    from app.strategy.strategy_service import StrategyService
except Exception:
    StrategyService = None

try:
    from app.ai.ranking_service import AiRankingService
except Exception:
    AiRankingService = None

try:
    from app.risk.risk_service import RiskService
except Exception:
    RiskService = None

try:
    from app.execution.paper_execution_service import PaperExecutionService
except Exception:
    PaperExecutionService = None


class SchedulerService:
    """Safe automation loop foundation with event publishing and database persistence."""

    def __init__(self) -> None:
        self.events = EventBusService() if EventBusService is not None else None

    def run_once(self, enable_paper_execution: bool = False) -> SchedulerRunResult:
        run_id = str(uuid4())[:8]
        started = self._utc_now()
        start_perf = time.perf_counter()
        steps: list[SchedulerStepResult] = []

        self._publish(
            EventType.SCHEDULER_RUN_STARTED if EventType else None,
            {
                "run_id": run_id,
                "paper_execution_enabled": enable_paper_execution,
            },
        )

        steps.append(self._run_step("Quote Refresh", self._refresh_quotes, EventType.QUOTE_REFRESH_COMPLETED if EventType else None))
        steps.append(self._run_step("Strategy Signals", self._strategy_signals, EventType.STRATEGY_SIGNALS_GENERATED if EventType else None))
        steps.append(self._run_step("AI Ranking", self._ai_ranking, EventType.AI_RANKING_COMPLETED if EventType else None))
        steps.append(self._run_step("Risk Assessment", self._risk_assessment, EventType.RISK_ASSESSMENT_COMPLETED if EventType else None))

        if enable_paper_execution:
            steps.append(self._run_step("Paper Execution", self._paper_execution, EventType.PAPER_EXECUTION_COMPLETED if EventType else None))
        else:
            steps.append(
                SchedulerStepResult(
                    step_name="Paper Execution",
                    status=SchedulerStepStatus.SKIPPED,
                    items_processed=0,
                    latency_ms=0.0,
                    message="Paper execution disabled for this run.",
                )
            )

        total_latency_ms = (time.perf_counter() - start_perf) * 1000
        final_status = (
            SchedulerStepStatus.FAILED
            if any(step.status == SchedulerStepStatus.FAILED for step in steps)
            else SchedulerStepStatus.OK
        )

        result = SchedulerRunResult(
            run_id=run_id,
            started_at=started,
            completed_at=self._utc_now(),
            status=final_status,
            paper_execution_enabled=enable_paper_execution,
            total_latency_ms=round(total_latency_ms, 2),
            steps=steps,
        )

        self._persist_run(result)

        self._publish(
            EventType.SCHEDULER_RUN_COMPLETED if EventType else None,
            {
                "run_id": result.run_id,
                "status": result.status.value if hasattr(result.status, "value") else str(result.status),
                "total_latency_ms": result.total_latency_ms,
                "steps": len(result.steps),
            },
        )

        return result

    def _run_step(self, name: str, fn, completed_event_type) -> SchedulerStepResult:
        start = time.perf_counter()
        try:
            count, message = fn()
            status = SchedulerStepStatus.OK
        except Exception as exc:
            count = 0
            message = str(exc)
            status = SchedulerStepStatus.FAILED
            self._publish(
                EventType.ERROR if EventType else None,
                {"step": name, "error": str(exc)},
            )

        latency_ms = (time.perf_counter() - start) * 1000
        step = SchedulerStepResult(
            step_name=name,
            status=status,
            items_processed=count,
            latency_ms=round(latency_ms, 2),
            message=message,
        )

        self._publish(
            completed_event_type,
            {
                "step_name": step.step_name,
                "status": step.status.value if hasattr(step.status, "value") else str(step.status),
                "items_processed": step.items_processed,
                "latency_ms": step.latency_ms,
                "message": step.message,
            },
        )

        return step

    @staticmethod
    def _refresh_quotes() -> tuple[int, str]:
        if QuoteService is None:
            return 0, "QuoteService not available."
        quotes = QuoteService().get_base_quotes()
        return len(quotes), "Quote refresh completed."

    @staticmethod
    def _strategy_signals() -> tuple[int, str]:
        if StrategyService is None:
            return 0, "StrategyService not available."
        signals = StrategyService().get_all_signals()
        return len(signals), "Strategy signal generation completed."

    @staticmethod
    def _ai_ranking() -> tuple[int, str]:
        if AiRankingService is None:
            return 0, "AiRankingService not available."
        ranked = AiRankingService().rank_strategy_signals()
        return len(ranked), "AI ranking completed."

    @staticmethod
    def _risk_assessment() -> tuple[int, str]:
        if RiskService is None:
            return 0, "RiskService not available."
        assessments = RiskService().assess_ranked_signals()
        return len(assessments), "Risk assessment completed."

    @staticmethod
    def _paper_execution() -> tuple[int, str]:
        if PaperExecutionService is None:
            return 0, "PaperExecutionService not available."
        batch = PaperExecutionService().run_once()
        return batch.filled_orders, "Paper execution simulation completed."

    @staticmethod
    def _utc_now() -> str:
        return datetime.utcnow().isoformat(timespec="seconds") + "Z"

    def _publish(self, event_type, payload: dict) -> None:
        if self.events is None or event_type is None:
            return
        try:
            self.events.publish(event_type=event_type, source="scheduler", payload=payload)
        except Exception:
            return

    @staticmethod
    def _persist_run(result: SchedulerRunResult) -> None:
        if initialize_database is None or get_connection is None:
            return

        try:
            initialize_database()
            with get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO scheduler_runs
                    (run_id, started_at, completed_at, status,
                     paper_execution_enabled, total_latency_ms)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        result.run_id,
                        result.started_at,
                        result.completed_at,
                        result.status.value if hasattr(result.status, "value") else str(result.status),
                        1 if result.paper_execution_enabled else 0,
                        result.total_latency_ms,
                    ),
                )

                for step in result.steps:
                    conn.execute(
                        """
                        INSERT INTO scheduler_steps
                        (run_id, step_name, status, items_processed, latency_ms, message)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            result.run_id,
                            step.step_name,
                            step.status.value if hasattr(step.status, "value") else str(step.status),
                            step.items_processed,
                            step.latency_ms,
                            step.message,
                        ),
                    )

                conn.commit()

            if EventStore is not None:
                EventStore().record_event("scheduler_run", "scheduler", result)
        except Exception:
            return
