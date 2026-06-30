from __future__ import annotations

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

from app.research.pool_depth_ladder_service import PoolDepthLadderService


class PoolDepthLadderServiceTests(unittest.TestCase):
    def test_marks_route_depth_ready_when_two_dexes_hold_requested_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data, reports = self._dirs(tmp)
            self._write_settings(reports, max_notional="1000")
            self._write_portfolio(data, cash="1000")

            payload = PoolDepthLadderService(
                data_dir=data,
                report_dir=reports,
                quote_manager=FakeQuoteManager(
                    {
                        "Uniswap V2": Decimal("0.04"),
                        "Uniswap V3": Decimal("0.05"),
                    }
                ),
                dexscreener=FakeDexScreener(),
            ).generate()

            self.assertEqual(payload["overall_status"], "DEPTH_EVIDENCE_READY")
            self.assertEqual(payload["confidence"], "MEDIUM")
            self.assertEqual(payload["depth_ready_route_count"], 2)
            self.assertTrue((reports / "pool_depth_ladder.json").exists())
            self.assertTrue((reports / "pool_depth_ladder.md").exists())
            self.assertTrue((data / "quote_size_ladder.jsonl").exists())

    def test_marks_route_size_limited_when_large_quotes_degrade(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data, reports = self._dirs(tmp)
            self._write_settings(reports, max_notional="1000")
            self._write_portfolio(data, cash="1000")

            payload = PoolDepthLadderService(
                data_dir=data,
                report_dir=reports,
                quote_manager=FakeQuoteManager(
                    {
                        "Uniswap V2": Decimal("0.80"),
                        "Uniswap V3": Decimal("0.90"),
                    },
                    impact_starts_at_usd=Decimal("500"),
                ),
                dexscreener=FakeDexScreener(),
            ).generate()

            statuses = {route["status"] for route in payload["routes"]}
            self.assertIn("SIZE_LIMITED", statuses)
            self.assertEqual(payload["overall_status"], "DEPTH_EVIDENCE_WATCH")
            self.assertEqual(payload["confidence"], "LOW")

    @staticmethod
    def _dirs(tmp: str) -> tuple[Path, Path]:
        root = Path(tmp)
        data = root / "data"
        reports = root / "reports"
        data.mkdir()
        reports.mkdir()
        return data, reports

    @staticmethod
    def _write_settings(reports: Path, *, max_notional: str) -> None:
        (reports / "paper_trading_settings.json").write_text(
            json.dumps(
                {
                    "paper_capital_usd": "1000.00",
                    "settings": {
                        "paper_capital": {
                            "eth_reference_usd": "1000",
                            "max_notional_usd_per_trade": max_notional,
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _write_portfolio(data: Path, *, cash: str) -> None:
        (data / "paper_portfolio_state.json").write_text(
            json.dumps({"initial_cash_usd": "1000.00", "cash_usd": cash, "positions": []}),
            encoding="utf-8",
        )


class FakeQuoteManager:
    def __init__(self, impact_by_dex: dict[str, Decimal], impact_starts_at_usd: Decimal = Decimal("0")) -> None:
        self.impact_by_dex = impact_by_dex
        self.impact_starts_at_usd = impact_starts_at_usd
        self.providers = [SimpleNamespace(chain="base", dex=dex) for dex in impact_by_dex]

    def get_quote(self, request):
        reference = Decimal("1000")
        if request.token_in == "WETH":
            notional = request.amount_in * reference
        else:
            notional = request.amount_in
        impact = self.impact_by_dex[request.dex] if notional >= self.impact_starts_at_usd else Decimal("0.02")
        if request.token_in == "WETH":
            price = reference * (Decimal("1") - impact / Decimal("100"))
            amount_out = request.amount_in * price
        else:
            price = reference * (Decimal("1") + impact / Decimal("100"))
            amount_out = request.amount_in / price
        return SimpleNamespace(
            chain=request.chain,
            dex=request.dex,
            token_in=request.token_in,
            token_out=request.token_out,
            amount_in=request.amount_in,
            amount_out=amount_out,
            price=price,
            error="",
        )


class FakeDexScreener:
    def get_base_major_pairs(self) -> list[dict]:
        return [
            {
                "chainId": "base",
                "dexId": "uniswap",
                "pairAddress": "0x1",
                "baseToken": {"symbol": "WETH"},
                "quoteToken": {"symbol": "USDC"},
                "liquidity": {"usd": "5000000"},
                "volume": {"h24": "1000000"},
            }
        ]


if __name__ == "__main__":
    unittest.main()
