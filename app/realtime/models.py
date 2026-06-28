from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class MarketTick:
    source: str
    symbol: str
    price_usd: Decimal
    event_time: str
    received_at: str
    raw: dict


@dataclass(frozen=True)
class RealtimeFeedStatus:
    source: str
    symbol: str
    connected: bool
    last_price_usd: Decimal | None
    last_event_time: str | None
    last_received_at: str | None
    message: str
