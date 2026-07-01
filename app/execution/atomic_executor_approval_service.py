from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable

from web3 import Web3

from app.blockchain.chains import SUPPORTED_CHAINS
from app.blockchain.rpc_client import RpcClient
from app.config.feature_flags import load_feature_flags
from app.execution.atomic_arbitrage_execution_service import AtomicArbitrageExecutionService
from app.execution.tiny_live_pilot_service import ERC20_ABI
from app.registry.tokens import get_token


TxSender = Callable[[dict[str, Any], str], dict[str, Any]]


@dataclass(frozen=True)
class AtomicApprovalPlan:
    wallet_address: str
    executor_address: str
    approval_usd: Decimal
    amount_units: int = 0
    usdc_balance_units: int = 0
    allowance_units: int = 0
    chain_id: int | None = None
    latest_block: int | None = None
    rpc_url: str | None = None
    executor_code_bytes: int = 0
    approval_tx: dict[str, Any] | None = None
    error: str | None = None

    @property
    def allowance_sufficient(self) -> bool:
        return self.amount_units > 0 and self.allowance_units >= self.amount_units

    def with_error(self, error: str) -> "AtomicApprovalPlan":
        return AtomicApprovalPlan(
            wallet_address=self.wallet_address,
            executor_address=self.executor_address,
            approval_usd=self.approval_usd,
            error=error,
        )

    def to_report(self) -> dict[str, Any]:
        decimals = Decimal(10**6)
        return {
            "wallet_address": self.wallet_address,
            "executor_address": self.executor_address,
            "approval_usd": str(self.approval_usd),
            "amount_units": str(self.amount_units),
            "usdc_balance": str(Decimal(self.usdc_balance_units) / decimals),
            "usdc_balance_units": str(self.usdc_balance_units),
            "usdc_allowance": str(Decimal(self.allowance_units) / decimals),
            "usdc_allowance_units": str(self.allowance_units),
            "allowance_sufficient": self.allowance_sufficient,
            "chain_id": self.chain_id,
            "latest_block": self.latest_block,
            "rpc_url": self.rpc_url,
            "executor_code_bytes": self.executor_code_bytes,
            "approval_tx_available": self.approval_tx is not None,
            "error": self.error,
        }


