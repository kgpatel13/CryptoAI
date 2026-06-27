from abc import ABC, abstractmethod

from app.marketdata.models import MarketPrice


class MarketDataProvider(ABC):
    @abstractmethod
    def get_prices(self, coingecko_ids: list[str]) -> list[MarketPrice]:
        pass