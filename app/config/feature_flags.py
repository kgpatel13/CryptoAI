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
    max_live_wallet_usd: Decimal
    max_daily_loss_usd: Decimal
    live_kill_switch_enabled: bool
    require_manual_confirmation: bool
    private_key_configured: bool
    live_wallet_address: str
    main_wallet_address: str
    live_allowed_chains: tuple[str, ...]
    live_allowed_dexes: tuple[str, ...]
    live_allowed_tokens: tuple[str, ...]
    require_transaction_simulation: bool
    transaction_simulation_passed: bool
    require_paper_evidence: bool
    min_paper_closed_trades: int
    min_execution_cost_confidence: str
    tiny_live_trade_ceiling_usd: Decimal


def load_feature_flags() -> FeatureFlags:
    """Load runtime safety flags.

    Defaults are intentionally conservative. Live trading is disabled unless
    explicitly enabled in environment variables, and even then the live guard
    must pass additional checks.
    """

    return FeatureFlags(
        live_trading_enabled=_bool_env("CRYPTOAI_LIVE_TRADING_ENABLED", False),
        paper_trading_enabled=_bool_env("CRYPTOAI_PAPER_TRADING_ENABLED", True),
        max_live_trade_usd=_decimal_env("CRYPTOAI_MAX_LIVE_TRADE_USD", "0"),
        max_live_wallet_usd=_decimal_env("CRYPTOAI_MAX_LIVE_WALLET_USD", "0"),
        max_daily_loss_usd=_decimal_env("CRYPTOAI_MAX_DAILY_LOSS_USD", "0"),
        live_kill_switch_enabled=_bool_env("CRYPTOAI_LIVE_KILL_SWITCH_ENABLED", True),
        require_manual_confirmation=_bool_env("CRYPTOAI_REQUIRE_MANUAL_CONFIRMATION", True),
        private_key_configured=bool(os.getenv("CRYPTOAI_PRIVATE_KEY")),
        live_wallet_address=os.getenv("CRYPTOAI_LIVE_WALLET_ADDRESS", "").strip(),
        main_wallet_address=os.getenv("CRYPTOAI_MAIN_WALLET_ADDRESS", "").strip(),
        live_allowed_chains=_csv_env("CRYPTOAI_LIVE_ALLOWED_CHAINS", "base"),
        live_allowed_dexes=_csv_env("CRYPTOAI_LIVE_ALLOWED_DEXES", "Uniswap V3,Aerodrome"),
        live_allowed_tokens=_csv_env("CRYPTOAI_LIVE_ALLOWED_TOKENS", "WETH,USDC"),
        require_transaction_simulation=_bool_env("CRYPTOAI_REQUIRE_TX_SIMULATION", True),
        transaction_simulation_passed=_bool_env("CRYPTOAI_TX_SIMULATION_PASSED", False),
        require_paper_evidence=_bool_env("CRYPTOAI_REQUIRE_PAPER_EVIDENCE", True),
        min_paper_closed_trades=_int_env("CRYPTOAI_MIN_PAPER_CLOSED_TRADES", 30),
        min_execution_cost_confidence=os.getenv("CRYPTOAI_MIN_EXECUTION_COST_CONFIDENCE", "HIGH").strip().upper(),
        tiny_live_trade_ceiling_usd=_decimal_env("CRYPTOAI_TINY_LIVE_TRADE_CEILING_USD", "100"),
    )


def _bool_env(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _decimal_env(key: str, default: str) -> Decimal:
    try:
        return Decimal(os.getenv(key, default))
    except Exception:
        return Decimal(default)


def _int_env(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except Exception:
        return default


def _csv_env(key: str, default: str) -> tuple[str, ...]:
    raw = os.getenv(key, default)
    return tuple(part.strip() for part in raw.split(",") if part.strip())
