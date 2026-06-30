from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable

from web3 import Web3

from app.automation.paper_autopilot import active_autopilot_processes
from app.blockchain.chains import SUPPORTED_CHAINS
from app.blockchain.rpc_client import RpcClient
from app.config.feature_flags import load_feature_flags
from app.execution.transaction_simulation_service import TransactionSimulationService
from app.registry.dexes import get_dexes_for_chain
from app.registry.tokens import get_token


ERC20_ABI = [
    {
        "name": "allowance",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "approve",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}],
        "outputs": [{"name": "", "type": "bool"}],
    },
    {
        "name": "balanceOf",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },
]


TxSender = Callable[[dict[str, Any], str], dict[str, Any]]


@dataclass(frozen=True)
class PreparedTx:
    kind: str
    tx: dict[str, Any]
    amount_units: int
    amount_decimal: str
    router_address: str | None = None


class TinyLivePilotService:
    """Manual one-transaction live smoke-test harness.

    This is intentionally not an autonomous arbitrage engine. It can prepare a
    tiny USDC->WETH smoke swap from the latest simulated route after all gates
    pass. Approvals and swaps are separate explicit modes.
    """

    MAX_SMOKE_TRADE_USD = Decimal("10")
    CONFIRM_PHRASE = "LIVE_PILOT_APPROVED"

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
        self.output_json = self.report_dir / "tiny_live_pilot.json"
        self.output_md = self.report_dir / "tiny_live_pilot.md"
        self.journal_file = self.data_dir / "live_pilot_orders.jsonl"
        self.tx_sender = tx_sender or self._default_tx_sender

    def generate(self, mode: str = "plan", confirm: str = "") -> dict[str, Any]:
        mode = mode.lower().strip()
        if mode not in {"plan", "approve", "swap"}:
            raise ValueError("mode must be plan, approve, or swap")

        flags = load_feature_flags()
        context = self._context()
        prepared = self._prepare(flags)
        checks = self._checks(flags=flags, context=context, prepared=prepared, mode=mode, confirm=confirm)
        blockers = [row for row in checks if row["severity"] == "BLOCK"]
        sent: dict[str, Any] | None = None

        if mode in {"approve", "swap"} and not blockers:
            tx = prepared.approval_tx if mode == "approve" else prepared.swap_tx
            if tx is None:
                blockers.append(
                    {
                        "name": f"{mode}_transaction_available",
                        "severity": "BLOCK",
                        "passed": False,
                        "detail": f"No {mode} transaction is available.",
                    }
                )
            else:
                sent = self.tx_sender(tx.tx, str(flags.private_key_configured))
                self._append_journal(mode=mode, prepared=prepared, sent=sent)

        status = "LIVE_PILOT_SENT" if sent and not blockers else ("LIVE_PILOT_READY" if not blockers else "LIVE_PILOT_BLOCKED")
        payload = {
            "generated_at": self._utc_now(),
            "mode": mode,
            "overall_status": status,
            "live_trading_approval": False,
            "send_attempted": sent is not None,
            "send_result": sent,
            "blocked_check_count": len(blockers),
            "check_count": len(checks),
            "checks": checks,
            "context": context,
            "pilot_plan": prepared.to_report(),
            "notes": [
                "Tiny Live Pilot is a manual smoke-test harness, not an autonomous trading loop.",
                "It supports a capped one-leg USDC->WETH live test only; cross-DEX arbitrage still requires an atomic executor contract before production live trading.",
                "Never paste a private key into chat. Configure it only in your local environment when intentionally running approve/swap mode.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _context(self) -> dict[str, Any]:
        return {
            "wallet_preflight": self._read_json("wallet_preflight.json"),
            "live_readiness": self._read_json("live_readiness_checklist.json"),
            "live_safety": self._read_json("live_safety.json"),
            "transaction_simulation": self._read_json("transaction_simulation.json"),
            "report_audit": self._read_json("report_audit.json"),
            "provider_monitor": self._read_json("provider_monitor.json"),
            "active_autopilot_processes": active_autopilot_processes(),
        }

    def _prepare(self, flags: Any) -> "PilotPreparation":
        wallet = flags.live_wallet_address
        smoke_usd = min(self._decimal_env("CRYPTOAI_TINY_LIVE_SMOKE_USD", "5"), self.MAX_SMOKE_TRADE_USD)
        if flags.max_live_trade_usd > 0:
            smoke_usd = min(smoke_usd, flags.max_live_trade_usd)

        base = PilotPreparation(smoke_usd=smoke_usd, wallet_address=wallet)
        if not wallet:
            return base.with_error("Missing CRYPTOAI_LIVE_WALLET_ADDRESS.")

        token_usdc = get_token("base", "USDC")
        token_weth = get_token("base", "WETH")
        if token_usdc is None or token_weth is None:
            return base.with_error("USDC/WETH token metadata is missing.")

        dexes = {dex.name: dex for dex in get_dexes_for_chain("base")}
        dex_name = os.getenv("CRYPTOAI_TINY_LIVE_DEX", "Uniswap V3").strip() or "Uniswap V3"
        dex = dexes.get(dex_name)
        if dex is None or not dex.router_address:
            return base.with_error(f"Tiny live DEX is not configured: {dex_name}.")

        try:
            wallet_address = Web3.to_checksum_address(wallet)
            router_address = Web3.to_checksum_address(dex.router_address)
        except Exception as exc:
            return base.with_error(f"Invalid wallet or router address: {exc}")

        amount_in_units = self._to_units(smoke_usd, token_usdc.decimals)
        try:
            client = RpcClient(SUPPORTED_CHAINS["base"])
            web3 = client.web3
            usdc_contract = web3.eth.contract(address=Web3.to_checksum_address(token_usdc.address), abi=ERC20_ABI)
            usdc_balance = int(usdc_contract.functions.balanceOf(wallet_address).call())
            allowance = int(usdc_contract.functions.allowance(wallet_address, router_address).call())
            eth_balance = int(web3.eth.get_balance(wallet_address))
            chain_id = int(web3.eth.chain_id)
            latest_block = int(web3.eth.block_number)
            approval_tx = self._build_approval_tx(
                web3=web3,
                token_address=Web3.to_checksum_address(token_usdc.address),
                wallet=wallet_address,
                spender=router_address,
                amount_units=amount_in_units,
            )
            swap_tx = None
            if allowance >= amount_in_units:
                swap_leg = TransactionSimulationService()._build_leg(
                    leg="TINY_LIVE_SMOKE_SWAP",
                    chain="base",
                    dex_name=dex_name,
                    token_in_symbol="USDC",
                    token_out_symbol="WETH",
                    amount_in_decimal=smoke_usd,
                    amount_out_min_decimal=Decimal("0.000000000000000001"),
                    recipient=wallet_address,
                    deadline=int(time.time()) + 120,
                )
                swap_tx = self._build_call_tx(web3=web3, wallet=wallet_address, call=swap_leg["eth_call"])
        except Exception as exc:
            return base.with_error(f"{type(exc).__name__}: {exc}")

        return PilotPreparation(
            smoke_usd=smoke_usd,
            wallet_address=wallet_address,
            dex=dex_name,
            router_address=router_address,
            chain_id=chain_id,
            latest_block=latest_block,
            rpc_url=self._redact_url(client.rpc_url_used),
            usdc_balance_units=usdc_balance,
            usdc_balance=str(Decimal(usdc_balance) / Decimal(10**token_usdc.decimals)),
            eth_balance=str(Decimal(eth_balance) / Decimal(10**18)),
            allowance_units=allowance,
            allowance_sufficient=allowance >= amount_in_units,
            approval_tx=PreparedTx("approve", approval_tx, amount_in_units, str(smoke_usd), router_address),
            swap_tx=PreparedTx("swap", swap_tx, amount_in_units, str(smoke_usd), router_address),
        )

    def _checks(self, *, flags: Any, context: dict[str, Any], prepared: "PilotPreparation", mode: str, confirm: str) -> list[dict[str, Any]]:
        readiness = context["live_readiness"]
        tx_sim = context["transaction_simulation"]
        audit = context["report_audit"]
        provider = context["provider_monitor"]
        active_autopilot = context["active_autopilot_processes"]
        private_key = os.getenv("CRYPTOAI_PRIVATE_KEY", "").strip()
        derived = self._private_key_address(private_key) if private_key else ""
        amount_units = prepared.approval_tx.amount_units if prepared.approval_tx else 0

        send_mode = mode in {"approve", "swap"}
        return [
            self._check("pilot_enabled", mode == "plan" or self._bool_env("CRYPTOAI_ENABLE_TINY_LIVE_PILOT", False), "Set CRYPTOAI_ENABLE_TINY_LIVE_PILOT=true for approve/swap mode.", "Tiny live pilot flag is enabled or mode is plan."),
            self._check("live_feature_flag", mode == "plan" or flags.live_trading_enabled, "CRYPTOAI_LIVE_TRADING_ENABLED must be true for approve/swap mode.", "Live trading flag is enabled or mode is plan."),
            self._check("kill_switch_off_for_send", mode == "plan" or not flags.live_kill_switch_enabled, "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED must be false for approve/swap mode.", "Kill switch is off for send mode or mode is plan."),
            self._check("manual_confirmation", mode == "plan" or confirm == self.CONFIRM_PHRASE, f"Pass --confirm {self.CONFIRM_PHRASE} for approve/swap mode.", "Manual confirmation phrase is present or mode is plan."),
            self._check("private_key_available", not send_mode or bool(private_key), "CRYPTOAI_PRIVATE_KEY is required only for approve/swap mode.", "Private key is available for send mode or not required."),
            self._check("private_key_matches_wallet", not send_mode or (derived and derived.lower() == str(flags.live_wallet_address).lower()), "Private key does not match CRYPTOAI_LIVE_WALLET_ADDRESS.", "Private key matches isolated live wallet or not required."),
            self._check("no_paper_autopilot_running", not active_autopilot, "Paper autopilot must be stopped before live pilot.", "No paper autopilot process is running."),
            self._check("wallet_preflight_ready", context["wallet_preflight"].get("wallet_preflight_allowed") is True, "Wallet preflight must be ready.", "Wallet preflight is ready."),
            self._check("live_readiness_ready", readiness.get("live_review_ready") is True, "Live readiness checklist must be LIVE_REVIEW_READY.", "Live readiness checklist is ready."),
            self._check("transaction_simulation_passed", tx_sim.get("transaction_simulation_passed") is True, "Transaction simulation must pass before live pilot.", "Transaction simulation passed."),
            self._check("report_audit_clean", self._int(audit.get("blocking_finding_count")) == 0, "Report audit has blocking findings.", "Report audit has no blocking findings."),
            self._check("provider_ok", provider.get("overall_status") == "OK", "Provider monitor must be OK.", "Provider monitor is OK."),
            self._check("pilot_plan_prepared", prepared.error is None, prepared.error or "Tiny live pilot plan could not be prepared.", "Tiny live pilot plan is prepared."),
            self._check("chain_id_base", prepared.chain_id in {None, 8453}, "Prepared transaction must be on Base chain ID 8453.", "Prepared transaction is on Base or not yet prepared."),
            self._check("smoke_size_cap", Decimal("0") < prepared.smoke_usd <= self.MAX_SMOKE_TRADE_USD, "Smoke test size must be > $0 and <= $10.", "Smoke test size is within cap."),
            self._check("usdc_balance", prepared.usdc_balance_units >= amount_units, "USDC balance is below smoke-test amount.", "USDC balance covers smoke-test amount."),
            self._check("allowance_for_swap", mode != "swap" or prepared.allowance_sufficient, "USDC allowance is insufficient; run approve mode first.", "USDC allowance is sufficient or not needed for this mode."),
            self._check("atomic_arbitrage_blocked", mode != "swap" or self._bool_env("CRYPTOAI_ALLOW_ONE_LEG_SMOKE_SWAP", False), "Swap mode is only a one-leg smoke test; set CRYPTOAI_ALLOW_ONE_LEG_SMOKE_SWAP=true to acknowledge this is not arbitrage.", "One-leg smoke swap acknowledgement is present or not swapping."),
        ]

    def _build_approval_tx(self, *, web3: Web3, token_address: str, wallet: str, spender: str, amount_units: int) -> dict[str, Any]:
        contract = web3.eth.contract(address=token_address, abi=ERC20_ABI)
        data = contract.functions.approve(spender, amount_units)._encode_transaction_data()
        return self._build_call_tx(web3=web3, wallet=wallet, call={"from": wallet, "to": token_address, "data": data, "value": "0x0"})

    def _build_call_tx(self, *, web3: Web3, wallet: str, call: dict[str, Any]) -> dict[str, Any]:
        latest = web3.eth.get_block("latest")
        base_fee = int(latest.get("baseFeePerGas") or web3.eth.gas_price)
        priority_fee = int(os.getenv("CRYPTOAI_LIVE_MAX_PRIORITY_FEE_WEI", str(Web3.to_wei(0.01, "gwei"))))
        max_fee = int(os.getenv("CRYPTOAI_LIVE_MAX_FEE_WEI", str(base_fee * 2 + priority_fee)))
        tx = {
            "chainId": 8453,
            "from": wallet,
            "to": Web3.to_checksum_address(call["to"]),
            "data": call["data"],
            "value": int(str(call.get("value", "0x0")), 16) if isinstance(call.get("value"), str) else int(call.get("value", 0)),
            "nonce": web3.eth.get_transaction_count(wallet, "pending"),
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": priority_fee,
            "type": 2,
        }
        gas = web3.eth.estimate_gas(tx)
        tx["gas"] = min(int(gas * Decimal("1.20")), int(os.getenv("CRYPTOAI_LIVE_GAS_LIMIT_CAP", "500000")))
        return tx

    def _default_tx_sender(self, tx: dict[str, Any], _private_key_configured: str) -> dict[str, Any]:
        private_key = os.getenv("CRYPTOAI_PRIVATE_KEY", "").strip()
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

    def _append_journal(self, *, mode: str, prepared: "PilotPreparation", sent: dict[str, Any]) -> None:
        payload = {
            "timestamp": self._utc_now(),
            "mode": mode,
            "wallet_address": prepared.wallet_address,
            "dex": prepared.dex,
            "smoke_usd": str(prepared.smoke_usd),
            "send_result": sent,
        }
        with self.journal_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")

    def _read_json(self, name: str) -> dict[str, Any]:
        path = self.report_dir / name
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

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
    def _decimal_env(key: str, default: str) -> Decimal:
        try:
            return Decimal(os.getenv(key, default))
        except (InvalidOperation, ValueError):
            return Decimal(default)

    @staticmethod
    def _bool_env(key: str, default: bool) -> bool:
        raw = os.getenv(key)
        if raw is None:
            return default
        return raw.strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _int(value: Any) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _redact_url(url: str) -> str:
        return url.split("?", 1)[0] + "?redacted=true" if "?" in url else url

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# Tiny Live Pilot",
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
        lines.extend(["", "## Pilot Plan", "", "```json", json.dumps(payload["pilot_plan"], indent=2), "```", "", "## Notes", ""])
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class PilotPreparation:
    smoke_usd: Decimal
    wallet_address: str = ""
    dex: str | None = None
    router_address: str | None = None
    chain_id: int | None = None
    latest_block: int | None = None
    rpc_url: str | None = None
    usdc_balance_units: int = 0
    usdc_balance: str = "0"
    eth_balance: str = "0"
    allowance_units: int = 0
    allowance_sufficient: bool = False
    approval_tx: PreparedTx | None = None
    swap_tx: PreparedTx | None = None
    error: str | None = None

    def with_error(self, error: str) -> "PilotPreparation":
        return PilotPreparation(smoke_usd=self.smoke_usd, wallet_address=self.wallet_address, error=error)

    def to_report(self) -> dict[str, Any]:
        return {
            "smoke_usd": str(self.smoke_usd),
            "wallet_address": self.wallet_address,
            "dex": self.dex,
            "router_address": self.router_address,
            "chain_id": self.chain_id,
            "latest_block": self.latest_block,
            "rpc_url": self.rpc_url,
            "usdc_balance": self.usdc_balance,
            "eth_balance": self.eth_balance,
            "allowance_units": str(self.allowance_units),
            "allowance_sufficient": self.allowance_sufficient,
            "approval_tx_available": self.approval_tx is not None,
            "swap_tx_available": self.swap_tx is not None,
            "error": self.error,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="CryptoAI tiny live pilot harness")
    parser.add_argument("--mode", choices=["plan", "approve", "swap"], default="plan")
    parser.add_argument("--confirm", default="")
    args = parser.parse_args()
    payload = TinyLivePilotService().generate(mode=args.mode, confirm=args.confirm)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
