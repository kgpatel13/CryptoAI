from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


class StrategyIntelligenceService:
    """Builds v5.0 strategy-level intelligence from measured paper evidence."""

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.report_json = self.report_dir / "strategy_intelligence.json"
        self.report_md = self.report_dir / "strategy_intelligence.md"

    def generate(self) -> dict[str, Any]:
        strategy_center = self._read_json("strategy_center.json")
        feature_store = self._read_json("feature_store.json")
        optimization = self._read_json("optimization_report.json")
        replay_diagnostics = self._read_json("replay_diagnostics.json")
        execution_cost = self._read_json("execution_cost_evidence.json")
        market_universe = self._read_json("market_universe_evidence.json")
        quote_coverage = self._read_json("quote_coverage_evidence.json")
        eth_route = self._read_json("eth_route_architecture.json")
        experiment = self._read_json("experiment_report.json")
        provider = self._read_json("provider_monitor.json")
        paper = self._read_json("paper_report.json")
        audit = self._read_json("report_audit.json")

        strategies = strategy_center.get("strategies", [])
        if not isinstance(strategies, list):
            strategies = []

        context = self._context(
            feature_store=feature_store,
            optimization=optimization,
            replay_diagnostics=replay_diagnostics,
            execution_cost=execution_cost,
            market_universe=market_universe,
            quote_coverage=quote_coverage,
            eth_route=eth_route,
            experiment=experiment,
            provider=provider,
            paper=paper,
            audit=audit,
        )
        rows = [self._strategy_row(row, context) for row in strategies if isinstance(row, dict)]
        rows.sort(key=lambda row: (row["intelligence_score"], row["strategy_name"]), reverse=True)

        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "strategy_count": len(rows),
            "top_recommendation": rows[0]["recommendation"] if rows else "NEEDS_MORE_DATA",
            "promotion_allowed": False,
            "context": context,
            "strategies": rows,
            "notes": [
                "Strategy Intelligence is advisory and paper-only.",
                "Risk engine remains the final authority before paper execution.",
                "promotion_allowed is always false until dedicated live-readiness gates are implemented and approved.",
            ],
        }
        self.report_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.report_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _context(
        self,
        *,
        feature_store: dict[str, Any],
        optimization: dict[str, Any],
        replay_diagnostics: dict[str, Any],
        execution_cost: dict[str, Any],
        market_universe: dict[str, Any],
        quote_coverage: dict[str, Any],
        eth_route: dict[str, Any],
        experiment: dict[str, Any],
        provider: dict[str, Any],
        paper: dict[str, Any],
        audit: dict[str, Any],
    ) -> dict[str, Any]:
        best = optimization.get("best_scenario") if isinstance(optimization.get("best_scenario"), dict) else {}
        latest_experiment = (
            experiment.get("latest_experiment")
            if isinstance(experiment.get("latest_experiment"), dict)
            else experiment
        )
        paper_analytics = paper.get("portfolio_analytics", {}) if isinstance(paper.get("portfolio_analytics"), dict) else {}
        cost_assessment = execution_cost.get("assessment") if isinstance(execution_cost.get("assessment"), dict) else {}
        primary_focus = market_universe.get("primary_focus") if isinstance(market_universe.get("primary_focus"), dict) else {}
        eth_promotion = eth_route.get("buffer_promotion", {}) if isinstance(eth_route.get("buffer_promotion"), dict) else {}
        eth_scenarios = eth_route.get("combined_buffer_scenarios", {}) if isinstance(eth_route.get("combined_buffer_scenarios"), dict) else {}
        eth_candidate = eth_scenarios.get("candidate_0_20", {}) if isinstance(eth_scenarios.get("candidate_0_20"), dict) else {}
        eth_production = eth_scenarios.get("production_0_30", {}) if isinstance(eth_scenarios.get("production_0_30"), dict) else {}
        return {
            "feature_count": self._int(feature_store.get("feature_count")),
            "tradeable_or_filled_count": self._int(feature_store.get("tradeable_or_filled_count")),
            "optimization_best_trades": self._int(best.get("trade_count")),
            "optimization_best_pnl_usd": str(best.get("total_pnl_usd", "0")),
            "optimization_best_cost_buffer_pct": str(best.get("cost_buffer_pct", "-")),
            "replay_production_cost_buffer_pct": str(replay_diagnostics.get("production_cost_buffer_pct", "-")),
            "replay_production_trade_count": self._int(replay_diagnostics.get("production_trade_count")),
            "replay_best_profitable_cost_buffer_pct": str(replay_diagnostics.get("best_profitable_cost_buffer_pct", "-")),
            "replay_best_profitable_trade_count": self._int(replay_diagnostics.get("best_profitable_trade_count")),
            "replay_best_profitable_total_pnl_usd": str(replay_diagnostics.get("best_profitable_total_pnl_usd", "0")),
            "execution_cost_buffer_status": str(execution_cost.get("buffer_status", cost_assessment.get("buffer_status", "UNKNOWN"))),
            "execution_cost_confidence": str(execution_cost.get("confidence", cost_assessment.get("confidence", "UNKNOWN"))),
            "execution_cost_lower_bound_pct": str(
                execution_cost.get(
                    "observed_total_cost_lower_bound_pct",
                    cost_assessment.get("observed_total_cost_lower_bound_pct", "-"),
                )
            ),
            "execution_cost_buffer_surplus_pct": str(
                execution_cost.get(
                    "buffer_surplus_vs_lower_bound_pct",
                    cost_assessment.get("buffer_surplus_vs_lower_bound_pct", "-"),
                )
            ),
            "market_primary_focus": self._format_focus(primary_focus),
            "market_active_focus_count": self._int(market_universe.get("active_focus_count")),
            "market_research_target_count": self._int(market_universe.get("research_target_count")),
            "market_blocked_count": self._int(market_universe.get("blocked_count")),
            "quote_coverage_available": bool(quote_coverage),
            "quote_active_pair_count": self._int(quote_coverage.get("active_pair_count")),
            "quote_provider_gap_count": self._int(quote_coverage.get("provider_gap_count")),
            "quote_test_gap_count": self._int(quote_coverage.get("quote_gap_count")),
            "quote_next_target": self._format_quote_target(quote_coverage),
            "eth_route_available": bool(eth_route),
            "eth_route_decision": str(eth_route.get("route_architecture_decision", "-")),
            "eth_candidate_buffer_pct": str(eth_route.get("candidate_buffer_pct", "-")),
            "eth_production_buffer_pct": str(eth_route.get("production_buffer_pct", "-")),
            "eth_promotion_passed_gates": self._int(eth_promotion.get("passed_gate_count")),
            "eth_promotion_gate_count": self._int(eth_promotion.get("gate_count")),
            "eth_candidate_positive_count": self._int(eth_candidate.get("positive_after_buffer_count")),
            "eth_production_positive_count": self._int(eth_production.get("positive_after_buffer_count")),
            "experiment_status": str(latest_experiment.get("status", experiment.get("status", "UNKNOWN"))),
            "experiment_fail_count": self._int(latest_experiment.get("fail_count", experiment.get("fail_count"))),
            "experiment_warn_count": self._int(latest_experiment.get("warn_count", experiment.get("warn_count"))),
            "provider_status": str(provider.get("overall_status", "UNKNOWN")),
            "provider_alert_count": self._int(provider.get("alert_count")),
            "audit_finding_count": self._audit_finding_count(audit),
            "paper_total_pnl_usd": str(paper_analytics.get("total_pnl_usd", "0")),
            "paper_total_return_pct": str(paper_analytics.get("total_return_pct", "0")),
            "paper_filled_orders": self._int(paper.get("filled_orders")),
        }

    def _strategy_row(self, strategy: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        score, factors = self._score(strategy, context)
        blockers = self._blockers(strategy, context)
        recommendation = self._recommendation(strategy, context, score, blockers)
        return {
            "strategy_id": strategy.get("strategy_id", "unknown"),
            "strategy_name": strategy.get("strategy_name", strategy.get("name", "unknown")),
            "enabled": bool(strategy.get("enabled")),
            "health": strategy.get("health", "UNKNOWN"),
            "orders": self._int(strategy.get("orders")),
            "filled_orders": self._int(strategy.get("filled_orders")),
            "closed_positions": self._int(strategy.get("closed_positions")),
            "risk_rejected_orders": self._int(strategy.get("risk_rejected_orders")),
            "realized_pnl_usd": str(strategy.get("realized_pnl_usd", "0")),
            "win_rate_pct": str(strategy.get("win_rate_pct", "-")),
            "avg_slippage_bps": strategy.get("avg_slippage_bps"),
            "avg_latency_ms": strategy.get("avg_latency_ms"),
            "intelligence_score": score,
            "recommendation": recommendation,
            "blockers": blockers,
            "score_factors": factors,
            "next_actions": self._next_actions(recommendation, blockers, context),
        }

    def _score(self, strategy: dict[str, Any], context: dict[str, Any]) -> tuple[int, list[str]]:
        score = 0
        factors: list[str] = []
        if strategy.get("enabled"):
            score += 15
            factors.append("+15 enabled strategy")
        else:
            factors.append("+0 disabled strategy")

        filled = self._int(strategy.get("filled_orders"))
        filled_points = min(20, filled * 2)
        score += filled_points
        factors.append(f"+{filled_points} filled-order evidence")

        closed = self._int(strategy.get("closed_positions"))
        pnl = self._decimal(strategy.get("realized_pnl_usd"))
        if pnl > 0:
            score += 18
            factors.append("+18 positive realized PnL")
        elif pnl == 0:
            score += 6
            factors.append("+6 non-negative realized PnL")
        else:
            score -= 15
            factors.append("-15 negative realized PnL")

        win_rate = self._decimal(strategy.get("win_rate_pct"))
        if closed >= 10 and win_rate >= Decimal("55"):
            score += 12
            factors.append("+12 meaningful positive win-rate sample")
        elif closed > 0 and win_rate >= Decimal("50"):
            score += 6
            factors.append("+6 early positive win-rate sample")

        if context["optimization_best_trades"] >= 5 and self._decimal(context["optimization_best_pnl_usd"]) > 0:
            score += 15
            factors.append("+15 optimization has positive sample")

        paper_pnl = self._decimal(context["paper_total_pnl_usd"])
        if paper_pnl >= 0:
            score += 8
            factors.append("+8 paper portfolio PnL non-negative")
        else:
            score -= 12
            factors.append("-12 paper portfolio PnL negative")

        provider_status = context["provider_status"]
        if provider_status == "OK":
            score += 8
            factors.append("+8 provider status OK")
        elif provider_status == "WATCH":
            score += 3
            factors.append("+3 provider status WATCH")
        elif provider_status in {"CRITICAL", "DEGRADED"}:
            score -= 20
            factors.append("-20 provider status blocks tuning")

        if context["audit_finding_count"] == 0:
            score += 7
            factors.append("+7 report audit clean")
        else:
            score -= 10
            factors.append("-10 report audit findings")

        feature_points = min(10, context["feature_count"] // 50)
        score += feature_points
        factors.append(f"+{feature_points} feature-store depth")

        if context["experiment_fail_count"]:
            score -= 15
            factors.append("-15 experiment gate failure")
        elif context["experiment_warn_count"]:
            score += 2
            factors.append("+2 experiment watchlist")
        else:
            score += 8
            factors.append("+8 experiment gates pass")

        return max(0, min(100, score)), factors

    def _blockers(self, strategy: dict[str, Any], context: dict[str, Any]) -> list[str]:
        blockers = ["Live trading is disabled; this is advisory paper intelligence only."]
        if not strategy.get("enabled"):
            blockers.append("Strategy is disabled in the strategy registry.")
        if context["provider_status"] in {"CRITICAL", "DEGRADED"}:
            blockers.append(f"Provider status is {context['provider_status']}.")
        if context["audit_finding_count"]:
            blockers.append(f"Report audit has {context['audit_finding_count']} finding(s).")
        if context["experiment_fail_count"]:
            blockers.append(f"Experiment evidence has {context['experiment_fail_count']} failing gate(s).")
        if context["replay_production_trade_count"] == 0 and context["replay_best_profitable_trade_count"] > 0:
            blockers.append(
                "Production replay has 0 trades while lower cost-buffer diagnostics are profitable."
            )
        if context["execution_cost_buffer_status"] == "INSUFFICIENT_EVIDENCE":
            blockers.append("Execution cost evidence is insufficient.")
        if context["execution_cost_buffer_status"] == "TOO_LOW":
            blockers.append("Execution cost evidence indicates the production buffer may be too low.")
        if context["market_blocked_count"] and context["market_active_focus_count"] == 0:
            blockers.append("No active market universe focus has enough quote evidence.")
        if context["quote_coverage_available"] and context["quote_active_pair_count"] == 0:
            blockers.append("No configured pair has two-DEX quote coverage.")
        if context["eth_route_available"] and context["eth_route_decision"] == "KEEP_0_30_PRODUCTION_RESEARCH_0_20":
            blockers.append("ETH route evidence keeps 0.20% buffer research-only; production buffer remains 0.30%.")
        if self._int(strategy.get("closed_positions")) < 10:
            blockers.append("Closed paper-trade sample is below the 10-trade minimum for strategy confidence.")
        return blockers

    @staticmethod
    def _recommendation(strategy: dict[str, Any], context: dict[str, Any], score: int, blockers: list[str]) -> str:
        if not strategy.get("enabled"):
            return "RESEARCH_DISABLED"
        if context["provider_status"] in {"CRITICAL", "DEGRADED"} or context["audit_finding_count"]:
            return "HOLD_FIX_OPERATIONS"
        if context["experiment_fail_count"]:
            return "CONTINUE_RESEARCH"
        if score >= 75 and context["experiment_warn_count"] == 0 and len(blockers) == 1:
            return "PAPER_OPTIMIZE_CANDIDATE"
        if score >= 55:
            return "WATCHLIST"
        return "NEEDS_MORE_DATA"

    @staticmethod
    def _next_actions(recommendation: str, blockers: list[str], context: dict[str, Any]) -> list[str]:
        if recommendation == "HOLD_FIX_OPERATIONS":
            return ["Fix provider/audit findings, regenerate reports, and rerun experiment evidence."]
        if recommendation == "CONTINUE_RESEARCH":
            if context.get("execution_cost_buffer_status") == "TOO_HIGH":
                return [
                    (
                        "Keep production buffer unchanged; prepare a research-only cost-buffer candidate "
                        "after confirming high-confidence execution-cost evidence."
                    )
                ]
            if context.get("execution_cost_buffer_status") in {"CONSERVATIVE", "SLIGHTLY_CONSERVATIVE"}:
                return [
                    (
                        f"Keep production buffer unchanged; focus {context['market_primary_focus']} and collect more "
                        f"execution-cost samples until {context['execution_cost_lower_bound_pct']}% lower-bound evidence is high confidence. "
                        f"Next quote expansion target: {context['quote_next_target']}. "
                        f"ETH route buffer gates: {context['eth_promotion_passed_gates']}/{context['eth_promotion_gate_count']}."
                    )
                ]
            if context.get("replay_best_profitable_trade_count", 0):
                return [
                    (
                        "Keep production buffer unchanged; collect execution-cost evidence to prove whether "
                        f"{context['replay_best_profitable_cost_buffer_pct']}% is realistic."
                    )
                ]
            return ["Improve replay coverage until default replay produces positive production-buffer trades."]
        if recommendation == "WATCHLIST":
            return ["Continue paper cycles and collect more closed-trade evidence before tuning risk upward."]
        if recommendation == "PAPER_OPTIMIZE_CANDIDATE":
            return ["Run walk-forward validation and compare optimization stability across cost buffers."]
        if "Strategy is disabled in the strategy registry." in blockers:
            return ["Keep disabled until its feature pipeline and validation tests are implemented."]
        if context["feature_count"] < 100:
            return ["Collect more feature vectors through paper cycles before strategy comparison."]
        return ["Keep collecting paper evidence and review the next report audit."]

    def _markdown(self, payload: dict[str, Any]) -> str:
        context = payload["context"]
        lines = [
            "# CryptoAI Strategy Intelligence",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Mode: `{payload['mode']}`",
            f"- Strategies: `{payload['strategy_count']}`",
            f"- Top recommendation: `{payload['top_recommendation']}`",
            f"- Promotion allowed: `{payload['promotion_allowed']}`",
            f"- Provider status: `{context['provider_status']}`",
            f"- Experiment: `{context['experiment_status']}` with `{context['experiment_fail_count']}` fail / `{context['experiment_warn_count']}` warn",
            f"- Report audit findings: `{context['audit_finding_count']}`",
            f"- Replay production trades: `{context['replay_production_trade_count']}` at `{context['replay_production_cost_buffer_pct']}` cost buffer",
            f"- Replay best profitable buffer: `{context['replay_best_profitable_cost_buffer_pct']}` with `{context['replay_best_profitable_trade_count']}` trade(s)",
            f"- Execution cost status: `{context['execution_cost_buffer_status']}` with `{context['execution_cost_confidence']}` confidence",
            f"- Observed cost lower bound %: `{context['execution_cost_lower_bound_pct']}`",
            f"- Market primary focus: `{context['market_primary_focus']}`",
            f"- Market universe: `{context['market_active_focus_count']}` active / `{context['market_research_target_count']}` research / `{context['market_blocked_count']}` blocked",
            f"- Quote coverage: `{context['quote_active_pair_count']}` active / `{context['quote_test_gap_count']}` quote-test gaps / `{context['quote_provider_gap_count']}` provider gaps",
            f"- Next quote target: `{context['quote_next_target']}`",
            f"- ETH route decision: `{context['eth_route_decision']}`",
            f"- ETH route buffers: production `{context['eth_production_buffer_pct']}` / candidate `{context['eth_candidate_buffer_pct']}`",
            f"- ETH route promotion gates: `{context['eth_promotion_passed_gates']}/{context['eth_promotion_gate_count']}`",
            "",
            "## Strategies",
            "",
            "| Strategy | Enabled | Score | Recommendation | Filled | Closed | PnL | Win Rate | Blockers |",
            "|---|---:|---:|---|---:|---:|---:|---:|---|",
        ]
        for row in payload["strategies"]:
            blockers = "; ".join(row.get("blockers", []))
            lines.append(
                f"| {row['strategy_name']} | {row['enabled']} | {row['intelligence_score']} | "
                f"{row['recommendation']} | {row['filled_orders']} | {row['closed_positions']} | "
                f"{row['realized_pnl_usd']} | {row['win_rate_pct']} | {blockers.replace('|', '/')} |"
            )
        lines += ["", "## Next Actions", ""]
        for row in payload["strategies"]:
            lines.append(f"### {row['strategy_name']}")
            for action in row.get("next_actions", []):
                lines.append(f"- {action}")
            lines.append("")
        lines += ["## Notes", ""]
        for note in payload["notes"]:
            lines.append(f"- {note}")
        return "\n".join(lines).rstrip() + "\n"

    def _read_json(self, name: str) -> dict[str, Any]:
        path = self.report_dir / name
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def _int(value: Any) -> int:
        try:
            return int(value or 0)
        except Exception:
            return 0

    @staticmethod
    def _format_focus(focus: dict[str, Any]) -> str:
        chain = focus.get("chain")
        pair = focus.get("pair")
        if chain and pair:
            return f"{chain} {pair}"
        return "-"

    @staticmethod
    def _format_quote_target(quote_coverage: dict[str, Any]) -> str:
        targets = quote_coverage.get("next_provider_targets")
        if isinstance(targets, list) and targets and isinstance(targets[0], dict):
            chain = targets[0].get("chain")
            pair = targets[0].get("pair")
            if chain and pair:
                return f"{chain} {pair}"
        return "-"

    @classmethod
    def _audit_finding_count(cls, audit: dict[str, Any]) -> int:
        findings = audit.get("findings")
        if not isinstance(findings, list):
            return cls._int(audit.get("finding_count"))
        actionable = [
            finding
            for finding in findings
            if not (
                isinstance(finding, dict)
                and finding.get("report") in {"strategy_intelligence.json", "strategy_intelligence.md"}
                and finding.get("message") == "Report is older than freshness window."
            )
        ]
        return len(actionable)

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        try:
            if value in {None, "", "-"}:
                return Decimal("0")
            return Decimal(str(value))
        except Exception:
            return Decimal("0")

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    payload = StrategyIntelligenceService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
