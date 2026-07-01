from __future__ import annotations

import os
import tempfile
import unittest
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from web3 import Web3

from app.execution.tiny_live_pilot_service import PilotPreparation, PreparedTx, TinyLivePilotService


class TinyLivePilotServiceTests(unittest.TestCase):
    def test_plan_mode_never_sends_and_does_not_require_swap_readiness(self) -> None:
        sent: list[dict] = []

        with tempfile.TemporaryDirectory() as tmp:
            service = TinyLivePilotService(
                data_dir=Path(tmp) / "data",
                report_dir=Path(tmp) / "reports",
                tx_sender=lambda tx, configured: sent.append(tx) or {"tx_hash": "0xabc"},
            )
            with patch.object(service, "_context", return_value=self._context(live_ready=False)):
                with patch.object(service, "_prepare", return_value=self._prepared()):
                    with self._env(self._base_env()):
                        payload = service.generate(mode="plan")

        self.assertFalse(payload["send_attempted"])
        self.assertEqual(sent, [])
        blockers = {row["name"] for row in payload["checks"] if row["severity"] == "BLOCK"}
        self.assertNotIn("live_readiness_ready", blockers)
        self.assertNotIn("transaction_simulation_passed", blockers)

    def test_approve_mode_sends_only_after_gates_and_confirmation(self) -> None:
        sent: list[dict] = []
        private_key = "0x" + "1" * 64
        wallet = Web3().eth.account.from_key(private_key).address
        env = {
            **self._base_env(),
            "CRYPTOAI_ENABLE_TINY_LIVE_PILOT": "true",
            "CRYPTOAI_LIVE_TRADING_ENABLED": "true",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": "false",
            "CRYPTOAI_PRIVATE_KEY": private_key,
            "CRYPTOAI_LIVE_WALLET_ADDRESS": wallet,
        }

        with tempfile.TemporaryDirectory() as tmp:
            service = TinyLivePilotService(
                data_dir=Path(tmp) / "data",
                report_dir=Path(tmp) / "reports",
                tx_sender=lambda tx, configured: sent.append(tx) or {"tx_hash": "0xabc", "receipt_status": 1},
            )
            with patch.object(service, "_context", return_value=self._context(live_ready=False)):
                with patch.object(service, "_prepare", return_value=self._prepared(wallet=wallet)):
                    with self._env(env):
                        payload = service.generate(mode="approve", confirm=TinyLivePilotService.CONFIRM_PHRASE)

        self.assertTrue(payload["send_attempted"])
        self.assertEqual(payload["overall_status"], "LIVE_PILOT_SENT")
        self.assertEqual(len(sent), 1)

    def test_swap_mode_requires_one_leg_smoke_acknowledgement(self) -> None:
        private_key = "0x" + "1" * 64
        wallet = Web3().eth.account.from_key(private_key).address
        env = {
            **self._base_env(),
            "CRYPTOAI_ENABLE_TINY_LIVE_PILOT": "true",
            "CRYPTOAI_LIVE_TRADING_ENABLED": "true",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": "false",
            "CRYPTOAI_PRIVATE_KEY": private_key,
            "CRYPTOAI_LIVE_WALLET_ADDRESS": wallet,
        }

        with tempfile.TemporaryDirectory() as tmp:
            service = TinyLivePilotService(data_dir=Path(tmp) / "data", report_dir=Path(tmp) / "reports")
            with patch.object(service, "_context", return_value=self._context(live_ready=True)):
                with patch.object(service, "_prepare", return_value=self._prepared(wallet=wallet, allowance=True)):
                    with self._env(env):
                        payload = service.generate(mode="swap", confirm=TinyLivePilotService.CONFIRM_PHRASE)

        self.assertFalse(payload["send_attempted"])
        blockers = {row["name"] for row in payload["checks"] if row["severity"] == "BLOCK"}
        self.assertIn("atomic_arbitrage_blocked", blockers)

    def test_swap_mode_can_send_after_smoke_simulation_without_full_arbitrage_readiness(self) -> None:
        sent: list[dict] = []
        private_key = "0x" + "1" * 64
        wallet = Web3().eth.account.from_key(private_key).address
        env = {
            **self._base_env(),
            "CRYPTOAI_ALLOW_ONE_LEG_SMOKE_SWAP": "true",
            "CRYPTOAI_ENABLE_TINY_LIVE_PILOT": "true",
            "CRYPTOAI_LIVE_TRADING_ENABLED": "true",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": "false",
            "CRYPTOAI_PRIVATE_KEY": private_key,
            "CRYPTOAI_LIVE_WALLET_ADDRESS": wallet,
        }
        context = self._context(live_ready=False)
        context["live_readiness"] = {"live_review_ready": False, "blocked_check_count": 0}
        context["transaction_simulation"] = {"transaction_simulation_passed": True}

        with tempfile.TemporaryDirectory() as tmp:
            service = TinyLivePilotService(
                data_dir=Path(tmp) / "data",
                report_dir=Path(tmp) / "reports",
                tx_sender=lambda tx, configured: sent.append(tx) or {"tx_hash": "0xabc", "receipt_status": 1},
            )
            with patch.object(service, "_context", return_value=context):
                with patch.object(service, "_prepare", return_value=self._prepared(wallet=wallet, allowance=True)):
                    with self._env(env):
                        payload = service.generate(mode="swap", confirm=TinyLivePilotService.CONFIRM_PHRASE)

        self.assertTrue(payload["send_attempted"])
        self.assertEqual(payload["overall_status"], "LIVE_PILOT_SENT")
        self.assertEqual(len(sent), 1)

    @staticmethod
    def _base_env() -> dict[str, str]:
        return {
            "CRYPTOAI_LIVE_TRADING_ENABLED": "false",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": "true",
            "CRYPTOAI_LIVE_WALLET_ADDRESS": "0x1111111111111111111111111111111111111111",
            "CRYPTOAI_MAX_LIVE_WALLET_USD": "500",
            "CRYPTOAI_MAX_LIVE_TRADE_USD": "20",
            "CRYPTOAI_MAX_DAILY_LOSS_USD": "5",
        }

    @staticmethod
    def _context(live_ready: bool) -> dict:
        return {
            "wallet_preflight": {"wallet_preflight_allowed": True},
            "live_readiness": {"live_review_ready": live_ready},
            "live_safety": {"overall_status": "LIVE_BLOCKED"},
            "transaction_simulation": {"transaction_simulation_passed": live_ready},
            "report_audit": {"blocking_finding_count": 0},
            "provider_monitor": {"overall_status": "OK"},
            "active_autopilot_processes": [],
        }

    @staticmethod
    def _prepared(wallet: str = "0x1111111111111111111111111111111111111111", allowance: bool = False) -> PilotPreparation:
        approval_tx = PreparedTx("approve", {"to": "0x2222222222222222222222222222222222222222"}, 20_000_000, "20")
        swap_tx = PreparedTx("swap", {"to": "0x3333333333333333333333333333333333333333"}, 20_000_000, "20")
        return PilotPreparation(
            smoke_usd=Decimal("20"),
            wallet_address=wallet,
            dex="Uniswap V3",
            router_address="0x3333333333333333333333333333333333333333",
            chain_id=8453,
            latest_block=1,
            usdc_balance_units=20_000_000,
            usdc_balance="20",
            eth_balance="0.01",
            allowance_units=20_000_000 if allowance else 0,
            allowance_sufficient=allowance,
            approval_tx=approval_tx,
            swap_tx=swap_tx,
        )

    @contextmanager
    def _env(self, values: dict[str, str]):
        keys = {
            "CRYPTOAI_ALLOW_ONE_LEG_SMOKE_SWAP",
            "CRYPTOAI_ENABLE_TINY_LIVE_PILOT",
            "CRYPTOAI_LIVE_TRADING_ENABLED",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED",
            "CRYPTOAI_PRIVATE_KEY",
            "CRYPTOAI_LIVE_WALLET_ADDRESS",
            "CRYPTOAI_MAX_LIVE_WALLET_USD",
            "CRYPTOAI_MAX_LIVE_TRADE_USD",
            "CRYPTOAI_MAX_DAILY_LOSS_USD",
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
