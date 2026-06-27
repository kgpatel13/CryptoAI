from dataclasses import dataclass
from decimal import Decimal

from app.quotes.quote_service import QuoteService


@dataclass(frozen=True)
class GrossOpportunity:
    chain: str
    pair: str
    best_buy_dex: str
    best_sell_dex: str
    buy_price: Decimal
    sell_price: Decimal
    gross_spread_pct: Decimal


class OpportunityScanner:
    def __init__(self) -> None:
        self.quote_service = QuoteService()

    def scan_base_gross_opportunities(self) -> list[GrossOpportunity]:
        quotes = self.quote_service.get_base_quotes()

        grouped: dict[str, list] = {}

        for quote in quotes:
            if quote.error or quote.price is None:
                continue

            pair_key = f"{quote.token_in}/{quote.token_out}"
            grouped.setdefault(pair_key, []).append(quote)

        opportunities: list[GrossOpportunity] = []

        for pair, pair_quotes in grouped.items():
            if len(pair_quotes) < 2:
                continue

            sorted_quotes = sorted(pair_quotes, key=lambda q: q.price)
            low = sorted_quotes[0]
            high = sorted_quotes[-1]

            if low.dex == high.dex:
                continue

            spread_pct = ((high.price - low.price) / low.price) * Decimal("100")

            opportunities.append(
                GrossOpportunity(
                    chain="base",
                    pair=pair,
                    best_buy_dex=low.dex,
                    best_sell_dex=high.dex,
                    buy_price=low.price,
                    sell_price=high.price,
                    gross_spread_pct=spread_pct,
                )
            )

        return opportunities