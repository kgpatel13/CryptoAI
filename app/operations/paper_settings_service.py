from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


DEFAULT_PAPER_SETTINGS: dict[str, Any] = {
    "version": 1,
    "mode": "paper",
    "live_trading_enabled": False,
    "operations": {
        "loop_interval_seconds": 300,
        "heartbeat_interval_seconds": 60,
        "max_cycles": None,
    },
    "market_scope": {
        "asset_focus": "ETH",
        "chains": ["base"],
        "routes": ["WETH/USDC", "USDC/WETH"],
        "dexes": ["Uniswap V2", "Aerodrome"],
        "allow_stale_quotes_for_live": False,
    },
    "paper_capital": {
        "initial_capital_eth": "1.0",
        "eth_reference_usd": "3500",
        "max_notional_usd_per_trade": "100",
        "max_daily_paper_trades": 24,
    },
    "opportunity": {
        "production_cost_buffer_pct": "0.30",
        "research_candidate_buffer_pct": "0.20",
        "paper_buy_threshold_pct": "0.30",
        "watch_threshold_pct": "0.05",
        "min_quote_ok_rate_pct": "90",
    },
    "risk": {
        "max_open_positions": 1,
        "duplicate_position_block": True,
        "cooldown_seconds": 900,
        "max_daily_loss_usd": "25",
        "kill_switch_enabled": True,
    },
    "evidence_gates": {
        "require_report_audit_clean": True,
        "require_provider_not_critical": True,
        "min_execution_cost_confidence": "LOW",
        "min_eth_coverage_score": 50,
    },
    "notes": [
        "Paper settings are launch controls for continuous simulation only.",
        "Live trading remains disabled until live-readiness gates pass.",
        "The 0.20% buffer is research-only; production and paper BUY gates remain at 0.30%.",
        "One ETH is treated as a paper capital profile and future live ceiling, not an all-in per-trade size.",
    ],
}


