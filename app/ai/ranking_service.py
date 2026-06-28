from __future__ import annotations

from decimal import Decimal

from app.ai.models import AiRankedSignal, AiRecommendation

try:
    from app.strategy.strategy_service import StrategyService
except Exception:
    StrategyService = None


class AiRankingService:
    """First version of the AI ranking engine.

    v1.2 is deterministic and explainable. It does not call an LLM yet.
    Later, this service can use OpenAI/Claude as a second-pass reviewer,
    but the hard risk rules should remain deterministic.
    """

    def rank_strategy_signals(self) -> list[AiRankedSignal]:
        if StrategyService is None:
            return [
                AiRankedSignal(
                    strategy_name="AI Ranking",
                    chain="-",
                    pair="-",
                    source_action="UNAVAILABLE",
                    confidence_score=0,
                    expected_edge_pct=None,
                    ai_score=0,
                    recommendation=AiRecommendation.NEEDS_MORE_DATA,
                    reasoning="StrategyService is not available.",
                )
            ]

        try:
            signals = StrategyService().get_all_signals()
        except Exception as exc:
            return [
                AiRankedSignal(
                    strategy_name="AI Ranking",
                    chain="-",
                    pair="-",
                    source_action="ERROR",
                    confidence_score=0,
                    expected_edge_pct=None,
                    ai_score=0,
                    recommendation=AiRecommendation.NEEDS_MORE_DATA,
                    reasoning=f"Could not load strategy signals: {exc}",
                )
            ]

        ranked: list[AiRankedSignal] = []
        for signal in signals:
            ranked.append(self._rank_one(signal))

        return sorted(ranked, key=lambda x: x.ai_score, reverse=True)

    def _rank_one(self, signal) -> AiRankedSignal:
        strategy_name = str(getattr(signal, "strategy_name", "Strategy"))
        chain = str(getattr(signal, "chain", "-"))
        pair = str(getattr(signal, "pair", "-"))
        action_obj = getattr(signal, "action", "")
        source_action = action_obj.value if hasattr(action_obj, "value") else str(action_obj)
        confidence = int(getattr(signal, "confidence_score", 0) or 0)
        edge = getattr(signal, "expected_edge_pct", None)

        edge_decimal = self._to_decimal(edge)

        ai_score = self._score(
            source_action=source_action,
            confidence=confidence,
            expected_edge_pct=edge_decimal,
        )

        recommendation = self._recommend(ai_score, source_action, edge_decimal)
        reasoning = self._reason(ai_score, source_action, confidence, edge_decimal, recommendation)

        return AiRankedSignal(
            strategy_name=strategy_name,
            chain=chain,
            pair=pair,
            source_action=source_action,
            confidence_score=confidence,
            expected_edge_pct=edge_decimal,
            ai_score=ai_score,
            recommendation=recommendation,
            reasoning=reasoning,
        )

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _score(
        source_action: str,
        confidence: int,
        expected_edge_pct: Decimal | None,
    ) -> int:
        score = 0

        if source_action == "READY_FOR_PAPER":
            score += 35
        elif source_action == "WATCH":
            score += 15
        elif source_action == "SKIP":
            score -= 20

        score += min(40, max(0, confidence) // 2)

        if expected_edge_pct is None:
            score -= 15
        elif expected_edge_pct <= 0:
            score -= 25
        elif expected_edge_pct < Decimal("0.10"):
            score += 5
        elif expected_edge_pct < Decimal("0.50"):
            score += 15
        elif expected_edge_pct < Decimal("1.50"):
            score += 25
        else:
            # Very large edge may be stale data, illiquidity, or bad quote.
            score += 10

        return max(0, min(100, score))

    @staticmethod
    def _recommend(
        ai_score: int,
        source_action: str,
        expected_edge_pct: Decimal | None,
    ) -> AiRecommendation:
        if expected_edge_pct is None:
            return AiRecommendation.NEEDS_MORE_DATA

        if source_action == "SKIP" or ai_score < 35:
            return AiRecommendation.IGNORE

        if ai_score >= 70 and source_action == "READY_FOR_PAPER":
            return AiRecommendation.PAPER_TRADE_CANDIDATE

        return AiRecommendation.WATCH

    @staticmethod
    def _reason(
        ai_score: int,
        source_action: str,
        confidence: int,
        expected_edge_pct: Decimal | None,
        recommendation: AiRecommendation,
    ) -> str:
        if expected_edge_pct is None:
            return "Missing expected edge data. More data is needed before ranking."

        if recommendation == AiRecommendation.PAPER_TRADE_CANDIDATE:
            return (
                f"Signal action is {source_action}, confidence is {confidence}, "
                f"and expected edge is {expected_edge_pct:.4f}%. Suitable for paper trading only."
            )

        if recommendation == AiRecommendation.WATCH:
            return (
                f"AI score {ai_score}/100. Signal has some potential, but it does not yet "
                "meet the threshold for paper-trade candidate status."
            )

        return (
            f"AI score {ai_score}/100. Signal should be ignored for now due to low confidence, "
            "low edge, missing data, or scanner skip action."
        )
