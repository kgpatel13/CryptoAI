from decimal import Decimal

from app.quotes.aerodrome_quote_provider import AerodromeQuoteProvider
from app.quotes.models import DexQuote
from app.quotes.provider import QuoteProvider
from app.quotes.uniswap_v2_quote_provider import UniswapV2QuoteProvider


class QuoteManager:
    """Coordinates quote providers across chains and DEXs.

    Today this starts with Base/Aerodrome and Base/Uniswap V2 style quotes.
    The scanner should talk to this manager instead of individual DEX classes.
    """

    def __init__(self) -> None:
        self.providers: list[QuoteProvider] = [
            AerodromeQuoteProvider(),
            UniswapV2QuoteProvider(),
        ]

    def get_providers_for_chain(self, chain: str) -> list[QuoteProvider]:
        return [p for p in self.providers if p.chain.lower() == chain.lower()]

    def get_quotes_for_chain_pair(
        self,
        chain: str,
        token_in_symbol: str,
        token_out_symbol: str,
        amount_in: Decimal,
    ) -> list[DexQuote]:
        quotes: list[DexQuote] = []
        for provider in self.get_providers_for_chain(chain):
            quotes.append(
                provider.get_quote(
                    token_in_symbol=token_in_symbol,
                    token_out_symbol=token_out_symbol,
                    amount_in=amount_in,
                )
            )
        return quotes
