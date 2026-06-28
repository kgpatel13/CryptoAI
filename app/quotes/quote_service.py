from decimal import Decimal

from app.quotes.models import DexQuote
from app.quotes.quote_manager import QuoteManager


class QuoteService:
    def __init__(self) -> None:
        self.manager = QuoteManager()

    def get_base_quotes(self) -> list[DexQuote]:
        quotes: list[DexQuote] = []
        requests = [
            ("WETH", "USDC", Decimal("1")),
            ("USDC", "WETH", Decimal("1000")),
            ("cbBTC", "USDC", Decimal("0.01")),
        ]
        for token_in, token_out, amount in requests:
            quotes.extend(
                self.manager.get_quotes_for_request_across_base_dexes(
                    token_in=token_in,
                    token_out=token_out,
                    amount_in=amount,
                )
            )
        return quotes
