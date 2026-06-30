from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.operations.paper_settings_service import PaperSettingsService


class PaperSettingsServiceTests(unittest.TestCase):
    def test_defaults_are_valid_and_generate_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            service = PaperSettingsService(
                settings_path=root / "config" / "paper_trading_settings.json",
                report_dir=root / "reports",
            )

            settings = service.save()
            payload = service.generate_report(settings)

            self.assertEqual(payload["status"], "VALID")
            self.assertEqual(payload["paper_capital_usd"], "3500.00")
            self.assertEqual(payload["settings"]["paper_capital"]["initial_capital_eth"], "1.0")
            self.assertIn("Uniswap V3", payload["settings"]["market_scope"]["dexes"])
            self.assertFalse(payload["settings"]["live_trading_enabled"])
            self.assertTrue((root / "reports" / "paper_trading_settings.json").exists())
            self.assertTrue((root / "reports" / "paper_trading_settings.md").exists())

            saved = json.loads((root / "config" / "paper_trading_settings.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["opportunity"]["production_cost_buffer_pct"], "0.30")

    def test_rejects_live_trading_flag(self) -> None:
        service = PaperSettingsService(settings_path="missing.json", report_dir="reports")
        settings = service.defaults()
        settings["live_trading_enabled"] = True

        payload = service.validate(settings)

        self.assertEqual(payload["status"], "INVALID")
        self.assertIn("Live trading must remain disabled.", [row["message"] for row in payload["findings"]])

    def test_rejects_lower_production_buffer_and_buy_threshold(self) -> None:
        service = PaperSettingsService(settings_path="missing.json", report_dir="reports")
        settings = service.defaults()
        settings["opportunity"]["production_cost_buffer_pct"] = "0.20"
        settings["opportunity"]["paper_buy_threshold_pct"] = "0.20"

        payload = service.validate(settings)

        messages = [row["message"] for row in payload["findings"]]
        self.assertEqual(payload["status"], "INVALID")
        self.assertIn("Production cost buffer cannot be below 0.30%.", messages)
        self.assertIn("Paper BUY threshold cannot be below 0.30%.", messages)

    def test_warns_when_trade_size_exceeds_ten_percent_of_paper_capital(self) -> None:
        service = PaperSettingsService(settings_path="missing.json", report_dir="reports")
        settings = service.defaults()
        settings["paper_capital"]["max_notional_usd_per_trade"] = "500"

        payload = service.validate(settings)

        self.assertEqual(payload["status"], "VALID")
        self.assertEqual(payload["warning_count"], 1)
        self.assertIn("above 10%", payload["findings"][0]["message"])

    def test_rejects_expansion_outside_base_eth_scope(self) -> None:
        service = PaperSettingsService(settings_path="missing.json", report_dir="reports")
        settings = service.defaults()
        settings["market_scope"]["chains"] = ["base", "ethereum"]
        settings["market_scope"]["routes"] = ["WETH/USDC", "WBTC/USDC"]

        payload = service.validate(settings)

        messages = [row["message"] for row in payload["findings"]]
        self.assertEqual(payload["status"], "INVALID")
        self.assertIn("Only Base is enabled for the first paper launch profile.", messages)
        self.assertIn("Only WETH/USDC and USDC/WETH are enabled for the Base ETH paper profile.", messages)

    def test_aggressive_paper_profile_exports_runtime_environment(self) -> None:
        service = PaperSettingsService(settings_path="missing.json", report_dir="reports")
        settings = service.defaults()
        settings["paper_profile"] = "aggressive_paper"
        settings["operations"]["loop_interval_seconds"] = 30
        settings["paper_capital"]["eth_reference_usd"] = "10000"
        settings["paper_capital"]["max_notional_usd_per_trade"] = "1000"
        settings["paper_capital"]["max_daily_paper_trades"] = 200
        settings["risk"]["cooldown_seconds"] = 60
        settings["risk"]["max_daily_loss_usd"] = "500"

        payload = service.validate(settings)
        env = payload["runtime_environment"]

        self.assertEqual(payload["status"], "VALID")
        self.assertEqual(payload["paper_capital_usd"], "10000.00")
        self.assertEqual(env["CRYPTOAI_PAPER_INITIAL_CASH_USD"], "10000.00")
        self.assertEqual(env["CRYPTOAI_MAX_PAPER_NOTIONAL_USD"], "1000")
        self.assertEqual(env["CRYPTOAI_DEFAULT_PAPER_NOTIONAL_USD"], "1000")
        self.assertEqual(env["CRYPTOAI_PAPER_RISK_PER_TRADE_PCT"], "10.00")
        self.assertEqual(env["CRYPTOAI_PAPER_MAX_CASH_USAGE_PCT"], "10.00")
        self.assertEqual(env["CRYPTOAI_MAX_DAILY_PAPER_TRADES"], "200")
        self.assertEqual(env["CRYPTOAI_TRADE_COOLDOWN_SECONDS"], "60")
        self.assertEqual(env["CRYPTOAI_MIN_EDGE_FOR_PAPER_PCT"], "0.30")

    def test_unbounded_paper_lab_allows_zero_limits_and_large_capital(self) -> None:
        service = PaperSettingsService(settings_path="missing.json", report_dir="reports")
        settings = service.defaults()
        settings["paper_profile"] = "unbounded_paper_lab"
        settings["operations"]["loop_interval_seconds"] = 0
        settings["paper_capital"]["initial_capital_eth"] = "10.0"
        settings["paper_capital"]["eth_reference_usd"] = "10000"
        settings["paper_capital"]["max_notional_usd_per_trade"] = "100000"
        settings["paper_capital"]["max_daily_paper_trades"] = 0
        settings["paper_capital"]["sizing_mode"] = "full_available_cash"
        settings["risk"]["max_open_positions"] = 1
        settings["risk"]["duplicate_position_block"] = True
        settings["risk"]["cooldown_seconds"] = 0
        settings["risk"]["max_daily_loss_usd"] = "0"
        settings["evidence_gates"]["require_report_audit_clean"] = False
        settings["evidence_gates"]["require_provider_not_critical"] = False

        payload = service.validate(settings)
        env = payload["runtime_environment"]

        self.assertEqual(payload["status"], "VALID")
        self.assertEqual(payload["warning_count"], 0)
        self.assertEqual(payload["paper_capital_usd"], "100000.00")
        self.assertEqual(env["CRYPTOAI_MAX_PAPER_NOTIONAL_USD"], "100000")
        self.assertEqual(env["CRYPTOAI_PAPER_RISK_PER_TRADE_PCT"], "100.00")
        self.assertEqual(env["CRYPTOAI_PAPER_MAX_CASH_USAGE_PCT"], "100.00")
        self.assertEqual(env["CRYPTOAI_PAPER_SIZING_MODE"], "full_available_cash")
        self.assertEqual(env["CRYPTOAI_MAX_DAILY_PAPER_TRADES"], "0")
        self.assertEqual(env["CRYPTOAI_MAX_OPEN_POSITIONS"], "1")
        self.assertEqual(env["CRYPTOAI_TRADE_COOLDOWN_SECONDS"], "0")
        self.assertEqual(env["CRYPTOAI_DUPLICATE_SIGNAL_WINDOW_SECONDS"], "0")
        self.assertEqual(env["CRYPTOAI_BLOCK_SAME_PAIR_OPEN_POSITION"], "true")
        self.assertEqual(env["CRYPTOAI_MAX_DAILY_LOSS_USD"], "0")

    def test_shadow_500_profile_exports_production_like_paper_environment(self) -> None:
        service = PaperSettingsService(settings_path="missing.json", report_dir="reports")
        settings = service.defaults()
        settings["paper_profile"] = "shadow_500"
        settings["operations"]["loop_interval_seconds"] = 0
        settings["paper_capital"]["initial_capital_eth"] = "0.5"
        settings["paper_capital"]["eth_reference_usd"] = "1000"
        settings["paper_capital"]["max_notional_usd_per_trade"] = "500"
        settings["paper_capital"]["max_daily_paper_trades"] = 0
        settings["paper_capital"]["sizing_mode"] = "full_available_cash"
        settings["risk"]["max_open_positions"] = 1
        settings["risk"]["cooldown_seconds"] = 0
        settings["risk"]["max_daily_loss_usd"] = "0"
        settings["evidence_gates"]["require_report_audit_clean"] = False
        settings["evidence_gates"]["require_provider_not_critical"] = False

        payload = service.validate(settings)
        env = payload["runtime_environment"]

        self.assertEqual(payload["status"], "VALID")
        self.assertEqual(payload["paper_capital_usd"], "500.00")
        self.assertEqual(env["CRYPTOAI_PAPER_INITIAL_CASH_USD"], "500.00")
        self.assertEqual(env["CRYPTOAI_MAX_PAPER_NOTIONAL_USD"], "500")
        self.assertEqual(env["CRYPTOAI_PAPER_RISK_PER_TRADE_PCT"], "100.00")
        self.assertEqual(env["CRYPTOAI_PAPER_SIZING_MODE"], "full_available_cash")

    def test_live_parity_500_profile_exports_tiny_live_like_limits(self) -> None:
        service = PaperSettingsService(settings_path="missing.json", report_dir="reports")
        settings = service.live_parity_500_profile()

        payload = service.validate(settings)
        env = payload["runtime_environment"]

        self.assertEqual(payload["status"], "VALID")
        self.assertEqual(payload["paper_capital_usd"], "500.00")
        self.assertEqual(settings["paper_profile"], "live_parity_500")
        self.assertEqual(env["CRYPTOAI_PAPER_INITIAL_CASH_USD"], "500.00")
        self.assertEqual(env["CRYPTOAI_MAX_PAPER_NOTIONAL_USD"], "50")
        self.assertEqual(env["CRYPTOAI_DEFAULT_PAPER_NOTIONAL_USD"], "50")
        self.assertEqual(env["CRYPTOAI_PAPER_RISK_PER_TRADE_PCT"], "10.00")
        self.assertEqual(env["CRYPTOAI_MAX_DAILY_LOSS_USD"], "10")
        self.assertEqual(env["CRYPTOAI_MIN_EDGE_FOR_PAPER_PCT"], "0.30")
        self.assertEqual(settings["evidence_gates"]["min_execution_cost_confidence"], "HIGH")


if __name__ == "__main__":
    unittest.main()
