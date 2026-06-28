from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.config.feature_flags import FeatureFlags, load_feature_flags


@dataclass(frozen=True)
class LiveGuardDecision:
    allowed: bool
    reason: str
    max_trade_usd: Decimal
    max_daily_loss_usd: Decimal


class LiveTradingGuard:
    """Hard safety gate for any future live execution path.

    This class must be checked before any real transaction code is allowed
    to run. Current result should remain blocked unless the environment is
    explicitly configured and future live modules are reviewed.
    """

    def __init__(self, flags: FeatureFlags | None = None) -> None:
        self.flags = flags or load_feature_flags()

    def check(self) -> LiveGuardDecision:
        if not self.flags.live_trading_enabled:
            return LiveGuardDecision(
                allowed=False,
                reason="Live trading is disabled by feature flag.",
                max_trade_usd=Decimal("0"),
                max_daily_loss_usd=Decimal("0"),
            )

        if not self.flags.private_key_configured:
            return LiveGuardDecision(
                allowed=False,
                reason="No private key is configured. Live trading remains blocked.",
                max_trade_usd=Decimal("0"),
                max_daily_loss_usd=Decimal("0"),
            )

        if self.flags.max_live_trade_usd <= 0:
            return LiveGuardDecision(
                allowed=False,
                reason="Max live trade size must be greater than zero.",
                max_trade_usd=Decimal("0"),
                max_daily_loss_usd=self.flags.max_daily_loss_usd,
            )

        if self.flags.max_daily_loss_usd <= 0:
            return LiveGuardDecision(
                allowed=False,
                reason="Max daily loss limit must be configured before live trading.",
                max_trade_usd=self.flags.max_live_trade_usd,
                max_daily_loss_usd=Decimal("0"),
            )

        if self.flags.require_manual_confirmation:
            return LiveGuardDecision(
                allowed=False,
                reason="Manual confirmation is required. Fully autonomous live execution is blocked.",
                max_trade_usd=self.flags.max_live_trade_usd,
                max_daily_loss_usd=self.flags.max_daily_loss_usd,
            )

        return LiveGuardDecision(
            allowed=True,
            reason="Live trading guard passed. Future execution module may continue.",
            max_trade_usd=self.flags.max_live_trade_usd,
            max_daily_loss_usd=self.flags.max_daily_loss_usd,
        )
