from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.config.feature_flags import FeatureFlags, load_feature_flags


@dataclass(frozen=True)
class LiveGuardCheck:
    name: str
    passed: bool
    severity: str
    detail: str


@dataclass(frozen=True)
class LiveGuardDecision:
    allowed: bool
    reason: str
    max_trade_usd: Decimal
    max_daily_loss_usd: Decimal
    max_wallet_usd: Decimal
    checks: tuple[LiveGuardCheck, ...]


class LiveTradingGuard:
    """Hard safety gate for any future real transaction path."""

    APPROVED_CHAINS = {"base"}
    APPROVED_DEXES = {"Uniswap V2", "Aerodrome", "Uniswap V3"}
    APPROVED_TOKENS = {"USDC", "WETH"}
    MAX_TINY_PILOT_WALLET_USD = Decimal("500")

    def __init__(self, flags: FeatureFlags | None = None, report_dir: Path | str = "reports") -> None:
        self.flags = flags or load_feature_flags()
        self.report_dir = Path(report_dir)

    def check(self) -> LiveGuardDecision:
        checks = list(self._runtime_checks())
        if self.flags.require_paper_evidence:
            checks.extend(self._paper_evidence_checks())

        allowed = self.flags.live_trading_enabled and all(check.passed for check in checks)
        if allowed:
            reason = "Live trading guard passed for a reviewed tiny-pilot execution path."
        else:
            first_blocker = next((check for check in checks if not check.passed), None)
            reason = first_blocker.detail if first_blocker else "Live trading is blocked by policy."

        return LiveGuardDecision(
            allowed=allowed,
            reason=reason,
            max_trade_usd=self.flags.max_live_trade_usd if allowed else Decimal("0"),
            max_daily_loss_usd=self.flags.max_daily_loss_usd if allowed else Decimal("0"),
            max_wallet_usd=self.flags.max_live_wallet_usd if allowed else Decimal("0"),
            checks=tuple(checks),
        )

    def _runtime_checks(self) -> list[LiveGuardCheck]:
        flags = self.flags
        return [
            self._check(
                "live_feature_flag",
                flags.live_trading_enabled,
                "Live trading feature flag is disabled.",
                "Live trading feature flag is enabled.",
            ),
            self._check(
                "kill_switch",
                not flags.live_kill_switch_enabled,
                "Live kill switch is ON.",
                "Live kill switch is OFF.",
            ),
            self._check(
                "private_key",
                flags.private_key_configured,
                "No private key is configured. Live trading remains blocked.",
                "Private key is configured for the isolated live wallet.",
            ),
            self._check(
                "isolated_wallet_address",
                bool(flags.live_wallet_address),
                "No isolated live wallet address is configured.",
                "Isolated live wallet address is configured.",
            ),
            self._check(
                "wallet_isolation",
                self._wallet_isolated(flags.live_wallet_address, flags.main_wallet_address),
                "Live wallet matches the configured main wallet; wallet isolation failed.",
                "Live wallet is isolated from the configured main wallet.",
            ),
            self._check(
                "wallet_ceiling",
                Decimal("0") < flags.max_live_wallet_usd <= self.MAX_TINY_PILOT_WALLET_USD,
                f"Max live wallet ceiling must be > $0 and <= ${self.MAX_TINY_PILOT_WALLET_USD}.",
                "Max live wallet ceiling is within tiny-pilot policy.",
            ),
            self._check(
                "trade_cap",
                Decimal("0") < flags.max_live_trade_usd <= min(flags.max_live_wallet_usd, flags.tiny_live_trade_ceiling_usd),
                "Max live trade size must be > $0 and below wallet and tiny-pilot ceilings.",
                "Max live trade size is within tiny-pilot policy.",
            ),
            self._check(
                "daily_loss_cap",
                Decimal("0") < flags.max_daily_loss_usd <= flags.max_live_trade_usd,
                "Max daily loss must be > $0 and no larger than max live trade size.",
                "Max daily loss cap is configured.",
            ),
            self._check(
                "manual_confirmation",
                not flags.require_manual_confirmation,
                "Manual confirmation is required; autonomous live execution is blocked.",
                "Manual confirmation block is cleared for reviewed execution path.",
            ),
            self._check(
                "chain_allowlist",
                self._allowlist_ok(flags.live_allowed_chains, self.APPROVED_CHAINS, normalize=True),
                "Live chain allowlist is empty or contains unapproved chains.",
                "Live chain allowlist is restricted to approved chains.",
            ),
            self._check(
                "dex_allowlist",
                self._allowlist_ok(flags.live_allowed_dexes, self.APPROVED_DEXES),
                "Live DEX allowlist is empty or contains unapproved DEXs.",
                "Live DEX allowlist is restricted to approved DEXs.",
            ),
            self._check(
                "token_allowlist",
                self._allowlist_ok(flags.live_allowed_tokens, self.APPROVED_TOKENS, normalize=True),
                "Live token allowlist is empty or contains unapproved tokens.",
                "Live token allowlist is restricted to approved tokens.",
            ),
            self._check(
                "transaction_simulation",
                (not flags.require_transaction_simulation) or flags.transaction_simulation_passed,
                "Transaction simulation is required and has not passed.",
                "Transaction simulation gate passed.",
            ),
        ]

    def _paper_evidence_checks(self) -> list[LiveGuardCheck]:
        paper_run = self._read_json("paper_run_review.json")
        cost = self._read_json("execution_cost_evidence.json")
        audit = self._read_json("report_audit.json")
        provider = self._read_json("provider_monitor.json")
        realism = self._read_json("execution_realism.json")

        paper_samples = self._int(cost.get("paper_execution_evidence", {}).get("sample_count"))
        confidence = str(cost.get("confidence", "INSUFFICIENT")).upper()
        min_confidence = self.flags.min_execution_cost_confidence
        confidence_rank = {"INSUFFICIENT": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}

        return [
            self._check(
                "paper_shadow_review",
                paper_run.get("shadow_decision") == "REVIEW_READY",
                "Paper run is not yet ready for shadow review.",
                "Paper run is ready for shadow review.",
            ),
            self._check(
                "paper_closed_trades",
                self._int(paper_run.get("closed_trade_count")) >= self.flags.min_paper_closed_trades,
                f"Fresh paper run needs at least {self.flags.min_paper_closed_trades} closed trades.",
                "Fresh paper run has enough closed trades.",
            ),
            self._check(
                "execution_cost_confidence",
                confidence_rank.get(confidence, 0) >= confidence_rank.get(min_confidence, 3),
                f"Execution-cost confidence is {confidence}; required {min_confidence}.",
                "Execution-cost confidence meets policy.",
            ),
            self._check(
                "execution_cost_samples",
                paper_samples >= self.flags.min_paper_closed_trades,
                f"Execution-cost evidence needs at least {self.flags.min_paper_closed_trades} paper samples.",
                "Execution-cost evidence has enough paper samples.",
            ),
            self._check(
                "provider_health",
                provider.get("overall_status") == "OK",
                "Provider monitor is not OK.",
                "Provider monitor is OK.",
            ),
            self._check(
                "report_audit",
                self._audit_blocking_findings(audit) == 0,
                "Report audit has blocking operational findings.",
                "Report audit has no blocking operational findings.",
            ),
            self._check(
                "execution_realism",
                self._int(realism.get("shadow_ready_count")) > 0 and self._int(realism.get("live_ready_count")) == 0,
                "Execution realism must have shadow-ready evidence and zero live-ready approvals.",
                "Execution realism has shadow-ready evidence and no live approvals.",
            ),
        ]

    @staticmethod
    def _check(name: str, passed: bool, fail_detail: str, pass_detail: str) -> LiveGuardCheck:
        return LiveGuardCheck(
            name=name,
            passed=bool(passed),
            severity="PASS" if passed else "BLOCK",
            detail=pass_detail if passed else fail_detail,
        )

    @staticmethod
    def _wallet_isolated(live_wallet: str, main_wallet: str) -> bool:
        if not live_wallet:
            return False
        if not main_wallet:
            return True
        return live_wallet.lower() != main_wallet.lower()

    @staticmethod
    def _allowlist_ok(values: tuple[str, ...], approved: set[str], normalize: bool = False) -> bool:
        if not values:
            return False
        if normalize:
            return {value.upper() for value in values}.issubset({value.upper() for value in approved})
        return set(values).issubset(approved)

    def _read_json(self, name: str) -> dict[str, Any]:
        path = self.report_dir / name
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    def _audit_blocking_findings(self, audit: dict[str, Any]) -> int:
        if "blocking_finding_count" in audit:
            return self._int(audit.get("blocking_finding_count"))
        return self._int(audit.get("finding_count"))

    @staticmethod
    def _int(value: Any) -> int:
        try:
            return int(value)
        except Exception:
            return 0
