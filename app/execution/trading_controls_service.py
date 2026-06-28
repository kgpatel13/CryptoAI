from __future__ import annotations

from dataclasses import asdict

from app.config.feature_flags import load_feature_flags
from app.execution.live_guard import LiveTradingGuard


class TradingControlsService:
    """Status service for dashboard and future execution engine."""

    def get_status(self) -> dict:
        flags = load_feature_flags()
        decision = LiveTradingGuard(flags).check()

        return {
            "live_trading_enabled": flags.live_trading_enabled,
            "paper_trading_enabled": flags.paper_trading_enabled,
            "private_key_configured": flags.private_key_configured,
            "require_manual_confirmation": flags.require_manual_confirmation,
            "max_live_trade_usd": str(flags.max_live_trade_usd),
            "max_daily_loss_usd": str(flags.max_daily_loss_usd),
            "live_guard_allowed": decision.allowed,
            "live_guard_reason": decision.reason,
            "guard_max_trade_usd": str(decision.max_trade_usd),
            "guard_max_daily_loss_usd": str(decision.max_daily_loss_usd),
        }

    def checklist(self) -> list[dict]:
        status = self.get_status()

        return [
            {
                "Check": "Paper trading enabled",
                "Status": "✅ OK" if status["paper_trading_enabled"] else "⚠️ Disabled",
                "Details": "Paper trading can run without real funds.",
            },
            {
                "Check": "Live trading feature flag",
                "Status": "⚠️ Enabled" if status["live_trading_enabled"] else "✅ Disabled",
                "Details": "Should remain disabled until v2.x reviewed live execution.",
            },
            {
                "Check": "Private key configured",
                "Status": "⚠️ Present" if status["private_key_configured"] else "✅ Absent",
                "Details": "No private key should be configured during research mode.",
            },
            {
                "Check": "Manual confirmation required",
                "Status": "✅ Required" if status["require_manual_confirmation"] else "⚠️ Not required",
                "Details": "Manual confirmation should stay required before live execution.",
            },
            {
                "Check": "Live guard decision",
                "Status": "⚠️ Allowed" if status["live_guard_allowed"] else "✅ Blocked",
                "Details": status["live_guard_reason"],
            },
        ]
