from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from app.strategy.models import StrategyConfig


DEFAULT_STRATEGIES = {
    "arbitrage": {
        "name": "DEX Arbitrage Strategy",
        "enabled": True,
        "weight": "1.00",
        "min_confidence": 50,
        "max_signals_per_cycle": 10,
        "mode": "paper",
        "notes": "Primary strategy. Uses Opportunity Explorer and existing multi-DEX scanner output.",
    },
    "momentum": {
        "name": "Momentum Strategy",
        "enabled": False,
        "weight": "0.70",
        "min_confidence": 65,
        "max_signals_per_cycle": 5,
        "mode": "research",
        "notes": "Research placeholder. Will require historical candles and trend features.",
    },
    "mean_reversion": {
        "name": "Mean Reversion Strategy",
        "enabled": False,
        "weight": "0.70",
        "min_confidence": 65,
        "max_signals_per_cycle": 5,
        "mode": "research",
        "notes": "Research placeholder. Will require volatility bands and fair-value features.",
    },
    "breakout": {
        "name": "Breakout Strategy",
        "enabled": False,
        "weight": "0.70",
        "min_confidence": 65,
        "max_signals_per_cycle": 5,
        "mode": "research",
        "notes": "Research placeholder. Will require range, volume, and volatility expansion features.",
    },
    "ai_ranked": {
        "name": "AI Ranked Strategy",
        "enabled": False,
        "weight": "0.80",
        "min_confidence": 70,
        "max_signals_per_cycle": 5,
        "mode": "research",
        "notes": "Research placeholder. AI advises only; risk engine remains final authority.",
    },
}


class StrategyConfigService:
    """Loads strategy configuration without requiring PyYAML.

    The committed file is JSON so the project keeps zero extra dependency risk.
    Operators can change strategy enablement and weights without editing code.
    """

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path("config") / "strategies.json"

    def load(self) -> dict[str, StrategyConfig]:
        raw = self._read_raw()
        configs: dict[str, StrategyConfig] = {}
        for strategy_id, payload in raw.items():
            merged = dict(DEFAULT_STRATEGIES.get(strategy_id, {}))
            if isinstance(payload, dict):
                merged.update(payload)
            configs[strategy_id] = StrategyConfig(
                strategy_id=strategy_id,
                name=str(merged.get("name", strategy_id)),
                enabled=bool(merged.get("enabled", False)),
                weight=self._decimal(merged.get("weight", "1.0")),
                min_confidence=int(merged.get("min_confidence", 0) or 0),
                max_signals_per_cycle=max(1, int(merged.get("max_signals_per_cycle", 10) or 10)),
                mode=str(merged.get("mode", "paper")),
                notes=str(merged.get("notes", "")),
            )
        return configs

    def _read_raw(self) -> dict:
        if not self.path.exists():
            return DEFAULT_STRATEGIES
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8", errors="replace"))
            strategies = payload.get("strategies", payload)
            if not isinstance(strategies, dict):
                return DEFAULT_STRATEGIES
            merged = dict(DEFAULT_STRATEGIES)
            for key, value in strategies.items():
                if isinstance(value, dict):
                    base = dict(merged.get(key, {}))
                    base.update(value)
                    merged[key] = base
            return merged
        except Exception:
            return DEFAULT_STRATEGIES

    @staticmethod
    def _decimal(value) -> Decimal:
        try:
            return Decimal(str(value))
        except Exception:
            return Decimal("1.0")
