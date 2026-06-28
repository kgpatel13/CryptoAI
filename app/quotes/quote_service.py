from decimal import Decimal

from app.quotes.models import DexQuote
from app.quotes.quote_manager import QuoteManager


class QuoteService:
    def __init__(self) -> None:
        self.manager = QuoteManager()

    def get_base_quotes(self, include_experimental_pairs: bool = False) -> list[DexQuote]:
        """Return current Base quotes.

        v0.8 deliberately keeps the default request set small to reduce public RPC
        rate-limit errors while we are still building infrastructure.
        """
        quotes: list[DexQuote] = []
        requests = [
            ("WETH", "USDC", Decimal("1")),
            ("USDC", "WETH", Decimal("1000")),
        ]

        if include_experimental_pairs:
            requests.append(("cbBTC", "USDC", Decimal("0.01")))

        for token_in, token_out, amount in requests:
            quotes.extend(
                self.manager.get_quotes_for_request_across_base_dexes(
                    token_in=token_in,
                    token_out=token_out,
                    amount_in=amount,
                )
            )
        return quotes

    def get_provider_status(self) -> list[dict[str, str]]:
        return self.manager.provider_status()
