from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


class EthRouteArchitectureService:
    """Builds Base ETH route architecture and buffer promotion evidence."""

    FOCUS_CHAIN = "base"
    FOCUS_ROUTES = ("WETH/USDC", "USDC/WETH")
    CURRENT_PRODUCTION_BUFFER = Decimal("0.30")
    RESEARCH_BUFFER_CANDIDATE = Decimal("0.20")
    REPLAY_NOTIONAL_USD = Decimal("1000")

    TRUSTED_VENUES = [
        {
            "chain": "base",
            "venue": "Uniswap V2",
            "role": "implemented_quote_provider",
            "status": "ACTIVE",
            "source": "local_provider",
            "notes": "Currently producing Base WETH/USDC and USDC/WETH quote evidence.",
        },
        {
            "chain": "base",
            "venue": "Aerodrome",
            "role": "implemented_quote_provider",
            "status": "ACTIVE",
            "source": "local_provider",
            "notes": "Currently producing Base WETH/USDC and USDC/WETH quote evidence.",
        },
        {
            "chain": "base",
            "venue": "Uniswap V3",
            "role": "verified_next_provider_target",
            "status": "NOT_IMPLEMENTED",
            "source": "official_uniswap_base_deployments",
            "notes": "Official Base deployment exists; quote provider and route tests are still required locally.",
        },
    ]

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.report_json = self.report_dir / "eth_route_architecture.json"
        self.report_md = self.report_dir / "eth_route_architecture.md"

    def generate(self) -> dict[str, Any]:
        quote_rows = self._read_jsonl(self.data_dir / "quote_diagnostics.jsonl")[-500:]
        opportunity_rows = self._dedupe_opportunity_rows(self._read_jsonl(self.data_dir / "multi_dex_opportunities.jsonl"))
        quote_coverage = self._read_json(self.report_dir / "quote_coverage_evidence.json")
        execution_cost = self._read_json(self.report_dir / "execution_cost_evidence.json")
        provider_monitor = self._read_json(self.report_dir / "provider_monitor.json")
        report_audit = self._read_json(self.report_dir / "report_audit.json")

        route_rows = self._route_rows(quote_rows=quote_rows, opportunity_rows=opportunity_rows)
        combined_candidate = self._scenario_for_rows(opportunity_rows, self.RESEARCH_BUFFER_CANDIDATE, self.FOCUS_ROUTES)
        combined_production = self._scenario_for_rows(opportunity_rows, self.CURRENT_PRODUCTION_BUFFER, self.FOCUS_ROUTES)
        promotion = self._buffer_promotion(
            quote_coverage=quote_coverage,
            execution_cost=execution_cost,
            provider_monitor=provider_monitor,
            report_audit=report_audit,
            candidate=combined_candidate,
        )
        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "focus_chain": self.FOCUS_CHAIN,
            "focus_routes": list(self.FOCUS_ROUTES),
            "production_buffer_pct": str(self.CURRENT_PRODUCTION_BUFFER),
            "candidate_buffer_pct": str(self.RESEARCH_BUFFER_CANDIDATE),
            "route_architecture_decision": promotion["decision"],
            "trusted_venues": self.TRUSTED_VENUES,
            "route_evidence": route_rows,
            "combined_buffer_scenarios": {
                "candidate_0_20": combined_candidate,
                "production_0_30": combined_production,
            },
            "buffer_promotion": promotion,
            "real_money_architecture": self._real_money_architecture(),
            "findings": self._findings(promotion, route_rows, combined_candidate, combined_production),
            "references": [
                {
                    "name": "Uniswap v3 Base deployments",
                    "url": "https://developers.uniswap.org/docs/protocols/v3/deployments/v3-base-deployments",
                    "usage": "Verify Base Uniswap v3 deployment before local provider implementation.",
                },
                {
                    "name": "Uniswap deployments guidance",
                    "url": "https://developers.uniswap.org/docs/protocols/v3/deployments",
                    "usage": "Do not assume contract addresses are identical across chains.",
                },
                {
                    "name": "Aerodrome documentation",
                    "url": "https://aerodrome.finance/docs",
                    "usage": "Base DEX and liquidity hub reference for implemented Aerodrome route evidence.",
                },
            ],
            "notes": [
                "This report is architecture and paper evidence only.",
                "It does not change production cost buffers, paper thresholds, risk thresholds, or live eligibility.",
                "A 0.20% buffer remains research-only until every promotion gate passes and the project owner approves a separate change.",
            ],
        }
        self.report_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.report_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _route_rows(self, *, quote_rows: list[dict[str, Any]], opportunity_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = []
        for route in self.FOCUS_ROUTES:
            ok_dexes = sorted(
                {
                    str(row.get("dex"))
                    for row in quote_rows
                    if str(row.get("chain", "")).lower() == self.FOCUS_CHAIN
                    and str(row.get("pair", "")).upper() == route
                    and str(row.get("status", "")).upper() == "OK"
                    and row.get("dex")
                }
            )
            candidate = self._scenario_for_rows(opportunity_rows, self.RESEARCH_BUFFER_CANDIDATE, (route,))
            production = self._scenario_for_rows(opportunity_rows, self.CURRENT_PRODUCTION_BUFFER, (route,))
            rows.append(
                {
                    "chain": self.FOCUS_CHAIN,
                    "route": route,
                    "trusted_active_dex_count": len(ok_dexes),
                    "trusted_active_dexes": ok_dexes,
                    "two_dex_quote_ready": len(ok_dexes) >= 2,
                    "candidate_0_20": candidate,
                    "production_0_30": production,
                    "recommended_action": self._route_action(route, ok_dexes, candidate, production),
                }
            )
        return rows

    def _scenario_for_rows(
        self,
        rows: list[dict[str, Any]],
        buffer_pct: Decimal,
        routes: tuple[str, ...],
    ) -> dict[str, Any]:
        route_set = {route.upper() for route in routes}
        considered = 0
        trades = []
        for row in rows[-1000:]:
            if str(row.get("mode", "REAL")).upper() != "REAL":
                continue
            if str(row.get("chain", "")).lower() != self.FOCUS_CHAIN:
                continue
            if str(row.get("pair", "")).upper() not in route_set:
                continue
            gross_edge = self._to_decimal(row.get("gross_edge_pct"))
            if gross_edge is None:
                continue
            considered += 1
            net_edge = gross_edge - buffer_pct
            if net_edge <= 0:
                continue
            pnl = (self.REPLAY_NOTIONAL_USD * net_edge / Decimal("100")).quantize(Decimal("0.0001"))
            trades.append(
                {
                    "timestamp": str(row.get("timestamp", "-")),
                    "route": str(row.get("pair", "-")),
                    "buy_dex": str(row.get("buy_dex", "-")),
                    "sell_dex": str(row.get("sell_dex", "-")),
                    "gross_edge_pct": str(gross_edge),
                    "net_edge_pct": str(net_edge.quantize(Decimal("0.0001"))),
                    "pnl_usd": str(pnl),
                }
            )
        total_pnl = sum((self._decimal(row["pnl_usd"]) for row in trades), Decimal("0")).quantize(Decimal("0.0001"))
        avg_net = (
            sum((self._decimal(row["net_edge_pct"]) for row in trades), Decimal("0")) / Decimal(len(trades))
        ).quantize(Decimal("0.0001")) if trades else Decimal("0.0000")
        max_net = max((self._decimal(row["net_edge_pct"]) for row in trades), default=Decimal("0")).quantize(Decimal("0.0001"))
        return {
            "buffer_pct": str(buffer_pct),
            "replay_notional_usd": str(self.REPLAY_NOTIONAL_USD),
            "considered_signals": considered,
            "positive_after_buffer_count": len(trades),
            "total_pnl_usd": str(total_pnl),
            "avg_net_edge_pct": str(avg_net),
            "max_net_edge_pct": str(max_net),
            "recent_trades": trades[-10:],
        }

    def _buffer_promotion(
        self,
        *,
        quote_coverage: dict[str, Any],
        execution_cost: dict[str, Any],
        provider_monitor: dict[str, Any],
        report_audit: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        execution_paper = execution_cost.get("paper_execution_evidence", {})
        quote_evidence = execution_cost.get("quote_evidence", {})
        gates = [
            self._gate("execution_cost_confidence_high", execution_cost.get("confidence") == "HIGH", execution_cost.get("confidence", "UNKNOWN")),
            self._gate("paper_slippage_samples_30_plus", self._int(execution_paper.get("sample_count")) >= 30, execution_paper.get("sample_count")),
            self._gate("quote_ok_rate_90_plus", self._decimal(quote_evidence.get("ok_rate_pct")) >= Decimal("90"), quote_evidence.get("ok_rate_pct")),
            self._gate("active_two_dex_eth_route", self._has_active_eth_route(quote_coverage), quote_coverage.get("active_pair_count")),
            self._gate("provider_not_critical", provider_monitor.get("overall_status") not in {"CRITICAL", "DEGRADED"}, provider_monitor.get("overall_status")),
            self._gate("report_audit_clean", self._int(report_audit.get("finding_count")) == 0, report_audit.get("finding_count")),
            self._gate("candidate_has_30_plus_signals", self._int(candidate.get("positive_after_buffer_count")) >= 30, candidate.get("positive_after_buffer_count")),
            self._gate("candidate_avg_net_edge_0_03_plus", self._decimal(candidate.get("avg_net_edge_pct")) >= Decimal("0.03"), candidate.get("avg_net_edge_pct")),
        ]
        passed = sum(1 for gate in gates if gate["passed"])
        if passed == len(gates):
            decision = "READY_FOR_SEPARATE_PAPER_BUFFER_REVIEW"
            next_action = "Open a separate reviewed change to test 0.20% in paper only; do not enable live trading."
        else:
            decision = "KEEP_0_30_PRODUCTION_RESEARCH_0_20"
            next_action = "Keep production buffer at 0.30%; collect missing evidence before any buffer change."
        return {
            "decision": decision,
            "current_production_buffer_pct": str(self.CURRENT_PRODUCTION_BUFFER),
            "research_candidate_buffer_pct": str(self.RESEARCH_BUFFER_CANDIDATE),
            "passed_gate_count": passed,
            "gate_count": len(gates),
            "gates": gates,
            "next_action": next_action,
        }

    @staticmethod
    def _has_active_eth_route(quote_coverage: dict[str, Any]) -> bool:
        rows = quote_coverage.get("pair_coverage")
        if not isinstance(rows, list):
            return False
        return any(
            isinstance(row, dict)
            and str(row.get("chain", "")).lower() == "base"
            and str(row.get("pair", "")).upper() == "WETH/USDC"
            and str(row.get("status")) == "ACTIVE_QUOTED"
            for row in rows
        )

    @staticmethod
    def _route_action(route: str, ok_dexes: list[str], candidate: dict[str, Any], production: dict[str, Any]) -> str:
        if len(ok_dexes) < 2:
            return f"Collect two-DEX quote evidence for {route} before route tuning."
        if int(candidate["positive_after_buffer_count"]) > int(production["positive_after_buffer_count"]):
            return f"Keep {route} in 0.20% research replay; production stays at 0.30%."
        return f"Keep {route} on 0.30% production-paper evidence path."

    @staticmethod
    def _real_money_architecture() -> list[dict[str, Any]]:
        return [
            {
                "stage": "1_quote_fanout",
                "purpose": "Fetch fresh WETH/USDC and USDC/WETH quotes from multiple trusted Base venues.",
                "required_controls": ["fresh quote TTL", "two-venue minimum", "stale quote live block", "provider health score"],
            },
            {
                "stage": "2_opportunity_and_cost_gate",
                "purpose": "Calculate gross edge, subtract observed cost buffer, and reject low-edge routes.",
                "required_controls": ["production buffer gate", "minimum net edge gate", "gas/slippage lower-bound evidence", "replay comparison"],
            },
            {
                "stage": "3_risk_gate",
                "purpose": "Let risk decide before any order can be created.",
                "required_controls": ["position size cap", "daily loss cap", "duplicate exposure block", "cooldown", "kill switch"],
            },
            {
                "stage": "4_transaction_preflight",
                "purpose": "Before real money, simulate exact calldata and amountOutMin against current state.",
                "required_controls": ["allowance cap", "nonce control", "amountOutMin", "deadline", "private RPC or MEV-aware submit path"],
            },
            {
                "stage": "5_execution_and_reconciliation",
                "purpose": "Submit only if all gates pass, then reconcile fill, gas, slippage, and balance changes.",
                "required_controls": ["tx receipt verification", "post-trade accounting", "gas attribution", "automatic halt on mismatch"],
            },
        ]

    @staticmethod
    def _findings(
        promotion: dict[str, Any],
        route_rows: list[dict[str, Any]],
        candidate: dict[str, Any],
        production: dict[str, Any],
    ) -> list[dict[str, str]]:
        route_ready = sum(1 for row in route_rows if row["two_dex_quote_ready"])
        return [
            {"severity": "INFO", "message": f"{route_ready} ETH route direction(s) have two-DEX quote readiness on Base."},
            {
                "severity": "WATCH",
                "message": (
                    f"0.20% candidate replay has {candidate['positive_after_buffer_count']} positive signal(s) versus "
                    f"{production['positive_after_buffer_count']} at 0.30%, but promotion decision is {promotion['decision']}."
                ),
            },
            {"severity": "ACTION", "message": promotion["next_action"]},
            {"severity": "ACTION", "message": "Next venue expansion target for this route is a verified Base Uniswap V3 quote provider."},
        ]

    @staticmethod
    def _gate(name: str, passed: bool, observed: Any) -> dict[str, Any]:
        return {"name": name, "passed": bool(passed), "observed": observed}

    def _markdown(self, payload: dict[str, Any]) -> str:
        promotion = payload["buffer_promotion"]
        lines = [
            "# CryptoAI ETH Route Architecture",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Focus chain: `{payload['focus_chain']}`",
            f"- Focus routes: `{', '.join(payload['focus_routes'])}`",
            f"- Production buffer %: `{payload['production_buffer_pct']}`",
            f"- Research candidate buffer %: `{payload['candidate_buffer_pct']}`",
            f"- Decision: `{payload['route_architecture_decision']}`",
            f"- Promotion gates: `{promotion['passed_gate_count']}/{promotion['gate_count']}`",
            "",
            "## Trusted Venues",
            "",
            "| Venue | Status | Role | Notes |",
            "|---|---|---|---|",
        ]
        for row in payload["trusted_venues"]:
            lines.append(f"| {row['venue']} | {row['status']} | {row['role']} | {row['notes']} |")
        lines += [
            "",
            "## Route Evidence",
            "",
            "| Route | Two-DEX Ready | DEXs | 0.20% Signals | 0.20% PnL | 0.30% Signals | 0.30% PnL | Action |",
            "|---|---|---|---:|---:|---:|---:|---|",
        ]
        for row in payload["route_evidence"]:
            candidate = row["candidate_0_20"]
            production = row["production_0_30"]
            lines.append(
                f"| {row['route']} | {row['two_dex_quote_ready']} | {', '.join(row['trusted_active_dexes'])} | "
                f"{candidate['positive_after_buffer_count']} | {candidate['total_pnl_usd']} | "
                f"{production['positive_after_buffer_count']} | {production['total_pnl_usd']} | "
                f"{row['recommended_action']} |"
            )
        lines += [
            "",
            "## Buffer Promotion Gates",
            "",
            "| Gate | Passed | Observed |",
            "|---|---|---|",
        ]
        for gate in promotion["gates"]:
            lines.append(f"| {gate['name']} | {gate['passed']} | {gate['observed']} |")
        lines += ["", "## Real Money Architecture", ""]
        for stage in payload["real_money_architecture"]:
            controls = ", ".join(stage["required_controls"])
            lines.append(f"- `{stage['stage']}`: {stage['purpose']} Controls: {controls}.")
        lines += ["", "## Findings", ""]
        for finding in payload["findings"]:
            lines.append(f"- `{finding['severity']}` {finding['message']}")
        lines += ["", "## References", ""]
        for ref in payload["references"]:
            lines.append(f"- [{ref['name']}]({ref['url']}) - {ref['usage']}")
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
    def _dedupe_opportunity_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen = set()
        deduped = []
        for row in rows:
            key = (
                row.get("timestamp"),
                row.get("mode"),
                row.get("chain"),
                row.get("pair"),
                row.get("buy_dex"),
                row.get("sell_dex"),
                row.get("gross_edge_pct"),
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(row)
        return deduped

    @staticmethod
    def _to_decimal(value: Any) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except Exception:
            return Decimal("0")

    @staticmethod
    def _int(value: Any) -> int:
        try:
            return int(value)
        except Exception:
            return 0

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    print(json.dumps(EthRouteArchitectureService().generate(), indent=2))


if __name__ == "__main__":
    main()
