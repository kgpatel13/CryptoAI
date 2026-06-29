import unittest

from app.quotes.aerodrome_quote_provider import AERODROME_FACTORY, AERODROME_ROUTER


class AerodromeQuoteProviderTests(unittest.TestCase):
    def test_base_contract_addresses_are_current(self):
        self.assertEqual(AERODROME_ROUTER.lower(), "0xcf77a3ba9a5ca399b7c97c74d54e5b1beb874e43")
        self.assertEqual(AERODROME_FACTORY.lower(), "0x420dd381b31aef6683db6b902084cb0ffece40da")


if __name__ == "__main__":
    unittest.main()
