from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.registry.dexes import get_dexes_for_chain
from app.registry.pairs import get_pairs_for_chain
from app.registry.tokens import get_token


class EthMarketCoverageService:
    """Scores ETH Golden Path market coverage before asset expansion."""

    TARGET_STABLES = ("USDC", "USDT", "DAI")
    TARGET_CHAINS: list[dict[str, Any]] = [
        {
            "chain": "base",
            "name": "Base",
            "stage": "reference",
            "dex_targets": ["Uniswap V2", "Aerodrome", "Uniswap V3"],
            "notes": "Current reference chain with three implemented DEX quote providers.",
        },
        {
            "chain": "ethereum",
            "name": "Ethereum",
            "stage": "planned",
            "dex_targets": ["Uniswap V3", "Curve", "SushiSwap", "Balancer"],
            "notes": "High-liquidity canonical ETH venue set; provider implementations required.",
        },
        {
            "chain": "arbitrum",
            "name": "Arbitrum One",
            "stage": "planned",
            "dex_targets": ["Uniswap V3", "Camelot", "SushiSwap"],
            "notes": "ETH L2 expansion target after Base evidence quality improves.",
        },
        {
            "chain": "optimism",
            "name": "Optimism",
            "stage": "planned_next",
            "dex_targets": ["Uniswap V3", "Velodrome"],
            "notes": "Recommended next chain, but not active until registry and providers are added.",
        },
        {
            "chain": "polygon",
            "name": "Polygon",
            "stage": "planned",
            "dex_targets": ["Uniswap V3", "QuickSwap"],
            "notes": "Secondary ETH coverage target; provider implementations required.",
        },
    ]

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.report_json = self.report_dir / "eth_market_coverage.json"
        self.report_md = self.report_dir / "eth_market_coverage.md"

    def generate(self) -> dict[str, Any]:
        quote_rows = self._read_jsonl(self.data_dir / "quote_diagnostics.jsonl")[-500:]
        provider_health = self._read_json(self.data_dir / "provider_health.json")
        quote_coverage = self._read_json(self.report_dir / "quote_coverage_evidence.json")
        eth_route = self._read_json(self.report_dir / "eth_route_architecture.json")
        execution_cost = self._read_json(self.report_dir / "execution_cost_evidence.json")

        chain_rows = [
            self._chain_coverage(
                target=target,
                quote_rows=quote_rows,
                provider_health=provider_health,
                quote_coverage=quote_coverage,
                eth_route=eth_route,
                execution_cost=execution_cost,
            )
            for target in self.TARGET_CHAINS
        ]
        overall_score = self._overall_score(chain_rows)
        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "asset_focus": "ETH",
            "coverage_model": "ETH_GOLDEN_PATH",
            "overall_coverage_score": overall_score,
            "overall_status": self._overall_status(overall_score),
            "target_chain_count": len(self.TARGET_CHAINS),
            "configured_target_chain_count": sum(1 for row in chain_rows if row["registry_chain_configured"]),
            "target_dex_count": sum(len(row["target_dexes"]) for row in chain_rows),
            "configured_target_dex_count": sum(row["configured_target_dex_count"] for row in chain_rows),
            "quote_ready_route_count": sum(row["quote_ready_route_count"] for row in chain_rows),
            "high_maturity_chain_count": sum(1 for row in chain_rows if row["coverage_status"] in {"REFERENCE_READY", "HIGH_MATURITY"}),
            "chains": chain_rows,
            "next_actions": self._next_actions(chain_rows),
            "findings": self._findings(chain_rows, overall_score),
            "notes": [
                "ETH Market Coverage scores target-vs-evidence maturity before adding BTC, blue chips, or long-tail tokens.",
                "A target chain or DEX is not treated as active coverage until registry metadata, quote providers, route diagnostics, and provider health exist.",
                "This report does not change production buffers, risk thresholds, or live-trading eligibility.",
            ],
        }
        self.report_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.report_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _chain_coverage(
        self,
        *,
        target: dict[str, Any],
        quote_rows: list[dict[str, Any]],
        provider_health: dict[str, Any],
        quote_coverage: dict[str, Any],
        eth_route: dict[str, Any],
        execution_cost: dict[str, Any],
    ) -> dict[str, Any]:
        chain = str(target["chain"])
        dex_targets = list(target["dex_targets"])
        configured_dexes = {dex.name for dex in get_dexes_for_chain(chain)}
        configured_pairs = {f"{pair.base_symbol}/{pair.quote_symbol}".upper() for pair in get_pairs_for_chain(chain)}
        token_targets = ["WETH", *self.TARGET_STABLES]
        configured_tokens = [symbol for symbol in token_targets if get_token(chain, symbol) is not None]
        configured_target_dexes = [dex for dex in dex_targets if dex in configured_dexes]
        missing_dexes = [dex for dex in dex_targets if dex not in configured_dexes]

        quote_ready_routes = self._quote_ready_routes(chain, quote_rows)
        active_quote_coverage = self._active_quote_coverage(chain, quote_coverage)
        provider_rows = [
            row
            for row in provider_health.get("providers", [])
            if isinstance(row, dict) and str(row.get("chain", "")).lower() == chain
        ] if isinstance(provider_health.get("providers"), list) else []

        provider_score = self._provider_score(provider_rows)
        score_parts = self._score_parts(
            chain=chain,
            configured_tokens=configured_tokens,
            token_targets=token_targets,
            configured_target_dexes=configured_target_dexes,
            dex_targets=dex_targets,
            quote_ready_routes=quote_ready_routes,
            active_quote_coverage=active_quote_coverage,
            provider_rows=provider_rows,
            provider_score=provider_score,
            eth_route=eth_route,
            execution_cost=execution_cost,
        )
        score = sum(score_parts.values())
        return {
            "chain": chain,
            "name": target["name"],
            "stage": target["stage"],
            "target_pairs": [f"WETH/{stable}" for stable in self.TARGET_STABLES],
            "configured_pairs": sorted(configured_pairs),
            "target_dexes": dex_targets,
            "configured_target_dexes": configured_target_dexes,
            "missing_target_dexes": missing_dexes,
            "configured_target_dex_count": len(configured_target_dexes),
            "configured_tokens": configured_tokens,
            "missing_tokens": [symbol for symbol in token_targets if symbol not in configured_tokens],
            "registry_chain_configured": bool(configured_tokens or configured_dexes or configured_pairs),
            "quote_ready_routes": quote_ready_routes,
            "quote_ready_route_count": len(quote_ready_routes),
            "active_quote_coverage": active_quote_coverage,
            "provider_count": len(provider_rows),
            "provider_score": str(provider_score.quantize(Decimal("0.0001"))),
            "coverage_score": score,
            "score_parts": score_parts,
            "coverage_status": self._coverage_status(score, target["stage"]),
            "next_action": self._chain_next_action(
                chain=chain,
                missing_dexes=missing_dexes,
                missing_tokens=[symbol for symbol in token_targets if symbol not in configured_tokens],
                quote_ready_routes=quote_ready_routes,
            ),
            "notes": target["notes"],
        }

    def _score_parts(
        self,
        *,
        chain: str,
        configured_tokens: list[str],
        token_targets: list[str],
        configured_target_dexes: list[str],
        dex_targets: list[str],
        quote_ready_routes: list[str],
        active_quote_coverage: bool,
        provider_rows: list[dict[str, Any]],
        provider_score: Decimal,
        eth_route: dict[str, Any],
        execution_cost: dict[str, Any],
    ) -> dict[str, int]:
        token_score = round(15 * (len(configured_tokens) / len(token_targets))) if token_targets else 0
        dex_score = round(15 * (len(configured_target_dexes) / len(dex_targets))) if dex_targets else 0
        provider_count = len([row for row in provider_rows if str(row.get("provider_type")) == "dex"])
        quote_provider_score = min(20, provider_count * 10)
        quote_score = min(20, len(quote_ready_routes) * 10)
        health_score = min(15, round(provider_score * Decimal("0.15"))) if provider_rows else 0
        execution_score = 0
        if chain == "base":
            confidence = str(execution_cost.get("confidence", "UNKNOWN"))
            execution_score = {"HIGH": 10, "MEDIUM": 6, "LOW": 3}.get(confidence, 0)
        route_score = 0
        if chain == "base" and eth_route.get("route_architecture_decision"):
            route_score = 5
        if active_quote_coverage:
            quote_score = max(quote_score, 10)
        return {
            "token_registry": token_score,
            "dex_registry": dex_score,
            "quote_provider": quote_provider_score,
            "quote_evidence": quote_score,
            "provider_health": health_score,
            "execution_cost_evidence": execution_score,
            "route_architecture": route_score,
        }

    @staticmethod
    def _quote_ready_routes(chain: str, quote_rows: list[dict[str, Any]]) -> list[str]:
        grouped: dict[str, set[str]] = {}
        for row in quote_rows:
            if str(row.get("chain", "")).lower() != chain:
                continue
            if str(row.get("status", "")).upper() != "OK":
                continue
            pair = str(row.get("pair", "")).upper()
            if pair not in {"WETH/USDC", "USDC/WETH", "WETH/USDT", "USDT/WETH", "WETH/DAI", "DAI/WETH"}:
                continue
            grouped.setdefault(pair, set()).add(str(row.get("dex", "")))
        return sorted(pair for pair, dexes in grouped.items() if len({dex for dex in dexes if dex}) >= 2)

    @staticmethod
    def _active_quote_coverage(chain: str, quote_coverage: dict[str, Any]) -> bool:
        rows = quote_coverage.get("pair_coverage")
        if not isinstance(rows, list):
            return False
        return any(
            isinstance(row, dict)
            and str(row.get("chain", "")).lower() == chain
            and str(row.get("pair", "")).upper() == "WETH/USDC"
            and str(row.get("status")) == "ACTIVE_QUOTED"
            for row in rows
        )

    @staticmethod
    def _provider_score(rows: list[dict[str, Any]]) -> Decimal:
        scores = []
        for row in rows:
            try:
                scores.append(Decimal(str(row.get("score"))))
            except Exception:
                continue
        if not scores:
            return Decimal("0")
        return sum(scores, Decimal("0")) / Decimal(len(scores))

    @staticmethod
    def _coverage_status(score: int, stage: str) -> str:
        if score >= 85 and stage == "reference":
            return "REFERENCE_READY"
        if score >= 85:
            return "HIGH_MATURITY"
        if score >= 60:
            return "DEVELOPING"
        if score >= 30:
            return "EARLY"
        return "TARGET_ONLY"

    @staticmethod
    def _overall_score(chain_rows: list[dict[str, Any]]) -> int:
        if not chain_rows:
            return 0
        base = next((row for row in chain_rows if row["chain"] == "base"), None)
        others = [row for row in chain_rows if row["chain"] != "base"]
        other_avg = sum((row["coverage_score"] for row in others), 0) / len(others) if others else 0
        if not base:
            return round(other_avg)
        return round((base["coverage_score"] * 0.55) + (other_avg * 0.45))

    @staticmethod
    def _overall_status(score: int) -> str:
        if score >= 85:
            return "ETH_COVERAGE_READY"
        if score >= 60:
            return "ETH_COVERAGE_DEVELOPING"
        if score >= 35:
            return "ETH_COVERAGE_EARLY"
        return "ETH_COVERAGE_TARGET_ONLY"

    @staticmethod
    def _chain_next_action(chain: str, missing_dexes: list[str], missing_tokens: list[str], quote_ready_routes: list[str]) -> str:
        if chain == "base" and quote_ready_routes:
            return "Improve sustained three-venue quote OK rate and paper execution samples before expanding beyond Base ETH."
        if missing_tokens:
            return f"Add verified token metadata for {chain}: {', '.join(missing_tokens)}."
        if missing_dexes:
            return f"Add verified DEX metadata/providers for {chain}: {', '.join(missing_dexes)}."
        return f"Run two-DEX quote diagnostics for {chain} ETH/stable routes."

    @staticmethod
    def _next_actions(chain_rows: list[dict[str, Any]]) -> list[str]:
        base = next((row for row in chain_rows if row["chain"] == "base"), None)
        actions = []
        if base and base["coverage_status"] != "REFERENCE_READY":
            actions.append("Keep ETH Golden Path on Base until coverage score reaches reference-ready maturity.")
        actions.append("Collect sustained Base Uniswap V3 quote diagnostics before adding a new asset class.")
        actions.append("Add Optimism registry metadata only after official token/DEX/router addresses are verified.")
        actions.append("Do not expand to BTC or blue chips until ETH coverage KPIs are stable.")
        return actions

    @staticmethod
    def _findings(chain_rows: list[dict[str, Any]], overall_score: int) -> list[dict[str, str]]:
        base = next((row for row in chain_rows if row["chain"] == "base"), {})
        target_only = [row for row in chain_rows if row["coverage_status"] == "TARGET_ONLY"]
        return [
            {"severity": "INFO", "message": f"ETH Golden Path overall coverage score is {overall_score}."},
            {
                "severity": "ACTION",
                "message": f"Base reference coverage score is {base.get('coverage_score', 0)} with status {base.get('coverage_status', 'UNKNOWN')}.",
            },
            {
                "severity": "ACTION",
                "message": f"{len(target_only)} target chain(s) still have target-only or near-empty evidence coverage.",
            },
        ]

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# CryptoAI ETH Market Coverage",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Asset focus: `{payload['asset_focus']}`",
            f"- Coverage model: `{payload['coverage_model']}`",
            f"- Overall score: `{payload['overall_coverage_score']}`",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Target chains: `{payload['target_chain_count']}`",
            f"- Configured target chains: `{payload['configured_target_chain_count']}`",
            f"- Target DEXs: `{payload['target_dex_count']}`",
            f"- Configured target DEXs: `{payload['configured_target_dex_count']}`",
            f"- Quote-ready routes: `{payload['quote_ready_route_count']}`",
            "",
            "## Chain Coverage",
            "",
            "| Chain | Stage | Score | Status | Tokens | DEXs | Quote Routes | Providers | Next Action |",
            "|---|---|---:|---|---:|---:|---:|---:|---|",
        ]
        for row in payload["chains"]:
            lines.append(
                f"| {row['name']} | {row['stage']} | {row['coverage_score']} | {row['coverage_status']} | "
                f"{len(row['configured_tokens'])}/{len(row['configured_tokens']) + len(row['missing_tokens'])} | "
                f"{row['configured_target_dex_count']}/{len(row['target_dexes'])} | "
                f"{row['quote_ready_route_count']} | {row['provider_count']} | {row['next_action']} |"
            )
        lines += ["", "## Next Actions", ""]
        for action in payload["next_actions"]:
            lines.append(f"- {action}")
        lines += ["", "## Findings", ""]
        for finding in payload["findings"]:
            lines.append(f"- `{finding['severity']}` {finding['message']}")
        lines += ["", "## Notes", ""]
        for note in payload["notes"]:
            lines.append(f"- {note}")
        return "\n".join(lines) + "\n"

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
    def _read_jsonl(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
        return rows

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    print(json.dumps(EthMarketCoverageService().generate(), indent=2))


if __name__ == "__main__":
    main()
