from __future__ import annotations

from collections import Counter
from typing import Any

from app.quotes.quote_service import QuoteService


class SystemHealthService:
    """Aggregates operational status for dashboard diagnostics."""

    def quote_provider_status(self) -> list[dict[str, str]]:
        return QuoteService().get_provider_status()

    def quote_error_summary(self) -> dict[str, Any]:
        quotes = QuoteService().get_base_quotes(include_experimental_pairs=False)
        total = len(quotes)
        success = sum(1 for quote in quotes if quote.error is None and quote.price is not None)
        errors = [quote.error or "" for quote in quotes if quote.error]

        categories = Counter(self._category(error) for error in errors)

        return {
            "total_quotes": total,
            "successful_quotes": success,
            "failed_quotes": total - success,
            "success_rate_pct": (success / total * 100) if total else 0,
            "error_categories": dict(categories),
        }

    @staticmethod
    def _category(error: str) -> str:
        lower = error.lower()
        if "rate limit" in lower or "429" in lower or "too many requests" in lower:
            return "RPC rate limit"
        if "unavailable" in lower or "could not transact" in lower:
            return "Provider/route unavailable"
        if "token not found" in lower:
            return "Registry issue"
        return "Other"
