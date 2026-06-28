from __future__ import annotations

from abc import ABC, abstractmethod

from app.strategy.models import StrategySignal


class BaseStrategy(ABC):
    """Base class for all strategy plugins."""

    name: str

    @abstractmethod
    def generate_signals(self) -> list[StrategySignal]:
        """Return strategy signals.

        Signals are read-only. They do not execute trades.
        """
        raise NotImplementedError