class AtomicExecutorApprovalService:
    """Capped USDC approval helper for the atomic arbitrage executor."""

    CONFIRM_PHRASE = "ATOMIC_EXECUTOR_APPROVED"

    def __init__(
        self,
        data_dir: Path | str = "data",
        report_dir: Path | str = "reports",
        tx_sender: TxSender | None = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.output_json = self.report_dir / "atomic_executor_approval.json"
        self.output_md = self.report_dir / "atomic_executor_approval.md"
        self.journal_file = self.data_dir / "atomic_executor_approvals.jsonl"
        self.tx_sender = tx_sender or self._default_tx_sender

    def generate(self, mode: str = "plan", confirm: str = "") -> dict[str, Any]:
        mode = mode.strip().lower()
        if mode not in {"plan", "approve"}:
            raise ValueError("mode must be plan or approve")

        flags = load_feature_flags()
        atomic_report = AtomicArbitrageExecutionService(report_dir=self.report_dir, refresh_transaction_simulation=False).generate()
        plan = self._prepare(flags)
        checks = self._checks(flags=flags, atomic_report=atomic_report, plan=plan, mode=mode, confirm=confirm)
        blockers = [row for row in checks if row["severity"] == "BLOCK"]
        sent: dict[str, Any] | None = None

        if mode == "approve" and not blockers:
            if plan.approval_tx is None:
                blockers.append(self._check("approval_tx_available", False, "Approval transaction is not available.", "Approval transaction is available."))
            else:
                sent = self.tx_sender(plan.approval_tx, os.getenv("CRYPTOAI_PRIVATE_KEY", "").strip())
                self._append_journal(plan=plan, sent=sent)

        payload = {
            "generated_at": self._utc_now(),
            "mode": mode,
            "overall_status": "ATOMIC_APPROVAL_SENT" if sent and not blockers else ("ATOMIC_APPROVAL_READY" if not blockers else "ATOMIC_APPROVAL_BLOCKED"),
            "send_attempted": sent is not None,
            "send_result": sent,
            "blocked_check_count": len(blockers),
            "check_count": len(checks),
            "checks": checks,
            "approval_plan": plan.to_report(),
            "atomic_report_status": atomic_report.get("overall_status"),
            "notes": [
                "Atomic executor approval is a real Base transaction in approve mode.",
                "It approves a capped USDC amount to the atomic executor, not to a router.",
                "Approval does not start trading. Atomic route simulation must still pass before live autopilot can send arbitrage.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _prepare(self, flags: Any) -> AtomicApprovalPlan:
        wallet = flags.live_wallet_address
        executor = os.getenv("CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS", "").strip()
        approval_usd = self._approval_usd(flags.max_live_trade_usd)
        base = AtomicApprovalPlan(wallet_address=wallet, executor_address=executor, approval_usd=approval_usd)
        if not wallet:
            return base.with_error("Missing CRYPTOAI_LIVE_WALLET_ADDRESS.")
        if not executor:
            return base.with_error("Missing CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS.")
        if approval_usd <= 0:
            return base.with_error("Atomic approval amount must be greater than zero.")

        token_usdc = get_token("base", "USDC")
        if token_usdc is None:
            return base.with_error("Base USDC token metadata is missing.")

        try:
            wallet_address = Web3.to_checksum_address(wallet)
            executor_address = Web3.to_checksum_address(executor)
            amount_units = self._to_units(approval_usd, token_usdc.decimals)
            client = RpcClient(SUPPORTED_CHAINS["base"])
            web3 = client.web3
            usdc = web3.eth.contract(address=Web3.to_checksum_address(token_usdc.address), abi=ERC20_ABI)
            balance_units = int(usdc.functions.balanceOf(wallet_address).call())
            allowance_units = int(usdc.functions.allowance(wallet_address, executor_address).call())
            code = web3.eth.get_code(executor_address)
            approval_tx = self._build_approval_tx(
                web3=web3,
                token_address=Web3.to_checksum_address(token_usdc.address),
                wallet=wallet_address,
                spender=executor_address,
                amount_units=amount_units,
            )
            return AtomicApprovalPlan(
                wallet_address=wallet_address,
                executor_address=executor_address,
                approval_usd=approval_usd,
                amount_units=amount_units,
                usdc_balance_units=balance_units,
                allowance_units=allowance_units,
                chain_id=int(web3.eth.chain_id),
                latest_block=int(web3.eth.block_number),
                rpc_url=self._redact_url(client.rpc_url_used),
                executor_code_bytes=len(code),
                approval_tx=approval_tx,
            )
        except Exception as exc:
            return base.with_error(f"{type(exc).__name__}: {exc}")

    def _checks(self, *, flags: Any, atomic_report: dict[str, Any], plan: AtomicApprovalPlan, mode: str, confirm: str) -> list[dict[str, Any]]:
        send_mode = mode == "approve"
        private_key = os.getenv("CRYPTOAI_PRIVATE_KEY", "").strip()
        derived = self._private_key_address(private_key) if private_key else ""
        return [
            self._check("approval_enabled", mode == "plan" or self._bool_env("CRYPTOAI_ENABLE_ATOMIC_EXECUTOR_APPROVAL"), "Set CRYPTOAI_ENABLE_ATOMIC_EXECUTOR_APPROVAL=true for approve mode.", "Atomic approval flag is enabled or mode is plan."),
            self._check("live_feature_flag", mode == "plan" or flags.live_trading_enabled, "CRYPTOAI_LIVE_TRADING_ENABLED must be true for approve mode.", "Live trading flag is enabled or mode is plan."),
            self._check("kill_switch_off_for_send", mode == "plan" or not flags.live_kill_switch_enabled, "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED must be false for approve mode.", "Kill switch is off for send mode or mode is plan."),
            self._check("manual_confirmation", mode == "plan" or confirm == self.CONFIRM_PHRASE, f"Pass --confirm {self.CONFIRM_PHRASE} for approve mode.", "Manual confirmation phrase is present or mode is plan."),
            self._check("private_key_available", not send_mode or bool(private_key), "CRYPTOAI_PRIVATE_KEY is required for approve mode.", "Private key is available for send mode or not required."),
            self._check("private_key_matches_wallet", not send_mode or (derived and derived.lower() == plan.wallet_address.lower()), "Private key does not match CRYPTOAI_LIVE_WALLET_ADDRESS.", "Private key matches isolated wallet or not required."),
            self._check("executor_enabled", self._bool_env("CRYPTOAI_ATOMIC_EXECUTOR_ENABLED"), "CRYPTOAI_ATOMIC_EXECUTOR_ENABLED must be true.", "Atomic executor enabled flag is set."),
            self._check("executor_reviewed", self._bool_env("CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED"), "CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED must be true after review.", "Atomic executor review flag is set."),
            self._check("plan_prepared", plan.error is None, plan.error or "Atomic approval plan could not be prepared.", "Atomic approval plan is prepared."),
            self._check("chain_id_base", plan.chain_id in {None, 8453}, "Approval transaction must be on Base chain ID 8453.", "Approval transaction is on Base or not yet prepared."),
            self._check("executor_deployed", plan.executor_code_bytes > 0, "Atomic executor address has no deployed bytecode.", "Atomic executor bytecode exists."),
            self._check("approval_size_cap", Decimal("0") < plan.approval_usd <= max(Decimal("20"), flags.max_live_trade_usd), "Atomic approval must be capped to the configured live trade size.", "Atomic approval amount is capped."),
            self._check("usdc_balance", plan.usdc_balance_units >= plan.amount_units, "USDC balance is below approval amount.", "USDC balance covers approval amount."),
            self._check("approval_needed", mode == "plan" or not plan.allowance_sufficient, "Existing USDC allowance already covers the atomic approval amount.", "Approval is needed or mode is plan."),
            self._check("atomic_report_not_live_approval", atomic_report.get("live_trading_approval") is False, "Atomic report must not auto-approve live trading.", "Atomic report is evidence-only."),
        ]

    def _build_approval_tx(self, *, web3: Web3, token_address: str, wallet: str, spender: str, amount_units: int) -> dict[str, Any]:
        contract = web3.eth.contract(address=token_address, abi=ERC20_ABI)
        data = contract.functions.approve(spender, amount_units)._encode_transaction_data()
        latest = web3.eth.get_block("latest")
        base_fee = int(latest.get("baseFeePerGas") or web3.eth.gas_price)
        priority_fee = int(os.getenv("CRYPTOAI_LIVE_MAX_PRIORITY_FEE_WEI", str(Web3.to_wei(0.01, "gwei"))))
        max_fee = int(os.getenv("CRYPTOAI_LIVE_MAX_FEE_WEI", str(base_fee * 2 + priority_fee)))
        tx = {
            "chainId": 8453,
            "from": wallet,
            "to": token_address,
            "data": data,
            "value": 0,
            "nonce": web3.eth.get_transaction_count(wallet, "pending"),
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": priority_fee,
            "type": 2,
        }
        gas = web3.eth.estimate_gas(tx)
        tx["gas"] = min(int(gas * Decimal("1.20")), int(os.getenv("CRYPTOAI_LIVE_GAS_LIMIT_CAP", "500000")))
        return tx

    @staticmethod
    def _default_tx_sender(tx: dict[str, Any], private_key: str) -> dict[str, Any]:
        if not private_key:
            raise RuntimeError("CRYPTOAI_PRIVATE_KEY is not configured.")
        client = RpcClient(SUPPORTED_CHAINS["base"])
        signed = client.web3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = client.web3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = client.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=int(os.getenv("CRYPTOAI_LIVE_RECEIPT_TIMEOUT_SECONDS", "120")))
        return {
            "tx_hash": tx_hash.hex(),
            "receipt_status": int(receipt.get("status", 0)),
            "block_number": int(receipt.get("blockNumber", 0)),
            "gas_used": int(receipt.get("gasUsed", 0)),
        }

    def _append_journal(self, *, plan: AtomicApprovalPlan, sent: dict[str, Any]) -> None:
        payload = {
            "timestamp": self._utc_now(),
            "wallet_address": plan.wallet_address,
            "executor_address": plan.executor_address,
            "approval_usd": str(plan.approval_usd),
            "amount_units": str(plan.amount_units),
            "send_result": sent,
        }
        with self.journal_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")

    def _approval_usd(self, max_live_trade_usd: Decimal) -> Decimal:
        configured = self._decimal_env("CRYPTOAI_ATOMIC_EXECUTOR_APPROVAL_USD", "")
        if configured > 0:
            return configured
        if max_live_trade_usd > 0:
            return max_live_trade_usd
        return Decimal("20")

    @staticmethod
    def _check(name: str, passed: bool, fail_detail: str, pass_detail: str) -> dict[str, Any]:
        return {"name": name, "passed": bool(passed), "severity": "PASS" if passed else "BLOCK", "detail": pass_detail if passed else fail_detail}

    @staticmethod
    def _private_key_address(private_key: str) -> str:
        try:
            return Web3().eth.account.from_key(private_key).address
        except Exception:
            return ""

    @staticmethod
    def _to_units(value: Decimal, decimals: int) -> int:
        return int((value * Decimal(10**decimals)).to_integral_value(rounding="ROUND_DOWN"))

    @staticmethod
    def _bool_env(key: str) -> bool:
        return os.getenv(key, "").strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _decimal_env(key: str, default: str) -> Decimal:
        raw = os.getenv(key, default)
        if raw == "":
            return Decimal("0")
        try:
            return Decimal(raw)
        except (InvalidOperation, ValueError):
            return Decimal("0")

    @staticmethod
    def _redact_url(url: str) -> str:
        return url.split("?", 1)[0] + "?redacted=true" if "?" in url else url

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# Atomic Executor Approval",
            "",
            f"Generated: `{payload['generated_at']}`",
            f"- Mode: `{payload['mode']}`",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Send attempted: `{payload['send_attempted']}`",
            f"- Blocked checks: `{payload['blocked_check_count']}` / `{payload['check_count']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "|---|---|---|",
        ]
        for row in payload["checks"]:
            lines.append(f"| {row['name']} | {row['severity']} | {row['detail']} |")
        lines.extend(["", "## Approval Plan", "", "```json", json.dumps(payload["approval_plan"], indent=2), "```", "", "## Notes", ""])
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="Approve capped USDC allowance to CryptoAI atomic executor.")
    parser.add_argument("--mode", choices=["plan", "approve"], default="plan")
    parser.add_argument("--confirm", default="")
    args = parser.parse_args()
    payload = AtomicExecutorApprovalService().generate(mode=args.mode, confirm=args.confirm)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