class PaperSettingsService:
    """Loads, validates, saves, and reports 24/7 paper launch settings."""

    SAFE_CHAINS = {"base"}
    SAFE_ROUTES = {"WETH/USDC", "USDC/WETH"}
    SAFE_DEXES = {"Uniswap V2", "Aerodrome"}
    CONFIDENCE_LEVELS = {"NONE", "LOW", "MEDIUM", "HIGH"}

    def __init__(
        self,
        settings_path: Path | str = "config/paper_trading_settings.json",
        report_dir: Path | str = "reports",
    ) -> None:
        self.settings_path = Path(settings_path)
        self.report_dir = Path(report_dir)

    def load(self) -> dict[str, Any]:
        if not self.settings_path.exists():
            return self.defaults()
        try:
            loaded = json.loads(self.settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return self.defaults()
        return self._merge(self.defaults(), loaded if isinstance(loaded, dict) else {})

    def save(self, settings: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = self._merge(self.defaults(), settings or {})
        validation = self.validate(payload)
        if validation["status"] != "VALID":
            raise ValueError("; ".join(row["message"] for row in validation["findings"]))
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self.settings_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def reset(self) -> dict[str, Any]:
        return self.save(self.defaults())

    def validate(self, settings: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = self._merge(self.defaults(), settings or self.load())
        findings: list[dict[str, str]] = []
        warnings: list[dict[str, str]] = []

        self._require(payload.get("mode") == "paper", "mode", "Mode must remain paper.", findings)
        self._require(payload.get("live_trading_enabled") is False, "live_trading_enabled", "Live trading must remain disabled.", findings)

        operations = payload["operations"]
        self._range_int(operations.get("loop_interval_seconds"), 60, 3600, "operations.loop_interval_seconds", findings)
        self._range_int(operations.get("heartbeat_interval_seconds"), 10, 300, "operations.heartbeat_interval_seconds", findings)
        max_cycles = operations.get("max_cycles")
        if max_cycles is not None:
            self._range_int(max_cycles, 1, 100000, "operations.max_cycles", findings)

        market = payload["market_scope"]
        chains = set(market.get("chains", []))
        routes = set(market.get("routes", []))
        dexes = set(market.get("dexes", []))
        self._require(market.get("asset_focus") == "ETH", "market_scope.asset_focus", "The v5.7 launch profile is ETH-only.", findings)
        self._require(bool(chains), "market_scope.chains", "At least one chain is required.", findings)
        self._require(chains.issubset(self.SAFE_CHAINS), "market_scope.chains", "Only Base is enabled for the first paper launch profile.", findings)
        self._require(bool(routes), "market_scope.routes", "At least one ETH route is required.", findings)
        self._require(routes.issubset(self.SAFE_ROUTES), "market_scope.routes", "Only WETH/USDC and USDC/WETH are enabled for v5.7.", findings)
        self._require(bool(dexes), "market_scope.dexes", "At least one DEX is required.", findings)
        self._require(dexes.issubset(self.SAFE_DEXES), "market_scope.dexes", "Only Uniswap V2 and Aerodrome are enabled for v5.7.", findings)
        self._require(market.get("allow_stale_quotes_for_live") is False, "market_scope.allow_stale_quotes_for_live", "Stale live quotes must never be allowed.", findings)

        capital = payload["paper_capital"]
        initial_eth = self._decimal(capital.get("initial_capital_eth"), "paper_capital.initial_capital_eth", findings)
        eth_reference = self._decimal(capital.get("eth_reference_usd"), "paper_capital.eth_reference_usd", findings)
        max_notional = self._decimal(capital.get("max_notional_usd_per_trade"), "paper_capital.max_notional_usd_per_trade", findings)
        self._range_int(capital.get("max_daily_paper_trades"), 1, 200, "paper_capital.max_daily_paper_trades", findings)
        if initial_eth is not None:
            self._require(Decimal("0") < initial_eth <= Decimal("1.0"), "paper_capital.initial_capital_eth", "Paper capital must be greater than 0 and no more than 1 ETH for this launch profile.", findings)
        if eth_reference is not None:
            self._require(eth_reference > Decimal("0"), "paper_capital.eth_reference_usd", "ETH reference price must be greater than 0.", findings)
        if max_notional is not None:
            self._require(max_notional > Decimal("0"), "paper_capital.max_notional_usd_per_trade", "Per-trade notional must be greater than 0.", findings)
        if initial_eth is not None and eth_reference is not None and max_notional is not None:
            paper_capital_usd = initial_eth * eth_reference
            max_alloc = paper_capital_usd * Decimal("0.10")
            if max_notional > max_alloc:
                warnings.append(
                    {
                        "severity": "WARN",
                        "field": "paper_capital.max_notional_usd_per_trade",
                        "message": "Per-trade notional is above 10% of the 1 ETH paper capital profile.",
                    }
                )

        opportunity = payload["opportunity"]
        production_buffer = self._decimal(opportunity.get("production_cost_buffer_pct"), "opportunity.production_cost_buffer_pct", findings)
        research_buffer = self._decimal(opportunity.get("research_candidate_buffer_pct"), "opportunity.research_candidate_buffer_pct", findings)
        buy_threshold = self._decimal(opportunity.get("paper_buy_threshold_pct"), "opportunity.paper_buy_threshold_pct", findings)
        watch_threshold = self._decimal(opportunity.get("watch_threshold_pct"), "opportunity.watch_threshold_pct", findings)
        quote_ok = self._decimal(opportunity.get("min_quote_ok_rate_pct"), "opportunity.min_quote_ok_rate_pct", findings)
        if production_buffer is not None:
            self._require(production_buffer >= Decimal("0.30"), "opportunity.production_cost_buffer_pct", "Production cost buffer cannot be below 0.30%.", findings)
        if research_buffer is not None and production_buffer is not None:
            self._require(research_buffer <= production_buffer, "opportunity.research_candidate_buffer_pct", "Research buffer must not exceed production buffer.", findings)
        if buy_threshold is not None:
            self._require(buy_threshold >= Decimal("0.30"), "opportunity.paper_buy_threshold_pct", "Paper BUY threshold cannot be below 0.30%.", findings)
        if watch_threshold is not None:
            self._require(Decimal("0") <= watch_threshold <= Decimal("0.30"), "opportunity.watch_threshold_pct", "Watch threshold must stay between 0 and 0.30%.", findings)
        if quote_ok is not None:
            self._require(Decimal("0") <= quote_ok <= Decimal("100"), "opportunity.min_quote_ok_rate_pct", "Quote OK rate must be 0-100%.", findings)

        risk = payload["risk"]
        self._range_int(risk.get("max_open_positions"), 1, 20, "risk.max_open_positions", findings)
        self._require(risk.get("duplicate_position_block") is True, "risk.duplicate_position_block", "Duplicate position block must stay enabled.", findings)
        self._range_int(risk.get("cooldown_seconds"), 60, 86400, "risk.cooldown_seconds", findings)
        max_daily_loss = self._decimal(risk.get("max_daily_loss_usd"), "risk.max_daily_loss_usd", findings)
        if max_daily_loss is not None:
            self._require(max_daily_loss > Decimal("0"), "risk.max_daily_loss_usd", "Max daily loss must be greater than 0.", findings)
        self._require(risk.get("kill_switch_enabled") is True, "risk.kill_switch_enabled", "Kill switch must stay enabled.", findings)

        gates = payload["evidence_gates"]
        self._require(gates.get("require_report_audit_clean") is True, "evidence_gates.require_report_audit_clean", "Report Audit clean gate must stay enabled.", findings)
        self._require(gates.get("require_provider_not_critical") is True, "evidence_gates.require_provider_not_critical", "Provider critical gate must stay enabled.", findings)
        confidence = str(gates.get("min_execution_cost_confidence", "")).upper()
        self._require(confidence in self.CONFIDENCE_LEVELS, "evidence_gates.min_execution_cost_confidence", "Execution-cost confidence must be NONE, LOW, MEDIUM, or HIGH.", findings)
        self._range_int(gates.get("min_eth_coverage_score"), 0, 100, "evidence_gates.min_eth_coverage_score", findings)

        all_findings = findings + warnings
        return {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "status": "VALID" if not findings else "INVALID",
            "error_count": len(findings),
            "warning_count": len(warnings),
            "paper_capital_usd": str((initial_eth * eth_reference).quantize(Decimal("0.01"))) if initial_eth is not None and eth_reference is not None else None,
            "launch_command": "python -m app.automation.paper_autopilot --loop --use-settings",
            "settings": payload,
            "findings": all_findings,
        }

    def generate_report(self, settings: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = self.validate(settings or self.load())
        self.report_dir.mkdir(parents=True, exist_ok=True)
        (self.report_dir / "paper_trading_settings.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self._write_markdown(payload)
        return payload

    @classmethod
    def defaults(cls) -> dict[str, Any]:
        return deepcopy(DEFAULT_PAPER_SETTINGS)

    @classmethod
    def _merge(cls, base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
        merged = deepcopy(base)
        for key, value in overlay.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = cls._merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    @staticmethod
    def _require(condition: bool, field: str, message: str, findings: list[dict[str, str]]) -> None:
        if not condition:
            findings.append({"severity": "ERROR", "field": field, "message": message})

    @classmethod
    def _range_int(cls, value: Any, minimum: int, maximum: int, field: str, findings: list[dict[str, str]]) -> None:
        try:
            number = int(value)
        except (TypeError, ValueError):
            findings.append({"severity": "ERROR", "field": field, "message": f"{field} must be an integer."})
            return
        cls._require(minimum <= number <= maximum, field, f"{field} must be between {minimum} and {maximum}.", findings)

    @staticmethod
    def _decimal(value: Any, field: str, findings: list[dict[str, str]]) -> Decimal | None:
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            findings.append({"severity": "ERROR", "field": field, "message": f"{field} must be a decimal number."})
            return None

    def _write_markdown(self, payload: dict[str, Any]) -> None:
        settings = payload["settings"]
        lines = [
            "# CryptoAI Paper Trading Settings",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Status: `{payload['status']}`",
            f"- Mode: `{payload['mode']}`",
            f"- Paper capital USD: `{payload['paper_capital_usd']}`",
            f"- Errors: `{payload['error_count']}`",
            f"- Warnings: `{payload['warning_count']}`",
            f"- Launch command: `{payload['launch_command']}`",
            "",
            "## Launch Profile",
            "",
            f"- Asset focus: `{settings['market_scope']['asset_focus']}`",
            f"- Chains: `{', '.join(settings['market_scope']['chains'])}`",
            f"- Routes: `{', '.join(settings['market_scope']['routes'])}`",
            f"- DEXs: `{', '.join(settings['market_scope']['dexes'])}`",
            f"- Initial paper capital ETH: `{settings['paper_capital']['initial_capital_eth']}`",
            f"- Max notional per trade USD: `{settings['paper_capital']['max_notional_usd_per_trade']}`",
            f"- Production buffer %: `{settings['opportunity']['production_cost_buffer_pct']}`",
            f"- Research candidate buffer %: `{settings['opportunity']['research_candidate_buffer_pct']}`",
            f"- Paper BUY threshold %: `{settings['opportunity']['paper_buy_threshold_pct']}`",
            "",
            "## Findings",
            "",
            "| Severity | Field | Message |",
            "|---|---|---|",
        ]
        for finding in payload["findings"]:
            lines.append(f"| {finding['severity']} | {finding['field']} | {finding['message']} |")
        if not payload["findings"]:
            lines.append("| OK | - | Settings are valid for paper-mode launch. |")
        lines += [
            "",
            "## Notes",
            "",
        ]
        for note in settings.get("notes", []):
            lines.append(f"- {note}")
        (self.report_dir / "paper_trading_settings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    service = PaperSettingsService()
    settings = service.save(service.load())
    payload = service.generate_report(settings)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
