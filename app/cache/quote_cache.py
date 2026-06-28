from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class QuoteCache:
    """Small in-memory TTL cache for quote results.

    This reduces repeated RPC/API calls from the dashboard and makes the
    quote path faster. It is process-local and intentionally simple.
    """

    def __init__(self) -> None:
        self._items: dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any | None:
        entry = self._items.get(key)
        now = time.time()

        if entry is None:
            self.misses += 1
            return None

        if entry.expires_at < now:
            self._items.pop(key, None)
            self.misses += 1
            return None

        self.hits += 1
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int = 10) -> None:
        self._items[key] = CacheEntry(
            value=value,
            expires_at=time.time() + ttl_seconds,
        )

    def clear(self) -> None:
        self._items.clear()
        self.hits = 0
        self.misses = 0

    def stats(self) -> dict[str, int | float]:
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total else 0.0
        return {
            "cache_items": len(self._items),
            "cache_hits": self.hits,
            "cache_misses": self.misses,
            "cache_hit_rate_pct": round(hit_rate, 2),
        }


quote_cache = QuoteCache()
