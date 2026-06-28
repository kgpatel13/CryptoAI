from abc import ABC, abstractmethod

from app.quotes.models import DexQuote, QuoteRequest


class QuoteProvider(ABC):
    @property
    @abstractmethod
    def chain(self) -> str:
        pass

    @property
    @abstractmethod
    def dex(self) -> str:
        pass

    @abstractmethod
    def supports(self, request: QuoteRequest) -> bool:
        pass

    @abstractmethod
    def get_quote(self, request: QuoteRequest) -> DexQuote:
        pass
