from __future__ import annotations

import json
import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from app.execution.transaction_simulation_service import TransactionSimulationService


class TransactionSimulationServiceTests(unittest.TestCase):
    def test_valid_shadow_candidate_builds_intent_but_does_not_pass_without_eth_call(self) -> None:
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
                        }
                    ]
                },
            )

            with self._env(env):
                payload = TransactionSimulationService(data_dir=root / "data", report_dir=reports).generate()

        self.assertEqual(payload["overall_status"], "TX_SIMULATION_ACTION")
        self.assertFalse(payload["transaction_simulation_passed"])
        self.assertEqual(payload["blocked_check_count"], 0)
        action_names = {row["name"] for row in payload["checks"] if row["severity"] == "ACTION"}
        self.assertIn("exact_calldata_built", action_names)
        self.assertIn("eth_call_simulation_passed", action_names)
        self.assertEqual(payload["simulation_intent"]["calldata_status"], "NOT_IMPLEMENTED")
        self.assertEqual(payload["simulation_intent"]["notional_usd"], "50.0000")

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
            "CRYPTOAI_TINY_LIVE_TRADE_CEILING_USD",
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
