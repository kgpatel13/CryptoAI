from __future__ import annotations

import argparse
import json
import os
import time
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable

from eth_abi import decode
from web3 import Web3

from app.blockchain.chains import SUPPORTED_CHAINS
from app.blockchain.rpc_client import RpcClient
from app.execution.tiny_live_pilot_service import ERC20_ABI
from app.execution.transaction_simulation_service import TransactionSimulationService
from app.registry.tokens import get_token


ATOMIC_EXECUTOR_ABI = [
    {
        "name": "executeTwoLegArbitrage",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {
                "name": "route",
                "type": "tuple",
                "components": [
                    {"name": "tokenIn", "type": "address"},
                    {"name": "tokenMid", "type": "address"},
                    {"name": "tokenOut", "type": "address"},
                    {"name": "amountIn", "type": "uint256"},
                    {"name": "minAmountOut", "type": "uint256"},
                    {"name": "minProfit", "type": "uint256"},
                    {"name": "buyRouter", "type": "address"},
                    {"name": "sellRouter", "type": "address"},
                    {"name": "buyCalldata", "type": "bytes"},
                    {"name": "sellCalldata", "type": "bytes"},
                    {"name": "recipient", "type": "address"},
                    {"name": "deadline", "type": "uint256"},
                ],
            }
        ],
        "outputs": [{"name": "amountOut", "type": "uint256"}, {"name": "profit", "type": "uint256"}],
    }
]


EthCallRunner = Callable[[dict[str, Any], str], dict[str, Any]]


