from decimal import Decimal

from app.quotes.aerodrome_quote_provider import AerodromeQuoteProvider
from app.quotes.models import DexQuote


class QuoteService:
    def __init__(self) -> None:
        self.aerodrome = AerodromeQuoteProvider()

    def get_base_quotes(self) -> list[DexQuote]:
        quotes: list[DexQuote] = []

        test_requests = [
            ("WETH", "USDC", Decimal("1")),
            ("USDC", "WETH", Decimal("1000")),
            ("cbBTC", "USDC", Decimal("0.01")),
        ]

        for token_in, token_out, amount in test_requests:
            quotes.append(
                self.aerodrome.get_quote(
                    token_in_symbol=token_in,
                    token_out_symbol=token_out,
                    amount_in=amount,
                )
            )

        return quotes