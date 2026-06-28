from __future__ import annotations

from decimal import Decimal

from app.strategy.base_strategy import BaseStrategy
from app.strategy.models import StrategyAction, StrategySignal


class ArbitrageStrategy(BaseStrategy):
    """Paper-only arbitrage strategy.

    v2.7 consumes OpportunityExplorer decisions first. This fixes the issue where
    paper orders had pair '-' and estimated_edge_pct null.
    """

    name = "DEX Arbitrage Strategy"

    def __init__(
        self,
        min_net_edge_pct: Decimal = Decimal("0.30"),
        min_watch_edge_pct: Decimal = Decimal("0.05"),
        min_confidence_score: int = 60,
    ) -> None:
        self.min_net_edge_pct = min_net_edge_pct
        self.min_watch_edge_pct = min_watch_edge_pct
        self.min_confidence_score = min_confidence_score

    def generate_signals(self) -> list[StrategySignal]:
        explorer_signals = self._signals_from_opportunity_explorer()
        if explorer_signals:
            return explorer_signals

        legacy_signals = self._signals_from_legacy_scanner()
        if legacy_signals:
            return legacy_signals

        return [
            StrategySignal(
                strategy_name=self.name,
                chain="base",
                pair="-",
                action=StrategyAction.WATCH,
                confidence_score=0,
                expected_edge_pct=None,
                reason="No opportunity decisions or legacy gross opportunities found.",
            )
        ]

    def _signals_from_opportunity_explorer(self) -> list[StrategySignal]:
        try:
            from app.opportunities.opportunity_explorer import OpportunityExplorerService
        except Exception:
            return []

        try:
            decisions = OpportunityExplorerService().scan()
        except Exception:
            return []

        signals: list[StrategySignal] = []

        for decision in decisions:
            pair = str(getattr(decision, "pair", "-"))
            chain = str(getattr(decision, "chain", "base"))
            net_edge = self._to_decimal(getattr(decision, "estimated_net_edge_pct", None))
            readiness_score = int(getattr(decision, "readiness_score", 0) or 0)
            decision_value = getattr(getattr(decision, "decision", ""), "value", str(getattr(decision, "decision", "")))
            reason = str(getattr(decision, "reason", ""))

            if pair == "-" or net_edge is None:
                signals.append(
                    StrategySignal(
                        strategy_name=self.name,
                        chain=chain,
                        pair=pair,
                        action=StrategyAction.WATCH,
                        confidence_score=readiness_score,
                        expected_edge_pct=net_edge,
                        reason=f"Opportunity Explorer: {reason}",
                    )
                )
                continue

            if decision_value == "BUY" and net_edge >= self.min_net_edge_pct:
                action = StrategyAction.READY_FOR_PAPER
                final_reason = (
                    f"Opportunity Explorer BUY: net edge {net_edge:.4f}% "
                    f">= threshold {self.min_net_edge_pct}%."
                )
            elif net_edge >= self.min_watch_edge_pct:
                action = StrategyAction.WATCH
                final_reason = (
                    f"Opportunity Explorer WATCH: net edge {net_edge:.4f}% "
                    f"is positive but below BUY threshold {self.min_net_edge_pct}%."
                )
            else:
                action = StrategyAction.SKIP
                final_reason = f"Opportunity Explorer SKIP: {reason}"

            signals.append(
                StrategySignal(
                    strategy_name=self.name,
                    chain=chain,
                    pair=pair,
                    action=action,
                    confidence_score=readiness_score,
                    expected_edge_pct=net_edge,
                    reason=final_reason,
                )
            )

        return signals

    def _signals_from_legacy_scanner(self) -> list[StrategySignal]:
        try:
            from app.scanner.opportunity_scanner import OpportunityScanner
            opportunities = OpportunityScanner().scan_base_gross_opportunities()
        except Exception:
            return []

        signals: list[StrategySignal] = []

        for opp in opportunities:
            spread = self._to_decimal(getattr(opp, "gross_spread_pct", None))
            pair = str(getattr(opp, "pair", "-"))
            chain = str(getattr(opp, "chain", "base"))

            if spread is None:
                continue

            confidence = self._score_edge(spread)

            if spread >= self.min_net_edge_pct:
                action = StrategyAction.READY_FOR_PAPER
                reason = f"Legacy gross spread {spread:.4f}% is above paper threshold."
            elif spread >= self.min_watch_edge_pct:
                action = StrategyAction.WATCH
                reason = f"Legacy gross spread {spread:.4f}% is positive but below paper threshold."
            else:
                action = StrategyAction.SKIP
                reason = f"Legacy gross spread {spread:.4f}% is too low."

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

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _score_edge(edge_pct: Decimal | None) -> int:
        if edge_pct is None or edge_pct <= 0:
            return 0
        return int(max(1, min(95, edge_pct * Decimal("200"))))
