from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Callable

from app.strategy.arbitrage_strategy import ArbitrageStrategy
from app.strategy.models import StrategyConfig, StrategyDescriptor, StrategyHealth
from app.strategy.placeholder_strategies import (
    AiRankedStrategy,
    BreakoutStrategy,
    MeanReversionStrategy,
    MomentumStrategy,
)
from app.strategy.strategy_config import StrategyConfigService


@dataclass(frozen=True)
class RegisteredStrategy:
    strategy_id: str
    name: str
    enabled: bool
    weight: Decimal
    min_confidence: int
    max_signals_per_cycle: int
    mode: str
    notes: str
    strategy: object | None
    health: StrategyHealth
    reason: str = ""


class StrategyRegistry:
    """Central strategy plugin registry.

    v3.6 keeps discovery explicit and deterministic. Future releases can add
    dynamic module discovery after the plugin contract is stable.
    """

    FACTORIES: dict[str, Callable[[], object]] = {
        "arbitrage": ArbitrageStrategy,
        "momentum": MomentumStrategy,
        "mean_reversion": MeanReversionStrategy,
        "breakout": BreakoutStrategy,
        "ai_ranked": AiRankedStrategy,
    }

    def __init__(self, config_service: StrategyConfigService | None = None) -> None:
        self.config_service = config_service or StrategyConfigService()

    def list_strategies(self) -> list[RegisteredStrategy]:
        configs = self.config_service.load()
        rows: list[RegisteredStrategy] = []
        for strategy_id, config in configs.items():
            rows.append(self._register_one(strategy_id, config))
        return rows

    def enabled_strategies(self) -> list[RegisteredStrategy]:
        return [row for row in self.list_strategies() if row.enabled and row.strategy is not None]

    def descriptors(self) -> list[StrategyDescriptor]:
        descriptors: list[StrategyDescriptor] = []
        for row in self.list_strategies():
            descriptors.append(
                StrategyDescriptor(
                    strategy_id=row.strategy_id,
                    name=row.name,
                    enabled=row.enabled,
                    health=row.health,
                    weight=row.weight,
                    class_name=row.strategy.__class__.__name__ if row.strategy is not None else "-",
                    reason=row.reason,
                )
            )
        return descriptors

    def _register_one(self, strategy_id: str, config: StrategyConfig) -> RegisteredStrategy:
        factory = self.FACTORIES.get(strategy_id)
        if factory is None:
            return RegisteredStrategy(
                strategy_id=strategy_id,
                name=config.name,
                enabled=False,
                weight=config.weight,
                min_confidence=config.min_confidence,
                max_signals_per_cycle=config.max_signals_per_cycle,
                mode=config.mode,
                notes=config.notes,
                strategy=None,
                health=StrategyHealth.ERROR,
                reason="No factory registered for strategy_id.",
            )

        if not config.enabled:
            return RegisteredStrategy(
                strategy_id=strategy_id,
                name=config.name,
                enabled=False,
                weight=config.weight,
                min_confidence=config.min_confidence,
                max_signals_per_cycle=config.max_signals_per_cycle,
                mode=config.mode,
                notes=config.notes,
                strategy=None,
                health=StrategyHealth.DISABLED,
                reason="Disabled in config/strategies.json.",
            )

        try:
            strategy = factory()
            return RegisteredStrategy(
                strategy_id=strategy_id,
                name=getattr(strategy, "name", config.name),
                enabled=True,
                weight=config.weight,
                min_confidence=config.min_confidence,
                max_signals_per_cycle=config.max_signals_per_cycle,
                mode=config.mode,
                notes=config.notes,
                strategy=strategy,
                health=StrategyHealth.ACTIVE,
                reason="Registered successfully.",
            )
        except Exception as exc:
            return RegisteredStrategy(
                strategy_id=strategy_id,
                name=config.name,
                enabled=False,
                weight=config.weight,
                min_confidence=config.min_confidence,
                max_signals_per_cycle=config.max_signals_per_cycle,
                mode=config.mode,
                notes=config.notes,
                strategy=None,
                health=StrategyHealth.ERROR,
                reason=f"Registration failed: {exc}",
            )
