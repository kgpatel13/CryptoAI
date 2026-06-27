from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class MarketPrice:
    symbol: str
    name: str
    coingecko_id: str
    usd_price: Decimal | None
    market_cap: Decimal | None
    volume_24h: Decimal | None
    change_24h_pct: Decimal | None