from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from app.config.feature_flags import load_feature_flags


class WalletPreflightService:
    """Preparation checklist for an isolated future live wallet.

    This service never signs, sends, or simulates transactions. It only reviews
    configuration and the intended tiny-pilot funding plan.
    """

    APPROVED_CHAIN = "base"
    APPROVED_TOKENS = {"USDC", "WETH"}
    MAX_PREP_WALLET_USD = Decimal("500")
    MAX_TINY_TRADE_USD = Decimal("100")

    def __init__(self, report_dir: Path | str = "reports") -> None:
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.output_json = self.report_dir / "wallet_preflight.json"
        self.output_md = self.report_dir / "wallet_preflight.md"

    def generate(self) -> dict[str, Any]:
        flags = load_feature_flags()
        plan = self._funding_plan()
        checks = self._checks(flags=flags, plan=plan)
        blockers = [row for row in checks if row["severity"] == "BLOCK"]
        actions = [row for row in checks if row["severity"] == "ACTION"]
        status = "WALLET_PREP_READY" if not blockers and not actions else "WALLET_PREP_ACTION"
        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "overall_status": status,
            "wallet_preflight_allowed": status == "WALLET_PREP_READY",
            "live_trading_approval": False,
            "planned_chain": plan["chain"],
            "planned_usdc_usd": self._fmt(plan["usdc_usd"]),
            "planned_eth_gas_usd": self._fmt(plan["eth_gas_usd"]),
            "planned_total_usd": self._fmt(plan["total_usd"]),
            "max_prep_wallet_usd": self._fmt(self.MAX_PREP_WALLET_USD),
            "max_tiny_trade_usd": self._fmt(self.MAX_TINY_TRADE_USD),
            "live_wallet_configured": bool(flags.live_wallet_address),
            "private_key_configured": flags.private_key_configured,
            "live_trading_enabled": flags.live_trading_enabled,
            "live_kill_switch_enabled": flags.live_kill_switch_enabled,
            "check_count": len(checks),
            "action_count": len(actions),
            "blocked_check_count": len(blockers),
            "checks": checks,
            "notes": [
                "Wallet Preflight is preparation-only and never approves live trading.",
                "Do not configure private keys until the transaction path, simulation gate, and manual review are complete.",
                "The first real-money pilot should use an isolated wallet on Base with a total wallet ceiling of $500 or less.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _checks(self, *, flags: Any, plan: dict[str, Decimal | str]) -> list[dict[str, str]]:
        total = self._decimal(plan["total_usd"])
        configured_wallet_ceiling = flags.max_live_wallet_usd
        configured_trade_cap = flags.max_live_trade_usd
        configured_daily_loss = flags.max_daily_loss_usd
        allowed_chains = {chain.lower() for chain in flags.live_allowed_chains}
        allowed_tokens = {token.upper() for token in flags.live_allowed_tokens}

        return [
            self._check(
                "live_trading_disabled",
                not flags.live_trading_enabled,
                "BLOCK",
                "Live trading feature flag must stay disabled during wallet preparation.",
                "Live trading feature flag is disabled.",
            ),
            self._check(
                "kill_switch_enabled",
                flags.live_kill_switch_enabled,
                "BLOCK",
                "Live kill switch must stay enabled during wallet preparation.",
                "Live kill switch is enabled.",
            ),
            self._check(
                "private_key_absent",
                not flags.private_key_configured,
                "BLOCK",
                "Private key is configured; remove it during preflight preparation.",
                "No private key is configured.",
            ),
            self._check(
                "isolated_wallet_address",
                self._valid_address(flags.live_wallet_address),
                "ACTION",
                "Configure the isolated live wallet public address before funding.",
                "Isolated live wallet public address is configured.",
            ),
            self._check(
                "wallet_isolation",
                bool(flags.live_wallet_address)
                and (not flags.main_wallet_address or flags.live_wallet_address.lower() != flags.main_wallet_address.lower()),
                "ACTION",
                "Live wallet must be separate from the main wallet.",
                "Live wallet is separate from the main wallet.",
            ),
            self._check(
                "planned_chain_base",
                str(plan["chain"]).lower() == self.APPROVED_CHAIN,
                "BLOCK",
                "Initial wallet preflight must use Base only.",
                "Planned chain is Base.",
            ),
            self._check(
                "chain_allowlist_base",
                allowed_chains == {self.APPROVED_CHAIN},
                "ACTION",
                "Live chain allowlist should be exactly base for the tiny pilot.",
                "Live chain allowlist is restricted to Base.",
            ),
            self._check(
                "token_allowlist_usdc_weth",
                self.APPROVED_TOKENS.issubset(allowed_tokens),
                "ACTION",
                "Live token allowlist must include USDC and WETH.",
                "Live token allowlist includes USDC and WETH.",
            ),
            self._check(
                "planned_wallet_ceiling",
                Decimal("0") < total <= self.MAX_PREP_WALLET_USD,
                "BLOCK",
                "Planned funding must be > $0 and <= $500.",
                "Planned funding is within the $500 tiny-pilot ceiling.",
            ),
            self._check(
                "planned_gas_budget",
                Decimal("5") <= self._decimal(plan["eth_gas_usd"]) <= Decimal("75"),
                "ACTION",
                "Planned ETH gas budget should be between $5 and $75 for Base preparation.",
                "Planned ETH gas budget is within preparation range.",
            ),
            self._check(
                "configured_wallet_ceiling",
                Decimal("0") < configured_wallet_ceiling <= self.MAX_PREP_WALLET_USD,
                "ACTION",
                "Set CRYPTOAI_MAX_LIVE_WALLET_USD to a value > 0 and <= 500 before any live pilot.",
                "Configured wallet ceiling is within tiny-pilot policy.",
            ),
            self._check(
                "configured_trade_cap",
                Decimal("0") < configured_trade_cap <= min(self.MAX_TINY_TRADE_USD, configured_wallet_ceiling or self.MAX_TINY_TRADE_USD),
                "ACTION",
                "Set CRYPTOAI_MAX_LIVE_TRADE_USD to a small value, usually $25-$50, before any live pilot.",
                "Configured trade cap is within tiny-pilot policy.",
            ),
            self._check(
                "configured_daily_loss",
                Decimal("0") < configured_daily_loss <= configured_trade_cap,
                "ACTION",
                "Set CRYPTOAI_MAX_DAILY_LOSS_USD to a value > $0 and no larger than the live trade cap.",
                "Configured daily loss cap is within tiny-pilot policy.",
            ),
            self._check(
                "manual_confirmation_required",
                flags.require_manual_confirmation,
                "ACTION",
                "Manual confirmation should remain required until a reviewed live pilot is approved.",
                "Manual confirmation is required.",
            ),
            self._check(
                "transaction_simulation_required",
                flags.require_transaction_simulation,
                "BLOCK",
                "Transaction simulation must be required before any live pilot.",
                "Transaction simulation is required.",
            ),
        ]

    @staticmethod
    def _check(name: str, passed: bool, fail_severity: str, fail_detail: str, pass_detail: str) -> dict[str, str]:
        return {
            "name": name,
            "severity": "PASS" if passed else fail_severity,
            "passed": bool(passed),
            "detail": pass_detail if passed else fail_detail,
        }

    def _funding_plan(self) -> dict[str, Decimal | str]:
        usdc = self._decimal_env("CRYPTOAI_PLANNED_LIVE_USDC_USD", "450")
        gas = self._decimal_env("CRYPTOAI_PLANNED_LIVE_ETH_GAS_USD", "50")
        return {
            "chain": os.getenv("CRYPTOAI_PLANNED_LIVE_CHAIN", self.APPROVED_CHAIN).strip().lower() or self.APPROVED_CHAIN,
            "usdc_usd": usdc,
            "eth_gas_usd": gas,
            "total_usd": usdc + gas,
        }

    @staticmethod
    def _valid_address(value: str) -> bool:
        return bool(re.fullmatch(r"0x[a-fA-F0-9]{40}", value or ""))

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0")

    def _decimal_env(self, key: str, default: str) -> Decimal:
        return self._decimal(os.getenv(key, default))

    @staticmethod
    def _fmt(value: Decimal) -> str:
        return str(value.quantize(Decimal("0.0000")))

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# Wallet Preflight Report",
            "",
            f"Generated: `{payload['generated_at']}`",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Wallet preflight allowed: `{payload['wallet_preflight_allowed']}`",
            f"- Live trading approval: `{payload['live_trading_approval']}`",
            f"- Planned chain: `{payload['planned_chain']}`",
            f"- Planned USDC USD: `${payload['planned_usdc_usd']}`",
            f"- Planned ETH gas USD: `${payload['planned_eth_gas_usd']}`",
            f"- Planned total USD: `${payload['planned_total_usd']}`",
            f"- Blocked checks: `{payload['blocked_check_count']}`",
            f"- Action checks: `{payload['action_count']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "|---|---|---|",
        ]
        for row in payload["checks"]:
            lines.append(f"| {row['name']} | {row['severity']} | {row['detail']} |")
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    payload = WalletPreflightService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
