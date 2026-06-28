from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from app.strategy.models import RankedStrategySignal, StrategyAction, StrategySignal
from app.strategy.strategy_registry import StrategyRegistry


class StrategyService:
    """Coordinates enabled strategy plugins and ranks their signals.

    v3.6 turns CryptoAI into a strategy platform. Strategies produce read-only
    signals; downstream AI/risk/execution modules still decide whether a signal
    is safe to act on.
    """

    def __init__(self, registry: StrategyRegistry | None = None, data_dir: Path | None = None) -> None:
        self.registry = registry or StrategyRegistry()
        self.data_dir = data_dir or Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.signal_file = self.data_dir / "strategy_signals.jsonl"
        self.ranked_signal_file = self.data_dir / "strategy_ranked_signals.jsonl"

    def get_all_signals(self) -> list[StrategySignal]:
        signals: list[StrategySignal] = []
        for registered in self.registry.enabled_strategies():
            try:
                raw_signals = list(registered.strategy.generate_signals()) if registered.strategy is not None else []
                limited = raw_signals[: registered.max_signals_per_cycle]
                for signal in limited:
                    signals.append(self._normalize_signal(signal, registered))
            except Exception as exc:
                signals.append(
                    StrategySignal(
                        strategy_name=registered.name,
                        chain="-",
                        pair="-",
                        action=StrategyAction.SKIP,
                        confidence_score=0,
                        expected_edge_pct=None,
                        reason=f"Strategy failed: {exc}",
                        source="strategy_manager",
                        signal_id=self._signal_id(registered.strategy_id, "-", "-", "error"),
                        features={"strategy_id": registered.strategy_id, "health": "ERROR"},
                    )
                )
        self._persist_signals(signals)
        return signals

    def ranked_signals(self) -> list[RankedStrategySignal]:
        ranked: list[RankedStrategySignal] = []
        registry_by_name = {row.name: row for row in self.registry.list_strategies()}
        for signal in self.get_all_signals():
            registered = registry_by_name.get(signal.strategy_name)
            weight = registered.weight if registered is not None else Decimal("1.0")
            score = self._rank_score(signal, weight)
            strategy_id = str(signal.features.get("strategy_id", "unknown")) if signal.features else "unknown"
            ranked.append(
                RankedStrategySignal(
                    rank=0,
                    strategy_id=strategy_id,
                    strategy_name=signal.strategy_name,
                    chain=signal.chain,
                    pair=signal.pair,
                    action=signal.action,
                    confidence_score=signal.confidence_score,
                    expected_edge_pct=signal.expected_edge_pct,
                    rank_score=score,
                    reason=signal.reason,
                    features=signal.features,
                )
            )
        ranked = sorted(ranked, key=lambda item: item.rank_score, reverse=True)
        ranked = [
            RankedStrategySignal(
                rank=index + 1,
                strategy_id=item.strategy_id,
                strategy_name=item.strategy_name,
                chain=item.chain,
                pair=item.pair,
                action=item.action,
                confidence_score=item.confidence_score,
                expected_edge_pct=item.expected_edge_pct,
                rank_score=item.rank_score,
                reason=item.reason,
                source=item.source,
                features=item.features,
            )
            for index, item in enumerate(ranked)
        ]
        self._persist_ranked_signals(ranked)
        return ranked

    def strategy_descriptors(self) -> list[dict]:
        rows = []
        for descriptor in self.registry.descriptors():
            rows.append(
                {
                    "strategy_id": descriptor.strategy_id,
                    "name": descriptor.name,
                    "enabled": descriptor.enabled,
                    "health": descriptor.health.value if hasattr(descriptor.health, "value") else str(descriptor.health),
                    "weight": str(descriptor.weight),
                    "class_name": descriptor.class_name,
                    "reason": descriptor.reason,
                }
            )
        return rows

    def _normalize_signal(self, signal: StrategySignal, registered) -> StrategySignal:
        confidence = max(0, min(100, int(signal.confidence_score or 0)))
        action = signal.action if isinstance(signal.action, StrategyAction) else StrategyAction(str(signal.action))
        features = dict(signal.features or {})
        features.update(
            {
                "strategy_id": registered.strategy_id,
                "strategy_weight": str(registered.weight),
                "strategy_mode": registered.mode,
                "min_confidence": registered.min_confidence,
            }
        )
        if confidence < registered.min_confidence and action == StrategyAction.READY_FOR_PAPER:
            action = StrategyAction.WATCH
            reason = f"Strategy confidence {confidence} below configured minimum {registered.min_confidence}; downgraded to WATCH. Original: {signal.reason}"
        else:
            reason = signal.reason
        return StrategySignal(
            strategy_name=registered.name,
            chain=signal.chain,
            pair=signal.pair,
            action=action,
            confidence_score=confidence,
            expected_edge_pct=signal.expected_edge_pct,
            reason=reason,
            source=signal.source,
            signal_id=signal.signal_id or self._signal_id(registered.strategy_id, signal.chain, signal.pair, action.value),
            rank_score=self._rank_score(signal, registered.weight),
            features=features,
        )

    @staticmethod
    def _rank_score(signal: StrategySignal, weight: Decimal) -> int:
        action = signal.action.value if hasattr(signal.action, "value") else str(signal.action)
        base = 0
        if action == StrategyAction.READY_FOR_PAPER.value:
            base += 45
        elif action == StrategyAction.WATCH.value:
            base += 20
        elif action == StrategyAction.SKIP.value:
            base -= 15
        base += min(40, max(0, int(signal.confidence_score or 0)) // 2)
        edge = signal.expected_edge_pct
        if edge is None:
            base -= 10
        else:
            try:
                edge_decimal = Decimal(str(edge))
                if edge_decimal > 0:
                    base += min(25, int(edge_decimal * Decimal("30")))
                if edge_decimal > Decimal("3"):
                    base -= 15  # suspicious edge guard
            except Exception:
                base -= 10
        weighted = Decimal(max(0, base)) * weight
        return int(max(0, min(100, weighted)))

    def _persist_signals(self, signals: list[StrategySignal]) -> None:
        timestamp = self._utc_now()
        with self.signal_file.open("a", encoding="utf-8") as fh:
            for signal in signals:
                fh.write(json.dumps(self._signal_to_dict(signal, timestamp)) + "\n")

    def _persist_ranked_signals(self, signals: list[RankedStrategySignal]) -> None:
        timestamp = self._utc_now()
        with self.ranked_signal_file.open("a", encoding="utf-8") as fh:
            for signal in signals:
                payload = {
                    "timestamp": timestamp,
                    "rank": signal.rank,
                    "strategy_id": signal.strategy_id,
                    "strategy_name": signal.strategy_name,
                    "chain": signal.chain,
                    "pair": signal.pair,
                    "action": signal.action.value if hasattr(signal.action, "value") else str(signal.action),
                    "confidence_score": signal.confidence_score,
                    "expected_edge_pct": str(signal.expected_edge_pct) if signal.expected_edge_pct is not None else None,
                    "rank_score": signal.rank_score,
                    "reason": signal.reason,
                    "features": signal.features,
                }
                fh.write(json.dumps(payload) + "\n")

    @staticmethod
    def _signal_to_dict(signal: StrategySignal, timestamp: str) -> dict:
        return {
            "timestamp": timestamp,
            "signal_id": signal.signal_id,
            "strategy_name": signal.strategy_name,
            "chain": signal.chain,
            "pair": signal.pair,
            "action": signal.action.value if hasattr(signal.action, "value") else str(signal.action),
            "confidence_score": signal.confidence_score,
            "expected_edge_pct": str(signal.expected_edge_pct) if signal.expected_edge_pct is not None else None,
            "rank_score": signal.rank_score,
            "reason": signal.reason,
            "source": signal.source,
            "features": signal.features,
        }

    @staticmethod
    def _signal_id(strategy_id: str, chain: str, pair: str, action: str) -> str:
        safe_pair = pair.replace("/", "-") if pair else "-"
        return f"{strategy_id}:{chain}:{safe_pair}:{action}"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
