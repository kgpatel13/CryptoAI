from __future__ import annotations

import json
import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from app.execution.atomic_arbitrage_execution_service import AtomicArbitrageExecutionService


class AtomicArbitrageExecutionServiceTests(unittest.TestCase):
    def test_builds_executor_calldata_and_passes_mocked_eth_call(self) -> None:
        env = {
            "CRYPTOAI_LIVE_TRADING_ENABLED": "false",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": "true",
            "CRYPTOAI_LIVE_WALLET_ADDRESS": "0x1111111111111111111111111111111111111111",
            "CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS": "0x2222222222222222222222222222222222222222",
            "CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED": "true",
            "CRYPTOAI_MAX_LIVE_TRADE_USD": "20",
            "CRYPTOAI_TINY_LIVE_TRADE_CEILING_USD": "100",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            self._write_base_reports(reports)

            with self._env(env):
                service = AtomicArbitrageExecutionService(
                    data_dir=root / "data",
                    report_dir=reports,
                    eth_call_runner=lambda tx, chain: {"status": "PASS", "chain": chain, "tx_to": tx["to"]},
                )
                with patch.object(service, "_executor_preflight", return_value={"status": "READY", "executor_code_bytes": 1, "allowance_sufficient": True}):
                    payload = service.generate()

        self.assertEqual(payload["overall_status"], "ATOMIC_ROUTE_SIMULATION_PASSED")
        self.assertTrue(payload["atomic_route_simulation_passed"])
        self.assertEqual(payload["route_diagnostics"]["blocker_type"], "ATOMIC_BUILDER_OR_ETH_CALL")
        self.assertEqual(payload["route_diagnostics"]["shadow_ready_count"], 1)
        route = payload["atomic_route"]
        self.assertEqual(route["executor_address"], "0x2222222222222222222222222222222222222222")
        self.assertTrue(route["calldata"].startswith("0x"))
        self.assertEqual(route["approval_spender"], "0x2222222222222222222222222222222222222222")
        self.assertEqual(len(route["swap_legs"]), 2)
        self.assertEqual(route["swap_legs"][0]["eth_call"]["from"], route["executor_address"])

    def test_blocks_one_leg_smoke_route(self) -> None:
        env = {
            "CRYPTOAI_LIVE_WALLET_ADDRESS": "0x1111111111111111111111111111111111111111",
            "CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS": "0x2222222222222222222222222222222222222222",
            "CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED": "true",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "transaction_simulation.json").write_text(
                json.dumps(
                    {
                        "transaction_simulation_passed": True,
                        "simulation_intent": {"simulation_type": "TINY_LIVE_SMOKE", "swap_legs": [{}]},
                    }
                ),
                encoding="utf-8",
            )
            with self._env(env):
                service = AtomicArbitrageExecutionService(
                    data_dir=root / "data",
                    report_dir=reports,
                    refresh_transaction_simulation=False,
                )
                with patch.object(service, "_executor_preflight", return_value={"status": "READY", "executor_code_bytes": 1, "allowance_sufficient": False}):
                    payload = service.generate()

        self.assertEqual(payload["overall_status"], "ATOMIC_ROUTE_ACTION")
        self.assertFalse(payload["atomic_route_simulation_passed"])
        self.assertEqual(payload["route_diagnostics"]["blocker_type"], "NO_TWO_LEG_CANDIDATE")

    def test_diagnostics_explain_watch_only_market_blocker(self) -> None:
        env = {
            "CRYPTOAI_LIVE_WALLET_ADDRESS": "0x1111111111111111111111111111111111111111",
            "CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS": "0x2222222222222222222222222222222222222222",
            "CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED": "true",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "transaction_simulation.json").write_text(
                json.dumps(
                    {
                        "overall_status": "TX_SIMULATION_ACTION",
                        "transaction_simulation_passed": False,
                        "selected_candidate": {},
                        "simulation_intent": {"simulation_type": "TINY_LIVE_SMOKE", "swap_legs": [{}]},
                        "checks": [{"name": "eth_call_simulation_passed", "passed": False, "severity": "ACTION", "detail": "Base eth_call simulation has not passed yet."}],
                    }
                ),
                encoding="utf-8",
            )
            (reports / "execution_realism.json").write_text(
                json.dumps(
                    {
                        "opportunities": [
                            {
                                "timestamp": "now",
                                "chain": "base",
                                "pair": "WETH/USDC",
                                "buy_source": "Uniswap V2",
                                "sell_source": "Uniswap V3",
                                "source_decision": "WATCH",
                                "realism_status": "WATCH_ONLY",
                                "gross_edge_pct": "0.40",
                                "reported_net_edge_pct": "0.10",
                                "stress_net_edge_pct": "0.02",
                                "confidence": "MEDIUM",
                                "reason": "Below BUY threshold.",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with self._env(env):
                service = AtomicArbitrageExecutionService(
                    data_dir=root / "data",
                    report_dir=reports,
                    refresh_transaction_simulation=False,
                )
                with patch.object(service, "_executor_preflight", return_value={"status": "READY", "executor_code_bytes": 1, "allowance_sufficient": False}):
                    payload = service.generate()

        diagnostics = payload["route_diagnostics"]
        self.assertEqual(diagnostics["blocker_type"], "NO_TWO_LEG_CANDIDATE")
        self.assertEqual(diagnostics["latest_diagnostics_count"], 1)
        self.assertIn("source_decision is WATCH", diagnostics["latest_opportunities"][0]["diagnostic_reasons"][0])

    def test_decodes_profit_too_low_custom_error(self) -> None:
        decoded = AtomicArbitrageExecutionService._decode_executor_error(
            "ContractCustomError: ('0x88215f9c00000000000000000000000000000000000000000000000000000000012eabb40000000000000000000000000000000000000000000000000000000001315410')"
        )

        self.assertEqual(decoded["name"], "ProfitTooLow")
        self.assertEqual(decoded["amount_out_usdc"], "19.835828")
        self.assertEqual(decoded["required_out_usdc"], "20.01")
        self.assertEqual(decoded["shortfall_usdc"], "0.174172")

    def test_profit_reconciliation_compares_estimate_to_atomic_result(self) -> None:
        service = AtomicArbitrageExecutionService()
        diagnostics = {
            "selected_candidate": {
                "gross_edge_pct": "0.6981",
                "reported_net_edge_pct": "0.3981",
                "stress_net_edge_pct": "0.3268",
                "requested_notional_usd": "500.0000",
            }
        }
        route = {
            "amount_in_units": "19000000",
            "eth_call_decoded_error": {
                "name": "ProfitTooLow",
                "amount_out_usdc": "18.820366",
                "required_out_usdc": "19.0095",
            },
        }

        result = service._profit_reconciliation(diagnostics=diagnostics, route=route)

        self.assertEqual(result["status"], "LOSS_AFTER_ATOMIC_SIMULATION")
        self.assertEqual(result["amount_in_usdc"], "19")
        self.assertEqual(result["simulated_atomic_net_pct"], "-0.9454")
        self.assertIn("Executor profit guard is working", " ".join(result["findings"]))

    @staticmethod
    def _write_base_reports(reports: Path) -> None:
        (reports / "wallet_preflight.json").write_text(json.dumps({"wallet_preflight_allowed": True}), encoding="utf-8")
        (reports / "live_readiness_checklist.json").write_text(json.dumps({"live_review_ready": True}), encoding="utf-8")
        (reports / "execution_realism.json").write_text(
            json.dumps(
                {
                    "opportunities": [
                        {
                            "chain": "base",
                            "pair": "WETH/USDC",
                            "buy_source": "Aerodrome",
                            "sell_source": "Uniswap V3",
                            "source_decision": "BUY",
                            "realism_status": "SHADOW_READY",
                            "requested_notional_usd": "20",
                            "buy_price": "2500",
                            "sell_price": "2510",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

    @contextmanager
    def _env(self, values: dict[str, str]):
        keys = {
            "CRYPTOAI_LIVE_TRADING_ENABLED",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED",
            "CRYPTOAI_LIVE_WALLET_ADDRESS",
            "CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS",
            "CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED",
            "CRYPTOAI_MAX_LIVE_TRADE_USD",
            "CRYPTOAI_TINY_LIVE_TRADE_CEILING_USD",
            "CRYPTOAI_PRIVATE_KEY",
        }
        previous = {key: os.environ.get(key) for key in keys}
        try:
            for key in keys:
                os.environ.pop(key, None)
            os.environ.update(values)
            yield
        finally:
            for key in keys:
                os.environ.pop(key, None)
                if previous[key] is not None:
                    os.environ[key] = previous[key]


if __name__ == "__main__":
    unittest.main()
