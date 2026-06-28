from decimal import Decimal

from app.papertrading.models import PaperTrade
from app.scanner.opportunity_scanner import NetOpportunity


class PaperTrader:
    def __init__(self, minimum_net_profit_usd: Decimal = Decimal("1.00")) -> None:
        self.minimum_net_profit_usd = minimum_net_profit_usd

    def evaluate(self, opportunities: list[NetOpportunity]) -> list[PaperTrade]:
        trades: list[PaperTrade] = []

        for opportunity in opportunities:
            if opportunity.estimated_net_profit_usd >= self.minimum_net_profit_usd:
                status = "PAPER_EXECUTED"
                reason = "Simulated trade only. Passed minimum net profit threshold."
            else:
                status = "PAPER_SKIPPED"
                reason = "Simulated skip. Net profit below threshold."

            trades.append(
                PaperTrade.now(
                    chain=opportunity.chain,
                    pair=opportunity.pair,
                    buy_dex=opportunity.best_buy_dex,
                    sell_dex=opportunity.best_sell_dex,
                    trade_size_usd=opportunity.trade_size_usd,
                    estimated_net_profit_usd=opportunity.estimated_net_profit_usd,
                    estimated_net_profit_pct=opportunity.estimated_net_profit_pct,
                    status=status,
                    reason=reason,
                )
            )

        return trades
