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
        self.assertIn("Only WETH/USDC and USDC/WETH are enabled for v5.7.", messages)


if __name__ == "__main__":
    unittest.main()
