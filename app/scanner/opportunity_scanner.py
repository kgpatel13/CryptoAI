from dataclasses import dataclass
from decimal import Decimal

from app.marketdata.market_service import MarketDataService
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
class NetOpportunityEstimate:
    chain: str
    pair: str
    buy_dex: str
    sell_dex: str
    notional_usd: Decimal
    gross_spread_pct: Decimal
    estimated_gross_profit_usd: Decimal
    estimated_total_cost_usd: Decimal
    estimated_net_profit_usd: Decimal
    estimated_net_profit_pct: Decimal
    decision: str
    reason: str


class OpportunityScanner:
    """Scans opportunities and produces gross and estimated-net views.

    This is still read-only research code. It does not trade, sign transactions,
    or connect to a wallet.
    """

    def __init__(self) -> None:
        self.quote_service = QuoteService()
        self.market_data_service = MarketDataService()

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

    def scan_base_net_estimates(self) -> list[NetOpportunityEstimate]:
        """Estimate net profitability using conservative placeholder costs.

        These are NOT execution-ready signals. They are research estimates used
        to teach the engine to reject weak spreads before we add deeper slippage,
        pool liquidity, gas simulation, and MEV modeling.
        """
        gross_opportunities = self.scan_base_gross_opportunities()
        estimates: list[NetOpportunityEstimate] = []

        for opp in gross_opportunities:
            notional_usd = self._estimate_notional_usd(opp.pair)
            gross_profit_usd = notional_usd * (opp.gross_spread_pct / Decimal("100"))

            estimated_total_cost_usd = self._estimate_total_cost_usd(notional_usd)
            net_profit_usd = gross_profit_usd - estimated_total_cost_usd
            net_profit_pct = (net_profit_usd / notional_usd) * Decimal("100") if notional_usd > 0 else Decimal("0")

            if net_profit_usd > Decimal("1") and net_profit_pct > Decimal("0.05"):
                decision = "WATCH"
                reason = "Estimated net is positive, but execution risk checks are not complete."
            else:
                decision = "SKIP"
                reason = "Estimated costs consume the spread or net edge is too small."

            estimates.append(
                NetOpportunityEstimate(
                    chain=opp.chain,
                    pair=opp.pair,
                    buy_dex=opp.best_buy_dex,
                    sell_dex=opp.best_sell_dex,
                    notional_usd=notional_usd,
                    gross_spread_pct=opp.gross_spread_pct,
                    estimated_gross_profit_usd=gross_profit_usd,
                    estimated_total_cost_usd=estimated_total_cost_usd,
                    estimated_net_profit_usd=net_profit_usd,
                    estimated_net_profit_pct=net_profit_pct,
                    decision=decision,
                    reason=reason,
                )
            )

        return estimates

    def _estimate_notional_usd(self, pair: str) -> Decimal:
        # For WETH/USDC, amount is 1 WETH. Use ETH/USD from market data.
        if pair.upper() == "WETH/USDC":
            return self._get_market_price("ethereum") or Decimal("0")

        # For cbBTC/USDC, amount is 0.01 BTC in our current quote service.
        if pair.upper() in {"CBBTC/USDC", "WBTC/USDC"}:
            btc_price = self._get_market_price("bitcoin") or Decimal("0")
            return btc_price * Decimal("0.01")

        # USDC/WETH quote uses 1000 USDC in our current quote service.
        if pair.upper() == "USDC/WETH":
            return Decimal("1000")

        return Decimal("0")

    def _get_market_price(self, coingecko_id: str) -> Decimal | None:
        try:
            for price in self.market_data_service.get_registered_asset_prices():
                if price.coingecko_id == coingecko_id:
                    return price.usd_price
        except Exception:
            return None
        return None

    @staticmethod
    def _estimate_total_cost_usd(notional_usd: Decimal) -> Decimal:
        # Conservative first-pass estimate for research only:
        # - two DEX legs fee/slippage buffer: 0.70%
        # - Base network + transaction overhead placeholder: $0.25
        # Later we will replace this with pool-specific fee, slippage, and gas simulation.
        fee_and_slippage_buffer = notional_usd * Decimal("0.007")
        gas_and_overhead = Decimal("0.25")
        return fee_and_slippage_buffer + gas_and_overhead
