from __future__ import annotations

from app.strategy.base_strategy import BaseStrategy
from app.strategy.models import StrategySignal


class ResearchPlaceholderStrategy(BaseStrategy):
    """Disabled-by-default research strategy placeholder.

    It intentionally emits no tradeable signals. This lets CryptoAI expose a real
    strategy registry today without pretending unvalidated strategies are ready.
    """

    def __init__(self, name: str, strategy_id: str) -> None:
        self.name = name
        self.strategy_id = strategy_id

    def generate_signals(self) -> list[StrategySignal]:
        return []


class MomentumStrategy(ResearchPlaceholderStrategy):
    def __init__(self) -> None:
        super().__init__("Momentum Strategy", "momentum")


class MeanReversionStrategy(ResearchPlaceholderStrategy):
    def __init__(self) -> None:
        super().__init__("Mean Reversion Strategy", "mean_reversion")


class BreakoutStrategy(ResearchPlaceholderStrategy):
    def __init__(self) -> None:
        super().__init__("Breakout Strategy", "breakout")


class AiRankedStrategy(ResearchPlaceholderStrategy):
    def __init__(self) -> None:
        super().__init__("AI Ranked Strategy", "ai_ranked")
