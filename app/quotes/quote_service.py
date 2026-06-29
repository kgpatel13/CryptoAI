from __future__ import annotations

import json
import os
import time
from decimal import Decimal
from pathlib import Path

from app.cache.quote_cache import quote_cache
from app.metrics.metrics import metrics
from app.quotes.models import DexQuote, QuoteRequest
from app.quotes.provider_interface import QuoteProvider

try:
    from app.quotes.aerodrome_quote_provider import AerodromeQuoteProvider
except Exception:
    AerodromeQuoteProvider = None

try:
    from app.quotes.uniswap_v2_quote_provider import UniswapV2QuoteProvider
except Exception:
    UniswapV2QuoteProvider = None

try:
    from app.quotes.uniswap_v3_quote_provider import UniswapV3QuoteProvider
except Exception:
    UniswapV3QuoteProvider = None


class QuoteService:
    """Resilient quote service.

    Uses the canonical QuoteRequest provider interface, reduces public RPC
    rate-limit pressure, and reuses recent healthy quote snapshots when live
    RPC calls fail.
    """

    def __init__(self) -> None:
        self.providers: list[QuoteProvider] = []
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.snapshot_file = self.data_dir / "quote_snapshot.json"

        self.fresh_cache_seconds = int(os.getenv("CRYPTOAI_QUOTE_CACHE_SECONDS", "120"))
        self.stale_quote_seconds = int(os.getenv("CRYPTOAI_STALE_QUOTE_SECONDS", "900"))
        self.live_trading_enabled = os.getenv("CRYPTOAI_LIVE_TRADING_ENABLED", "false").lower() in {"1", "true", "yes", "on"}

        if UniswapV2QuoteProvider is not None:
            self._try_add_provider(UniswapV2QuoteProvider)

        if AerodromeQuoteProvider is not None:
            self._try_add_provider(AerodromeQuoteProvider)

        if UniswapV3QuoteProvider is not None:
            self._try_add_provider(UniswapV3QuoteProvider)

    def get_base_quotes(self) -> list[DexQuote]:
        cache_key = "base:default_quotes:v5_8_uniswap_v3"
        cached = quote_cache.get(cache_key)
        if cached is not None:
            return cached

        expected_dexes = {provider.dex for provider in self.providers}
        file_cached = self._load_snapshot(max_age_seconds=self.fresh_cache_seconds, required_dexes=expected_dexes)
        if file_cached:
            quote_cache.set(cache_key, file_cached, ttl_seconds=self.fresh_cache_seconds)
            return file_cached

        with metrics.timer("quote_service.get_base_quotes"):
            quotes = self._load_base_quotes_resilient()

        healthy = [q for q in quotes if self._is_healthy(q)]

        if healthy:
            self._save_snapshot(quotes)
            quote_cache.set(cache_key, quotes, ttl_seconds=self.fresh_cache_seconds)
            return quotes

        stale = self._load_snapshot(max_age_seconds=self.stale_quote_seconds)
        if stale and not self.live_trading_enabled:
            quote_cache.set(cache_key, stale, ttl_seconds=min(60, self.fresh_cache_seconds))
            return stale

        if stale and self.live_trading_enabled:
            return [self._live_blocked_quote("Live mode blocked stale/degraded quote snapshot. Fresh quotes are required for real trading.")]

        quote_cache.set(cache_key, quotes, ttl_seconds=30)
        return quotes

    def _try_add_provider(self, provider_cls) -> None:
        try:
            self.providers.append(provider_cls())
        except Exception:
            return

    def _load_base_quotes_resilient(self) -> list[DexQuote]:
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
                    error="No quote providers registered.",
                )
            ]

        quotes: list[DexQuote] = []

        # Sequential calls reduce public RPC 429s compared with concurrent calls.
        for provider in self.providers:
            for token_in, token_out, amount in quote_inputs:
                request = QuoteRequest(
                    chain="base",
                    dex=provider.dex,
                    token_in=token_in,
                    token_out=token_out,
                    amount_in=amount,
                )
                quotes.append(self._safe_provider_quote(provider, request))
                time.sleep(0.20)

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
                    error=f"Provider {provider.__class__.__name__} does not support this request.",
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

    def _save_snapshot(self, quotes: list[DexQuote]) -> None:
        payload = {
            "saved_at": time.time(),
            "quotes": [self._quote_to_dict(q) for q in quotes],
        }
        self.snapshot_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _load_snapshot(self, max_age_seconds: int, required_dexes: set[str] | None = None) -> list[DexQuote]:
        if not self.snapshot_file.exists():
            return []
        try:
            payload = json.loads(self.snapshot_file.read_text(encoding="utf-8"))
            saved_at = float(payload.get("saved_at", 0))
            if time.time() - saved_at > max_age_seconds:
                return []
            rows = payload.get("quotes", [])
            if required_dexes:
                snapshot_dexes = {str(row.get("dex", "")) for row in rows if isinstance(row, dict)}
                if not required_dexes.issubset(snapshot_dexes):
                    return []
            for row in rows:
                if isinstance(row, dict):
                    row["saved_at"] = saved_at
            return [self._quote_from_dict(row) for row in rows]
        except Exception:
            return []

    @staticmethod
    def _quote_to_dict(q: DexQuote) -> dict:
        return {
            "chain": q.chain,
            "dex": q.dex,
            "token_in": q.token_in,
            "token_out": q.token_out,
            "amount_in": str(q.amount_in),
            "amount_out": str(q.amount_out) if q.amount_out is not None else None,
            "price": str(q.price) if q.price is not None else None,
            "error": q.error,
            "source": q.source,
            "age_seconds": q.age_seconds,
            "is_stale": q.is_stale,
            "rpc_provider": q.rpc_provider,
        }

    @staticmethod
    def _quote_from_dict(row: dict) -> DexQuote:
        return DexQuote(
            chain=str(row.get("chain", "base")),
            dex=str(row.get("dex", "-")),
            token_in=str(row.get("token_in", "-")),
            token_out=str(row.get("token_out", "-")),
            amount_in=Decimal(str(row.get("amount_in", "0"))),
            amount_out=Decimal(str(row["amount_out"])) if row.get("amount_out") is not None else None,
            price=Decimal(str(row["price"])) if row.get("price") is not None else None,
            error=row.get("error"),
            source=str(row.get("source", "snapshot")),
            age_seconds=max(0.0, time.time() - float(row.get("saved_at", 0))) if row.get("saved_at") else float(row.get("age_seconds", 0.0)),
            is_stale=True,
            rpc_provider=row.get("rpc_provider"),
        )

    @staticmethod
    def _live_blocked_quote(error: str) -> DexQuote:
        return DexQuote(
            chain="base",
            dex="SafetyGate",
            token_in="-",
            token_out="-",
            amount_in=Decimal("0"),
            amount_out=None,
            price=None,
            error=error,
            source="safety_gate",
            is_stale=True,
        )

    @staticmethod
    def _is_healthy(q: DexQuote) -> bool:
        return q.error is None and q.price is not None and q.price > 0 and q.amount_out is not None and q.amount_out > 0
