from __future__ import annotations

from decimal import Decimal

from app.strategy.base_strategy import BaseStrategy
from app.strategy.models import StrategyAction, StrategySignal


class ArbitrageStrategy(BaseStrategy):
    """First read-only arbitrage strategy plugin.

    This strategy consumes the existing scanner layer and converts raw
    opportunities into standardized strategy signals.

    Live execution is intentionally disabled.
    """

    name = "DEX Arbitrage Strategy"

    def __init__(
        self,
        min_gross_spread_pct: Decimal = Decimal("0.10"),
        min_confidence_score: int = 60,
    ) -> None:
        self.min_gross_spread_pct = min_gross_spread_pct
        self.min_confidence_score = min_confidence_score

    def generate_signals(self) -> list[StrategySignal]:
        opportunities = self._load_opportunities()
        signals: list[StrategySignal] = []

        if not opportunities:
            return [
                StrategySignal(
                    strategy_name=self.name,
                    chain="base",
                    pair="-",
                    action=StrategyAction.WATCH,
                    confidence_score=0,
                    expected_edge_pct=None,
                    reason="No qualifying gross opportunities found right now.",
                )
            ]

        for opp in opportunities:
            spread = self._get_decimal(opp, "gross_spread_pct")
            pair = str(getattr(opp, "pair", "-"))
            chain = str(getattr(opp, "chain", "base"))

            if spread is None:
                signals.append(
                    StrategySignal(
                        strategy_name=self.name,
                        chain=chain,
                        pair=pair,
                        action=StrategyAction.SKIP,
                        confidence_score=0,
                        expected_edge_pct=None,
                        reason="Opportunity missing spread data.",
                    )
                )
                continue

            confidence = self._score_spread(spread)

            if spread < self.min_gross_spread_pct:
                action = StrategyAction.SKIP
                reason = (
                    f"Gross spread {spread:.4f}% is below threshold "
                    f"{self.min_gross_spread_pct}%."
                )
            elif confidence >= self.min_confidence_score:
                action = StrategyAction.READY_FOR_PAPER
                reason = (
                    "Gross spread is high enough for paper-trading simulation. "
                    "Still not approved for live trading."
                )
            else:
                action = StrategyAction.WATCH
                reason = "Potential opportunity, but confidence is not high enough."

            signals.append(
                StrategySignal(
                    strategy_name=self.name,
                    chain=chain,
                    pair=pair,
                    action=action,
                    confidence_score=confidence,
                    expected_edge_pct=spread,
                    reason=reason,
                )
            )

        return signals

    def _load_opportunities(self) -> list:
        try:
            from app.scanner.opportunity_scanner import OpportunityScanner

            return OpportunityScanner().scan_base_gross_opportunities()
        except Exception:
            return []

    @staticmethod
    def _get_decimal(obj, attr: str) -> Decimal | None:
        try:
            value = getattr(obj, attr)
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _score_spread(spread_pct: Decimal) -> int:
        if spread_pct <= 0:
            return 0

        # Simple v1 scoring. Later AI/risk engines will replace this.
        score = int(min(95, max(1, spread_pct * Decimal("250"))))
        return score