class AtomicArbitrageExecutionService:
    """Build and simulate a single-transaction live arbitrage call.

    The service prepares calldata for the deployed executor contract, routes
    both swap legs through the executor as recipient, and uses eth_call as the
    final evidence gate. It does not sign or broadcast transactions.
    """

    def __init__(
        self,
        data_dir: Path | str = "data",
        report_dir: Path | str = "reports",
        eth_call_runner: EthCallRunner | None = None,
        refresh_transaction_simulation: bool = True,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.output_json = self.report_dir / "atomic_live_arbitrage.json"
        self.output_md = self.report_dir / "atomic_live_arbitrage.md"
        self.eth_call_runner = eth_call_runner or self._default_eth_call_runner
        self.refresh_transaction_simulation = refresh_transaction_simulation

    def generate(self) -> dict[str, Any]:
        if self.refresh_transaction_simulation:
            tx_sim = TransactionSimulationService(data_dir=self.data_dir, report_dir=self.report_dir, eth_call_runner=self.eth_call_runner).generate()
        else:
            tx_sim = self._read_json(self.report_dir / "transaction_simulation.json")
        intent = tx_sim.get("simulation_intent", {}) if isinstance(tx_sim.get("simulation_intent"), dict) else {}
        diagnostics = self._route_diagnostics(tx_sim=tx_sim, intent=intent)
        route = self._build_atomic_route(intent)
        executor_preflight = self._executor_preflight(route)
        checks = self._checks(tx_sim=tx_sim, intent=intent, route=route, executor_preflight=executor_preflight)
        blockers = [row for row in checks if row["severity"] == "BLOCK"]
        actions = [row for row in checks if row["severity"] == "ACTION"]
        passed = not blockers and not actions
        payload = {
            "generated_at": self._utc_now(),
            "mode": "atomic_live_arbitrage_simulation",
            "overall_status": "ATOMIC_ROUTE_SIMULATION_PASSED" if passed else "ATOMIC_ROUTE_ACTION",
            "atomic_route_simulation_passed": passed,
            "live_trading_approval": False,
            "transaction_simulation_status": tx_sim.get("overall_status"),
            "route_diagnostics": diagnostics,
            "executor_preflight": executor_preflight,
            "atomic_route": route,
            "check_count": len(checks),
            "pass_count": sum(1 for row in checks if row["severity"] == "PASS"),
            "action_count": len(actions),
            "blocked_check_count": len(blockers),
            "checks": checks,
            "notes": [
                "This report is the final evidence gate for atomic live arbitrage.",
                "It builds one executor transaction and simulates it with eth_call only.",
                "No transaction is signed or broadcast by this service.",
                "The wallet must approve USDC to the atomic executor, not just to an individual router.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _build_atomic_route(self, intent: dict[str, Any]) -> dict[str, Any]:
        executor = os.getenv("CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS", "").strip()
        wallet = os.getenv("CRYPTOAI_LIVE_WALLET_ADDRESS", "").strip()
        if not self._valid_address(executor):
            return {"status": "BLOCKED", "reason": "CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS must be a valid deployed executor address."}
        if not self._valid_address(wallet):
            return {"status": "BLOCKED", "reason": "CRYPTOAI_LIVE_WALLET_ADDRESS must be a valid isolated wallet address."}
        if str(intent.get("simulation_type", "")).upper() == "TINY_LIVE_SMOKE":
            return {"status": "BLOCKED", "reason": "Atomic arbitrage requires a two-leg SHADOW_READY arbitrage candidate, not the one-leg smoke route."}

        legs = intent.get("swap_legs", []) if isinstance(intent.get("swap_legs"), list) else []
        if len(legs) != 2:
            return {"status": "BLOCKED", "reason": "Atomic arbitrage requires exactly two simulated swap legs."}

        token_usdc = get_token("base", "USDC")
        token_weth = get_token("base", "WETH")
        if token_usdc is None or token_weth is None:
            return {"status": "BLOCKED", "reason": "Base USDC/WETH token metadata is missing."}

        try:
            executor_address = Web3.to_checksum_address(executor)
            wallet_address = Web3.to_checksum_address(wallet)
            notional = self._decimal(intent.get("notional_usd"))
            amount_in_units = self._to_units(notional, token_usdc.decimals)
            min_profit_bps = self._decimal(os.getenv("CRYPTOAI_ATOMIC_MIN_PROFIT_BPS", "5"))
            min_profit_units = int((Decimal(amount_in_units) * min_profit_bps / Decimal("10000")).to_integral_value(rounding="ROUND_DOWN"))
            min_amount_out_units = amount_in_units + min_profit_units
            deadline = int(time.time()) + int(os.getenv("CRYPTOAI_ATOMIC_DEADLINE_SECONDS", "90"))
            rebuilt_legs = self._executor_recipient_legs(intent=intent, recipient=executor_address, deadline=deadline)
            route_tuple = (
                Web3.to_checksum_address(token_usdc.address),
                Web3.to_checksum_address(token_weth.address),
                Web3.to_checksum_address(token_usdc.address),
                amount_in_units,
                min_amount_out_units,
                min_profit_units,
                Web3.to_checksum_address(rebuilt_legs[0]["router_address"]),
                Web3.to_checksum_address(rebuilt_legs[1]["router_address"]),
                bytes.fromhex(str(rebuilt_legs[0]["calldata"])[2:]),
                bytes.fromhex(str(rebuilt_legs[1]["calldata"])[2:]),
                wallet_address,
                deadline,
            )
            web3 = Web3()
            contract = web3.eth.contract(address=executor_address, abi=ATOMIC_EXECUTOR_ABI)
            calldata = contract.functions.executeTwoLegArbitrage(route_tuple)._encode_transaction_data()
            tx = {"from": wallet_address, "to": executor_address, "data": calldata, "value": "0x0"}
            eth_call = self.eth_call_runner(tx, "base")
            decoded_error = self._decode_executor_error(eth_call.get("error"))
        except Exception as exc:
            return {"status": "ERROR", "reason": f"{type(exc).__name__}: {exc}"}

        return {
            "status": "SIMULATION_READY" if eth_call.get("status") == "PASS" else "SIMULATION_ATTEMPTED",
            "chain": "base",
            "chain_id": 8453,
            "executor_address": executor_address,
            "wallet_address": wallet_address,
            "token_in": "USDC",
            "token_mid": "WETH",
            "token_out": "USDC",
            "amount_in_units": str(amount_in_units),
            "min_amount_out_units": str(min_amount_out_units),
            "min_profit_units": str(min_profit_units),
            "min_profit_bps": str(min_profit_bps),
            "deadline": deadline,
            "calldata": calldata,
            "calldata_bytes": (len(calldata) - 2) // 2,
            "swap_legs": rebuilt_legs,
            "eth_call": tx,
            "eth_call_result": eth_call,
            "eth_call_status": eth_call.get("status", "FAIL"),
            "eth_call_decoded_error": decoded_error,
            "approval_spender": executor_address,
        }

    def _route_diagnostics(self, *, tx_sim: dict[str, Any], intent: dict[str, Any]) -> dict[str, Any]:
        realism = self._read_json(self.report_dir / "execution_realism.json")
        opportunities = realism.get("opportunities", []) if isinstance(realism.get("opportunities"), list) else []
        selected_candidate = tx_sim.get("selected_candidate", {}) if isinstance(tx_sim.get("selected_candidate"), dict) else {}
        simulation_type = str(intent.get("simulation_type") or "TWO_LEG_ARBITRAGE").upper()
        latest_rows = opportunities[-10:]
        route_rows = [self._diagnose_opportunity(row) for row in latest_rows if isinstance(row, dict)]
        selected_diagnostics = self._diagnose_opportunity(selected_candidate) if selected_candidate else {}
        shadow_ready = [row for row in route_rows if row.get("realism_status") == "SHADOW_READY"]
        buy_rows = [row for row in route_rows if row.get("source_decision") == "BUY"]
        tx_checks = tx_sim.get("checks", []) if isinstance(tx_sim.get("checks"), list) else []
        failed_tx_checks = [
            {
                "name": str(row.get("name", "-")),
                "severity": str(row.get("severity", "-")),
                "detail": str(row.get("detail", "-")),
            }
            for row in tx_checks
            if isinstance(row, dict) and row.get("passed") is not True
        ]

        if selected_candidate and simulation_type != "TINY_LIVE_SMOKE":
            blocker_type = "ATOMIC_BUILDER_OR_ETH_CALL"
            next_action = "Inspect atomic_calldata_built and atomic_eth_call_passed details."
        elif shadow_ready:
            blocker_type = "TRANSACTION_SIMULATION_SELECTION"
            next_action = "A SHADOW_READY row exists but transaction simulation did not select it; inspect DEX allowlist, prices, and route metadata."
        elif buy_rows:
            blocker_type = "REALISM_FILTER"
            next_action = "BUY rows exist but are not SHADOW_READY; inspect stress net edge, confidence, executable ratio, and pool-depth status."
        else:
            blocker_type = "MARKET_NO_BUY_SIGNAL"
            next_action = "No latest BUY plus SHADOW_READY two-leg route exists; continue paper/shadow scanning or review thresholds."

        if simulation_type == "TINY_LIVE_SMOKE":
            blocker_type = "NO_TWO_LEG_CANDIDATE"
            next_action = "The simulator fell back to one-leg smoke mode because no approved two-leg SHADOW_READY route was selected."

        return {
            "blocker_type": blocker_type,
            "next_action": next_action,
            "transaction_simulation_passed": tx_sim.get("transaction_simulation_passed") is True,
            "transaction_simulation_status": tx_sim.get("overall_status"),
            "simulation_type": simulation_type,
            "selected_candidate_found": bool(selected_candidate),
            "selected_candidate": selected_diagnostics,
            "latest_opportunity_count": len(opportunities),
            "latest_diagnostics_count": len(route_rows),
            "buy_candidate_count": len(buy_rows),
            "shadow_ready_count": len(shadow_ready),
            "latest_opportunities": route_rows,
            "failed_transaction_simulation_checks": failed_tx_checks,
        }

    def _diagnose_opportunity(self, row: dict[str, Any]) -> dict[str, Any]:
        gross = self._decimal(row.get("gross_edge_pct"))
        reported_net = self._decimal(row.get("reported_net_edge_pct"))
        stress_net = self._decimal(row.get("stress_net_edge_pct"))
        source_decision = str(row.get("source_decision") or row.get("decision") or "-")
        realism_status = str(row.get("realism_status") or "-")
        reasons: list[str] = []
        if source_decision != "BUY":
            reasons.append(f"source_decision is {source_decision}, not BUY")
        if realism_status != "SHADOW_READY":
            reasons.append(f"realism_status is {realism_status}, not SHADOW_READY")
        if stress_net is not None and stress_net < 0:
            reasons.append("stress_net_edge_pct is negative")
        if str(row.get("confidence") or "").upper() in {"", "NONE", "LOW"}:
            reasons.append(f"confidence is {row.get('confidence') or 'NONE'}")
        if self._decimal(row.get("buy_price")) <= 0 or self._decimal(row.get("sell_price")) <= 0:
            reasons.append("buy_price/sell_price missing or non-positive")
        if not reasons and source_decision == "BUY" and realism_status == "SHADOW_READY":
            reasons.append("candidate is eligible for atomic route building")

        return {
            "timestamp": row.get("timestamp"),
            "chain": row.get("chain"),
            "pair": row.get("pair"),
            "buy_dex": row.get("buy_source") or row.get("buy_dex"),
            "sell_dex": row.get("sell_source") or row.get("sell_dex"),
            "source_decision": source_decision,
            "realism_status": realism_status,
            "gross_edge_pct": str(gross) if gross is not None else None,
            "reported_net_edge_pct": str(reported_net) if reported_net is not None else None,
            "stress_net_edge_pct": str(stress_net) if stress_net is not None else None,
            "required_threshold_pct": os.getenv("CRYPTOAI_MIN_EDGE_FOR_PAPER_PCT", "0.30"),
            "confidence": row.get("confidence"),
            "requested_notional_usd": row.get("requested_notional_usd"),
            "max_executable_notional_usd": row.get("max_executable_notional_usd"),
            "executable_ratio_pct": row.get("executable_ratio_pct"),
            "pool_depth_status": row.get("pool_depth_status"),
            "reason": row.get("reason"),
            "diagnostic_reasons": reasons,
        }

    def _executor_recipient_legs(self, *, intent: dict[str, Any], recipient: str, deadline: int) -> list[dict[str, Any]]:
        tx_service = TransactionSimulationService(data_dir=self.data_dir, report_dir=self.report_dir, eth_call_runner=self.eth_call_runner)
        candidate = tx_service._select_candidate(tx_service._read_json(self.report_dir / "execution_realism.json"))
        if not candidate:
            candidate = self._candidate_from_intent(intent)
        return tx_service._build_swap_legs(candidate, {**intent, "wallet_address": recipient, "deadline_seconds": str(max(1, deadline - int(time.time())))})

    @staticmethod
    def _candidate_from_intent(intent: dict[str, Any]) -> dict[str, Any]:
        return {
            "chain": "base",
            "pair": intent.get("pair"),
            "buy_source": intent.get("buy_dex"),
            "sell_source": intent.get("sell_dex"),
            "buy_price": intent.get("buy_price"),
            "sell_price": intent.get("sell_price"),
            "requested_notional_usd": intent.get("notional_usd"),
        }

    def _executor_preflight(self, route: dict[str, Any]) -> dict[str, Any]:
        executor = os.getenv("CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS", "").strip()
        wallet = os.getenv("CRYPTOAI_LIVE_WALLET_ADDRESS", "").strip()
        token_usdc = get_token("base", "USDC")
        if not self._valid_address(executor) or not self._valid_address(wallet) or token_usdc is None:
            return {
                "status": "BLOCKED",
                "reason": "Valid executor address, wallet address, and Base USDC metadata are required.",
            }
        try:
            client = RpcClient(SUPPORTED_CHAINS["base"])
            web3 = client.web3
            executor_address = Web3.to_checksum_address(executor)
            wallet_address = Web3.to_checksum_address(wallet)
            usdc = web3.eth.contract(address=Web3.to_checksum_address(token_usdc.address), abi=ERC20_ABI)
            code = web3.eth.get_code(executor_address)
            balance_units = int(usdc.functions.balanceOf(wallet_address).call())
            allowance_units = int(usdc.functions.allowance(wallet_address, executor_address).call())
            required_units = self._int(route.get("amount_in_units"))
            return {
                "status": "READY" if len(code) > 0 else "BLOCKED",
                "executor_address": executor_address,
                "wallet_address": wallet_address,
                "executor_code_bytes": len(code),
                "usdc_balance_units": str(balance_units),
                "usdc_balance": str(Decimal(balance_units) / Decimal(10**token_usdc.decimals)),
                "usdc_allowance_units": str(allowance_units),
                "usdc_allowance": str(Decimal(allowance_units) / Decimal(10**token_usdc.decimals)),
                "required_amount_units": str(required_units),
                "allowance_sufficient": required_units > 0 and allowance_units >= required_units,
                "rpc_url": self._redact_url(client.rpc_url_used),
            }
        except Exception as exc:
            return {"status": "ERROR", "reason": f"{type(exc).__name__}: {exc}"}

    def _checks(
        self,
        *,
        tx_sim: dict[str, Any],
        intent: dict[str, Any],
        route: dict[str, Any],
        executor_preflight: dict[str, Any],
    ) -> list[dict[str, Any]]:
        return [
            self._check("two_leg_candidate_selected", bool(tx_sim.get("selected_candidate")), "ACTION", "A BUY plus SHADOW_READY two-leg candidate must be selected.", "A BUY plus SHADOW_READY two-leg candidate is selected."),
            self._check("not_one_leg_smoke", str(intent.get("simulation_type", "")).upper() != "TINY_LIVE_SMOKE", "BLOCK", "Atomic live arbitrage cannot use the one-leg smoke route.", "Route is a two-leg arbitrage candidate."),
            self._check("executor_configured", self._valid_address(os.getenv("CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS", "")), "BLOCK", "Configure a valid deployed CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS.", "Atomic executor address is configured."),
            self._check("executor_deployed", self._int(executor_preflight.get("executor_code_bytes")) > 0, "BLOCK", "Atomic executor address has no deployed bytecode on Base.", "Atomic executor bytecode exists on Base."),
            self._check("executor_reviewed", self._bool_env("CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED"), "ACTION", "Set CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED=true only after contract/deployment review.", "Atomic executor review flag is present."),
            self._check("executor_usdc_allowance", route.get("status") != "SIMULATION_READY" or executor_preflight.get("allowance_sufficient") is True, "ACTION", "Approve USDC to the atomic executor before live atomic execution.", "USDC allowance to atomic executor is sufficient or no executable route is ready."),
            self._check("atomic_calldata_built", route.get("calldata", "").startswith("0x"), "ACTION", "Atomic executor calldata was not built.", "Atomic executor calldata is built."),
            self._check("atomic_eth_call_passed", route.get("eth_call_status") == "PASS", "ACTION", "Atomic executor eth_call did not pass.", "Atomic executor eth_call passed."),
        ]

    @staticmethod
    def _check(name: str, passed: bool, fail_severity: str, fail_detail: str, pass_detail: str) -> dict[str, Any]:
        return {"name": name, "passed": bool(passed), "severity": "PASS" if passed else fail_severity, "detail": pass_detail if passed else fail_detail}

    def _default_eth_call_runner(self, tx: dict[str, Any], chain: str) -> dict[str, Any]:
        if chain not in SUPPORTED_CHAINS:
            return {"status": "FAIL", "error": f"Unsupported chain: {chain}"}
        client = RpcClient(SUPPORTED_CHAINS[chain])
        try:
            result = client.web3.eth.call(tx, block_identifier="latest")
            return {"status": "PASS", "rpc_url": self._redact_url(client.rpc_url_used), "block_number": int(client.web3.eth.block_number), "result": result.hex()}
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            return {"status": "REVERT" if "revert" in message.lower() else "FAIL", "error": message[:500]}

    @staticmethod
    def _decode_executor_error(error: Any) -> dict[str, Any]:
        raw = str(error or "")
        hex_payload = ""
        for part in raw.replace("'", " ").replace('"', " ").replace("(", " ").replace(")", " ").replace(",", " ").split():
            if part.startswith("0x") and len(part) >= 10:
                hex_payload = part
                break
        if not hex_payload:
            return {}
        selector = hex_payload[:10].lower()
        data = bytes.fromhex(hex_payload[10:])
        if selector == "0x88215f9c":
            try:
                amount_out, required_out = decode(["uint256", "uint256"], data)
                return {
                    "name": "ProfitTooLow",
                    "amount_out_units": str(amount_out),
                    "required_out_units": str(required_out),
                    "amount_out_usdc": str(Decimal(amount_out) / Decimal(10**6)),
                    "required_out_usdc": str(Decimal(required_out) / Decimal(10**6)),
                    "shortfall_usdc": str((Decimal(required_out) - Decimal(amount_out)) / Decimal(10**6)),
                    "explanation": "Atomic route executed in simulation but did not meet the executor's minimum profitable output.",
                }
            except Exception:
                return {"selector": selector, "raw": hex_payload}
        return {"selector": selector, "raw": hex_payload}

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def _valid_address(value: str) -> bool:
        try:
            Web3.to_checksum_address(value)
            return True
        except Exception:
            return False

    @staticmethod
    def _bool_env(key: str) -> bool:
        return os.getenv(key, "").strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0")

    @staticmethod
    def _to_units(value: Decimal, decimals: int) -> int:
        return int((value * Decimal(10**decimals)).to_integral_value(rounding="ROUND_DOWN"))

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
        route = payload["atomic_route"]
        lines = [
            "# Atomic Live Arbitrage Simulation",
            "",
            f"Generated: `{payload['generated_at']}`",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Atomic route simulation passed: `{payload['atomic_route_simulation_passed']}`",
            f"- Live trading approval: `{payload['live_trading_approval']}`",
            f"- Executor: `{route.get('executor_address', '-')}`",
            f"- Executor preflight: `{payload.get('executor_preflight', {}).get('status', '-')}`",
            f"- eth_call status: `{route.get('eth_call_status', '-')}`",
            f"- Route blocker: `{payload.get('route_diagnostics', {}).get('blocker_type', '-')}`",
            f"- Blocked checks: `{payload['blocked_check_count']}`",
            f"- Action checks: `{payload['action_count']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "|---|---|---|",
        ]
        for row in payload["checks"]:
            lines.append(f"| {row['name']} | {row['severity']} | {row['detail']} |")
        lines.extend(
            [
                "",
                "## Route Diagnostics",
                "",
                "```json",
                json.dumps(payload.get("route_diagnostics", {}), indent=2),
                "```",
                "",
                "## Atomic Route",
                "",
                "```json",
                json.dumps(route, indent=2),
                "```",
                "",
                "## Notes",
                "",
            ]
        )
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and simulate atomic live arbitrage calldata.")
    parser.add_argument("--generate", action="store_true", help="Generate the atomic arbitrage simulation report.")
    args = parser.parse_args()
    payload = AtomicArbitrageExecutionService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
