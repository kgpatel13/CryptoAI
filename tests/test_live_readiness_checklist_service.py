from __future__ import annotations

import json
import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from app.execution.live_readiness_checklist_service import LiveReadinessChecklistService


class LiveReadinessChecklistServiceTests(unittest.TestCase):
    def test_live_parity_paper_profile_can_be_review_ready_without_live_approval(self) -> None:
        env = {
            "CRYPTOAI_LIVE_TRADING_ENABLED": "false",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": "true",
            "CRYPTOAI_MAX_LIVE_WALLET_USD": "500",
            "CRYPTOAI_MAX_LIVE_TRADE_USD": "50",
            "CRYPTOAI_MAX_DAILY_LOSS_USD": "10",
            "CRYPTOAI_TINY_LIVE_TRADE_CEILING_USD": "100",
            "CRYPTOAI_MIN_PAPER_CLOSED_TRADES": "30",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_ready_fixture(root, paper_trade_cap="50", paper_daily_loss="10", order_notional="50")

            with self._env(env):
                payload = LiveReadinessChecklistService(data_dir=root / "data", report_dir=root / "reports").generate()

        self.assertEqual(payload["overall_status"], "LIVE_REVIEW_READY")
        self.assertTrue(payload["live_review_ready"])
        self.assertFalse(payload["live_trading_approval"])
        self.assertEqual(payload["blocked_check_count"], 0)
        self.assertEqual(payload["action_count"], 0)

    def test_full_wallet_paper_trade_profile_fails_live_parity_checks(self) -> None:
        env = {
            "CRYPTOAI_LIVE_TRADING_ENABLED": "false",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": "true",
            "CRYPTOAI_MAX_LIVE_WALLET_USD": "500",
            "CRYPTOAI_MAX_LIVE_TRADE_USD": "50",
            "CRYPTOAI_MAX_DAILY_LOSS_USD": "10",
            "CRYPTOAI_TINY_LIVE_TRADE_CEILING_USD": "100",
            "CRYPTOAI_MIN_PAPER_CLOSED_TRADES": "30",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_ready_fixture(root, paper_trade_cap="500", paper_daily_loss="0", order_notional="500")

            with self._env(env):
                payload = LiveReadinessChecklistService(data_dir=root / "data", report_dir=root / "reports").generate()

        self.assertEqual(payload["overall_status"], "LIVE_REVIEW_NOT_READY")
        actions = {row["name"] for row in payload["checks"] if row["severity"] == "ACTION"}
        self.assertIn("paper_live_trade_cap_parity", actions)
        self.assertIn("paper_live_daily_loss_parity", actions)

    def _write_ready_fixture(self, root: Path, *, paper_trade_cap: str, paper_daily_loss: str, order_notional: str) -> None:
        data = root / "data"
        reports = root / "reports"
        data.mkdir()
        reports.mkdir()
        orders = [
            {
                "order_id": f"o{i}",
                "timestamp": "2026-06-30T00:00:00Z",
                "status": "CLOSED",
                "execution_type": "ARBITRAGE_ROUND_TRIP",
                "pair": "USDC/WETH",
                "notional_usd": order_notional,
                "realized_pnl_usd": "0.10",
            }
            for i in range(30)
        ]
        (data / "paper_orders.jsonl").write_text("\n".join(json.dumps(row) for row in orders) + "\n", encoding="utf-8")

        payloads = {
            "paper_report.json": {
                "filled_orders": 30,
                "risk_rejected_orders": 0,
                "pnl_reconciliation": {"status": "RECONCILED"},
                "latest_orders": orders[-3:],
            },
            "portfolio_analytics.json": {
                "pnl_reconciliation": {"status": "RECONCILED"},
                "open_positions": 0,
                "trade_journal": [{"order_id": "o1"}],
            },
            "paper_run_review.json": {
                "shadow_decision": "REVIEW_READY",
                "closed_trade_count": 30,
                "losing_trade_count": 0,
                "open_position_count": 0,
                "cash_usd": "503.0000",
                "realized_pnl_usd": "3.0000",
            },
            "execution_realism.json": {"shadow_ready_count": 1, "live_ready_count": 0},
            "execution_cost_evidence.json": {"confidence": "HIGH"},
            "provider_monitor.json": {"overall_status": "OK"},
            "report_audit.json": {"finding_count": 0, "blocking_finding_count": 0},
            "live_safety.json": {"overall_status": "LIVE_BLOCKED", "live_guard_allowed": False},
            "wallet_preflight.json": {"wallet_preflight_allowed": True},
            "paper_trading_settings.json": {
                "paper_profile": "live_parity_500",
                "settings": {
                    "paper_capital": {
                        "initial_capital_eth": "0.5",
                        "eth_reference_usd": "1000",
                        "max_notional_usd_per_trade": paper_trade_cap,
                    },
                    "risk": {
                        "max_open_positions": 1,
                        "duplicate_position_block": True,
                        "max_daily_loss_usd": paper_daily_loss,
                        "kill_switch_enabled": True,
                    },
                    "market_scope": {
                        "chains": ["base"],
                        "routes": ["WETH/USDC", "USDC/WETH"],
                        "dexes": ["Uniswap V3", "Aerodrome"],
                    },
                },
            },
        }
        for name, payload in payloads.items():
            (reports / name).write_text(json.dumps(payload), encoding="utf-8")

    @contextmanager
    def _env(self, values: dict[str, str]):
        keys = {
            "CRYPTOAI_PRIVATE_KEY",
            "CRYPTOAI_LIVE_TRADING_ENABLED",
            "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED",
            "CRYPTOAI_MAX_LIVE_WALLET_USD",
            "CRYPTOAI_MAX_LIVE_TRADE_USD",
            "CRYPTOAI_MAX_DAILY_LOSS_USD",
            "CRYPTOAI_TINY_LIVE_TRADE_CEILING_USD",
            "CRYPTOAI_MIN_PAPER_CLOSED_TRADES",
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
