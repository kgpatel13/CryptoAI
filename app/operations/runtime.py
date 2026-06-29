from __future__ import annotations

import json
import os
import signal
import time
from collections import Counter
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.operations.models import (
    Heartbeat,
    MissionSummary,
    OperationalMetrics,
    RuntimeState,
    RuntimeStatus,
)


CycleRunner = Callable[[], dict[str, Any]]


class OperationsRuntime:
    """Owns long-running paper-mode process health and graceful shutdown."""

    def __init__(
        self,
        service_name: str,
        interval_seconds: float,
        heartbeat_interval_seconds: float = 60.0,
        max_cycles: int | None = None,
        data_dir: Path | str = "data",
        report_dir: Path | str = "reports",
    ) -> None:
        if interval_seconds < 0:
            raise ValueError("interval_seconds must be >= 0")
        if heartbeat_interval_seconds <= 0:
            raise ValueError("heartbeat_interval_seconds must be > 0")
        if max_cycles is not None and max_cycles <= 0:
            raise ValueError("max_cycles must be > 0 when provided")

        self.service_name = service_name
        self.interval_seconds = interval_seconds
        self.heartbeat_interval_seconds = heartbeat_interval_seconds
        self.max_cycles = max_cycles
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.run_id = str(uuid4())[:12]
        self.started_at = self._utc_now()
        self._started_perf = time.perf_counter()
        self._shutdown_requested = False
        self._stop_reason: str | None = None
        self._cycles_completed = 0
        self._cycles_failed = 0
        self._heartbeats_emitted = 0
        self._latencies_ms: list[float] = []
        self._status_counts: Counter[str] = Counter()
        self._last_cycle_started_at: str | None = None
        self._last_cycle_completed_at: str | None = None
        self._last_cycle_status: str | None = None
        self._last_error: str | None = None

    def install_signal_handlers(self) -> None:
        """Request shutdown on SIGINT/SIGTERM while preserving safe final writes."""
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, self._handle_signal)
            except (AttributeError, ValueError):
                continue

    def request_shutdown(self, reason: str = "shutdown_requested") -> None:
        self._shutdown_requested = True
        self._stop_reason = reason

    def run(self, cycle_runner: CycleRunner) -> MissionSummary:
        self._ensure_dirs()
        self._write_state(RuntimeStatus.STARTING)
        self._emit_heartbeat(RuntimeStatus.STARTING, "Runtime starting.")

        status = RuntimeStatus.RUNNING
        summary: MissionSummary | None = None
        self._write_state(status)

        try:
            while not self._shutdown_requested:
                self._run_cycle(cycle_runner)
                self._write_reports(status)

                if self.max_cycles is not None and self._cycles_completed >= self.max_cycles:
                    self.request_shutdown("max_cycles_reached")
                    break

                self._wait_until_next_cycle(status)
        except KeyboardInterrupt:
            self.request_shutdown("keyboard_interrupt")
        except Exception as exc:
            status = RuntimeStatus.FAILED
            self._last_error = str(exc)
            self._cycles_failed += 1
            self._status_counts["FAILED"] += 1
        finally:
            final_status = RuntimeStatus.FAILED if status == RuntimeStatus.FAILED else RuntimeStatus.STOPPED
            if self._stop_reason is None:
                self._stop_reason = "failed" if final_status == RuntimeStatus.FAILED else "stopped"
            self._write_state(RuntimeStatus.STOPPING)
            self._emit_heartbeat(RuntimeStatus.STOPPING, "Runtime stopping.")
            self._write_state(final_status)
            summary = self._write_reports(final_status)
            self._emit_heartbeat(final_status, f"Runtime {final_status.value.lower()}.")

        if summary is None:
            raise RuntimeError("Operations runtime stopped without a mission summary.")
        return summary

    def _run_cycle(self, cycle_runner: CycleRunner) -> None:
        self._last_cycle_started_at = self._utc_now()
        start = time.perf_counter()
        try:
            result = cycle_runner()
            cycle_status = str(result.get("status", "UNKNOWN"))
            self._last_error = None
        except Exception as exc:
            cycle_status = "FAILED"
            self._last_error = str(exc)

        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        self._latencies_ms.append(latency_ms)
        self._last_cycle_completed_at = self._utc_now()
        self._last_cycle_status = cycle_status
        self._status_counts[cycle_status] += 1
        self._cycles_completed += 1
        if cycle_status.upper() == "FAILED":
            self._cycles_failed += 1

        self._write_state(RuntimeStatus.RUNNING)
        self._emit_heartbeat(RuntimeStatus.RUNNING, f"Completed cycle {self._cycles_completed}.")

    def _wait_until_next_cycle(self, status: RuntimeStatus) -> None:
        deadline = time.monotonic() + self.interval_seconds
        while not self._shutdown_requested:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return
            wait_for = min(remaining, self.heartbeat_interval_seconds)
            time.sleep(wait_for)
            if not self._shutdown_requested:
                self._write_reports(status)
                self._emit_heartbeat(status, "Runtime healthy.")

    def _write_state(self, status: RuntimeStatus) -> RuntimeState:
        state = RuntimeState(
            service_name=self.service_name,
            status=status,
            run_id=self.run_id,
            started_at=self.started_at,
            updated_at=self._utc_now(),
            uptime_seconds=self._uptime_seconds(),
            cycle_count=self._cycles_completed,
            last_cycle_started_at=self._last_cycle_started_at,
            last_cycle_completed_at=self._last_cycle_completed_at,
            last_cycle_status=self._last_cycle_status,
            last_error=self._last_error,
            stop_reason=self._stop_reason,
        )
        self._write_json(self.data_dir / "runtime_state.json", state.to_dict())
        return state

    def _emit_heartbeat(self, status: RuntimeStatus, message: str) -> Heartbeat:
        self._heartbeats_emitted += 1
        heartbeat = Heartbeat(
            service_name=self.service_name,
            status=status,
            emitted_at=self._utc_now(),
            run_id=self.run_id,
            cycle_count=self._cycles_completed,
            uptime_seconds=self._uptime_seconds(),
            message=message,
        )
        payload = heartbeat.to_dict()
        self._write_json(self.data_dir / "heartbeat.json", payload)
        with (self.data_dir / "heartbeat_history.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
        return heartbeat

    def _write_reports(self, status: RuntimeStatus) -> MissionSummary:
        metrics = OperationalMetrics(
            service_name=self.service_name,
            run_id=self.run_id,
            uptime_seconds=self._uptime_seconds(),
            cycles_completed=self._cycles_completed,
            cycles_failed=self._cycles_failed,
            heartbeats_emitted=self._heartbeats_emitted,
            last_cycle_latency_ms=self._latencies_ms[-1] if self._latencies_ms else 0.0,
            average_cycle_latency_ms=round(sum(self._latencies_ms) / len(self._latencies_ms), 2)
            if self._latencies_ms
            else 0.0,
            scheduler_status_counts=dict(sorted(self._status_counts.items())),
        )
        self._write_json(self.report_dir / "operational_metrics.json", metrics.to_dict())

        summary = MissionSummary(
            service_name=self.service_name,
            run_id=self.run_id,
            status=status,
            mode="PAPER",
            started_at=self.started_at,
            updated_at=self._utc_now(),
            uptime_seconds=self._uptime_seconds(),
            cycles_completed=self._cycles_completed,
            cycles_failed=self._cycles_failed,
            last_cycle_status=self._last_cycle_status,
            last_error=self._last_error,
            live_trading_enabled=self._live_trading_enabled(),
            stop_reason=self._stop_reason,
        )
        self._write_json(self.report_dir / "mission_summary.json", summary.to_dict())
        self._write_mission_markdown(summary, metrics)
        return summary

    def _write_mission_markdown(self, summary: MissionSummary, metrics: OperationalMetrics) -> None:
        lines = [
            "# Mission Summary",
            "",
            f"- Service: {summary.service_name}",
            f"- Status: {summary.status.value}",
            f"- Mode: {summary.mode}",
            f"- Run ID: {summary.run_id}",
            f"- Started At: {summary.started_at}",
            f"- Updated At: {summary.updated_at}",
            f"- Uptime Seconds: {summary.uptime_seconds}",
            f"- Cycles Completed: {summary.cycles_completed}",
            f"- Cycles Failed: {summary.cycles_failed}",
            f"- Last Cycle Status: {summary.last_cycle_status or '-'}",
            f"- Live Trading Enabled: {summary.live_trading_enabled}",
            f"- Stop Reason: {summary.stop_reason or '-'}",
            "",
            "## Operational Metrics",
            "",
            f"- Heartbeats Emitted: {metrics.heartbeats_emitted}",
            f"- Last Cycle Latency ms: {metrics.last_cycle_latency_ms}",
            f"- Average Cycle Latency ms: {metrics.average_cycle_latency_ms}",
            f"- Scheduler Status Counts: {metrics.scheduler_status_counts}",
        ]
        if summary.last_error:
            lines.extend(["", "## Last Error", "", summary.last_error])
        (self.report_dir / "mission_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _handle_signal(self, signum: int, _frame: Any) -> None:
        self.request_shutdown(f"signal_{signum}")

    def _ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _uptime_seconds(self) -> float:
        return round(time.perf_counter() - self._started_perf, 2)

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")

    @staticmethod
    def _live_trading_enabled() -> bool:
        return os.getenv("CRYPTOAI_LIVE_TRADING_ENABLED", "false").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
