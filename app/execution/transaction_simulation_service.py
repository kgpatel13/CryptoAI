from __future__ import annotations

import json
import os
import time
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable

from web3 import Web3

from app.blockchain.chains import SUPPORTED_CHAINS
from app.blockchain.rpc_client import RpcClient
from app.config.feature_flags import load_feature_flags
from app.registry.dexes import get_dexes_for_chain
from app.registry.tokens import get_token


UNISWAP_V2_SWAP_ABI = [
    {
        "name": "swapExactTokensForTokens",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
    }
]

UNISWAP_V3_SWAP_ROUTER_02_ABI = [
    {
        "name": "exactInputSingle",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [
            {
                "name": "params",
                "type": "tuple",
                "components": [
                    {"name": "tokenIn", "type": "address"},
                    {"name": "tokenOut", "type": "address"},
                    {"name": "fee", "type": "uint24"},
                    {"name": "recipient", "type": "address"},
                    {"name": "amountIn", "type": "uint256"},
                    {"name": "amountOutMinimum", "type": "uint256"},
                    {"name": "sqrtPriceLimitX96", "type": "uint160"},
                ],
            }
        ],
        "outputs": [{"name": "amountOut", "type": "uint256"}],
    }
]

AERODROME_SWAP_ABI = [
    {
        "name": "swapExactTokensForTokens",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMin", "type": "uint256"},
            {
                "name": "routes",
                "type": "tuple[]",
                "components": [
                    {"name": "from", "type": "address"},
                    {"name": "to", "type": "address"},
                    {"name": "stable", "type": "bool"},
                    {"name": "factory", "type": "address"},
                ],
            },
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
    }
]

AERODROME_BASE_FACTORY = "0x420dd381b31aef6683db6b902084cb0ffece40da"

EthCallRunner = Callable[[dict[str, Any], str], dict[str, Any]]


