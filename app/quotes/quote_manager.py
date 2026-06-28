from app.quotes.aerodrome_quote_provider import AerodromeQuoteProvider
from app.quotes.models import DexQuote, QuoteRequest
from app.quotes.provider_interface import QuoteProvider
from app.quotes.uniswap_v2_quote_provider import UniswapV2QuoteProvider


class QuoteManager:
    def __init__(self) -> None:
        self.providers: list[QuoteProvider] = [
            AerodromeQuoteProvider(),
            UniswapV2QuoteProvider(),
        ]

    def get_quote(self, request: QuoteRequest) -> DexQuote:
        for provider in self.providers:
            if provider.supports(request):
                return provider.get_quote(request)

        return DexQuote(
            chain=request.chain,
            dex=request.dex,
            token_in=request.token_in,
            token_out=request.token_out,
            amount_in=request.amount_in,
            amount_out=None,
            price=None,
            error=f"No quote provider registered for {request.chain}/{request.dex}",
        )

    def get_quotes_for_request_across_base_dexes(
        self,
        token_in: str,
        token_out: str,
        amount_in,
    ) -> list[DexQuote]:
        return [
            self.get_quote(QuoteRequest("base", provider.dex, token_in, token_out, amount_in))
            for provider in self.providers
            if provider.chain == "base"
        ]
