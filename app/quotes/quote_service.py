from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal

from app.cache.quote_cache import quote_cache
from app.metrics.metrics import metrics
from app.quotes.models import DexQuote, QuoteRequest
from app.quotes.provider_interface import QuoteProvider

try:
    from app.quotes.aerodrome_quote_provider import AerodromeQuoteProvider
except Exception:  # pragma: no cover
    AerodromeQuoteProvider = None

try:
    from app.quotes.uniswap_v2_quote_provider import UniswapV2QuoteProvider
except Exception:  # pragma: no cover
    UniswapV2QuoteProvider = None


class QuoteService:
    """Quote service using the canonical QuoteRequest provider interface.

    v2.9 fix:
    Providers implement `get_quote(request: QuoteRequest)`.
    Older QuoteService versions incorrectly called `get_quote(token_in, token_out, amount)`,
    which made every quote fail before any blockchain call was attempted.
    """

    def __init__(self) -> None:
        self.providers: list[QuoteProvider] = []

        if AerodromeQuoteProvider is not None:
            try:
                self.providers.append(AerodromeQuoteProvider())
            except Exception:
                # Provider init errors are reported as quote rows below.
                pass

        if UniswapV2QuoteProvider is not None:
            try:
                self.providers.append(UniswapV2QuoteProvider())
            except Exception:
                pass

    def get_base_quotes(self) -> list[DexQuote]:
        # Versioned key prevents old cached signature-error rows from being reused.
        cache_key = "base:default_quotes:v2_9_request_interface"
        cached = quote_cache.get(cache_key)
        if cached is not None:
            return cached

        with metrics.timer("quote_service.get_base_quotes"):
            quotes = self._load_base_quotes_fast()

        quote_cache.set(cache_key, quotes, ttl_seconds=12)
        return quotes

    def _load_base_quotes_fast(self) -> list[DexQuote]:
        quote_inputs = [
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
                    error="No quote providers registered. Provider initialization likely failed.",
                )
            ]

        tasks = []
        quotes: list[DexQuote] = []

        with ThreadPoolExecutor(max_workers=4) as executor:
            for provider in self.providers:
                for token_in, token_out, amount in quote_inputs:
                    request = QuoteRequest(
                        chain="base",
                        dex=provider.dex,
                        token_in=token_in,
                        token_out=token_out,
                        amount_in=amount,
                    )
                    tasks.append(executor.submit(self._safe_provider_quote, provider, request))

            for future in as_completed(tasks, timeout=12):
                try:
                    quotes.append(future.result(timeout=2))
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
                            error=f"Quote task failed: {type(exc).__name__}: {exc}",
                        )
                    )

        return quotes

    @staticmethod
    def _safe_provider_quote(provider: QuoteProvider, request: QuoteRequest) -> DexQuote:
        try:
            if not provider.supports(request):
                return DexQuote(
                    chain=request.chain,
                    dex=request.dex,
                    token_in=request.token_in,
                    token_out=request.token_out,
                    amount_in=request.amount_in,
                    amount_out=None,
                    price=None,
                    error=(
                        f"Provider {provider.__class__.__name__} does not support "
                        f"{request.chain}/{request.dex}/{request.token_in}/{request.token_out}"
                    ),
                )

            quote = provider.get_quote(request)

            if not isinstance(quote, DexQuote):
                return DexQuote(
                    chain=request.chain,
                    dex=request.dex,
                    token_in=request.token_in,
                    token_out=request.token_out,
                    amount_in=request.amount_in,
                    amount_out=None,
                    price=None,
                    error=f"Provider returned unsupported quote type: {type(quote).__name__}",
                )

            return quote

        except Exception as exc:
            return DexQuote(
                chain=request.chain,
                dex=request.dex,
                token_in=request.token_in,
                token_out=request.token_out,
                amount_in=request.amount_in,
                amount_out=None,
                price=None,
                error=f"{type(exc).__name__}: {exc}",
            )
