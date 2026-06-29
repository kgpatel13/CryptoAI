from __future__ import annotations

import tempfile
import unittest

from app.diagnostics.quote_diagnostics import QuoteDiagnostic, QuoteDiagnosticStatus, QuoteDiagnosticsService


class QuoteDiagnosticsTests(unittest.TestCase):
    def test_same_dex_ok_rows_do_not_imply_real_arbitrage_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            service = QuoteDiagnosticsService(data_dir=tmp, report_dir=tmp)
            service._write_report(
                [
                    QuoteDiagnostic(
                        timestamp="2026-06-29T02:00:00Z",
                        chain="base",
                        dex="Uniswap V2",
                        pair="WETH/USDC",
                        token_in="WETH",
                        token_out="USDC",
                        amount_in="1",
                        amount_out="1500",
                        price="1500",
                        latency_ms=10.0,
                        status=QuoteDiagnosticStatus.OK,
                        error="",
                    ),
                    QuoteDiagnostic(
                        timestamp="2026-06-29T02:00:00Z",
                        chain="base",
                        dex="Uniswap V2",
                        pair="USDC/WETH",
                        token_in="USDC",
                        token_out="WETH",
                        amount_in="1",
                        amount_out="0.0006",
                        price="0.0006",
                        latency_ms=10.0,
                        status=QuoteDiagnosticStatus.OK,
                        error="",
                    ),
                ]
            )

            text = service.report_file.read_text(encoding="utf-8")

            self.assertIn("fewer than two healthy DEX venues", text)
            self.assertNotIn("at least two valid DEX venues", text)


if __name__ == "__main__":
    unittest.main()
