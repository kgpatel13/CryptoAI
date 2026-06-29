from __future__ import annotations

import time
from decimal import Decimal

from app.cache.ttl_cache import TTLCache
from app.quotes.aerodrome_quote_provider import AerodromeQuoteProvider
from app.quotes.models import DexQuote, QuoteRequest
from app.quotes.provider_interface import QuoteProvider
from app.quotes.uniswap_v2_quote_provider import UniswapV2QuoteProvider
from app.quotes.uniswap_v3_quote_provider import UniswapV3QuoteProvider


class QuoteManager:
    """Routes quote requests to registered providers with lightweight caching."""

    _quote_cache: TTLCache[DexQuote] = TTLCache(default_ttl_seconds=15)

    def __init__(self) -> None:
        self.providers: list[QuoteProvider] = []
        for provider_cls in (AerodromeQuoteProvider, UniswapV2QuoteProvider, UniswapV3QuoteProvider):
            try:
                self.providers.append(provider_cls())
            except Exception:
                continue

    def get_quote(self, request: QuoteRequest) -> DexQuote:
        cache_key = self._cache_key(request)
        cached = self._quote_cache.get(cache_key)
        if cached is not None:
            return cached

        time.sleep(0.05)

        for provider in self.providers:
            if provider.supports(request):
                quote = provider.get_quote(request)
                self._quote_cache.set(cache_key, quote)
                return quote

        quote = DexQuote(
            chain=request.chain,
            dex=request.dex,
            token_in=request.token_in,
            token_out=request.token_out,
            amount_in=request.amount_in,
            amount_out=None,
            price=None,
            error=f"No quote provider registered for {request.chain}/{request.dex}",
        )
        self._quote_cache.set(cache_key, quote)
        return quote

    def get_quotes_for_request_across_base_dexes(
        self,
        token_in: str,
        token_out: str,
        amount_in: Decimal,
    ) -> list[DexQuote]:
        return [
            self.get_quote(
                QuoteRequest(
                    chain="base",
                    dex=provider.dex,
                    token_in=token_in,
                    token_out=token_out,
                    amount_in=amount_in,
                )
            )
            for provider in self.providers
            if provider.chain == "base"
        ]

    def provider_status(self) -> list[dict[str, str]]:
        return [
            {"chain": provider.chain, "dex": provider.dex, "status": "registered"}
            for provider in self.providers
        ]

    @staticmethod
    def _cache_key(request: QuoteRequest) -> str:
        return "|".join(
            [
                "v5_8",
                request.chain.lower(),
                request.dex.lower(),
                request.token_in.upper(),
                request.token_out.upper(),
                str(request.amount_in),
            ]
        )
