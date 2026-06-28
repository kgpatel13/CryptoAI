from decimal import Decimal
import unittest

from app.quotes.models import DexQuote


class QuoteModelTests(unittest.TestCase):
    def test_quote_has_freshness_metadata(self):
        quote = DexQuote("base", "TestDEX", "WETH", "USDC", Decimal("1"), Decimal("100"), Decimal("100"))
        self.assertEqual(quote.source, "live")
        self.assertFalse(quote.is_stale)
        self.assertEqual(quote.age_seconds, 0.0)


if __name__ == "__main__":
    unittest.main()
