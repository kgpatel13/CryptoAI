from __future__ import annotations

import os
from decimal import Decimal

from app.risk.models import RiskAssessment, RiskDecision

try:
    from app.ai.ranking_service import AiRankingService
except Exception:
    AiRankingService = None


class RiskService:
    """Paper risk engine with deterministic approval rules."""

    def __init__(self) -> None:
        self.min_ai_score_for_paper = int(os.getenv("CRYPTOAI_MIN_AI_SCORE_FOR_PAPER", "50"))
        self.min_edge_for_paper_pct = Decimal(os.getenv("CRYPTOAI_MIN_EDGE_FOR_PAPER_PCT", "0.30"))
        self.default_paper_notional_usd = Decimal(os.getenv("CRYPTOAI_DEFAULT_PAPER_NOTIONAL_USD", "100"))
        self.max_paper_notional_usd = Decimal(os.getenv("CRYPTOAI_MAX_PAPER_NOTIONAL_USD", "250"))
        self.paper_sizing_mode = os.getenv("CRYPTOAI_PAPER_SIZING_MODE", "edge_scaled").strip().lower()
        self.live_trading_enabled = os.getenv("CRYPTOAI_LIVE_TRADING_ENABLED", "false").lower() in {"1", "true", "yes", "on"}

    def assess_ranked_signals(self) -> list[RiskAssessment]:
        ranked_signals = self._load_ranked_signals()
        return [self._assess_one(signal) for signal in ranked_signals]

    def _assess_one(self, signal) -> RiskAssessment:
        strategy_name = str(getattr(signal, "strategy_name", "Strategy"))
        chain = str(getattr(signal, "chain", "base"))
        pair = str(getattr(signal, "pair", "-"))
        ai_score = int(getattr(signal, "ai_score", 0) or 0)
        expected_edge = self._to_decimal(getattr(signal, "expected_edge_pct", None))
        recommendation_obj = getattr(signal, "recommendation", "")
        recommendation = recommendation_obj.value if hasattr(recommendation_obj, "value") else str(recommendation_obj)
        source_action = str(getattr(signal, "source_action", ""))

        if self.live_trading_enabled:
            return self._blocked(strategy_name, chain, pair, ai_score, expected_edge, recommendation, "Live trading flag is enabled; refusing approval.")

        if pair == "-" or "/" not in pair:
            return self._watch(strategy_name, chain, pair, ai_score, expected_edge, recommendation, "Missing real pair; watchlist only.")

        if expected_edge is None:
            return self._watch(strategy_name, chain, pair, ai_score, expected_edge, recommendation, "Missing expected edge; watchlist only.")

        if expected_edge < self.min_edge_for_paper_pct:
            return self._watch(strategy_name, chain, pair, ai_score, expected_edge, recommendation, f"Expected edge {expected_edge:.4f}% is below paper threshold {self.min_edge_for_paper_pct}%.")

        if ai_score < self.min_ai_score_for_paper:
            return self._watch(strategy_name, chain, pair, ai_score, expected_edge, recommendation, f"AI score {ai_score} is below paper threshold {self.min_ai_score_for_paper}.")

        if recommendation not in {"PAPER_TRADE_CANDIDATE", "WATCH"} and source_action != "READY_FOR_PAPER":
            return self._watch(strategy_name, chain, pair, ai_score, expected_edge, recommendation, f"Recommendation {recommendation} with source action {source_action} is not approved for paper.")

        if self.paper_sizing_mode == "full_available_cash":
            notional = self.max_paper_notional_usd
        else:
            notional = min(
                self.max_paper_notional_usd,
                max(self.default_paper_notional_usd, expected_edge * Decimal("300")),
            )

        return RiskAssessment(
            strategy_name=strategy_name,
            chain=chain,
            pair=pair,
            ai_score=ai_score,
            expected_edge_pct=expected_edge,
            recommendation=recommendation,
            decision=RiskDecision.APPROVED_FOR_PAPER,
            max_allowed_notional_usd=notional,
            reason=f"Approved for simulated paper trade: edge {expected_edge:.4f}%, AI score {ai_score}, action {source_action}, recommendation {recommendation}.",
        )

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

    @staticmethod
    def _watch(strategy_name, chain, pair, ai_score, expected_edge, recommendation, reason) -> RiskAssessment:
        return RiskAssessment(strategy_name=strategy_name, chain=chain, pair=pair, ai_score=ai_score, expected_edge_pct=expected_edge, recommendation=recommendation, decision=RiskDecision.WATCHLIST, max_allowed_notional_usd=Decimal("0"), reason=reason)

    @staticmethod
    def _blocked(strategy_name, chain, pair, ai_score, expected_edge, recommendation, reason) -> RiskAssessment:
        return RiskAssessment(strategy_name=strategy_name, chain=chain, pair=pair, ai_score=ai_score, expected_edge_pct=expected_edge, recommendation=recommendation, decision=RiskDecision.BLOCKED, max_allowed_notional_usd=Decimal("0"), reason=reason)
