from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class FeatureFlags:
    live_trading_enabled: bool
    paper_trading_enabled: bool
    max_live_trade_usd: Decimal
    max_daily_loss_usd: Decimal
    require_manual_confirmation: bool
    private_key_configured: bool


def load_feature_flags() -> FeatureFlags:
    """Load runtime safety flags.

    Defaults are intentionally conservative. Live trading is disabled unless
    explicitly enabled in environment variables, and even then the live guard
    must pass additional checks.
    """

    return FeatureFlags(
        live_trading_enabled=_bool_env("CRYPTOAI_LIVE_TRADING_ENABLED", False),
        paper_trading_enabled=_bool_env("CRYPTOAI_PAPER_TRADING_ENABLED", True),
        max_live_trade_usd=Decimal(os.getenv("CRYPTOAI_MAX_LIVE_TRADE_USD", "0")),
        max_daily_loss_usd=Decimal(os.getenv("CRYPTOAI_MAX_DAILY_LOSS_USD", "0")),
        require_manual_confirmation=_bool_env("CRYPTOAI_REQUIRE_MANUAL_CONFIRMATION", True),
        private_key_configured=bool(os.getenv("CRYPTOAI_PRIVATE_KEY")),
    )


def _bool_env(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}
