from decimal import Decimal

from app.quotes.models import DexQuote
from app.quotes.quote_manager import QuoteManager


class QuoteService:
    def __init__(self) -> None:
        self.manager = QuoteManager()

    def get_base_quotes(self) -> list[DexQuote]:
        quotes: list[DexQuote] = []

        test_requests = [
            ("WETH", "USDC", Decimal("1")),
            ("USDC", "WETH", Decimal("1000")),
            ("cbBTC", "USDC", Decimal("0.01")),
        ]

        for token_in, token_out, amount in test_requests:
            quotes.extend(
                self.manager.get_quotes_for_chain_pair(
                    chain="base",
                    token_in_symbol=token_in,
                    token_out_symbol=token_out,
                    amount_in=amount,
                )
            )

        return quotes

    def get_quotes_for_pair(
        self,
        chain: str,
        token_in: str,
        token_out: str,
        amount_in: Decimal,
    ) -> list[DexQuote]:
        return self.manager.get_quotes_for_chain_pair(
            chain=chain,
            token_in_symbol=token_in,
            token_out_symbol=token_out,
            amount_in=amount_in,
        )
