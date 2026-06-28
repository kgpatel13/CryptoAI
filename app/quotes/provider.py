from abc import ABC, abstractmethod
from decimal import Decimal

from app.quotes.models import DexQuote


class QuoteProvider(ABC):
    """Common interface for every DEX quote provider.

    Each DEX connector should implement this class so the scanner can use
    providers interchangeably without knowing exchange-specific details.
    """

    chain: str
    dex_name: str

    @abstractmethod
    def get_quote(
        self,
        token_in_symbol: str,
        token_out_symbol: str,
        amount_in: Decimal,
    ) -> DexQuote:
        raise NotImplementedError
