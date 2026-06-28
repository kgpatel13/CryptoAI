from __future__ import annotations

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from app.analytics.pnl_analytics_service import PnLAnalyticsService


class PnLAnalyticsServiceTests(unittest.TestCase):
    def test_generates_realistic_pnl_metrics_from_state_and_orders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            reports = root / "reports"
            data.mkdir()
            reports.mkdir()

            (data / "paper_orders.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "order_id": "o1",
                                "timestamp": "2026-06-28T10:00:00Z",
                                "pair": "WETH/USDC",
                                "side": "BUY",
                                "status": "FILLED",
                                "filled_notional_usd": "100",
                                "slippage_bps": "5",
                                "latency_ms": 250,
                                "execution_quality": "GOOD",
                                "reason": "filled",
                            }
                        ),
                        json.dumps(
                            {
                                "order_id": "o2",
                                "timestamp": "2026-06-28T11:00:00Z",
                                "pair": "USDC/WETH",
                                "side": "BUY",
                                "status": "FILLED",
                                "filled_notional_usd": "100.0035",
                                "slippage_bps": "5",
                                "latency_ms": 250,
                                "execution_quality": "GOOD",
                                "reason": "filled",
                            }
                        ),
                    ]
                ),
                encoding="utf-8",
            )
            (data / "paper_portfolio_state.json").write_text(
                json.dumps(
                    {
                        "initial_cash_usd": "10000",
                        "cash_usd": "9800.3465",
                        "realized_pnl_usd": "0.3500",
                        "positions": [
                            {
                                "pair": "USDC/WETH",
                                "status": "CLOSED",
                                "notional_usd": "100.0035",
                                "realized_pnl_usd": "0.3500",
                            },
                            {
                                "pair": "WETH/USDC",
                                "status": "OPEN",
                                "notional_usd": "100",
                                "quantity": "0.064",
                                "current_price_usd": "1563",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            analytics = PnLAnalyticsService(data_dir=data, report_dir=reports).generate()
            self.assertEqual(analytics["realized_pnl_usd"], "0.3500")
            self.assertEqual(analytics["win_count"], 1)
            self.assertEqual(analytics["loss_count"], 0)
            self.assertEqual(analytics["avg_slippage_bps"], "5.0000")
            self.assertTrue((reports / "portfolio_analytics.json").exists())
            self.assertTrue((reports / "portfolio_analytics.md").exists())

    def test_drawdown_is_calculated_from_daily_equity_curve(self) -> None:
        service = PnLAnalyticsService()
        journal = []
        initial = Decimal("10000")
        daily = [
            {"date": "2026-01-01", "realized_pnl_usd": "100"},
            {"date": "2026-01-02", "realized_pnl_usd": "-50"},
        ]
        curve = service._equity_curve(daily, initial)
        dd = service._max_drawdown(curve)
        self.assertEqual(dd["drawdown_usd"], Decimal("50"))
        self.assertEqual(dd["drawdown_pct"], Decimal("0.4950"))


if __name__ == "__main__":
    unittest.main()
