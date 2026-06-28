from __future__ import annotations

from decimal import Decimal

from app.risk.models import RiskAssessment, RiskDecision, RiskPolicy

try:
    from app.ai.ranking_service import AiRankingService
except Exception:
    AiRankingService = None


class RiskService:
    """Deterministic risk layer.

    This engine is intentionally strict. It does not allow live trading.
    It only determines whether a ranked signal may be considered for paper
    trading simulation.
    """

    def __init__(self, policy: RiskPolicy | None = None) -> None:
        self.policy = policy or RiskPolicy()

    def assess_ranked_signals(self) -> list[RiskAssessment]:
        if AiRankingService is None:
            return [
                RiskAssessment(
                    strategy_name="Risk Engine",
                    chain="-",
                    pair="-",
                    ai_score=0,
                    expected_edge_pct=None,
                    recommendation="UNAVAILABLE",
                    decision=RiskDecision.DISABLED,
                    max_allowed_notional_usd=Decimal("0"),
                    reason="AiRankingService is not available.",
                )
            ]

        try:
            ranked_signals = AiRankingService().rank_strategy_signals()
        except Exception as exc:
            return [
                RiskAssessment(
                    strategy_name="Risk Engine",
                    chain="-",
                    pair="-",
                    ai_score=0,
                    expected_edge_pct=None,
                    recommendation="ERROR",
                    decision=RiskDecision.DISABLED,
                    max_allowed_notional_usd=Decimal("0"),
                    reason=f"AI ranking failed: {exc}",
                )
            ]

        return [self._assess_one(signal) for signal in ranked_signals]

    def _assess_one(self, signal) -> RiskAssessment:
        strategy_name = str(getattr(signal, "strategy_name", "Strategy"))
        chain = str(getattr(signal, "chain", "-")).lower()
        pair = str(getattr(signal, "pair", "-"))
        ai_score = int(getattr(signal, "ai_score", 0) or 0)
        edge = self._to_decimal(getattr(signal, "expected_edge_pct", None))
        recommendation_obj = getattr(signal, "recommendation", "")
        recommendation = (
            recommendation_obj.value
            if hasattr(recommendation_obj, "value")
            else str(recommendation_obj)
        )

        decision, reason, max_notional = self._decision(
            chain=chain,
            ai_score=ai_score,
            expected_edge_pct=edge,
            recommendation=recommendation,
        )

        return RiskAssessment(
            strategy_name=strategy_name,
            chain=chain,
            pair=pair,
            ai_score=ai_score,
            expected_edge_pct=edge,
            recommendation=recommendation,
            decision=decision,
            max_allowed_notional_usd=max_notional,
            reason=reason,
        )

    def _decision(
        self,
        chain: str,
        ai_score: int,
        expected_edge_pct: Decimal | None,
        recommendation: str,
    ) -> tuple[RiskDecision, str, Decimal]:
        if self.policy.live_trading_enabled:
            return (
                RiskDecision.BLOCKED,
                "Live trading flag must remain disabled in this build.",
                Decimal("0"),
            )

        if chain not in self.policy.allowed_chains:
            return (
                RiskDecision.BLOCKED,
                f"Chain {chain} is not in the allowed chain list.",
                Decimal("0"),
            )

        if expected_edge_pct is None:
            return (
                RiskDecision.WATCHLIST,
                "Missing edge estimate. Keep on watchlist until more data is available.",
                Decimal("0"),
            )

        if expected_edge_pct < self.policy.min_expected_edge_pct:
            return (
                RiskDecision.BLOCKED,
                (
                    f"Expected edge {expected_edge_pct}% is below minimum "
                    f"{self.policy.min_expected_edge_pct}%."
                ),
                Decimal("0"),
            )

        if expected_edge_pct > self.policy.max_expected_edge_pct:
            return (
                RiskDecision.WATCHLIST,
                (
                    f"Expected edge {expected_edge_pct}% is unusually high. "
                    "This may indicate stale quote, bad liquidity, or pricing error."
                ),
                Decimal("0"),
            )

        if ai_score < self.policy.min_ai_score_for_paper:
            return (
                RiskDecision.WATCHLIST,
                (
                    f"AI score {ai_score} is below paper-trading threshold "
                    f"{self.policy.min_ai_score_for_paper}."
                ),
                Decimal("0"),
            )

        if recommendation != "PAPER_TRADE_CANDIDATE":
            return (
                RiskDecision.WATCHLIST,
                f"AI recommendation is {recommendation}, not PAPER_TRADE_CANDIDATE.",
                Decimal("0"),
            )

        return (
            RiskDecision.APPROVED_FOR_PAPER,
            "Approved for paper-trading simulation only. Live execution remains disabled.",
            self.policy.max_paper_trade_usd,
        )

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None
