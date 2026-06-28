from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    value: T
    expires_at: float


class TTLCache(Generic[T]):
    """Tiny in-memory TTL cache for read-only market data.

    This intentionally stays simple. It reduces repeat RPC calls from the
    dashboard while we are using public rate-limited endpoints.
    """

    def __init__(self, default_ttl_seconds: int = 15) -> None:
        self.default_ttl_seconds = default_ttl_seconds
        self._store: dict[str, CacheEntry[T]] = {}

    def get(self, key: str) -> T | None:
        entry = self._store.get(key)
        if entry is None:
            return None

        if entry.expires_at < time.time():
            self._store.pop(key, None)
            return None

        return entry.value

    def set(self, key: str, value: T, ttl_seconds: int | None = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
        self._store[key] = CacheEntry(value=value, expires_at=time.time() + ttl)

    def clear(self) -> None:
        self._store.clear()

    def size(self) -> int:
        return len(self._store)
