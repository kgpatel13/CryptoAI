from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_TRUE_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AtomicLiveExecutionAdapter:
    """Reviewed-adapter boundary for future atomic live arbitrage sends.

    This adapter deliberately does not synthesize calldata. Atomic arbitrage is
    only safe when the exact deployed executor ABI, function, route encoding,
    min-out limits, deadlines, and revert handling have been reviewed together.
    Until that reviewed calldata builder exists, the adapter can be selected and
    audited but it still refuses to send real money.
    """

    report_dir: Path | str = "reports"

    def execute(self, engine: dict[str, Any]) -> dict[str, Any]:
        checks = self._checks(engine)
        blockers = [row for row in checks if not row["passed"]]
        executor_address = os.getenv("CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS", "").strip()
        if blockers:
            return {
                "status": "REFUSED_ATOMIC_EXECUTOR_NOT_READY",
                "transaction_sent": False,
                "reason": blockers[0]["detail"],
                "executor_address": executor_address or None,
                "checks": checks,
            }

        return {
            "status": "REFUSED_ATOMIC_EXECUTOR_CALLDATA_MISSING",
            "transaction_sent": False,
            "reason": (
                "Reviewed atomic executor configuration is present, but this adapter has no reviewed "
                "atomic calldata builder/ABI. Continuous live arbitrage remains blocked until that "
                "implementation is added and tested."
            ),
            "executor_address": executor_address,
            "checks": checks,
        }

    def _checks(self, engine: dict[str, Any]) -> list[dict[str, Any]]:
        reconciliation = self._read_json("live_pilot_reconciliation.json")
        gates = engine.get("gates", {}) if isinstance(engine.get("gates"), dict) else {}
        executor_address = os.getenv("CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS", "").strip()
        return [
            self._check(
                "engine_ready",
                engine.get("can_run_continuous_live") is True and engine.get("overall_status") == "READY_FOR_CONTINUOUS_LIVE",
                "Live execution engine is not READY_FOR_CONTINUOUS_LIVE.",
            ),
            self._check(
                "executor_enabled",
                self._bool_env("CRYPTOAI_ATOMIC_EXECUTOR_ENABLED"),
                "CRYPTOAI_ATOMIC_EXECUTOR_ENABLED must be true.",
            ),
            self._check(
                "executor_address_valid",
                is_valid_evm_address(executor_address),
                "CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS must be a valid 20-byte EVM address.",
            ),
            self._check(
                "executor_reviewed",
                self._bool_env("CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED"),
                "CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED must be true after code and deployment review.",
            ),
            self._check(
                "adapter_selected",
                reviewed_atomic_adapter_selected(),
                "Select the reviewed adapter with CRYPTOAI_LIVE_EXECUTION_ADAPTER=atomic.",
            ),
            self._check(
                "private_key_present",
                bool(os.getenv("CRYPTOAI_PRIVATE_KEY", "").strip()),
                "CRYPTOAI_PRIVATE_KEY must be present only in the live shell that sends transactions.",
            ),
            self._check(
                "transaction_simulation_passed",
                gates.get("transaction_simulation_passed") is True,
                "Exact calldata plus eth_call transaction simulation must pass.",
            ),
            self._check(
                "live_pilot_reconciled",
                reconciliation.get("overall_status") == "LIVE_PILOT_RECONCILED",
                "Live pilot reconciliation must be LIVE_PILOT_RECONCILED.",
            ),
        ]

    @staticmethod
    def _check(name: str, passed: bool, detail: str) -> dict[str, Any]:
        return {"name": name, "passed": bool(passed), "detail": "PASS" if passed else detail}

    @staticmethod
    def _bool_env(key: str) -> bool:
        return os.getenv(key, "").strip().lower() in _TRUE_VALUES

    def _read_json(self, name: str) -> dict[str, Any]:
        path = Path(self.report_dir) / name
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}


def is_valid_evm_address(value: str) -> bool:
    return bool(re.fullmatch(r"0x[a-fA-F0-9]{40}", value or ""))


def reviewed_atomic_adapter_selected() -> bool:
    selected = os.getenv("CRYPTOAI_LIVE_EXECUTION_ADAPTER", "").strip().lower()
    reviewed = os.getenv("CRYPTOAI_REVIEWED_LIVE_ADAPTER", "").strip().lower()
    return selected == "atomic" or reviewed == "atomic_v1"
