from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from web3 import Web3

from app.blockchain.chains import SUPPORTED_CHAINS
from app.blockchain.rpc_client import RpcClient
from app.execution.atomic_arbitrage_execution_service import AtomicArbitrageExecutionService


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
        atomic_report = AtomicArbitrageExecutionService(report_dir=self.report_dir, refresh_transaction_simulation=False).generate()
        checks = self._checks(engine, atomic_report=atomic_report)
        blockers = [row for row in checks if not row["passed"]]
        executor_address = os.getenv("CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS", "").strip()
        if blockers:
            return {
                "status": "REFUSED_ATOMIC_EXECUTOR_NOT_READY",
                "transaction_sent": False,
                "reason": blockers[0]["detail"],
                "executor_address": executor_address or None,
                "checks": checks,
                "atomic_report_status": atomic_report.get("overall_status"),
            }
        if not self._bool_env("CRYPTOAI_ATOMIC_EXECUTOR_SEND_ENABLED"):
            return {
                "status": "REFUSED_ATOMIC_SEND_FLAG_DISABLED",
                "transaction_sent": False,
                "reason": "Set CRYPTOAI_ATOMIC_EXECUTOR_SEND_ENABLED=true only after reviewing the passing atomic eth_call report.",
                "executor_address": executor_address,
                "checks": checks,
                "atomic_report_status": atomic_report.get("overall_status"),
            }

        sent = self._send_atomic_transaction(atomic_report)
        return {
            "status": "ATOMIC_LIVE_SENT",
            "transaction_sent": True,
            "reason": "Atomic live arbitrage transaction was sent after all live gates and atomic simulation checks passed.",
            "executor_address": executor_address,
            "checks": checks,
            "atomic_report_status": atomic_report.get("overall_status"),
            "send_result": sent,
        }

    def _checks(self, engine: dict[str, Any], *, atomic_report: dict[str, Any]) -> list[dict[str, Any]]:
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
            self._check(
                "atomic_route_simulation_passed",
                atomic_report.get("atomic_route_simulation_passed") is True,
                "Atomic route report must pass exact executor calldata plus eth_call simulation.",
            ),
        ]

    @staticmethod
    def _send_atomic_transaction(atomic_report: dict[str, Any]) -> dict[str, Any]:
        private_key = os.getenv("CRYPTOAI_PRIVATE_KEY", "").strip()
        if not private_key:
            raise RuntimeError("CRYPTOAI_PRIVATE_KEY is not configured.")
        route = atomic_report.get("atomic_route", {}) if isinstance(atomic_report.get("atomic_route"), dict) else {}
        call = route.get("eth_call", {}) if isinstance(route.get("eth_call"), dict) else {}
        if not call.get("to") or not call.get("data"):
            raise RuntimeError("Atomic route report does not include transaction calldata.")

        client = RpcClient(SUPPORTED_CHAINS["base"])
        web3 = client.web3
        wallet = Web3.to_checksum_address(str(call["from"]))
        latest = web3.eth.get_block("latest")
        base_fee = int(latest.get("baseFeePerGas") or web3.eth.gas_price)
        priority_fee = int(os.getenv("CRYPTOAI_LIVE_MAX_PRIORITY_FEE_WEI", str(Web3.to_wei(0.01, "gwei"))))
        max_fee = int(os.getenv("CRYPTOAI_LIVE_MAX_FEE_WEI", str(base_fee * 2 + priority_fee)))
        tx = {
            "chainId": 8453,
            "from": wallet,
            "to": Web3.to_checksum_address(str(call["to"])),
            "data": str(call["data"]),
            "value": 0,
            "nonce": web3.eth.get_transaction_count(wallet, "pending"),
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": priority_fee,
            "type": 2,
        }
        gas = web3.eth.estimate_gas(tx)
        tx["gas"] = min(int(gas * 1.2), int(os.getenv("CRYPTOAI_ATOMIC_LIVE_GAS_LIMIT_CAP", "900000")))
        signed = web3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=int(os.getenv("CRYPTOAI_LIVE_RECEIPT_TIMEOUT_SECONDS", "120")))
        return {
            "tx_hash": tx_hash.hex(),
            "receipt_status": int(receipt.get("status", 0)),
            "block_number": int(receipt.get("blockNumber", 0)),
            "gas_used": int(receipt.get("gasUsed", 0)),
        }

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
