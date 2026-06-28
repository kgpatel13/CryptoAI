from __future__ import annotations

from app.strategy.arbitrage_strategy import ArbitrageStrategy
from app.strategy.models import StrategySignal


class StrategyService:
    """Coordinates all enabled strategy plugins."""

    def __init__(self) -> None:
        self.strategies = [
            ArbitrageStrategy(),
        ]

    def get_all_signals(self) -> list[StrategySignal]:
        signals: list[StrategySignal] = []

        for strategy in self.strategies:
            try:
                signals.extend(strategy.generate_signals())
            except Exception as exc:
                signals.append(
                    StrategySignal(
                        strategy_name=getattr(strategy, "name", strategy.__class__.__name__),
                        chain="-",
                        pair="-",
                        action="SKIP",
                        confidence_score=0,
                        expected_edge_pct=None,
                        reason=f"Strategy failed: {exc}",
                    )
                )

        return signals