class TransactionSimulationService:
    """Builds transaction-simulation evidence for a future live pilot.

    This is intentionally not a transaction sender. It does not sign, approve,
    or submit transactions. It builds unsigned swap calldata and simulates it
    with eth_call when a reviewed paper/shadow candidate exists.
    """

    APPROVED_CHAINS = {"base"}
    APPROVED_TOKENS = {"USDC", "WETH"}
    APPROVED_DEXES = {"Uniswap V3", "Aerodrome"}

    def __init__(
        self,
        data_dir: Path | str = "data",
        report_dir: Path | str = "reports",
        eth_call_runner: EthCallRunner | None = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.output_json = self.report_dir / "transaction_simulation.json"
        self.output_md = self.report_dir / "transaction_simulation.md"
        self.eth_call_runner = eth_call_runner or self._default_eth_call_runner

    def generate(self) -> dict[str, Any]:
        flags = load_feature_flags()
        wallet = self._read_json(self.report_dir / "wallet_preflight.json")
        readiness = self._read_json(self.report_dir / "live_readiness_checklist.json")
        realism = self._read_json(self.report_dir / "execution_realism.json")
        candidate = self._select_candidate(realism)
        intent = self._simulation_intent(candidate, flags)
        checks = self._checks(flags=flags, wallet=wallet, readiness=readiness, candidate=candidate, intent=intent)
        blockers = [row for row in checks if row["severity"] == "BLOCK"]
        actions = [row for row in checks if row["severity"] == "ACTION"]
        simulation_passed = not blockers and not actions
        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "overall_status": "TX_SIMULATION_READY" if simulation_passed else "TX_SIMULATION_ACTION",
            "transaction_simulation_passed": simulation_passed,
            "live_trading_approval": False,
            "selected_candidate": candidate,
            "simulation_intent": intent,
            "check_count": len(checks),
            "pass_count": sum(1 for row in checks if row["severity"] == "PASS"),
            "action_count": len(actions),
            "blocked_check_count": len(blockers),
            "checks": checks,
            "notes": [
                "Transaction Simulation is evidence-only and never sends a transaction.",
                "The gate remains non-passing until exact calldata is built, Base eth_call simulation succeeds for both arbitrage legs, and the surrounding readiness checks pass.",
                "Private keys must remain absent while developing this report.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _select_candidate(self, realism: dict[str, Any]) -> dict[str, Any]:
        rows = realism.get("opportunities", [])
        if isinstance(rows, list):
            for row in rows:
                enriched = self._enrich_candidate(dict(row))
                if (
                    str(enriched.get("source_decision", "")).upper() == "BUY"
                    and str(enriched.get("realism_status", "")).upper() == "SHADOW_READY"
                    and str(enriched.get("chain", "")).lower() in self.APPROVED_CHAINS
                    and {str(enriched.get("buy_source", "")), str(enriched.get("sell_source", ""))}.issubset(self.APPROVED_DEXES)
                    and self._decimal(enriched.get("buy_price")) > 0
                    and self._decimal(enriched.get("sell_price")) > 0
                ):
                    return enriched
        return {}

    def _enrich_candidate(self, candidate: dict[str, Any]) -> dict[str, Any]:
        if self._decimal(candidate.get("buy_price")) > 0 and self._decimal(candidate.get("sell_price")) > 0:
            return candidate
        for row in reversed(self._read_jsonl(self.data_dir / "opportunity_decisions.jsonl")):
            if (
                str(row.get("timestamp", "")) == str(candidate.get("timestamp", ""))
                and str(row.get("chain", "")).lower() == str(candidate.get("chain", "")).lower()
                and str(row.get("pair", "")).upper() == str(candidate.get("pair", "")).upper()
                and str(row.get("buy_source", "")) == str(candidate.get("buy_source", ""))
                and str(row.get("sell_source", "")) == str(candidate.get("sell_source", ""))
            ):
                candidate["buy_price"] = row.get("buy_price") or row.get("buy_price_usd")
                candidate["sell_price"] = row.get("sell_price") or row.get("sell_price_usd")
                break
        return candidate

    def _simulation_intent(self, candidate: dict[str, Any], flags: Any) -> dict[str, Any]:
        if not candidate:
            if not flags.live_wallet_address or flags.max_live_trade_usd <= 0:
                return {
                    "status": "NO_CANDIDATE",
                    "calldata_status": "NOT_BUILT",
                    "eth_call_status": "NOT_RUN",
                    "reason": "No latest approved BUY plus SHADOW_READY opportunity or configured tiny smoke route is available.",
                }
            return self._tiny_smoke_intent(flags)

        chain = str(candidate.get("chain", "")).lower()
        pair = str(candidate.get("pair", "")).upper()
        symbols = pair.split("/")
        base_symbol = symbols[0] if symbols else ""
        quote_symbol = symbols[1] if len(symbols) > 1 else ""
        buy_dex = str(candidate.get("buy_source", ""))
        sell_dex = str(candidate.get("sell_source", ""))
        dexes = {dex.name: dex for dex in get_dexes_for_chain(chain)}
        token_rows = []
        for symbol in [base_symbol, quote_symbol]:
            token = get_token(chain, symbol)
            token_rows.append(
                {
                    "symbol": symbol,
                    "address": token.address if token else None,
                    "decimals": token.decimals if token else None,
                    "configured": token is not None,
                }
            )
        router_rows = []
        for name in [buy_dex, sell_dex]:
            dex = dexes.get(name)
            router_rows.append(
                {
                    "dex": name,
                    "router_address": dex.router_address if dex else None,
                    "dex_type": dex.dex_type if dex else None,
                    "configured": bool(dex and dex.router_address),
                }
            )

        max_trade = flags.max_live_trade_usd if flags.max_live_trade_usd > 0 else Decimal("0")
        requested = self._decimal(candidate.get("requested_notional_usd")) or max_trade
        notional = min(value for value in [requested, max_trade] if value > 0) if requested > 0 or max_trade > 0 else Decimal("0")
        slippage_bps = Decimal("50")

        intent: dict[str, Any] = {
            "status": "INTENT_READY",
            "chain": chain,
            "chain_id": 8453 if chain == "base" else None,
            "wallet_address": flags.live_wallet_address or None,
            "pair": pair,
            "buy_dex": buy_dex,
            "sell_dex": sell_dex,
            "notional_usd": self._fmt(notional),
            "max_slippage_bps": str(slippage_bps),
            "deadline_seconds": "120",
            "tokens": token_rows,
            "routers": router_rows,
            "calldata_status": "NOT_BUILT",
            "eth_call_status": "NOT_RUN",
        }
        intent.update(self._build_and_simulate_route(candidate, intent))
        return intent

    def _tiny_smoke_intent(self, flags: Any) -> dict[str, Any]:
        wallet = flags.live_wallet_address or ""
        max_trade = flags.max_live_trade_usd if flags.max_live_trade_usd > 0 else Decimal("0")
        smoke_usd = self._decimal(os.getenv("CRYPTOAI_TINY_LIVE_SMOKE_USD", "20"))
        if max_trade > 0:
            smoke_usd = min(smoke_usd, max_trade)
        smoke_usd = min(smoke_usd, Decimal("20"))
        dex_name = os.getenv("CRYPTOAI_TINY_LIVE_DEX", "Uniswap V3").strip() or "Uniswap V3"
        token_usdc = get_token("base", "USDC")
        token_weth = get_token("base", "WETH")
        dexes = {dex.name: dex for dex in get_dexes_for_chain("base")}
        dex = dexes.get(dex_name)
        intent: dict[str, Any] = {
            "status": "INTENT_READY",
            "simulation_type": "TINY_LIVE_SMOKE",
            "chain": "base",
            "chain_id": 8453,
            "wallet_address": wallet or None,
            "pair": "USDC/WETH",
            "buy_dex": dex_name,
            "sell_dex": None,
            "notional_usd": self._fmt(smoke_usd),
            "max_slippage_bps": "50",
            "deadline_seconds": "120",
            "tokens": [
                {"symbol": "USDC", "address": token_usdc.address if token_usdc else None, "decimals": token_usdc.decimals if token_usdc else None, "configured": token_usdc is not None},
                {"symbol": "WETH", "address": token_weth.address if token_weth else None, "decimals": token_weth.decimals if token_weth else None, "configured": token_weth is not None},
            ],
            "routers": [
                {"dex": dex_name, "router_address": dex.router_address if dex else None, "dex_type": dex.dex_type if dex else None, "configured": bool(dex and dex.router_address)}
            ],
            "calldata_status": "NOT_BUILT",
            "eth_call_status": "NOT_RUN",
            "reason": "No approved two-leg arbitrage candidate is available; simulating the configured one-leg tiny live smoke swap.",
        }
        intent.update(self._build_and_simulate_tiny_smoke(intent))
        return intent

    def _build_and_simulate_tiny_smoke(self, intent: dict[str, Any]) -> dict[str, Any]:
        wallet = str(intent.get("wallet_address") or "")
        if not self._valid_address(wallet):
            return {"calldata_status": "BLOCKED", "eth_call_status": "NOT_RUN", "reason": "A valid isolated wallet address is required."}
        notional = self._decimal(intent.get("notional_usd"))
        if notional <= 0:
            return {"calldata_status": "BLOCKED", "eth_call_status": "NOT_RUN", "reason": "Tiny smoke notional must be greater than zero."}
        try:
            leg = self._build_leg(
                leg="TINY_LIVE_SMOKE_SWAP",
                chain="base",
                dex_name=str(intent.get("buy_dex")),
                token_in_symbol="USDC",
                token_out_symbol="WETH",
                amount_in_decimal=notional,
                amount_out_min_decimal=Decimal("0.000000000000000001"),
                recipient=wallet,
                deadline=int(time.time()) + int(intent.get("deadline_seconds", "120")),
            )
        except Exception as exc:
            return {"calldata_status": "ERROR", "eth_call_status": "NOT_RUN", "reason": f"{type(exc).__name__}: {exc}"}
        result = self.eth_call_runner(leg["eth_call"], "base")
        leg["eth_call_result"] = result
        return {
            "status": "SIMULATION_READY" if result.get("status") == "PASS" else "SIMULATION_ATTEMPTED",
            "calldata_status": "BUILT",
            "eth_call_status": result.get("status", "FAIL"),
            "swap_legs": [leg],
            "eth_call_summary": {
                "leg_count": 1,
                "pass_count": 1 if result.get("status") == "PASS" else 0,
                "revert_count": 1 if result.get("status") == "REVERT" else 0,
                "fail_count": 0 if result.get("status") in {"PASS", "REVERT"} else 1,
            },
        }

    def _build_and_simulate_route(self, candidate: dict[str, Any], intent: dict[str, Any]) -> dict[str, Any]:
        chain = str(intent.get("chain", "")).lower()
        wallet = str(intent.get("wallet_address") or "")
        if chain not in self.APPROVED_CHAINS:
            return {"calldata_status": "BLOCKED", "eth_call_status": "NOT_RUN", "reason": "Chain is outside the simulation allowlist."}
        if not self._valid_address(wallet):
            return {"calldata_status": "BLOCKED", "eth_call_status": "NOT_RUN", "reason": "A valid isolated wallet address is required."}

        try:
            legs = self._build_swap_legs(candidate, intent)
        except Exception as exc:
            return {
                "calldata_status": "ERROR",
                "eth_call_status": "NOT_RUN",
                "reason": f"{type(exc).__name__}: {exc}",
            }

        call_results = [self.eth_call_runner(leg["eth_call"], chain) for leg in legs]
        for leg, result in zip(legs, call_results, strict=False):
            leg["eth_call_result"] = result

        if all(result.get("status") == "PASS" for result in call_results):
            eth_call_status = "PASS"
        elif any(result.get("status") == "REVERT" for result in call_results):
            eth_call_status = "REVERT"
        else:
            eth_call_status = "FAIL"

        return {
            "status": "SIMULATION_READY" if eth_call_status == "PASS" else "SIMULATION_ATTEMPTED",
            "calldata_status": "BUILT",
            "eth_call_status": eth_call_status,
            "swap_legs": legs,
            "eth_call_summary": {
                "leg_count": len(legs),
                "pass_count": sum(1 for row in call_results if row.get("status") == "PASS"),
                "revert_count": sum(1 for row in call_results if row.get("status") == "REVERT"),
                "fail_count": sum(1 for row in call_results if row.get("status") not in {"PASS", "REVERT"}),
            },
        }

    def _build_swap_legs(self, candidate: dict[str, Any], intent: dict[str, Any]) -> list[dict[str, Any]]:
        pair = str(intent.get("pair", "")).upper()
        symbols = pair.split("/")
        if {"USDC", "WETH"} - set(symbols):
            raise ValueError("Only USDC/WETH simulation routes are supported.")

        token_usdc = get_token("base", "USDC")
        token_weth = get_token("base", "WETH")
        if token_usdc is None or token_weth is None:
            raise ValueError("USDC/WETH token metadata is missing.")

        buy_price = self._decimal(candidate.get("buy_price"))
        sell_price = self._decimal(candidate.get("sell_price"))
        notional = self._decimal(intent.get("notional_usd"))
        if notional <= 0:
            raise ValueError("Simulation notional must be greater than zero.")
        if buy_price <= 0 or sell_price <= 0:
            raise ValueError("Simulation candidate must include buy and sell prices.")

        slippage_bps = self._decimal(intent.get("max_slippage_bps")) or Decimal("50")
        deadline = int(time.time()) + int(intent.get("deadline_seconds", "120"))
        buy_expected_weth = self._expected_weth_out(pair=pair, usdc_in=notional, price=buy_price)
        sell_expected_usdc = self._expected_usdc_out(pair=pair, weth_in=buy_expected_weth, price=sell_price)

        buy_leg = self._build_leg(
            leg="BUY_WETH",
            chain="base",
            dex_name=str(intent.get("buy_dex")),
            token_in_symbol="USDC",
            token_out_symbol="WETH",
            amount_in_decimal=notional,
            amount_out_min_decimal=self._apply_slippage(buy_expected_weth, slippage_bps),
            recipient=str(intent.get("wallet_address")),
            deadline=deadline,
        )
        sell_leg = self._build_leg(
            leg="SELL_WETH",
            chain="base",
            dex_name=str(intent.get("sell_dex")),
            token_in_symbol="WETH",
            token_out_symbol="USDC",
            amount_in_decimal=buy_expected_weth,
            amount_out_min_decimal=self._apply_slippage(sell_expected_usdc, slippage_bps),
            recipient=str(intent.get("wallet_address")),
            deadline=deadline,
        )
        return [buy_leg, sell_leg]

    def _build_leg(
        self,
        *,
        leg: str,
        chain: str,
        dex_name: str,
        token_in_symbol: str,
        token_out_symbol: str,
        amount_in_decimal: Decimal,
        amount_out_min_decimal: Decimal,
        recipient: str,
        deadline: int,
    ) -> dict[str, Any]:
        dexes = {dex.name: dex for dex in get_dexes_for_chain(chain)}
        dex = dexes.get(dex_name)
        token_in = get_token(chain, token_in_symbol)
        token_out = get_token(chain, token_out_symbol)
        if dex is None or not dex.router_address:
            raise ValueError(f"Router metadata is missing for {dex_name}.")
        if token_in is None or token_out is None:
            raise ValueError(f"Token metadata is missing for {token_in_symbol}/{token_out_symbol}.")

        amount_in_units = self._to_units(amount_in_decimal, token_in.decimals)
        amount_out_min_units = max(1, self._to_units(amount_out_min_decimal, token_out.decimals))
        router = Web3.to_checksum_address(dex.router_address)
        token_in_address = Web3.to_checksum_address(token_in.address)
        token_out_address = Web3.to_checksum_address(token_out.address)
        recipient_address = Web3.to_checksum_address(recipient)
        web3 = Web3()

        if dex.dex_type == "v3":
            fee_tier = int(os.getenv("CRYPTOAI_UNISWAP_V3_FEE_TIER", "500"))
            contract = web3.eth.contract(address=router, abi=UNISWAP_V3_SWAP_ROUTER_02_ABI)
            params = (
                token_in_address,
                token_out_address,
                fee_tier,
                recipient_address,
                amount_in_units,
                amount_out_min_units,
                0,
            )
            calldata = contract.functions.exactInputSingle(params)._encode_transaction_data()
            route_metadata: dict[str, Any] = {"fee_tier": fee_tier, "sqrt_price_limit_x96": 0}
        elif dex.dex_type == "solidly":
            contract = web3.eth.contract(address=router, abi=AERODROME_SWAP_ABI)
            routes = [(token_in_address, token_out_address, False, Web3.to_checksum_address(AERODROME_BASE_FACTORY))]
            calldata = contract.functions.swapExactTokensForTokens(
                amount_in_units,
                amount_out_min_units,
                routes,
                recipient_address,
                deadline,
            )._encode_transaction_data()
            route_metadata = {"stable": False, "factory": AERODROME_BASE_FACTORY}
        elif dex.dex_type == "v2":
            contract = web3.eth.contract(address=router, abi=UNISWAP_V2_SWAP_ABI)
            path = [token_in_address, token_out_address]
            calldata = contract.functions.swapExactTokensForTokens(
                amount_in_units,
                amount_out_min_units,
                path,
                recipient_address,
                deadline,
            )._encode_transaction_data()
            route_metadata = {"path": path}
        else:
            raise ValueError(f"Unsupported router type for transaction simulation: {dex.dex_type}")

        eth_call = {
            "from": recipient_address,
            "to": router,
            "data": calldata,
            "value": "0x0",
        }
        return {
            "leg": leg,
            "dex": dex_name,
            "router_type": dex.dex_type,
            "router_address": router,
            "token_in": token_in_symbol,
            "token_in_address": token_in_address,
            "token_out": token_out_symbol,
            "token_out_address": token_out_address,
            "amount_in_units": str(amount_in_units),
            "amount_out_min_units": str(amount_out_min_units),
            "deadline": deadline,
            "calldata": calldata,
            "calldata_bytes": (len(calldata) - 2) // 2,
            "eth_call": eth_call,
            "route_metadata": route_metadata,
        }

    def _default_eth_call_runner(self, tx: dict[str, Any], chain: str) -> dict[str, Any]:
        if chain not in SUPPORTED_CHAINS:
            return {"status": "FAIL", "error": f"Unsupported chain: {chain}"}

        client = RpcClient(SUPPORTED_CHAINS[chain])
        last_error = "No RPC candidates available."
        for endpoint, web3 in client.iter_web3_candidates():
            start = time.perf_counter()
            try:
                chain_id = web3.eth.chain_id
                expected_chain_id = SUPPORTED_CHAINS[chain].chain_id
                if chain_id != expected_chain_id:
                    last_error = f"RPC chain id {chain_id} did not match expected {expected_chain_id}."
                    client.record_rpc_failure(endpoint, last_error, (time.perf_counter() - start) * 1000)
                    continue
                block_number = web3.eth.block_number
                result = web3.eth.call(tx, block_identifier="latest")
                latency_ms = (time.perf_counter() - start) * 1000
                client.record_rpc_success(endpoint, latency_ms)
                return {
                    "status": "PASS",
                    "rpc": endpoint.name,
                    "rpc_url": self._redact_url(endpoint.url),
                    "chain_id": chain_id,
                    "block_number": block_number,
                    "latency_ms": round(latency_ms, 2),
                    "result": result.hex(),
                }
            except Exception as exc:
                latency_ms = (time.perf_counter() - start) * 1000
                message = f"{type(exc).__name__}: {exc}"
                last_error = message
                client.record_rpc_failure(endpoint, message, latency_ms)
                status = "REVERT" if "revert" in message.lower() or "execution reverted" in message.lower() else "FAIL"
                if status == "REVERT":
                    return {
                        "status": "REVERT",
                        "rpc": endpoint.name,
                        "rpc_url": self._redact_url(endpoint.url),
                        "latency_ms": round(latency_ms, 2),
                        "error": message[:500],
                    }

        return {"status": "FAIL", "error": last_error[:500]}

    def _checks(
        self,
        *,
        flags: Any,
        wallet: dict[str, Any],
        readiness: dict[str, Any],
        candidate: dict[str, Any],
        intent: dict[str, Any],
    ) -> list[dict[str, str]]:
        token_rows = intent.get("tokens", []) if isinstance(intent.get("tokens"), list) else []
        router_rows = intent.get("routers", []) if isinstance(intent.get("routers"), list) else []
        pair_tokens = {str(row.get("symbol", "")).upper() for row in token_rows}
        router_names = {str(row.get("dex", "")) for row in router_rows}
        candidate_exists = bool(candidate)
        smoke_simulation = str(intent.get("simulation_type", "")).upper() == "TINY_LIVE_SMOKE"
        return [
            self._check(
                "live_trading_disabled",
                not flags.live_trading_enabled,
                "BLOCK",
                "Live trading must remain disabled during transaction simulation development.",
                "Live trading is disabled.",
            ),
            self._check(
                "kill_switch_enabled",
                flags.live_kill_switch_enabled,
                "BLOCK",
                "Live kill switch must remain enabled during transaction simulation development.",
                "Live kill switch is enabled.",
            ),
            self._check(
                "private_key_absent",
                not flags.private_key_configured,
                "BLOCK",
                "Private key must not be configured for simulation report generation.",
                "Private key is absent.",
            ),
            self._check(
                "wallet_preflight_ready",
                wallet.get("wallet_preflight_allowed") is True,
                "ACTION",
                "Wallet Preflight must be ready before transaction simulation review.",
                "Wallet Preflight is ready.",
            ),
            self._check(
                "live_readiness_preconditions_ready",
                self._int(readiness.get("blocked_check_count")) == 0,
                "ACTION",
                "Live Readiness Checklist has blocking checks that must be cleared before transaction simulation can pass.",
                "Live Readiness Checklist has no blocking checks.",
            ),
            self._check(
                "shadow_candidate_available",
                bool(candidate) or smoke_simulation,
                "ACTION",
                "No BUY plus SHADOW_READY opportunity or tiny smoke simulation route is available.",
                "A simulation route is available.",
            ),
            self._check(
                "candidate_scope_allowed",
                smoke_simulation
                or (not candidate_exists)
                or (
                    str(candidate.get("chain", "")).lower() in self.APPROVED_CHAINS
                    and pair_tokens.issubset(self.APPROVED_TOKENS)
                    and bool(pair_tokens)
                ),
                "BLOCK",
                "Simulation candidate must be Base USDC/WETH scope only.",
                "Simulation candidate is Base USDC/WETH scope.",
            ),
            self._check(
                "routers_configured",
                (not candidate_exists) or (all(bool(row.get("configured")) for row in router_rows) and bool(router_rows)),
                "BLOCK",
                "Both route routers must be configured.",
                "Both route routers are configured.",
            ),
            self._check(
                "approved_live_dexes",
                (smoke_simulation and router_names.issubset(self.APPROVED_DEXES))
                or ((not smoke_simulation) and ((not candidate_exists) or router_names.issubset(self.APPROVED_DEXES))),
                "ACTION",
                "Simulation candidate uses a DEX outside the tiny-live allowlist.",
                "Simulation candidate DEXes are within the tiny-live allowlist.",
            ),
            self._check(
                "live_trade_cap_configured",
                Decimal("0") < flags.max_live_trade_usd <= flags.tiny_live_trade_ceiling_usd,
                "ACTION",
                "Configure a tiny live trade cap before transaction simulation review.",
                "Tiny live trade cap is configured.",
            ),
            self._check(
                "exact_calldata_built",
                intent.get("calldata_status") == "BUILT",
                "ACTION",
                "Exact router calldata was not built for the selected candidate.",
                "Exact router calldata is built.",
            ),
            self._check(
                "eth_call_simulation_passed",
                intent.get("eth_call_status") == "PASS",
                "ACTION",
                "Base eth_call simulation has not passed yet.",
                "Base eth_call simulation passed.",
            ),
        ]

    @staticmethod
    def _check(name: str, passed: bool, fail_severity: str, fail_detail: str, pass_detail: str) -> dict[str, str]:
        return {
            "name": name,
            "severity": "PASS" if passed else fail_severity,
            "passed": bool(passed),
            "detail": pass_detail if passed else fail_detail,
        }

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
    def _read_jsonl(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
        return rows

    @staticmethod
    def _valid_address(value: str) -> bool:
        try:
            Web3.to_checksum_address(value)
        except Exception:
            return False
        return True

    @staticmethod
    def _expected_weth_out(*, pair: str, usdc_in: Decimal, price: Decimal) -> Decimal:
        if pair == "WETH/USDC":
            return usdc_in / price
        if pair == "USDC/WETH":
            return usdc_in * price
        raise ValueError(f"Unsupported ETH route pair: {pair}")

    @staticmethod
    def _expected_usdc_out(*, pair: str, weth_in: Decimal, price: Decimal) -> Decimal:
        if pair == "WETH/USDC":
            return weth_in * price
        if pair == "USDC/WETH":
            return weth_in / price
        raise ValueError(f"Unsupported ETH route pair: {pair}")

    @staticmethod
    def _apply_slippage(value: Decimal, slippage_bps: Decimal) -> Decimal:
        multiplier = Decimal("1") - (slippage_bps / Decimal("10000"))
        return max(Decimal("0"), value * multiplier)

    @staticmethod
    def _to_units(value: Decimal, decimals: int) -> int:
        return int((value * Decimal(10**decimals)).to_integral_value(rounding="ROUND_DOWN"))

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0")

    @staticmethod
    def _int(value: Any) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _fmt(value: Decimal) -> str:
        return str(value.quantize(Decimal("0.0000")))

    @staticmethod
    def _redact_url(url: str) -> str:
        if "?" not in url:
            return url
        return url.split("?", 1)[0] + "?redacted=true"

    def _markdown(self, payload: dict[str, Any]) -> str:
        intent = payload.get("simulation_intent", {})
        lines = [
            "# Transaction Simulation Report",
            "",
            f"Generated: `{payload['generated_at']}`",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Transaction simulation passed: `{payload['transaction_simulation_passed']}`",
            f"- Live trading approval: `{payload['live_trading_approval']}`",
            f"- Candidate pair: `{intent.get('pair', '-')}`",
            f"- Buy DEX: `{intent.get('buy_dex', '-')}`",
            f"- Sell DEX: `{intent.get('sell_dex', '-')}`",
            f"- Notional USD: `${intent.get('notional_usd', '-')}`",
            f"- Calldata status: `{intent.get('calldata_status', '-')}`",
            f"- eth_call status: `{intent.get('eth_call_status', '-')}`",
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
        lines.extend(["", "## Intent", "", "```json", json.dumps(intent, indent=2), "```", "", "## Notes", ""])
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    payload = TransactionSimulationService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
