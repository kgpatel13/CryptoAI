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
            "live_wallet_configured": bool(flags.live_wallet_address),
            "main_wallet_configured": bool(flags.main_wallet_address),
            "require_manual_confirmation": flags.require_manual_confirmation,
            "live_kill_switch_enabled": flags.live_kill_switch_enabled,
            "max_live_trade_usd": str(flags.max_live_trade_usd),
            "max_live_wallet_usd": str(flags.max_live_wallet_usd),
            "max_daily_loss_usd": str(flags.max_daily_loss_usd),
            "live_allowed_chains": list(flags.live_allowed_chains),
            "live_allowed_dexes": list(flags.live_allowed_dexes),
            "live_allowed_tokens": list(flags.live_allowed_tokens),
            "require_transaction_simulation": flags.require_transaction_simulation,
            "transaction_simulation_passed": flags.transaction_simulation_passed,
            "require_paper_evidence": flags.require_paper_evidence,
            "min_paper_closed_trades": flags.min_paper_closed_trades,
            "min_execution_cost_confidence": flags.min_execution_cost_confidence,
            "live_guard_allowed": decision.allowed,
            "live_guard_reason": decision.reason,
            "guard_max_trade_usd": str(decision.max_trade_usd),
            "guard_max_wallet_usd": str(decision.max_wallet_usd),
            "guard_max_daily_loss_usd": str(decision.max_daily_loss_usd),
            "checks": [asdict(check) for check in decision.checks],
        }

    def checklist(self) -> list[dict]:
        status = self.get_status()
        rows = [
            {
                "Check": "Paper trading enabled",
                "Status": "PASS" if status["paper_trading_enabled"] else "WARN",
                "Details": "Paper trading can run without real funds.",
            },
            {
                "Check": "Live trading feature flag",
                "Status": "WARN" if status["live_trading_enabled"] else "PASS",
                "Details": "Should remain disabled until the live safety report is reviewed.",
            },
            {
                "Check": "Private key configured",
                "Status": "WARN" if status["private_key_configured"] else "PASS",
                "Details": "No private key should be configured during research mode.",
            },
            {
                "Check": "Manual confirmation required",
                "Status": "PASS" if status["require_manual_confirmation"] else "WARN",
                "Details": "Manual confirmation should stay required before live execution.",
            },
            {
                "Check": "Live guard decision",
                "Status": "WARN" if status["live_guard_allowed"] else "PASS",
                "Details": status["live_guard_reason"],
            },
        ]
        for check in status.get("checks", []):
            rows.append(
                {
                    "Check": check["name"],
                    "Status": check["severity"],
                    "Details": check["detail"],
                }
            )
        return rows
