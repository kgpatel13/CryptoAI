from __future__ import annotations

from decimal import Decimal
from datetime import datetime
from uuid import uuid4

from app.portfolio.models import Holding, PortfolioSnapshot, Position, PositionStatus

try:
    from app.marketdata.market_service import MarketDataService
except Exception:
    MarketDataService = None

try:
    from app.risk.risk_service import RiskService
except Exception:
    RiskService = None

try:
    from app.portfolio.persistence_service import PortfolioPersistenceService
except Exception:
    PortfolioPersistenceService = None


class PortfolioService:
    """Simulated portfolio engine with optional SQLite persistence."""

    def __init__(self) -> None:
        self.initial_cash_usd = Decimal("10000")
        self.realized_pnl_usd = Decimal("0")

    def get_snapshot(self, persist: bool = True) -> PortfolioSnapshot:
        prices = self._load_prices()
        holdings = self._build_default_holdings(prices)
        positions = self._build_simulated_positions(prices)

        holdings_value = sum((h.market_value_usd for h in holdings), Decimal("0"))
        positions_value = sum((p.notional_usd for p in positions if p.status == PositionStatus.OPEN), Decimal("0"))
        unrealized_pnl = (
            sum((h.unrealized_pnl_usd for h in holdings), Decimal("0"))
            + sum((p.unrealized_pnl_usd for p in positions), Decimal("0"))
        )

        total_value = self.initial_cash_usd + holdings_value + unrealized_pnl
        total_pnl = self.realized_pnl_usd + unrealized_pnl

        snapshot = PortfolioSnapshot(
            portfolio_name="CryptoAI Simulated Portfolio",
            cash_usd=self.initial_cash_usd,
            holdings_value_usd=holdings_value,
            open_positions_value_usd=positions_value,
            total_value_usd=total_value,
            realized_pnl_usd=self.realized_pnl_usd,
            unrealized_pnl_usd=unrealized_pnl,
            total_pnl_usd=total_pnl,
            open_positions=sum(1 for p in positions if p.status == PositionStatus.OPEN),
            closed_positions=sum(1 for p in positions if p.status == PositionStatus.CLOSED),
            holdings=holdings,
            positions=positions,
        )

        if persist and PortfolioPersistenceService is not None:
            try:
                PortfolioPersistenceService().save_snapshot(snapshot)
            except Exception:
                pass

        return snapshot

    def _load_prices(self) -> dict[str, Decimal]:
        fallback = {
            "ETH": Decimal("3500"),
            "BTC": Decimal("100000"),
            "USDC": Decimal("1"),
        }

        if MarketDataService is None:
            return fallback

        try:
            rows = MarketDataService().get_registered_asset_prices()
        except Exception:
            return fallback

        prices = dict(fallback)

        for row in rows:
            symbol = str(getattr(row, "symbol", "")).upper()
            price = getattr(row, "usd_price", None)
            if not symbol or price is None:
                continue

            prices[symbol] = Decimal(str(price))
            if symbol == "ETH":
                prices["WETH"] = Decimal(str(price))
            if symbol == "BTC":
                prices["WBTC"] = Decimal(str(price))
                prices["CBBTC"] = Decimal(str(price))

        return prices

    def _build_default_holdings(self, prices: dict[str, Decimal]) -> list[Holding]:
        raw = [
            ("base", "USDC", Decimal("2500"), Decimal("1")),
            ("base", "WETH", Decimal("0.50"), Decimal("3200")),
            ("base", "cbBTC", Decimal("0.01"), Decimal("95000")),
        ]

        holdings: list[Holding] = []
        for chain, symbol, qty, avg_cost in raw:
            current = self._price_for(symbol, prices)
            market_value = qty * current
            cost_value = qty * avg_cost
            pnl = market_value - cost_value
            pnl_pct = (pnl / cost_value * Decimal("100")) if cost_value else Decimal("0")

            holdings.append(
                Holding(
                    chain=chain,
                    symbol=symbol,
                    quantity=qty,
                    avg_cost_usd=avg_cost,
                    current_price_usd=current,
                    market_value_usd=market_value,
                    unrealized_pnl_usd=pnl,
                    unrealized_pnl_pct=pnl_pct,
                )
            )

        return holdings

    def _build_simulated_positions(self, prices: dict[str, Decimal]) -> list[Position]:
        positions: list[Position] = []

        if RiskService is not None:
            try:
                assessments = RiskService().assess_ranked_signals()
            except Exception:
                assessments = []

            for assessment in assessments[:5]:
                decision = getattr(assessment, "decision", "")
                decision_value = decision.value if hasattr(decision, "value") else str(decision)
                max_notional = Decimal(str(getattr(assessment, "max_allowed_notional_usd", "0")))

                if decision_value != "APPROVED_FOR_PAPER" or max_notional <= 0:
                    continue

                pair = str(getattr(assessment, "pair", "WETH/USDC"))
                base = pair.split("/")[0] if "/" in pair else "WETH"
                current = self._price_for(base, prices)
                entry = current * Decimal("0.999")
                quantity = max_notional / current if current else Decimal("0")
                pnl = (current - entry) * quantity
                pnl_pct = (pnl / max_notional * Decimal("100")) if max_notional else Decimal("0")

                positions.append(
                    Position(
                        position_id=str(uuid4())[:8],
                        strategy_name=str(getattr(assessment, "strategy_name", "Strategy")),
                        chain=str(getattr(assessment, "chain", "base")),
                        pair=pair,
                        base_symbol=base,
                        quote_symbol="USDC",
                        quantity=quantity,
                        entry_price_usd=entry,
                        current_price_usd=current,
                        notional_usd=max_notional,
                        unrealized_pnl_usd=pnl,
                        unrealized_pnl_pct=pnl_pct,
                        status=PositionStatus.OPEN,
                        opened_at=datetime.utcnow().isoformat(timespec="seconds") + "Z",
                    )
                )

        return positions

    @staticmethod
    def _price_for(symbol: str, prices: dict[str, Decimal]) -> Decimal:
        normalized = symbol.upper()
        aliases = {
            "WETH": "ETH",
            "WBTC": "BTC",
            "CBBTC": "BTC",
        }

        if normalized in prices:
            return prices[normalized]

        alias = aliases.get(normalized)
        if alias and alias in prices:
            return prices[alias]

        return Decimal("0")
