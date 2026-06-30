from __future__ import annotations

import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from app.execution.wallet_preflight_service import WalletPreflightService


class WalletPreflightServiceTests(unittest.TestCase):
    def test_default_preflight_is_action_only_without_wallet_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self._env({}):
                payload = WalletPreflightService(report_dir=Path(tmp)).generate()

        self.assertEqual(payload["overall_status"], "WALLET_PREP_ACTION")
        self.assertFalse(payload["live_trading_approval"])
        self.assertEqual(payload["planned_total_usd"], "500.0000")
        self.assertTrue(any(row["name"] == "isolated_wallet_address" and row["severity"] == "ACTION" for row in payload["checks"]))

    def test_completed_public_wallet_preflight_can_be_ready_without_private_key(self) -> None:
        env = {
            "CRYPTOAI_LIVE_WALLET_ADDRESS": "0x1111111111111111111111111111111111111111",
            "CRYPTOAI_MAIN_WALLET_ADDRESS": "0x2222222222222222222222222222222222222222",
            "CRYPTOAI_MAX_LIVE_WALLET_USD": "500",
            "CRYPTOAI_MAX_LIVE_TRADE_USD": "50",
            "CRYPTOAI_MAX_DAILY_LOSS_USD": "10",
            "CRYPTOAI_PLANNED_LIVE_CHAIN": "base",
            "CRYPTOAI_PLANNED_LIVE_USDC_USD": "450",
            "CRYPTOAI_PLANNED_LIVE_ETH_GAS_USD": "50",
            "CRYPTOAI_LIVE_TRADING_ENABLED": "false",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": "true",
            "CRYPTOAI_REQUIRE_MANUAL_CONFIRMATION": "true",
            "CRYPTOAI_REQUIRE_TX_SIMULATION": "true",
        }
        with tempfile.TemporaryDirectory() as tmp:
            with self._env(env):
                payload = WalletPreflightService(report_dir=Path(tmp)).generate()

        self.assertEqual(payload["overall_status"], "WALLET_PREP_READY")
        self.assertTrue(payload["wallet_preflight_allowed"])
        self.assertFalse(payload["live_trading_approval"])
        self.assertFalse(payload["private_key_configured"])
        self.assertEqual(payload["blocked_check_count"], 0)
        self.assertEqual(payload["action_count"], 0)

    def test_private_key_or_live_enabled_blocks_preflight(self) -> None:
        env = {
            "CRYPTOAI_PRIVATE_KEY": "not-a-real-key",
            "CRYPTOAI_LIVE_TRADING_ENABLED": "true",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": "false",
            "CRYPTOAI_LIVE_WALLET_ADDRESS": "0x1111111111111111111111111111111111111111",
            "CRYPTOAI_MAIN_WALLET_ADDRESS": "0x2222222222222222222222222222222222222222",
            "CRYPTOAI_MAX_LIVE_WALLET_USD": "500",
            "CRYPTOAI_MAX_LIVE_TRADE_USD": "50",
            "CRYPTOAI_MAX_DAILY_LOSS_USD": "10",
        }
        with tempfile.TemporaryDirectory() as tmp:
            with self._env(env):
                payload = WalletPreflightService(report_dir=Path(tmp)).generate()

        self.assertEqual(payload["overall_status"], "WALLET_PREP_ACTION")
        blockers = {row["name"] for row in payload["checks"] if row["severity"] == "BLOCK"}
        self.assertIn("live_trading_disabled", blockers)
        self.assertIn("kill_switch_enabled", blockers)
        self.assertIn("private_key_absent", blockers)

    @contextmanager
    def _env(self, values: dict[str, str]):
        keys = {
            "CRYPTOAI_PRIVATE_KEY",
            "CRYPTOAI_LIVE_TRADING_ENABLED",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED",
            "CRYPTOAI_LIVE_WALLET_ADDRESS",
            "CRYPTOAI_MAIN_WALLET_ADDRESS",
            "CRYPTOAI_MAX_LIVE_WALLET_USD",
            "CRYPTOAI_MAX_LIVE_TRADE_USD",
            "CRYPTOAI_MAX_DAILY_LOSS_USD",
            "CRYPTOAI_PLANNED_LIVE_CHAIN",
            "CRYPTOAI_PLANNED_LIVE_USDC_USD",
            "CRYPTOAI_PLANNED_LIVE_ETH_GAS_USD",
            "CRYPTOAI_REQUIRE_MANUAL_CONFIRMATION",
            "CRYPTOAI_REQUIRE_TX_SIMULATION",
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
