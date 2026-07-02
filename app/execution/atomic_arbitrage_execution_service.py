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
from app.config.feature_flags import load_feature_flags


ATOMIC_EXECUTOR_ABI_V1 = [
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


ATOMIC_EXECUTOR_ABI_V2 = [
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
                    {"name": "patchSellAmountIn", "type": "bool"},
                    {"name": "sellAmountInOffset", "type": "uint256"},
                ],
            }
        ],
        "outputs": [{"name": "amountOut", "type": "uint256"}, {"name": "profit", "type": "uint256"}],
    }
]

# Backwards-compatible default. _atomic_executor_abi() selects V2 when requested.
ATOMIC_EXECUTOR_ABI = ATOMIC_EXECUTOR_ABI_V1


EthCallRunner = Callable[[dict[str, Any], str], dict[str, Any]]


class AtomicArbitrageExecutionService:
    """Build and simulate a single-transaction live arbitrage call.

    The service prepares calldata for the deployed executor contract, routes
    both swap legs through the executor as recipient, and uses eth_call as the
    final evidence gate. It does not sign or broadcast transactions.
    """

    _executor_code_cache: dict[str, tuple[float, int]] = {}

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
        started_at = time.perf_counter()
        if self.refresh_transaction_simulation:
            tx_sim = TransactionSimulationService(data_dir=self.data_dir, report_dir=self.report_dir, eth_call_runner=self.eth_call_runner).generate()
        else:
            tx_sim = self._read_json(self.report_dir / "transaction_simulation.json")
        intent = tx_sim.get("simulation_intent", {}) if isinstance(tx_sim.get("simulation_intent"), dict) else {}
        diagnostics = self._route_diagnostics(tx_sim=tx_sim, intent=intent)
        route = self._build_best_atomic_route(tx_sim=tx_sim, intent=intent)
        if isinstance(route.get("route_sweep"), dict):
            diagnostics["route_sweep"] = route.get("route_sweep")
        reconciliation = self._profit_reconciliation(diagnostics=diagnostics, route=route)
        executor_preflight = self._executor_preflight(route)
        checks = self._checks(tx_sim=tx_sim, intent=intent, route=route, executor_preflight=executor_preflight)
        blockers = [row for row in checks if row["severity"] == "BLOCK"]
        actions = [row for row in checks if row["severity"] == "ACTION"]
        passed = not blockers and not actions
        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        payload = {
            "generated_at": self._utc_now(),
            "mode": "atomic_live_arbitrage_simulation",
            "overall_status": "ATOMIC_ROUTE_SIMULATION_PASSED" if passed else "ATOMIC_ROUTE_ACTION",
            "atomic_route_simulation_passed": passed,
            "live_trading_approval": False,
            "transaction_simulation_status": tx_sim.get("overall_status"),
            "route_diagnostics": diagnostics,
            "profit_reconciliation": reconciliation,
            "executor_preflight": executor_preflight,
            "atomic_route": route,
            "check_count": len(checks),
            "pass_count": sum(1 for row in checks if row["severity"] == "PASS"),
            "action_count": len(actions),
            "blocked_check_count": len(blockers),
            "checks": checks,
            "performance_metrics": {
                "generation_elapsed_ms": elapsed_ms,
                "route_sweep_attempt_count": self._int(route.get("route_sweep", {}).get("attempt_count") if isinstance(route.get("route_sweep"), dict) else 0),
                "selected_eth_call_elapsed_ms": self._int(route.get("eth_call_result", {}).get("elapsed_ms") if isinstance(route.get("eth_call_result"), dict) else 0),
            },
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


    def _build_best_atomic_route(self, *, tx_sim: dict[str, Any], intent: dict[str, Any]) -> dict[str, Any]:
        """Build/simulate multiple route candidates and return the best exact eth_call result.

        The paper/stress estimate can diverge materially from exact router execution.
        This sweep treats labels and stress edge as hints only: it builds exact executor
        calldata for several fresh two-leg candidates and chooses the candidate with the
        best atomic eth_call result. It still never approves live execution unless the
        executor eth_call passes.
        """
        if not self._bool_env("CRYPTOAI_ATOMIC_ROUTE_SWEEP_ENABLED", default=True):
            route = self._build_atomic_route(intent)
            route["route_sweep"] = {"enabled": False, "reason": "CRYPTOAI_ATOMIC_ROUTE_SWEEP_ENABLED is false."}
            return route

        candidates = self._atomic_sweep_candidates(tx_sim=tx_sim)
        if not candidates:
            route = self._build_atomic_route(intent)
            route["route_sweep"] = {"enabled": True, "candidate_count": 0, "attempt_count": 0, "reason": "No sweep candidates available."}
            return route

        tx_service = TransactionSimulationService(data_dir=self.data_dir, report_dir=self.report_dir, eth_call_runner=self.eth_call_runner)
        flags = load_feature_flags()
        max_attempts = max(1, self._int(os.getenv("CRYPTOAI_ATOMIC_ROUTE_SWEEP_MAX_ATTEMPTS", "36")))
        attempts: list[dict[str, Any]] = []
        best_route: dict[str, Any] | None = None
        best_score: Decimal | None = None

        for idx, candidate in enumerate(candidates[:max_attempts], start=1):
            try:
                candidate_intent = tx_service._simulation_intent(candidate, flags)
                candidate_intent["selected_candidate"] = candidate
                if candidate.get("sweep_notional_usd"):
                    candidate_intent["notional_usd"] = self._fmt(self._decimal(candidate.get("sweep_notional_usd")))
                if candidate.get("selection_mode") in {"ATOMIC_ROUTE_SWEEP_VENUE", "ATOMIC_ROUTE_SWEEP_REVERSE_DEX", "ATOMIC_ROUTE_SWEEP_NOTIONAL", "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"}:
                    # v6.8: sweep tight leg-slippage values. Because the executor uses static
                    # calldata, the sell leg amountIn is tied to the buy leg minimum. A loose
                    # buy minOut (for example 300 bps) can make the atomic route look like a
                    # large loss by selling only the conservative minimum WETH and leaving extra
                    # WETH in the executor. Tight slippage is tested by exact eth_call before send.
                    candidate_intent["max_slippage_bps"] = str(candidate.get("sweep_leg_slippage_bps") or os.getenv("CRYPTOAI_ATOMIC_SWEEP_LEG_SLIPPAGE_BPS", candidate_intent.get("max_slippage_bps", "50")))
                route = self._build_atomic_route(candidate_intent)
                summary = self._route_attempt_summary(idx=idx, candidate=candidate, intent=candidate_intent, route=route)
                attempts.append(summary)
                score = self._route_attempt_score(route)
                if best_score is None or score > best_score:
                    best_score = score
                    best_route = route
                if route.get("eth_call_status") == "PASS" and self._bool_env("CRYPTOAI_ATOMIC_ROUTE_SWEEP_STOP_ON_PASS", default=True):
                    break
            except Exception as exc:
                attempts.append({
                    "attempt": idx,
                    "status": "ERROR",
                    "error": f"{type(exc).__name__}: {exc}"[:300],
                    "candidate": self._candidate_summary(candidate),
                })

        if best_route is None:
            route = self._build_atomic_route(intent)
            route["route_sweep"] = {"enabled": True, "candidate_count": len(candidates), "attempt_count": len(attempts), "attempts": attempts, "reason": "Sweep produced no buildable route."}
            return route

        passing = [row for row in attempts if row.get("eth_call_status") == "PASS"]
        best_route["route_sweep"] = {
            "enabled": True,
            "strategy": "best_exact_atomic_eth_call_notional_venue_sweep",
            "candidate_count": len(candidates),
            "attempt_count": len(attempts),
            "passing_count": len(passing),
            "sweep_config": {
                "notionals_usd": [str(x) for x in self._sweep_notionals()],
                "venues": self._sweep_venues(),
                "venue_sweep_enabled": self._bool_env("CRYPTOAI_ATOMIC_ROUTE_SWEEP_VENUES_ENABLED", default=True),
                "leg_slippage_bps_list": [str(x) for x in self._sweep_leg_slippages()],
                "legacy_single_leg_slippage_bps": os.getenv("CRYPTOAI_ATOMIC_SWEEP_LEG_SLIPPAGE_BPS", os.getenv("CRYPTOAI_TINY_LIVE_MAX_SLIPPAGE_BPS", "50")),
            },
            "selected_attempt": self._route_attempt_summary(idx=0, candidate=best_route.get("selected_candidate", {}), intent=best_route.get("selected_intent", {}), route=best_route),
            "attempts": attempts,
            "selection_rule": "Prefer PASS; otherwise pick the route with the highest simulated atomic USDC output / smallest shortfall across candidate, venue, and notional variants.",
        }
        return best_route

    def _atomic_sweep_candidates(self, *, tx_sim: dict[str, Any]) -> list[dict[str, Any]]:
        tx_service = TransactionSimulationService(data_dir=self.data_dir, report_dir=self.report_dir, eth_call_runner=self.eth_call_runner)
        realism = self._read_json(self.report_dir / "execution_realism.json")
        raw_rows: list[dict[str, Any]] = []
        selected = tx_sim.get("selected_candidate", {}) if isinstance(tx_sim.get("selected_candidate"), dict) else {}
        if selected:
            raw_rows.append(dict(selected))
        rows = realism.get("opportunities", []) if isinstance(realism.get("opportunities"), list) else []
        for row in rows:
            if isinstance(row, dict):
                raw_rows.append(dict(row))

        seen: set[tuple[str, str, str, str, str]] = set()
        candidates: list[dict[str, Any]] = []
        for row in raw_rows:
            enriched = tx_service._enrich_candidate(dict(row))
            for candidate in self._candidate_variants(enriched):
                if not tx_service._candidate_allowed_for_atomic_route(candidate):
                    continue
                key = (
                    str(candidate.get("timestamp")),
                    str(candidate.get("pair", "")).upper(),
                    str(candidate.get("buy_source") or candidate.get("buy_dex")),
                    str(candidate.get("sell_source") or candidate.get("sell_dex")),
                    str(candidate.get("variant", "original")),
                    str(candidate.get("sweep_notional_usd") or candidate.get("requested_notional_usd")),
                )
                if key in seen:
                    continue
                seen.add(key)
                candidates.append(candidate)

        candidates.sort(
            key=lambda row: (
                self._timestamp_seconds(row.get("timestamp")),
                self._decimal(row.get("stress_net_edge_pct")),
                self._decimal(row.get("gross_edge_pct")),
            ),
            reverse=True,
        )
        return candidates

    def _candidate_variants(self, candidate: dict[str, Any]) -> list[dict[str, Any]]:
        base = dict(candidate)
        base.setdefault("buy_source", base.get("buy_dex"))
        base.setdefault("sell_source", base.get("sell_dex"))
        base["variant"] = base.get("variant", "original")
        route_variants: list[dict[str, Any]] = [base]

        if self._bool_env("CRYPTOAI_ATOMIC_ROUTE_SWEEP_REVERSE_DEX", default=True):
            buy_source = base.get("buy_source")
            sell_source = base.get("sell_source")
            buy_price = base.get("buy_price")
            sell_price = base.get("sell_price")
            if buy_source and sell_source and buy_price and sell_price and str(buy_source) != str(sell_source):
                rev = dict(base)
                rev["buy_source"] = sell_source
                rev["buy_dex"] = sell_source
                rev["sell_source"] = buy_source
                rev["sell_dex"] = buy_source
                rev["buy_price"] = sell_price
                rev["sell_price"] = buy_price
                rev["variant"] = "reverse_dex"
                rev["selection_mode"] = "ATOMIC_ROUTE_SWEEP_REVERSE_DEX"
                rev["selection_reason"] = "Synthetic reverse DEX candidate for exact atomic eth_call sweep."
                route_variants.append(rev)

        if self._bool_env("CRYPTOAI_ATOMIC_ROUTE_SWEEP_VENUES_ENABLED", default=True):
            venues = self._sweep_venues()
            for buy_venue in venues:
                for sell_venue in venues:
                    if buy_venue == sell_venue:
                        continue
                    venue_candidate = dict(base)
                    venue_candidate["buy_source"] = buy_venue
                    venue_candidate["buy_dex"] = buy_venue
                    venue_candidate["sell_source"] = sell_venue
                    venue_candidate["sell_dex"] = sell_venue
                    venue_candidate["variant"] = f"venue:{buy_venue}->{sell_venue}"
                    venue_candidate["selection_mode"] = "ATOMIC_ROUTE_SWEEP_VENUE"
                    venue_candidate["selection_reason"] = "Synthetic venue candidate for exact atomic eth_call sweep."
                    route_variants.append(venue_candidate)

        notionals = self._sweep_notionals() if self._bool_env("CRYPTOAI_ATOMIC_NOTIONAL_SWEEP_ENABLED", default=True) else []
        if not notionals:
            notionals = [self._decimal(base.get("requested_notional_usd"))]
        slippages = self._sweep_leg_slippages() if self._bool_env("CRYPTOAI_ATOMIC_LEG_SLIPPAGE_SWEEP_ENABLED", default=True) else []
        if not slippages:
            slippages = [self._decimal(os.getenv("CRYPTOAI_ATOMIC_SWEEP_LEG_SLIPPAGE_BPS", os.getenv("CRYPTOAI_TINY_LIVE_MAX_SLIPPAGE_BPS", "50")))]

        expanded: list[dict[str, Any]] = []
        for row in route_variants:
            for notional in notionals:
                if notional <= 0:
                    continue
                for slippage_bps in slippages:
                    if slippage_bps < 0:
                        continue
                    sized = dict(row)
                    sized["requested_notional_usd"] = self._fmt(notional)
                    sized["sweep_notional_usd"] = self._fmt(notional)
                    sized["sweep_leg_slippage_bps"] = self._fmt(slippage_bps)
                    if sized.get("selection_mode") not in {"ATOMIC_ROUTE_SWEEP_VENUE", "ATOMIC_ROUTE_SWEEP_REVERSE_DEX"}:
                        sized["selection_mode"] = "ATOMIC_ROUTE_SWEEP_NOTIONAL"
                        sized["selection_reason"] = "Notional-sized exact atomic eth_call sweep candidate."
                    if slippage_bps != self._decimal(os.getenv("CRYPTOAI_ATOMIC_SWEEP_LEG_SLIPPAGE_BPS", os.getenv("CRYPTOAI_TINY_LIVE_MAX_SLIPPAGE_BPS", "50"))):
                        sized["selection_mode"] = "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
                        sized["selection_reason"] = "Tight leg-slippage exact atomic eth_call sweep candidate."
                    expanded.append(sized)
        return expanded

    def _sweep_notionals(self) -> list[Decimal]:
        raw = os.getenv("CRYPTOAI_ATOMIC_NOTIONAL_SWEEP_USD", "1,2,5,10,15,19")
        max_live = self._decimal(os.getenv("CRYPTOAI_MAX_LIVE_TRADE_USD", "0"))
        values: list[Decimal] = []
        for part in raw.replace(";", ",").split(","):
            val = self._decimal(part.strip())
            if val <= 0:
                continue
            if max_live > 0 and val > max_live:
                continue
            if val not in values:
                values.append(val)
        if not values and max_live > 0:
            values.append(max_live)
        return sorted(values)


    def _sweep_leg_slippages(self) -> list[Decimal]:
        # Default to tight values. Loose values are useful for avoiding router reverts,
        # but with static two-leg calldata they can under-sell WETH on leg 2 and create
        # artificial ProfitTooLow failures. Exact eth_call remains the final safety gate.
        raw = os.getenv("CRYPTOAI_ATOMIC_SWEEP_LEG_SLIPPAGE_BPS_LIST", "1,2,5,10,25,50")
        values: list[Decimal] = []
        for part in raw.replace(";", ",").split(","):
            val = self._decimal(part.strip())
            if val < 0:
                continue
            if val not in values:
                values.append(val)
        if not values:
            single = self._decimal(os.getenv("CRYPTOAI_ATOMIC_SWEEP_LEG_SLIPPAGE_BPS", os.getenv("CRYPTOAI_TINY_LIVE_MAX_SLIPPAGE_BPS", "50")))
            values.append(single)
        return sorted(values)

    def _sweep_venues(self) -> list[str]:
        raw = os.getenv("CRYPTOAI_ATOMIC_ROUTE_SWEEP_VENUES", "Uniswap V2,Uniswap V3,Aerodrome")
        allowed = {"Uniswap V2", "Uniswap V3", "Aerodrome"}
        venues: list[str] = []
        for part in raw.split(","):
            name = part.strip()
            if name in allowed and name not in venues:
                venues.append(name)
        if len(venues) < 2:
            venues = ["Uniswap V2", "Uniswap V3"]
        return venues

    def _route_attempt_summary(self, *, idx: int, candidate: dict[str, Any], intent: dict[str, Any], route: dict[str, Any]) -> dict[str, Any]:
        decoded = route.get("eth_call_decoded_error", {}) if isinstance(route.get("eth_call_decoded_error"), dict) else {}
        success = route.get("eth_call_success", {}) if isinstance(route.get("eth_call_success"), dict) else {}
        amount_out = decoded.get("amount_out_usdc") or success.get("amount_out_usdc")
        required_out = decoded.get("required_out_usdc") or self._decimal_units(route.get("min_amount_out_units"), 6)
        shortfall = decoded.get("shortfall_usdc")
        if shortfall is None and amount_out is not None:
            shortfall = str(self._decimal(required_out) - self._decimal(amount_out))
        return {
            "attempt": idx,
            "status": route.get("status"),
            "eth_call_status": route.get("eth_call_status"),
            "decoded_error": decoded.get("name") or decoded.get("reason"),
            "amount_in_usdc": str(self._decimal_units(route.get("amount_in_units"), 6)),
            "simulated_atomic_out_usdc": str(amount_out) if amount_out is not None else None,
            "required_out_usdc": str(required_out) if required_out is not None else None,
            "shortfall_usdc": str(shortfall) if shortfall is not None else None,
            "candidate": self._candidate_summary(candidate),
            "intent": {
                "pair": intent.get("pair"),
                "buy_dex": intent.get("buy_dex"),
                "sell_dex": intent.get("sell_dex"),
                "notional_usd": intent.get("notional_usd"),
                "max_slippage_bps": intent.get("max_slippage_bps"),
                "sweep_leg_slippage_bps": candidate.get("sweep_leg_slippage_bps"),
                "selection_mode": intent.get("selection_mode"),
            },
        }

    @staticmethod
    def _candidate_summary(candidate: dict[str, Any]) -> dict[str, Any]:
        return {
            "timestamp": candidate.get("timestamp"),
            "pair": candidate.get("pair"),
            "buy_dex": candidate.get("buy_source") or candidate.get("buy_dex"),
            "sell_dex": candidate.get("sell_source") or candidate.get("sell_dex"),
            "variant": candidate.get("variant", "original"),
            "source_decision": candidate.get("source_decision"),
            "realism_status": candidate.get("realism_status"),
            "gross_edge_pct": candidate.get("gross_edge_pct"),
            "stress_net_edge_pct": candidate.get("stress_net_edge_pct"),
            "sweep_notional_usd": candidate.get("sweep_notional_usd"),
            "sweep_leg_slippage_bps": candidate.get("sweep_leg_slippage_bps"),
            "selection_mode": candidate.get("selection_mode"),
        }

    def _route_attempt_score(self, route: dict[str, Any]) -> Decimal:
        if route.get("eth_call_status") == "PASS":
            success = route.get("eth_call_success", {}) if isinstance(route.get("eth_call_success"), dict) else {}
            return Decimal("1000000000000") + self._decimal(success.get("profit_units"))
        decoded = route.get("eth_call_decoded_error", {}) if isinstance(route.get("eth_call_decoded_error"), dict) else {}
        if decoded.get("name") == "ProfitTooLow":
            return self._decimal(decoded.get("amount_out_units")) - self._decimal(decoded.get("required_out_units"))
        if decoded.get("name") == "RouterInsufficientOutputAmount":
            return Decimal("-1000000000")
        if route.get("calldata", "").startswith("0x"):
            return Decimal("-100000000")
        return Decimal("-10000000000")

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
            default_min_profit_bps = "1" if self._tiny_live_realism_enabled() else "5"
            min_profit_bps = self._decimal(os.getenv("CRYPTOAI_ATOMIC_MIN_PROFIT_BPS", default_min_profit_bps))
            min_profit_bps = max(Decimal("0"), min_profit_bps)
            min_profit_units = int((Decimal(amount_in_units) * min_profit_bps / Decimal("10000")).to_integral_value(rounding="ROUND_DOWN"))
            min_amount_out_units = amount_in_units + min_profit_units
            min_amount_out_usdc = Decimal(min_amount_out_units) / Decimal(10**token_usdc.decimals)
            deadline = int(time.time()) + int(os.getenv("CRYPTOAI_ATOMIC_DEADLINE_SECONDS", "90"))
            rebuilt_legs = self._executor_recipient_legs(
                intent={**intent, "atomic_min_amount_out_usdc": str(min_amount_out_usdc)},
                recipient=executor_address,
                deadline=deadline,
            )
            patch_sell_amount_in = self._should_patch_sell_amount_in()
            sell_amount_in_offset = self._sell_amount_in_offset(rebuilt_legs[1]) if patch_sell_amount_in else 0

            route_items = [
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
            ]
            if self._atomic_executor_is_v2():
                route_items.extend([patch_sell_amount_in, sell_amount_in_offset])
            route_tuple = tuple(route_items)

            web3 = Web3()
            contract = web3.eth.contract(address=executor_address, abi=self._atomic_executor_abi())
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
            "tiny_live_realism_enabled": self._tiny_live_realism_enabled(),
            "executor_version": "v2" if self._atomic_executor_is_v2() else "v1",
            "patch_sell_amount_in": patch_sell_amount_in,
            "sell_amount_in_offset": str(sell_amount_in_offset),
            "deadline": deadline,
            "calldata": calldata,
            "calldata_bytes": (len(calldata) - 2) // 2,
            "swap_legs": rebuilt_legs,
            "eth_call": tx,
            "eth_call_result": eth_call,
            "eth_call_status": eth_call.get("status", "FAIL"),
            "eth_call_decoded_error": decoded_error,
            "approval_spender": executor_address,
            "selected_candidate": intent.get("selected_candidate", {}),
            "selected_intent": {k: intent.get(k) for k in ["pair", "buy_dex", "sell_dex", "notional_usd", "max_slippage_bps", "selection_mode", "selection_reason"]},
            "v2_route_patch": {
                "enabled": self._atomic_executor_is_v2(),
                "patch_sell_amount_in": patch_sell_amount_in,
                "sell_amount_in_offset": str(sell_amount_in_offset),
                "sell_router_type": rebuilt_legs[1].get("router_type"),
                "sell_dex": rebuilt_legs[1].get("dex"),
                "explanation": "V2 patches sell calldata amountIn to the actual tokenMid balance received after leg 1.",
            },
            "eth_call_success": self._decode_executor_success(eth_call.get("result")) if eth_call.get("status") == "PASS" else {},
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
        tiny_eligible_rows = [row for row in route_rows if self._tiny_candidate_diagnostic_eligible(row)]
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
            next_action = "No two-leg route was selected. In tiny mode, confirm CRYPTOAI_TINY_LIVE_REALISM_ENABLED=true, market refresh succeeded, and tiny_live_eligible_count is greater than zero."

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
            "tiny_live_eligible_count": len(tiny_eligible_rows),
            "latest_opportunities": route_rows,
            "failed_transaction_simulation_checks": failed_tx_checks,
        }


    def _tiny_candidate_diagnostic_eligible(self, row: dict[str, Any]) -> bool:
        if not self._tiny_live_realism_enabled():
            return False
        if str(row.get("chain", "")).lower() != "base":
            return False
        if str(row.get("pair", "")).upper() not in {"USDC/WETH", "WETH/USDC"}:
            return False
        if str(row.get("source_decision", "")).upper() not in {"BUY", "WATCH"}:
            return False
        if str(row.get("realism_status", "")).upper() not in {"SHADOW_READY", "WATCH_ONLY"}:
            return False
        return self._decimal(row.get("gross_edge_pct")) > 0 and self._decimal(row.get("stress_net_edge_pct")) >= self._tiny_min_stress_pct()


    @staticmethod
    def _tiny_live_realism_enabled() -> bool:
        raw = os.getenv("CRYPTOAI_TINY_LIVE_REALISM_ENABLED")
        if raw is not None:
            return raw.strip().lower() in {"1", "true", "yes", "on"}
        return False

    def _tiny_min_stress_pct(self) -> Decimal:
        pct = os.getenv("CRYPTOAI_TINY_LIVE_MIN_STRESS_EDGE_PCT")
        if pct is not None:
            return self._decimal(pct)
        return self._decimal(os.getenv("CRYPTOAI_TINY_LIVE_MIN_STRESS_EDGE_BPS", "1")) / Decimal("100")

    def _profit_reconciliation(self, *, diagnostics: dict[str, Any], route: dict[str, Any]) -> dict[str, Any]:
        selected = diagnostics.get("selected_candidate", {}) if isinstance(diagnostics.get("selected_candidate"), dict) else {}
        amount_in = self._decimal_units(route.get("amount_in_units"), 6)
        decoded = route.get("eth_call_decoded_error", {}) if isinstance(route.get("eth_call_decoded_error"), dict) else {}
        success = route.get("eth_call_success", {}) if isinstance(route.get("eth_call_success"), dict) else {}
        simulated_out = self._decimal(decoded.get("amount_out_usdc") or success.get("amount_out_usdc"))
        required_out = self._decimal(decoded.get("required_out_usdc") or self._decimal_units(route.get("min_amount_out_units"), 6))
        if simulated_out <= 0 and route.get("eth_call_status") == "PASS":
            simulated_out = self._decimal(success.get("amount_out_usdc"))

        gross_edge_pct = self._decimal(selected.get("gross_edge_pct"))
        reported_net_pct = self._decimal(selected.get("reported_net_edge_pct"))
        stress_net_pct = self._decimal(selected.get("stress_net_edge_pct"))
        estimated_gross_out = amount_in * (Decimal("1") + gross_edge_pct / Decimal("100")) if amount_in > 0 else Decimal("0")
        estimated_net_out = amount_in * (Decimal("1") + reported_net_pct / Decimal("100")) if amount_in > 0 else Decimal("0")
        estimated_stress_out = amount_in * (Decimal("1") + stress_net_pct / Decimal("100")) if amount_in > 0 else Decimal("0")
        simulated_net_pct = ((simulated_out - amount_in) / amount_in * Decimal("100")) if simulated_out is not None and amount_in > 0 else None
        divergence_pct = (stress_net_pct - simulated_net_pct) if simulated_net_pct is not None else None
        output_delta_usdc = (simulated_out - amount_in) if simulated_out is not None and amount_in > 0 else None
        shortfall_to_required_usdc = (required_out - simulated_out) if simulated_out is not None and required_out > 0 else None
        near_pass_threshold_usdc = self._decimal(os.getenv("CRYPTOAI_NEAR_PASS_THRESHOLD_USDC", "0.001"))
        near_pass = bool(shortfall_to_required_usdc is not None and shortfall_to_required_usdc >= 0 and shortfall_to_required_usdc <= near_pass_threshold_usdc)

        findings: list[str] = []
        if simulated_net_pct is not None and simulated_net_pct < Decimal("0"):
            findings.append("Atomic eth_call shows the selected route loses money after real router execution.")
        if divergence_pct is not None and abs(divergence_pct) > Decimal("0.10"):
            findings.append("Opportunity stress estimate and atomic eth_call differ by more than 0.10 percentage points.")
        if selected.get("requested_notional_usd") and amount_in > 0 and self._decimal(selected.get("requested_notional_usd")) > amount_in:
            findings.append("Atomic simulation used live trade cap while opportunity evidence was assessed at a larger paper notional.")
        decoded_name = route.get("eth_call_decoded_error", {}).get("name") if isinstance(route.get("eth_call_decoded_error"), dict) else None
        if near_pass:
            findings.append(f"Near-pass route: shortfall to required output is <= {near_pass_threshold_usdc} USDC; keep monitoring but do not send unless eth_call passes.")
        if decoded_name == "ProfitTooLow":
            findings.append("Executor profit guard is working; do not send live until atomic eth_call passes.")
        if decoded_name == "RouterInsufficientOutputAmount":
            findings.append("A router leg reverted with INSUFFICIENT_OUTPUT_AMOUNT; route minOut/quote reconciliation must be conservative enough before live send.")

        if route.get("eth_call_status") == "PASS":
            status = "PASS"
        elif decoded_name == "RouterInsufficientOutputAmount":
            status = "ROUTER_INSUFFICIENT_OUTPUT_AMOUNT"
        elif simulated_net_pct is not None and simulated_net_pct < 0:
            status = "LOSS_AFTER_ATOMIC_SIMULATION"
        elif route.get("status") == "BLOCKED":
            status = "NO_ATOMIC_ROUTE"
        else:
            status = "PENDING_OR_PASS"

        return {
            "status": status,
            "amount_in_usdc": str(amount_in) if amount_in > 0 else None,
            "estimated_gross_out_usdc": self._fmt_decimal(estimated_gross_out),
            "estimated_net_out_usdc": self._fmt_decimal(estimated_net_out),
            "estimated_stress_out_usdc": self._fmt_decimal(estimated_stress_out),
            "simulated_atomic_out_usdc": str(simulated_out) if simulated_out is not None else None,
            "required_out_usdc": str(required_out) if required_out > 0 else None,
            "output_delta_usdc": str(output_delta_usdc) if output_delta_usdc is not None else None,
            "shortfall_to_required_usdc": str(shortfall_to_required_usdc) if shortfall_to_required_usdc is not None else None,
            "near_pass": near_pass,
            "near_pass_threshold_usdc": str(near_pass_threshold_usdc),
            "estimated_stress_net_pct": str(stress_net_pct),
            "simulated_atomic_net_pct": str(simulated_net_pct.quantize(Decimal("0.0001"))) if simulated_net_pct is not None else None,
            "stress_vs_atomic_divergence_pct": str(divergence_pct.quantize(Decimal("0.0001"))) if divergence_pct is not None else None,
            "findings": findings,
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
        if self._tiny_candidate_diagnostic_eligible({**row, "source_decision": source_decision, "realism_status": realism_status}):
            reasons.append("tiny-live eligible; exact atomic eth_call remains the final gate")
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
        candidate = self._candidate_from_intent(intent)
        if self._decimal(candidate.get("buy_price")) <= 0 or self._decimal(candidate.get("sell_price")) <= 0:
            candidate = tx_service._select_candidate(tx_service._read_json(self.report_dir / "execution_realism.json"))
        return tx_service._build_swap_legs(candidate, {**intent, "wallet_address": recipient, "deadline_seconds": str(max(1, deadline - int(time.time())))})

    def _atomic_executor_is_v2(self) -> bool:
        version = str(os.getenv("CRYPTOAI_ATOMIC_EXECUTOR_VERSION", "")).strip().lower()
        return version in {"v2", "2", "executor_v2"} or self._bool_env("CRYPTOAI_ATOMIC_PATCH_SELL_AMOUNT_IN", default=False)

    def _atomic_executor_abi(self) -> list[dict[str, Any]]:
        return ATOMIC_EXECUTOR_ABI_V2 if self._atomic_executor_is_v2() else ATOMIC_EXECUTOR_ABI_V1

    def _should_patch_sell_amount_in(self) -> bool:
        if not self._atomic_executor_is_v2():
            return False
        return self._bool_env("CRYPTOAI_ATOMIC_PATCH_SELL_AMOUNT_IN", default=True)

    def _sell_amount_in_offset(self, sell_leg: dict[str, Any]) -> int:
        """Return byte offset for amountIn in sell calldata, including 4-byte selector.

        V2 patches this word to the actual tokenMid balance after leg 1.
        Known router calldata layouts used by the current builder:
        - Uniswap V2 / Aerodrome swapExactTokensForTokens: amountIn at offset 4
        - Uniswap V3 Base router exactInputSingle flattened selector 0x04e45aaf: amountIn at offset 132
        """
        override = os.getenv("CRYPTOAI_ATOMIC_SELL_AMOUNT_IN_OFFSET", "").strip()
        if override:
            return max(0, int(override))

        router_type = str(sell_leg.get("router_type") or "").strip().lower()
        dex = str(sell_leg.get("dex") or "").strip().lower()
        calldata = str(sell_leg.get("calldata") or "")
        selector = calldata[:10].lower() if calldata.startswith("0x") else ""

        if router_type == "v3" or selector == "0x04e45aaf" or "uniswap v3" in dex:
            return 132
        # Uniswap V2 and Aerodrome in this project use V2-style swapExactTokensForTokens.
        return 4

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
            cache_key = f"base:{executor_address.lower()}"
            now = time.time()
            cached = self._executor_code_cache.get(cache_key)
            code_cache_ttl_seconds = max(0, self._int(os.getenv("CRYPTOAI_EXECUTOR_CODE_CACHE_TTL_SECONDS", "60")))
            if cached and code_cache_ttl_seconds > 0 and now - cached[0] <= code_cache_ttl_seconds:
                code_len = cached[1]
                code_cache_hit = True
            else:
                code_len = len(web3.eth.get_code(executor_address))
                self._executor_code_cache[cache_key] = (now, code_len)
                code_cache_hit = False
            balance_units = int(usdc.functions.balanceOf(wallet_address).call())
            allowance_units = int(usdc.functions.allowance(wallet_address, executor_address).call())
            required_units = self._int(route.get("amount_in_units"))
            return {
                "status": "READY" if code_len > 0 else "BLOCKED",
                "executor_address": executor_address,
                "wallet_address": wallet_address,
                "executor_code_bytes": code_len,
                "executor_code_cache_hit": code_cache_hit,
                "executor_code_cache_ttl_seconds": code_cache_ttl_seconds,
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
            self._check("two_leg_candidate_selected", bool(tx_sim.get("selected_candidate")), "ACTION", "A two-leg candidate must be selected; tiny mode may use WATCH/WATCH_ONLY but final eth_call must pass.", "A two-leg candidate is selected."),
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
        started_at = time.perf_counter()
        try:
            result = client.web3.eth.call(tx, block_identifier="latest")
            elapsed_ms = int((time.perf_counter() - started_at) * 1000)
            return {"status": "PASS", "rpc_url": self._redact_url(client.rpc_url_used), "block_number": int(client.web3.eth.block_number), "elapsed_ms": elapsed_ms, "result": result.hex()}
        except Exception as exc:
            elapsed_ms = int((time.perf_counter() - started_at) * 1000)
            message = f"{type(exc).__name__}: {exc}"
            return {"status": "REVERT" if "revert" in message.lower() else "FAIL", "elapsed_ms": elapsed_ms, "error": message[:500]}


    @staticmethod
    def _decode_executor_success(result: Any) -> dict[str, Any]:
        if not result:
            return {}
        try:
            if isinstance(result, (bytes, bytearray)):
                data = bytes(result)
            else:
                text = str(result)
                if text.startswith("0x"):
                    text = text[2:]
                data = bytes.fromhex(text)
            amount_out, profit = decode(["uint256", "uint256"], data)
            return {
                "amount_out_units": str(amount_out),
                "profit_units": str(profit),
                "amount_out_usdc": str(Decimal(amount_out) / Decimal(10**6)),
                "profit_usdc": str(Decimal(profit) / Decimal(10**6)),
            }
        except Exception:
            return {}

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
        revert_reason = AtomicArbitrageExecutionService._decode_nested_revert_reason(hex_payload)
        if revert_reason:
            name = "RouterRevert"
            if "INSUFFICIENT_OUTPUT_AMOUNT" in revert_reason:
                name = "RouterInsufficientOutputAmount"
            return {"name": name, "selector": selector, "reason": revert_reason, "raw": hex_payload}
        return {"selector": selector, "raw": hex_payload}

    @staticmethod
    def _decode_nested_revert_reason(hex_payload: str) -> str | None:
        # Some executor failures wrap the router's Error(string) payload inside
        # a custom error. Search for the standard Error(string) selector and
        # decode the trailing ABI payload when present.
        idx = hex_payload.lower().find("08c379a0")
        if idx < 0:
            return None
        try:
            payload = bytes.fromhex(hex_payload[idx + 8 :])
            (reason,) = decode(["string"], payload)
            return str(reason)
        except Exception:
            return None

    def _best_near_pass_attempt(self, attempts: list[dict[str, Any]]) -> dict[str, Any]:
        """Return the closest ProfitTooLow attempt for monitoring/alerting only.

        This never relaxes the executor guard. It helps distinguish a near miss
        from a route that is economically far away.
        """
        threshold = self._decimal(os.getenv("CRYPTOAI_NEAR_PASS_THRESHOLD_USDC", "0.001"))
        best: dict[str, Any] | None = None
        best_shortfall: Decimal | None = None
        for row in attempts:
            shortfall = self._decimal(row.get("shortfall_usdc"))
            if shortfall <= 0:
                continue
            if best_shortfall is None or shortfall < best_shortfall:
                best = row
                best_shortfall = shortfall
        if best is None or best_shortfall is None:
            return {"enabled": True, "found": False, "threshold_usdc": str(threshold)}
        return {
            "enabled": True,
            "found": best_shortfall <= threshold,
            "threshold_usdc": str(threshold),
            "best_shortfall_usdc": str(best_shortfall),
            "amount_in_usdc": best.get("amount_in_usdc"),
            "simulated_atomic_out_usdc": best.get("simulated_atomic_out_usdc"),
            "required_out_usdc": best.get("required_out_usdc"),
            "candidate": best.get("candidate", {}),
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
    def _valid_address(value: str) -> bool:
        try:
            Web3.to_checksum_address(value)
            return True
        except Exception:
            return False

    @staticmethod
    def _bool_env(key: str, default: bool = False) -> bool:
        raw = os.getenv(key)
        if raw is None:
            return default
        return raw.strip().lower() in {"1", "true", "yes", "on"}

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
    def _decimal_units(value: Any, decimals: int) -> Decimal:
        try:
            return Decimal(str(value or 0)) / Decimal(10**decimals)
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0")

    @staticmethod
    def _timestamp_seconds(value: Any) -> float:
        try:
            text = str(value or "")
            if not text:
                return 0.0
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            return datetime.fromisoformat(text).timestamp()
        except Exception:
            return 0.0

    @staticmethod
    def _int(value: Any) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _fmt_decimal(value: Decimal) -> str | None:
        if value <= 0:
            return None
        return str(value.quantize(Decimal("0.000001")))

    @staticmethod
    def _fmt(value: Any) -> str:
        """Format decimal-ish values for JSON reports/env-derived notional fields."""
        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            decimal_value = Decimal("0")
        if decimal_value == decimal_value.to_integral_value():
            return str(decimal_value.quantize(Decimal("1")))
        return format(decimal_value.normalize(), "f")

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
            f"- Profit reconciliation: `{payload.get('profit_reconciliation', {}).get('status', '-')}`",
            f"- Near pass: `{payload.get('profit_reconciliation', {}).get('near_pass', False)}`",
            f"- Generation elapsed ms: `{payload.get('performance_metrics', {}).get('generation_elapsed_ms', '-')}`",
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
                "## Profit Reconciliation",
                "",
                "```json",
                json.dumps(payload.get("profit_reconciliation", {}), indent=2),
                "```",
                "",
                "## Performance Metrics",
                "",
                "```json",
                json.dumps(payload.get("performance_metrics", {}), indent=2),
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
