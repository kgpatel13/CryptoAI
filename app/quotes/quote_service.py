from decimal import Decimal

from app.quotes.aerodrome_quote_provider import AerodromeQuoteProvider
from app.quotes.uniswap_v2_quote_provider import UniswapV2QuoteProvider
from app.quotes.models import DexQuote


class QuoteService:
    def __init__(self) -> None:
        self.aerodrome = AerodromeQuoteProvider()
        self.uniswap_v2 = UniswapV2QuoteProvider()

    def get_base_quotes(self) -> list[DexQuote]:
        quotes: list[DexQuote] = []

        test_requests = [
            ("WETH", "USDC", Decimal("1")),
            ("USDC", "WETH", Decimal("1000")),
            ("cbBTC", "USDC", Decimal("0.01")),
        ]

        for token_in, token_out, amount in test_requests:
            quotes.append(self.aerodrome.get_quote(token_in, token_out, amount))
            quotes.append(self.uniswap_v2.get_quote(token_in, token_out, amount))

        return quotes