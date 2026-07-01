from __future__ import annotations

import json
import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from app.execution.transaction_simulation_service import TransactionSimulationService


class TransactionSimulationServiceTests(unittest.TestCase):
    def test_valid_shadow_candidate_builds_exact_calldata_and_passes_mocked_eth_call(self) -> None:
        env = {
            "CRYPTOAI_LIVE_TRADING_ENABLED": "false",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": "true",
            "CRYPTOAI_LIVE_WALLET_ADDRESS": "0x1111111111111111111111111111111111111111",
            "CRYPTOAI_MAX_LIVE_TRADE_USD": "50",
            "CRYPTOAI_TINY_LIVE_TRADE_CEILING_USD": "100",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            self._write_json(reports / "wallet_preflight.json", {"wallet_preflight_allowed": True})
            self._write_json(reports / "live_readiness_checklist.json", {"live_review_ready": True})
            self._write_json(
                reports / "execution_realism.json",
                {
                    "opportunities": [
                        {
                            "chain": "base",
                            "pair": "WETH/USDC",
                            "buy_source": "Aerodrome",
                            "sell_source": "Uniswap V3",
                            "source_decision": "BUY",
                            "realism_status": "SHADOW_READY",
                            "requested_notional_usd": "50",
                            "buy_price": "2500",
                            "sell_price": "2510",
                        }
                    ]
                },
            )

            with self._env(env):
                payload = TransactionSimulationService(
                    data_dir=root / "data",
                    report_dir=reports,
                    eth_call_runner=lambda tx, chain: {
                        "status": "PASS",
                        "chain_id": 8453,
                        "block_number": 123,
                        "result": "0x",
                        "tx_to": tx["to"],
                    },
                ).generate()

        self.assertEqual(payload["overall_status"], "TX_SIMULATION_READY")
        self.assertTrue(payload["transaction_simulation_passed"])
        self.assertEqual(payload["blocked_check_count"], 0)
        self.assertEqual(payload["action_count"], 0)
        self.assertEqual(payload["simulation_intent"]["calldata_status"], "BUILT")
        self.assertEqual(payload["simulation_intent"]["eth_call_status"], "PASS")
        self.assertEqual(payload["simulation_intent"]["notional_usd"], "50.0000")
        legs = payload["simulation_intent"]["swap_legs"]
        self.assertEqual(len(legs), 2)
        self.assertEqual(legs[0]["dex"], "Aerodrome")
        self.assertEqual(legs[0]["router_type"], "solidly")
        self.assertTrue(legs[0]["calldata"].startswith("0xcac88ea9"))
        self.assertEqual(legs[1]["dex"], "Uniswap V3")
        self.assertEqual(legs[1]["router_type"], "v3")
        self.assertTrue(legs[1]["calldata"].startswith("0x04e45aaf"))
        self.assertEqual(legs[0]["amount_in_units"], "50000000")

    def test_eth_call_revert_keeps_report_actionable_not_passed(self) -> None:
        env = {
            "CRYPTOAI_LIVE_TRADING_ENABLED": "false",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": "true",
            "CRYPTOAI_LIVE_WALLET_ADDRESS": "0x1111111111111111111111111111111111111111",
            "CRYPTOAI_MAX_LIVE_TRADE_USD": "50",
            "CRYPTOAI_TINY_LIVE_TRADE_CEILING_USD": "100",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            self._write_json(reports / "wallet_preflight.json", {"wallet_preflight_allowed": True})
            self._write_json(reports / "live_readiness_checklist.json", {"live_review_ready": True})
            self._write_json(
                reports / "execution_realism.json",
                {
                    "opportunities": [
                        {
                            "chain": "base",
                            "pair": "WETH/USDC",
                            "buy_source": "Aerodrome",
                            "sell_source": "Uniswap V3",
                            "source_decision": "BUY",
                            "realism_status": "SHADOW_READY",
                            "requested_notional_usd": "50",
                            "buy_price": "2500",
                            "sell_price": "2510",
                        }
                    ]
                },
            )

            with self._env(env):
                payload = TransactionSimulationService(
                    data_dir=root / "data",
                    report_dir=reports,
                    eth_call_runner=lambda tx, chain: {"status": "REVERT", "error": "execution reverted"},
                ).generate()

        self.assertEqual(payload["overall_status"], "TX_SIMULATION_ACTION")
        self.assertFalse(payload["transaction_simulation_passed"])
        self.assertEqual(payload["simulation_intent"]["calldata_status"], "BUILT")
        self.assertEqual(payload["simulation_intent"]["eth_call_status"], "REVERT")
        action_names = {row["name"] for row in payload["checks"] if row["severity"] == "ACTION"}
        self.assertIn("eth_call_simulation_passed", action_names)

    def test_uniswap_v2_to_v3_shadow_candidate_builds_two_leg_route(self) -> None:
        env = {
            "CRYPTOAI_LIVE_TRADING_ENABLED": "false",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": "true",
            "CRYPTOAI_LIVE_WALLET_ADDRESS": "0x1111111111111111111111111111111111111111",
            "CRYPTOAI_MAX_LIVE_TRADE_USD": "20",
            "CRYPTOAI_TINY_LIVE_SMOKE_USD": "20",
            "CRYPTOAI_TINY_LIVE_TRADE_CEILING_USD": "100",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            self._write_json(reports / "wallet_preflight.json", {"wallet_preflight_allowed": True})
            self._write_json(reports / "live_readiness_checklist.json", {"blocked_check_count": 0, "live_review_ready": False})
            self._write_json(
                reports / "execution_realism.json",
                {
                    "opportunities": [
                        {
                            "chain": "base",
                            "pair": "USDC/WETH",
                            "buy_source": "Uniswap V2",
                            "sell_source": "Uniswap V3",
                            "source_decision": "BUY",
                            "realism_status": "SHADOW_READY",
                            "requested_notional_usd": "500",
                            "buy_price": "0.0006",
                            "sell_price": "0.0007",
                        }
                    ]
                },
            )

            with self._env(env):
                payload = TransactionSimulationService(
                    data_dir=root / "data",
                    report_dir=reports,
                    eth_call_runner=lambda tx, chain: {
                        "status": "PASS",
                        "chain_id": 8453,
                        "block_number": 123,
                        "result": "0x",
                    },
                ).generate()

        self.assertEqual(payload["overall_status"], "TX_SIMULATION_READY")
        self.assertTrue(payload["transaction_simulation_passed"])
        self.assertNotEqual(payload["simulation_intent"].get("simulation_type"), "TINY_LIVE_SMOKE")
        self.assertEqual(payload["simulation_intent"]["notional_usd"], "20.0000")
        legs = payload["simulation_intent"]["swap_legs"]
        self.assertEqual(len(legs), 2)
        self.assertEqual(legs[0]["dex"], "Uniswap V2")
        self.assertEqual(legs[0]["router_type"], "v2")
        self.assertEqual(legs[1]["dex"], "Uniswap V3")

    def test_missing_shadow_candidate_is_actionable_not_passed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            self._write_json(reports / "execution_realism.json", {"opportunities": []})

            with self._env({"CRYPTOAI_LIVE_TRADING_ENABLED": "false", "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": "true"}):
                payload = TransactionSimulationService(data_dir=root / "data", report_dir=reports).generate()

        self.assertEqual(payload["overall_status"], "TX_SIMULATION_ACTION")
        self.assertFalse(payload["transaction_simulation_passed"])
        self.assertEqual(payload["simulation_intent"]["status"], "NO_CANDIDATE")
        self.assertTrue(any(row["name"] == "shadow_candidate_available" and row["severity"] == "ACTION" for row in payload["checks"]))


    def test_select_candidate_prefers_freshest_highest_stress_edge(self) -> None:
        service = TransactionSimulationService()
        realism = {
            "opportunities": [
                {
                    "timestamp": "2026-01-01T00:00:00Z",
                    "chain": "base",
                    "pair": "USDC/WETH",
                    "buy_source": "Uniswap V2",
                    "sell_source": "Uniswap V3",
                    "source_decision": "BUY",
                    "realism_status": "SHADOW_READY",
                    "stress_net_edge_pct": "9.0000",
                    "reported_net_edge_pct": "9.0000",
                    "buy_price": "0.0006",
                    "sell_price": "0.0007",
                },
                {
                    "timestamp": "2099-01-01T00:00:00Z",
                    "chain": "base",
                    "pair": "USDC/WETH",
                    "buy_source": "Uniswap V2",
                    "sell_source": "Uniswap V3",
                    "source_decision": "BUY",
                    "realism_status": "SHADOW_READY",
                    "stress_net_edge_pct": "0.5000",
                    "reported_net_edge_pct": "0.5000",
                    "buy_price": "0.0006",
                    "sell_price": "0.0007",
                },
            ]
        }

        with self._env({"CRYPTOAI_ATOMIC_MAX_CANDIDATE_AGE_SECONDS": "45"}):
            selected = service._select_candidate(realism)

        self.assertEqual(selected["stress_net_edge_pct"], "0.5000")

    @staticmethod
    def _write_json(path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload), encoding="utf-8")

    @contextmanager
    def _env(self, values: dict[str, str]):
        keys = {
            "CRYPTOAI_PRIVATE_KEY",
            "CRYPTOAI_LIVE_TRADING_ENABLED",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED",
            "CRYPTOAI_LIVE_WALLET_ADDRESS",
            "CRYPTOAI_MAX_LIVE_TRADE_USD",
            "CRYPTOAI_TINY_LIVE_SMOKE_USD",
            "CRYPTOAI_TINY_LIVE_TRADE_CEILING_USD",
            "CRYPTOAI_ATOMIC_MAX_CANDIDATE_AGE_SECONDS",
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
