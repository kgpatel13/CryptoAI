from decimal import Decimal
import requests

from app.marketdata.models import MarketPrice
from app.marketdata.providers import MarketDataProvider


class CoinGeckoProvider(MarketDataProvider):
    BASE_URL = "https://api.coingecko.com/api/v3"

    def get_prices(self, coingecko_ids: list[str]) -> list[MarketPrice]:
        unique_ids = sorted(set(x for x in coingecko_ids if x))

        if not unique_ids:
            return []

        url = f"{self.BASE_URL}/coins/markets"

        params = {
            "vs_currency": "usd",
            "ids": ",".join(unique_ids),
            "order": "market_cap_desc",
            "per_page": 250,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h",
        }

        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()

        data = response.json()
        prices: list[MarketPrice] = []

        for item in data:
            prices.append(
                MarketPrice(
                    symbol=str(item.get("symbol", "")).upper(),
                    name=str(item.get("name", "")),
                    coingecko_id=str(item.get("id", "")),
                    usd_price=self._to_decimal(item.get("current_price")),
                    market_cap=self._to_decimal(item.get("market_cap")),
                    volume_24h=self._to_decimal(item.get("total_volume")),
                    change_24h_pct=self._to_decimal(
                        item.get("price_change_percentage_24h")
                    ),
                )
            )

        return prices

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if value is None:
            return None
        return Decimal(str(value))