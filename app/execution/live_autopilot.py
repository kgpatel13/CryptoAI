from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from app.automation.paper_autopilot import SingleInstanceLock, active_autopilot_processes
from app.execution.atomic_live_adapter import AtomicLiveExecutionAdapter, reviewed_atomic_adapter_selected
from app.execution.live_execution_engine_service import LiveExecutionEngineService


class LiveExecutionAdapter(Protocol):
    def execute(self, engine: dict[str, Any]) -> dict[str, Any]:
        """Execute one approved continuous-live cycle."""


@dataclass(frozen=True)
class MissingLiveExecutionAdapter:
    """Fail-closed adapter used until a reviewed atomic executor exists."""

    reason: str = "No reviewed atomic live execution adapter is configured."

    def execute(self, engine: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "REFUSED",
            "transaction_sent": False,
            "reason": self.reason,
            "engine_status": engine.get("overall_status"),
        }


def build_live_execution_adapter(report_dir: Path | str = "reports") -> LiveExecutionAdapter:
    if reviewed_atomic_adapter_selected():
        return AtomicLiveExecutionAdapter(report_dir=report_dir)
    return MissingLiveExecutionAdapter()


class LiveAutopilot:
    """Paper-like continuous live runner shell.

    This runner gives live trading the same operational shape as paper trading:
    a single command, cycle summaries, a journal, and dashboard-visible state.
    It sends transactions only after the live execution engine says continuous
    live is allowed, an explicit send flag is enabled, and a reviewed execution
    adapter is injected. The default adapter fails closed.
    """

    def __init__(
        self,
        data_dir: Path | str = "data",
        report_dir: Path | str = "reports",
        execution_adapter: LiveExecutionAdapter | None = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.journal_file = self.data_dir / "live_autopilot_decisions.jsonl"
        self.execution_adapter = execution_adapter or build_live_execution_adapter(report_dir=self.report_dir)

    def run_once(self) -> dict[str, Any]:
        engine = LiveExecutionEngineService(data_dir=self.data_dir, report_dir=self.report_dir).generate(refresh_control=True)
        decision = self._decision(engine)
        execution = self._execute_if_allowed(engine=engine, decision=decision)
        payload = {
            "timestamp": self._utc_now(),
            "status": decision["status"],
            "action": decision["action"],
            "reason": decision["reason"],
            "transaction_sent": execution["transaction_sent"],
            "execution_result": execution,
            "engine_status": engine.get("overall_status"),
            "execution_stage": engine.get("execution_stage"),
            "can_send_approval": engine.get("can_send_approval"),
            "can_send_smoke_swap": engine.get("can_send_smoke_swap"),
            "can_run_continuous_live": engine.get("can_run_continuous_live"),
            "next_unblock_step": engine.get("next_unblock_step"),
            "next_allowed_command": engine.get("next_allowed_command"),
            "live_execution_adapter": self.execution_adapter.__class__.__name__,
        }
        self._append_journal(payload)
        return payload

    def run_loop(self, interval_seconds: int = 30, max_cycles: int | None = None) -> dict[str, Any]:
        interval_label = "continuous" if interval_seconds == 0 else f"{interval_seconds}s"
        print(f"CryptoAI live autopilot started. Interval: {interval_label}")
        print("Live sends require green gates, CRYPTOAI_LIVE_AUTOPILOT_SEND_ENABLED=true, and a reviewed execution adapter.")
        cycles = 0
        last_payload: dict[str, Any] = {}
        try:
            while True:
                cycles += 1
                last_payload = self.run_once()
                print(json.dumps({"cycle": cycles, **last_payload}, indent=2))
                if max_cycles is not None and cycles >= max_cycles:
                    break
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            pass
        return {"status": "STOPPED", "cycles_completed": cycles, "last_payload": last_payload}

    @staticmethod
    def refuse_if_paper_autopilot_running() -> None:
        running = active_autopilot_processes()
        if not running:
            return
        raise RuntimeError(
            "Refusing live autopilot because paper autopilot is running; active_processes="
            + ", ".join(f"pid={row['pid']} parent={row['parent_pid']}" for row in running)
        )

    @staticmethod
    def _decision(engine: dict[str, Any]) -> dict[str, str]:
        if engine.get("can_run_continuous_live") is True:
            return {
                "status": "READY_FOR_CONTINUOUS_LIVE",
                "action": "SEND_CONTINUOUS_LIVE",
                "reason": "All live execution gates are green for continuous live; send still requires the explicit autopilot send flag and reviewed adapter.",
            }
        if engine.get("can_send_approval") is True:
            return {
                "status": "READY_FOR_MANUAL_APPROVAL",
                "action": "MANUAL_ONLY",
                "reason": "Manual approval is available from the live execution engine; this runner will not auto-approve.",
            }
        if engine.get("can_send_smoke_swap") is True:
            return {
                "status": "READY_FOR_MANUAL_SMOKE_SWAP",
                "action": "MANUAL_ONLY",
                "reason": "Manual tiny smoke swap is available; this runner will not auto-swap.",
            }
        return {
            "status": "BLOCKED",
            "action": "WAIT",
            "reason": str(engine.get("next_unblock_step") or "Live execution engine is blocked."),
        }

    def _execute_if_allowed(self, *, engine: dict[str, Any], decision: dict[str, str]) -> dict[str, Any]:
        if decision["action"] != "SEND_CONTINUOUS_LIVE":
            return {
                "status": "NOT_ATTEMPTED",
                "transaction_sent": False,
                "reason": "Decision did not permit continuous live execution.",
            }
        if not self._bool_env("CRYPTOAI_LIVE_AUTOPILOT_SEND_ENABLED", False):
            return {
                "status": "REFUSED_SEND_FLAG_DISABLED",
                "transaction_sent": False,
                "reason": "Set CRYPTOAI_LIVE_AUTOPILOT_SEND_ENABLED=true only after manual approval of continuous live mode.",
            }
        if engine.get("can_run_continuous_live") is not True:
            return {
                "status": "REFUSED_ENGINE_NOT_READY",
                "transaction_sent": False,
                "reason": "Live execution engine does not permit continuous live execution.",
            }
        result = self.execution_adapter.execute(engine)
        return {
            "status": str(result.get("status", "UNKNOWN")),
            "transaction_sent": bool(result.get("transaction_sent", False)),
            "reason": str(result.get("reason", "")),
            "adapter_result": result,
        }

    def _append_journal(self, payload: dict[str, Any]) -> None:
        with self.journal_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")

    @staticmethod
    def _bool_env(key: str, default: bool) -> bool:
        raw = os.getenv(key)
        if raw is None:
            return default
        return raw.strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="CryptoAI live autopilot runner")
    parser.add_argument("--once", action="store_true", help="Run one live readiness cycle.")
    parser.add_argument("--loop", action="store_true", help="Run continuous live readiness cycles.")
    parser.add_argument("--interval-seconds", type=int, default=int(os.getenv("CRYPTOAI_LIVE_AUTOPILOT_INTERVAL_SECONDS", "0")))
    parser.add_argument("--max-cycles", type=int, default=None)
    parser.add_argument("--disable-single-instance-lock", action="store_true")
    args = parser.parse_args()

    autopilot = LiveAutopilot()
    if args.loop:
        if args.disable_single_instance_lock:
            result = autopilot.run_loop(interval_seconds=max(0, args.interval_seconds), max_cycles=args.max_cycles)
        else:
            LiveAutopilot.refuse_if_paper_autopilot_running()
            with SingleInstanceLock("data/live_autopilot.lock"):
                result = autopilot.run_loop(interval_seconds=max(0, args.interval_seconds), max_cycles=args.max_cycles)
    else:
        result = autopilot.run_once()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
