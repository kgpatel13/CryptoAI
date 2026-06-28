from __future__ import annotations

from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.cache.quote_cache import quote_cache
from app.metrics.metrics import metrics
from app.quotes.models import DexQuote

try:
    from app.quotes.aerodrome_quote_provider import AerodromeQuoteProvider
except Exception:  # pragma: no cover
    AerodromeQuoteProvider = None

try:
    from app.quotes.uniswap_v2_quote_provider import UniswapV2QuoteProvider
except Exception:  # pragma: no cover
    UniswapV2QuoteProvider = None


class QuoteService:
    """Fast quote service with cache and parallel provider calls.

    The dashboard can refresh frequently without hammering public RPCs.
    For actual live trading later, this service will be replaced/augmented
    by lower-latency paid RPCs, private routes, and dedicated workers.
    """

    def __init__(self) -> None:
        self.providers = []

        if AerodromeQuoteProvider is not None:
            try:
                self.providers.append(AerodromeQuoteProvider())
            except Exception:
                pass

        if UniswapV2QuoteProvider is not None:
            try:
                self.providers.append(UniswapV2QuoteProvider())
            except Exception:
                pass

    def get_base_quotes(self) -> list[DexQuote]:
        cache_key = "base:default_quotes:v0_9"
        cached = quote_cache.get(cache_key)
        if cached is not None:
            return cached

        with metrics.timer("quote_service.get_base_quotes"):
            quotes = self._load_base_quotes_fast()

        quote_cache.set(cache_key, quotes, ttl_seconds=12)
        return quotes

    def _load_base_quotes_fast(self) -> list[DexQuote]:
        requests = [
            ("WETH", "USDC", Decimal("1")),
            ("USDC", "WETH", Decimal("1000")),
        ]

        if not self.providers:
            return [
                DexQuote(
                    chain="base",
                    dex="No Provider",
                    token_in="WETH",
                    token_out="USDC",
                    amount_in=Decimal("1"),
                    amount_out=None,
                    price=None,
                    error="No quote providers registered",
                )
            ]

        tasks = []
        quotes: list[DexQuote] = []

        with ThreadPoolExecutor(max_workers=4) as executor:
            for provider in self.providers:
                for token_in, token_out, amount in requests:
                    tasks.append(
                        executor.submit(
                            provider.get_quote,
                            token_in,
                            token_out,
                            amount,
                        )
                    )

            for future in as_completed(tasks, timeout=8):
                try:
                    quotes.append(future.result(timeout=1))
                except Exception as exc:
                    quotes.append(
                        DexQuote(
                            chain="base",
                            dex="Unknown",
                            token_in="-",
                            token_out="-",
                            amount_in=Decimal("0"),
                            amount_out=None,
                            price=None,
                            error=f"Quote task failed: {exc}",
                        )
                    )

        return quotes
