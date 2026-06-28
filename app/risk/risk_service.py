from __future__ import annotations

from decimal import Decimal

from app.risk.models import RiskAssessment, RiskDecision

try:
    from app.ai.ranking_service import AiRankingService
except Exception:
    AiRankingService = None


class RiskService:
    """Paper-only risk engine.

    v2.7 allows small simulated paper trades only when signal quality is high.
    Live trading remains blocked elsewhere by trading controls.
    """

    def __init__(self) -> None:
        self.min_ai_score_for_paper = 50
        self.min_edge_for_paper_pct = Decimal("0.30")
        self.default_paper_notional_usd = Decimal("100")
        self.max_paper_notional_usd = Decimal("250")

    def assess_ranked_signals(self) -> list[RiskAssessment]:
        ranked_signals = self._load_ranked_signals()
        assessments: list[RiskAssessment] = []

        for signal in ranked_signals:
            strategy_name = str(getattr(signal, "strategy_name", "Strategy"))
            chain = str(getattr(signal, "chain", "base"))
            pair = str(getattr(signal, "pair", "-"))
            ai_score = int(getattr(signal, "ai_score", 0) or 0)
            expected_edge = self._to_decimal(getattr(signal, "expected_edge_pct", None))
            recommendation = getattr(getattr(signal, "recommendation", ""), "value", str(getattr(signal, "recommendation", "")))

            if pair == "-" or expected_edge is None:
                assessments.append(
                    RiskAssessment(
                        strategy_name=strategy_name,
                        chain=chain,
                        pair=pair,
                        ai_score=ai_score,
                        expected_edge_pct=expected_edge,
                        recommendation=recommendation,
                        decision=RiskDecision.WATCHLIST,
                        max_allowed_notional_usd=Decimal("0"),
                        reason="Missing real pair or expected edge; watchlist only.",
                    )
                )
                continue

            if expected_edge < self.min_edge_for_paper_pct:
                assessments.append(
                    RiskAssessment(
                        strategy_name=strategy_name,
                        chain=chain,
                        pair=pair,
                        ai_score=ai_score,
                        expected_edge_pct=expected_edge,
                        recommendation=recommendation,
                        decision=RiskDecision.WATCHLIST,
                        max_allowed_notional_usd=Decimal("0"),
                        reason=(
                            f"Expected edge {expected_edge:.4f}% is below paper threshold "
                            f"{self.min_edge_for_paper_pct}%."
                        ),
                    )
                )
                continue

            if ai_score < self.min_ai_score_for_paper:
                assessments.append(
                    RiskAssessment(
                        strategy_name=strategy_name,
                        chain=chain,
                        pair=pair,
                        ai_score=ai_score,
                        expected_edge_pct=expected_edge,
                        recommendation=recommendation,
                        decision=RiskDecision.WATCHLIST,
                        max_allowed_notional_usd=Decimal("0"),
                        reason=f"AI score {ai_score} is below paper threshold {self.min_ai_score_for_paper}.",
                    )
                )
                continue

            notional = min(
                self.max_paper_notional_usd,
                max(self.default_paper_notional_usd, expected_edge * Decimal("300")),
            )

            assessments.append(
                RiskAssessment(
                    strategy_name=strategy_name,
                    chain=chain,
                    pair=pair,
                    ai_score=ai_score,
                    expected_edge_pct=expected_edge,
                    recommendation=recommendation,
                    decision=RiskDecision.APPROVED_FOR_PAPER,
                    max_allowed_notional_usd=notional,
                    reason=(
                        f"Approved for simulated paper trade: edge {expected_edge:.4f}% "
                        f"and AI score {ai_score} pass thresholds."
                    ),
                )
            )

        return assessments

    @staticmethod
    def _load_ranked_signals() -> list:
        if AiRankingService is None:
            return []
        try:
            return AiRankingService().rank_strategy_signals()
        except Exception:
            return []

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None
