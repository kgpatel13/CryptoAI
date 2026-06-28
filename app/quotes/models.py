from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class DexQuote:
    chain: str
    dex: str
    token_in: str
    token_out: str
    amount_in: Decimal
    amount_out: Decimal | None
    price: Decimal | None
    error: str | None = None
    source: str = "live"
    age_seconds: float = 0.0
    is_stale: bool = False
    rpc_provider: str | None = None


@dataclass(frozen=True)
class QuoteRequest:
    chain: str
    dex: str
    token_in: str
    token_out: str
    amount_in: Decimal
