from __future__ import annotations

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from app.config.feature_flags import FeatureFlags
from app.execution.live_guard import LiveTradingGuard


class LiveTradingGuardTests(unittest.TestCase):
    def test_default_like_flags_keep_live_trading_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            decision = LiveTradingGuard(self._flags(live_trading_enabled=False), report_dir=tmp).check()

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.max_trade_usd, Decimal("0"))
        self.assertTrue(any(check.name == "live_feature_flag" and not check.passed for check in decision.checks))
        self.assertTrue(any(check.name == "kill_switch" and not check.passed for check in decision.checks))

    def test_configured_runtime_still_blocks_without_paper_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            flags = self._configured_flags()
            decision = LiveTradingGuard(flags, report_dir=tmp).check()

        self.assertFalse(decision.allowed)
        self.assertIn("Paper run is not yet ready", decision.reason)
        self.assertTrue(any(check.name == "paper_shadow_review" and not check.passed for check in decision.checks))

    def test_tiny_pilot_can_pass_only_when_all_safety_and_evidence_gates_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_dir = Path(tmp)
            self._write_live_ready_reports(report_dir)

            decision = LiveTradingGuard(self._configured_flags(), report_dir=report_dir).check()

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.max_wallet_usd, Decimal("500"))
        self.assertEqual(decision.max_trade_usd, Decimal("50"))
        self.assertTrue(all(check.passed for check in decision.checks))

    def test_wallet_ceiling_above_500_blocks_tiny_live_pilot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_dir = Path(tmp)
            self._write_live_ready_reports(report_dir)
            flags = self._configured_flags(max_live_wallet_usd=Decimal("501"))

            decision = LiveTradingGuard(flags, report_dir=report_dir).check()

        self.assertFalse(decision.allowed)
        self.assertTrue(any(check.name == "wallet_ceiling" and not check.passed for check in decision.checks))

    def test_non_blocking_research_audit_findings_do_not_fail_live_guard_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_dir = Path(tmp)
            self._write_live_ready_reports(report_dir)
            (report_dir / "report_audit.json").write_text(
                json.dumps(
                    {
                        "finding_count": 5,
                        "blocking_finding_count": 0,
                        "operational_finding_count": 0,
                        "research_finding_count": 5,
                    }
                ),
                encoding="utf-8",
            )

            decision = LiveTradingGuard(self._configured_flags(), report_dir=report_dir).check()

        self.assertTrue(decision.allowed)
        self.assertTrue(any(check.name == "report_audit" and check.passed for check in decision.checks))

    def _configured_flags(self, **overrides) -> FeatureFlags:
        values = {
            "live_trading_enabled": True,
            "paper_trading_enabled": True,
            "max_live_trade_usd": Decimal("50"),
            "max_live_wallet_usd": Decimal("500"),
            "max_daily_loss_usd": Decimal("10"),
            "live_kill_switch_enabled": False,
            "require_manual_confirmation": False,
            "private_key_configured": True,
            "live_wallet_address": "0x1111111111111111111111111111111111111111",
            "main_wallet_address": "0x2222222222222222222222222222222222222222",
            "live_allowed_chains": ("base",),
            "live_allowed_dexes": ("Uniswap V2", "Uniswap V3", "Aerodrome"),
            "live_allowed_tokens": ("WETH", "USDC"),
            "require_transaction_simulation": True,
            "transaction_simulation_passed": True,
            "require_paper_evidence": True,
            "min_paper_closed_trades": 30,
            "min_execution_cost_confidence": "HIGH",
            "tiny_live_trade_ceiling_usd": Decimal("100"),
        }
        values.update(overrides)
        return FeatureFlags(**values)

    def _flags(self, **overrides) -> FeatureFlags:
        values = {
            "live_trading_enabled": False,
            "paper_trading_enabled": True,
            "max_live_trade_usd": Decimal("0"),
            "max_live_wallet_usd": Decimal("0"),
            "max_daily_loss_usd": Decimal("0"),
            "live_kill_switch_enabled": True,
            "require_manual_confirmation": True,
            "private_key_configured": False,
            "live_wallet_address": "",
            "main_wallet_address": "",
            "live_allowed_chains": ("base",),
            "live_allowed_dexes": ("Uniswap V2", "Uniswap V3", "Aerodrome"),
            "live_allowed_tokens": ("WETH", "USDC"),
            "require_transaction_simulation": True,
            "transaction_simulation_passed": False,
            "require_paper_evidence": True,
            "min_paper_closed_trades": 30,
            "min_execution_cost_confidence": "HIGH",
            "tiny_live_trade_ceiling_usd": Decimal("100"),
        }
        values.update(overrides)
        return FeatureFlags(**values)

    def _write_live_ready_reports(self, report_dir: Path) -> None:
        payloads = {
            "paper_run_review.json": {
                "shadow_decision": "REVIEW_READY",
                "closed_trade_count": 30,
            },
            "execution_cost_evidence.json": {
                "confidence": "HIGH",
                "paper_execution_evidence": {"sample_count": 30},
            },
            "report_audit.json": {"finding_count": 0},
            "provider_monitor.json": {"overall_status": "OK"},
            "execution_realism.json": {"shadow_ready_count": 1, "live_ready_count": 0},
        }
        for name, payload in payloads.items():
            (report_dir / name).write_text(json.dumps(payload), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
