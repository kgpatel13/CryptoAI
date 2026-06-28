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
    """Fast quote service with cache and compatibility wrapper.

    Some existing providers in your repo may expose get_quote() with no args,
    while newer providers expose get_quote(token_in, token_out, amount).
    This service supports both so upgrades do not break the dashboard.
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
        cache_key = "base:default_quotes:v0_9_1"
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
                            self._safe_provider_quote,
                            provider,
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

    @staticmethod
    def _safe_provider_quote(provider, token_in: str, token_out: str, amount: Decimal) -> DexQuote:
        provider_name = provider.__class__.__name__.replace("QuoteProvider", "")

        try:
            return provider.get_quote(token_in, token_out, amount)
        except TypeError:
            try:
                result = provider.get_quote()
                if isinstance(result, DexQuote):
                    return result
                return DexQuote(
                    chain="base",
                    dex=provider_name,
                    token_in=token_in,
                    token_out=token_out,
                    amount_in=amount,
                    amount_out=None,
                    price=None,
                    error="Provider returned unsupported quote format",
                )
            except Exception as exc:
                return DexQuote(
                    chain="base",
                    dex=provider_name,
                    token_in=token_in,
                    token_out=token_out,
                    amount_in=amount,
                    amount_out=None,
                    price=None,
                    error=str(exc),
                )
        except Exception as exc:
            return DexQuote(
                chain="base",
                dex=provider_name,
                token_in=token_in,
                token_out=token_out,
                amount_in=amount,
                amount_out=None,
                price=None,
                error=str(exc),
            )
