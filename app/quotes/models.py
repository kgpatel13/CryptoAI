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