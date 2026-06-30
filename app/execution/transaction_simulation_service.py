from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from app.config.feature_flags import load_feature_flags
from app.registry.dexes import get_dexes_for_chain
from app.registry.tokens import get_token


class TransactionSimulationService:
    """Builds transaction-simulation evidence for a future live pilot.

    This is intentionally not a transaction sender. It does not sign, approve,
    or submit transactions. The report remains non-passing until exact swap
    calldata and eth_call simulation are implemented for the selected route.
    """

    APPROVED_CHAINS = {"base"}
    APPROVED_TOKENS = {"USDC", "WETH"}
    APPROVED_DEXES = {"Uniswap V3", "Aerodrome"}

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.output_json = self.report_dir / "transaction_simulation.json"
        self.output_md = self.report_dir / "transaction_simulation.md"

    def generate(self) -> dict[str, Any]:
        flags = load_feature_flags()
        wallet = self._read_json(self.report_dir / "wallet_preflight.json")
        readiness = self._read_json(self.report_dir / "live_readiness_checklist.json")
        realism = self._read_json(self.report_dir / "execution_realism.json")
        candidate = self._select_candidate(realism)
        intent = self._simulation_intent(candidate, flags)
        checks = self._checks(flags=flags, wallet=wallet, readiness=readiness, candidate=candidate, intent=intent)
        blockers = [row for row in checks if row["severity"] == "BLOCK"]
        actions = [row for row in checks if row["severity"] == "ACTION"]
        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "overall_status": "TX_SIMULATION_READY" if not blockers and not actions else "TX_SIMULATION_ACTION",
            "transaction_simulation_passed": False,
            "live_trading_approval": False,
            "selected_candidate": candidate,
            "simulation_intent": intent,
            "check_count": len(checks),
            "pass_count": sum(1 for row in checks if row["severity"] == "PASS"),
            "action_count": len(actions),
            "blocked_check_count": len(blockers),
            "checks": checks,
            "notes": [
                "Transaction Simulation is evidence-only and never sends a transaction.",
                "The gate remains non-passing until exact calldata is built and eth_call simulation succeeds for both arbitrage legs.",
                "Private keys must remain absent while developing this report.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _select_candidate(self, realism: dict[str, Any]) -> dict[str, Any]:
        rows = realism.get("opportunities", [])
        if isinstance(rows, list):
            for row in rows:
                if (
                    str(row.get("source_decision", "")).upper() == "BUY"
                    and str(row.get("realism_status", "")).upper() == "SHADOW_READY"
                    and str(row.get("chain", "")).lower() in self.APPROVED_CHAINS
                ):
                    return dict(row)
        return {}

    def _simulation_intent(self, candidate: dict[str, Any], flags: Any) -> dict[str, Any]:
        if not candidate:
            return {
                "status": "NO_CANDIDATE",
                "calldata_status": "NOT_BUILT",
                "eth_call_status": "NOT_RUN",
                "reason": "No latest BUY plus SHADOW_READY opportunity is available.",
            }

        chain = str(candidate.get("chain", "")).lower()
        pair = str(candidate.get("pair", "")).upper()
        symbols = pair.split("/")
        base_symbol = symbols[0] if symbols else ""
        quote_symbol = symbols[1] if len(symbols) > 1 else ""
        buy_dex = str(candidate.get("buy_source", ""))
        sell_dex = str(candidate.get("sell_source", ""))
        dexes = {dex.name: dex for dex in get_dexes_for_chain(chain)}
        token_rows = []
        for symbol in [base_symbol, quote_symbol]:
            token = get_token(chain, symbol)
            token_rows.append(
                {
                    "symbol": symbol,
                    "address": token.address if token else None,
                    "decimals": token.decimals if token else None,
                    "configured": token is not None,
                }
            )
        router_rows = []
        for name in [buy_dex, sell_dex]:
            dex = dexes.get(name)
            router_rows.append(
                {
                    "dex": name,
                    "router_address": dex.router_address if dex else None,
                    "dex_type": dex.dex_type if dex else None,
                    "configured": bool(dex and dex.router_address),
                }
            )

        max_trade = flags.max_live_trade_usd if flags.max_live_trade_usd > 0 else Decimal("0")
        requested = self._decimal(candidate.get("requested_notional_usd")) or max_trade
        notional = min(value for value in [requested, max_trade] if value > 0) if requested > 0 or max_trade > 0 else Decimal("0")
        slippage_bps = Decimal("50")

        return {
            "status": "INTENT_READY",
            "chain": chain,
            "chain_id": 8453 if chain == "base" else None,
            "wallet_address": flags.live_wallet_address or None,
            "pair": pair,
            "buy_dex": buy_dex,
            "sell_dex": sell_dex,
            "notional_usd": self._fmt(notional),
            "max_slippage_bps": str(slippage_bps),
            "deadline_seconds": "120",
            "tokens": token_rows,
            "routers": router_rows,
            "calldata_status": "NOT_IMPLEMENTED",
            "eth_call_status": "NOT_RUN",
            "required_next_step": "Implement exact router calldata and run eth_call against Base for both arbitrage legs.",
        }

    def _checks(
        self,
        *,
        flags: Any,
        wallet: dict[str, Any],
        readiness: dict[str, Any],
        candidate: dict[str, Any],
        intent: dict[str, Any],
    ) -> list[dict[str, str]]:
        token_rows = intent.get("tokens", []) if isinstance(intent.get("tokens"), list) else []
        router_rows = intent.get("routers", []) if isinstance(intent.get("routers"), list) else []
        pair_tokens = {str(row.get("symbol", "")).upper() for row in token_rows}
        router_names = {str(row.get("dex", "")) for row in router_rows}
        candidate_exists = bool(candidate)
        return [
            self._check(
                "live_trading_disabled",
                not flags.live_trading_enabled,
                "BLOCK",
                "Live trading must remain disabled during transaction simulation development.",
                "Live trading is disabled.",
            ),
            self._check(
                "kill_switch_enabled",
                flags.live_kill_switch_enabled,
                "BLOCK",
                "Live kill switch must remain enabled during transaction simulation development.",
                "Live kill switch is enabled.",
            ),
            self._check(
                "private_key_absent",
                not flags.private_key_configured,
                "BLOCK",
                "Private key must not be configured for simulation report generation.",
                "Private key is absent.",
            ),
            self._check(
                "wallet_preflight_ready",
                wallet.get("wallet_preflight_allowed") is True,
                "ACTION",
                "Wallet Preflight must be ready before transaction simulation review.",
                "Wallet Preflight is ready.",
            ),
            self._check(
                "live_readiness_review_ready",
                readiness.get("live_review_ready") is True,
                "ACTION",
                "Live Readiness Checklist must be review-ready before transaction simulation can pass.",
                "Live Readiness Checklist is review-ready.",
            ),
            self._check(
                "shadow_candidate_available",
                bool(candidate),
                "ACTION",
                "No BUY plus SHADOW_READY opportunity is available for simulation.",
                "A BUY plus SHADOW_READY opportunity is available.",
            ),
            self._check(
                "candidate_scope_allowed",
                (not candidate_exists)
                or (
                    str(candidate.get("chain", "")).lower() in self.APPROVED_CHAINS
                    and pair_tokens.issubset(self.APPROVED_TOKENS)
                    and bool(pair_tokens)
                ),
                "BLOCK",
                "Simulation candidate must be Base USDC/WETH scope only.",
                "Simulation candidate is Base USDC/WETH scope.",
            ),
            self._check(
                "routers_configured",
                (not candidate_exists) or (all(bool(row.get("configured")) for row in router_rows) and bool(router_rows)),
                "BLOCK",
                "Both route routers must be configured.",
                "Both route routers are configured.",
            ),
            self._check(
                "approved_live_dexes",
                (not candidate_exists) or router_names.issubset(self.APPROVED_DEXES),
                "ACTION",
                "Simulation candidate uses a DEX outside the tiny-live allowlist.",
                "Simulation candidate DEXes are within the tiny-live allowlist.",
            ),
            self._check(
                "live_trade_cap_configured",
                Decimal("0") < flags.max_live_trade_usd <= flags.tiny_live_trade_ceiling_usd,
                "ACTION",
                "Configure a tiny live trade cap before transaction simulation review.",
                "Tiny live trade cap is configured.",
            ),
            self._check(
                "exact_calldata_built",
                intent.get("calldata_status") == "BUILT",
                "ACTION",
                "Exact router calldata is not implemented yet.",
                "Exact router calldata is built.",
            ),
            self._check(
                "eth_call_simulation_passed",
                intent.get("eth_call_status") == "PASS",
                "ACTION",
                "Base eth_call simulation has not passed yet.",
                "Base eth_call simulation passed.",
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

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0")

    @staticmethod
    def _fmt(value: Decimal) -> str:
        return str(value.quantize(Decimal("0.0000")))

    def _markdown(self, payload: dict[str, Any]) -> str:
        intent = payload.get("simulation_intent", {})
        lines = [
            "# Transaction Simulation Report",
            "",
            f"Generated: `{payload['generated_at']}`",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Transaction simulation passed: `{payload['transaction_simulation_passed']}`",
            f"- Live trading approval: `{payload['live_trading_approval']}`",
            f"- Candidate pair: `{intent.get('pair', '-')}`",
            f"- Buy DEX: `{intent.get('buy_dex', '-')}`",
            f"- Sell DEX: `{intent.get('sell_dex', '-')}`",
            f"- Notional USD: `${intent.get('notional_usd', '-')}`",
            f"- Calldata status: `{intent.get('calldata_status', '-')}`",
            f"- eth_call status: `{intent.get('eth_call_status', '-')}`",
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
        lines.extend(["", "## Intent", "", "```json", json.dumps(intent, indent=2), "```", "", "## Notes", ""])
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    payload = TransactionSimulationService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
