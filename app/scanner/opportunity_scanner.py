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


@dataclass(frozen=True)
class NetOpportunity:
    chain: str
    pair: str
    best_buy_dex: str
    best_sell_dex: str
    trade_size_usd: Decimal
    gross_spread_pct: Decimal
    estimated_gross_profit_usd: Decimal
    estimated_cost_usd: Decimal
    estimated_net_profit_usd: Decimal
    estimated_net_profit_pct: Decimal
    decision: str
    reason: str


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

            if low.dex == high.dex or low.price is None or high.price is None:
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

    def scan_base_net_opportunities(self) -> list[NetOpportunity]:
        # Conservative first-pass model. Later we will replace constants with pool liquidity,
        # gas estimates, slippage simulation, and execution probability.
        trade_size_usd = Decimal("1000")
        estimated_gas_usd = Decimal("0.25")
        estimated_dex_fee_pct = Decimal("0.60")  # two 0.30% swaps estimate
        estimated_slippage_pct = Decimal("0.15")
        mev_buffer_pct = Decimal("0.05")
        minimum_net_profit_usd = Decimal("1.00")

        net_opportunities: list[NetOpportunity] = []

        for gross in self.scan_base_gross_opportunities():
            gross_profit_usd = trade_size_usd * gross.gross_spread_pct / Decimal("100")
            variable_cost_pct = estimated_dex_fee_pct + estimated_slippage_pct + mev_buffer_pct
            variable_cost_usd = trade_size_usd * variable_cost_pct / Decimal("100")
            estimated_cost_usd = estimated_gas_usd + variable_cost_usd
            net_profit_usd = gross_profit_usd - estimated_cost_usd
            net_profit_pct = net_profit_usd / trade_size_usd * Decimal("100")

            if net_profit_usd >= minimum_net_profit_usd:
                decision = "WATCH"
                reason = "Estimated net profit is positive. Keep monitoring; not live-trade ready."
            else:
                decision = "SKIP"
                reason = "Estimated net profit is too small after estimated fees, gas, slippage, and MEV buffer."

            net_opportunities.append(
                NetOpportunity(
                    chain=gross.chain,
                    pair=gross.pair,
                    best_buy_dex=gross.best_buy_dex,
                    best_sell_dex=gross.best_sell_dex,
                    trade_size_usd=trade_size_usd,
                    gross_spread_pct=gross.gross_spread_pct,
                    estimated_gross_profit_usd=gross_profit_usd,
                    estimated_cost_usd=estimated_cost_usd,
                    estimated_net_profit_usd=net_profit_usd,
                    estimated_net_profit_pct=net_profit_pct,
                    decision=decision,
                    reason=reason,
                )
            )

        return net_opportunities
