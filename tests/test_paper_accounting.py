from __future__ import annotations

import unittest
from decimal import Decimal

from app.portfolio.accounting import PaperAccounting


class PaperAccountingTests(unittest.TestCase):
    def test_weth_usdc_is_usd_quoted(self) -> None:
        math = PaperAccounting.canonical_entry(
            pair="WETH/USDC",
            raw_price=Decimal("2000"),
            notional_usd=Decimal("100"),
            prices={"ETH": Decimal("2000"), "WETH": Decimal("2000")},
        )
        self.assertEqual(math.price_usd, Decimal("2000"))
        self.assertEqual(math.quantity, Decimal("0.05"))

    def test_usdc_weth_uses_stable_base_usd_price(self) -> None:
        math = PaperAccounting.canonical_entry(
            pair="USDC/WETH",
            raw_price=Decimal("0.0005"),
            notional_usd=Decimal("100"),
            prices={"ETH": Decimal("2000"), "WETH": Decimal("2000")},
        )
        self.assertEqual(math.price_usd, Decimal("1"))
        self.assertEqual(math.quantity, Decimal("100"))

    def test_unreasonable_closed_pnl_is_clamped_to_edge(self) -> None:
        pnl = PaperAccounting.reasonable_closed_pnl(
            notional_usd=Decimal("100"),
            stored_pnl=Decimal("157000"),
            estimated_edge_pct=Decimal("0.35"),
        )
        self.assertEqual(pnl, Decimal("0.3500"))


if __name__ == "__main__":
    unittest.main()
