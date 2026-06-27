from app.marketdata.coingecko import CoinGeckoProvider
from app.marketdata.models import MarketPrice
from app.registry.tokens import TOKENS


class MarketDataService:
    def __init__(self) -> None:
        self.provider = CoinGeckoProvider()

    def get_registered_asset_prices(self) -> list[MarketPrice]:
        ids: list[str] = []

        for tokens in TOKENS.values():
            for token in tokens:
                if token.coingecko_id:
                    ids.append(token.coingecko_id)

        return self.provider.get_prices(ids)