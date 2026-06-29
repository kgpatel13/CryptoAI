from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


class MarketUniverseEvidenceService:
    """Ranks chain/pair/DEX coverage and research-only settings from measured evidence."""

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.report_json = self.report_dir / "market_universe_evidence.json"
        self.report_md = self.report_dir / "market_universe_evidence.md"

    def generate(self) -> dict[str, Any]:
        market = self._read_json(self.report_dir / "market_intelligence.json")
        provider = self._read_json(self.report_dir / "provider_monitor.json")
        optimization = self._read_json(self.report_dir / "optimization_report.json")
        execution_cost = self._read_json(self.report_dir / "execution_cost_evidence.json")
        quote_rows = self._read_jsonl(self.data_dir / "quote_diagnostics.jsonl")[-500:]
        opportunity_rows = self._dedupe_opportunity_rows(self._read_jsonl(self.data_dir / "multi_dex_opportunities.jsonl"))

        quote_stats = self._quote_stats(quote_rows)
        opportunity_stats = self._opportunity_stats(
            opportunity_rows=opportunity_rows,
            production_cost_buffer_pct=self._decimal(execution_cost.get("production_cost_buffer_pct", "0.30")),
            paper_buy_threshold_pct=self._decimal(execution_cost.get("paper_buy_threshold_pct", "0.30")),
            observed_lower_bound_pct=self._to_decimal(execution_cost.get("observed_total_cost_lower_bound_pct")),
        )
        universe = self._universe_rows(
            market=market,
            quote_stats=quote_stats,
            opportunity_stats=opportunity_stats,
        )
        settings = self._settings_evidence(
            optimization=optimization,
            execution_cost=execution_cost,
        )

        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "active_focus_count": sum(1 for row in universe if row["classification"] == "ACTIVE_FOCUS"),
            "research_target_count": sum(1 for row in universe if row["classification"] == "RESEARCH_TARGET"),
            "blocked_count": sum(1 for row in universe if row["classification"].startswith("BLOCKED")),
            "primary_focus": self._primary_focus(universe),
            "universe": universe,
            "settings_evidence": settings,
            "provider_status": provider.get("overall_status", "UNKNOWN"),
            "provider_alert_count": provider.get("alert_count", 0),
            "findings": self._findings(universe, settings, provider),
            "notes": [
                "Market Universe Evidence ranks research coverage only.",
                "It does not add live exchange connectivity or change production cost/risk thresholds.",
                "Base WETH/USDC remains the default focus until other chains have quote-provider evidence.",
            ],
        }
        self.report_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.report_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _universe_rows(
        self,
        *,
        market: dict[str, Any],
        quote_stats: dict[tuple[str, str], dict[str, Any]],
        opportunity_stats: dict[tuple[str, str], dict[str, Any]],
    ) -> list[dict[str, Any]]:
        chain_readiness = {
            str(row.get("chain", "")).lower(): row
            for row in market.get("chains", [])
            if isinstance(row, dict)
        }
        rows = []
        for candidate in market.get("pair_candidates", []):
            if not isinstance(candidate, dict):
                continue
            chain = str(candidate.get("chain", "")).lower()
            pair = str(candidate.get("pair", "-")).upper()
            key = (chain, pair)
            chain_row = chain_readiness.get(chain, {})
            quotes = quote_stats.get(key, self._empty_quote_stats())
            opportunities = opportunity_stats.get(key, self._empty_opportunity_stats())
            priority = self._int(candidate.get("priority"), default=50)
            readiness_score = self._int(chain_row.get("readiness_score"))
            score = self._universe_score(
                priority=priority,
                readiness_score=readiness_score,
                quote_ok_rate_pct=self._decimal(quotes["ok_rate_pct"]),
                healthy_dex_count=self._int(quotes["healthy_dex_count"]),
                lower_bound_trade_count=self._int(opportunities["lower_bound_trade_count"]),
                production_trade_count=self._int(opportunities["production_trade_count"]),
            )
            classification = self._classification(
                configured=bool(candidate.get("configured")),
                pair=pair,
                score=score,
                healthy_dex_count=self._int(quotes["healthy_dex_count"]),
                lower_bound_trade_count=self._int(opportunities["lower_bound_trade_count"]),
                production_trade_count=self._int(opportunities["production_trade_count"]),
            )
            rows.append(
                {
                    "chain": chain,
                    "pair": pair,
                    "configured": bool(candidate.get("configured")),
                    "priority": priority,
                    "dex_count": self._int(candidate.get("dex_count")),
                    "chain_readiness_status": chain_row.get("readiness_status", "UNKNOWN"),
                    "chain_readiness_score": readiness_score,
                    "quote_sample_count": quotes["sample_count"],
                    "quote_ok_rate_pct": quotes["ok_rate_pct"],
                    "healthy_dex_count": quotes["healthy_dex_count"],
                    "healthy_dexes": quotes["healthy_dexes"],
                    "real_signal_count": opportunities["real_signal_count"],
                    "max_gross_edge_pct": opportunities["max_gross_edge_pct"],
                    "production_trade_count": opportunities["production_trade_count"],
                    "lower_bound_trade_count": opportunities["lower_bound_trade_count"],
                    "score": score,
                    "classification": classification,
                    "next_action": self._next_action(classification, chain, pair),
                }
            )
        return sorted(rows, key=lambda row: (row["score"], row["configured"], -row["priority"], row["chain"], row["pair"]), reverse=True)

    def _settings_evidence(self, *, optimization: dict[str, Any], execution_cost: dict[str, Any]) -> dict[str, Any]:
        best = optimization.get("best_scenario") if isinstance(optimization.get("best_scenario"), dict) else {}
        scenarios = optimization.get("scenarios", []) if isinstance(optimization.get("scenarios"), list) else []
        production_buffer = str(execution_cost.get("production_cost_buffer_pct", "0.30"))
        lower_bound = str(execution_cost.get("observed_total_cost_lower_bound_pct", "-"))
        confidence = str(execution_cost.get("confidence", "UNKNOWN"))
        status = str(execution_cost.get("buffer_status", "UNKNOWN"))
        production_scenarios = [row for row in scenarios if isinstance(row, dict) and str(row.get("cost_buffer_pct")) == production_buffer]
        best_production = self._best_scenario(production_scenarios)
        research_candidates = [
            self._scenario_summary(row)
            for row in scenarios
            if isinstance(row, dict)
            and self._decimal(row.get("total_pnl_usd")) > 0
            and self._int(row.get("trade_count")) >= 5
        ][:5]
        return {
            "production_cost_buffer_pct": production_buffer,
            "production_buffer_status": status,
            "execution_cost_confidence": confidence,
            "observed_cost_lower_bound_pct": lower_bound,
            "best_overall_research_scenario": self._scenario_summary(best),
            "best_production_buffer_scenario": self._scenario_summary(best_production),
            "top_research_candidates": research_candidates,
            "recommendation": self._settings_recommendation(status, confidence, best, best_production),
        }

    def _settings_recommendation(
        self,
        status: str,
        confidence: str,
        best: dict[str, Any],
        best_production: dict[str, Any] | None,
    ) -> str:
        best_production = best_production or {}
        if self._int(best_production.get("trade_count")) > 0 and self._decimal(best_production.get("total_pnl_usd")) > 0:
            return "Production cost-buffer has positive-after-cost evidence, but paper BUY threshold evidence is still insufficient."
        if status == "TOO_HIGH" and confidence == "HIGH":
            return "Research-only lower-buffer candidate may be justified; keep production unchanged until approved."
        if self._int(best.get("trade_count")) > 0:
            return "Lower-buffer optimization is promising, but keep production unchanged until execution-cost confidence is high."
        return "No profitable setting has enough replay support yet; expand paper evidence before tuning."

    @staticmethod
    def _universe_score(
        *,
        priority: int,
        readiness_score: int,
        quote_ok_rate_pct: Decimal,
        healthy_dex_count: int,
        lower_bound_trade_count: int,
        production_trade_count: int,
    ) -> int:
        score = min(30, readiness_score // 3)
        if priority == 1:
            score += 15
        elif priority <= 2:
            score += 8
        if healthy_dex_count >= 2:
            score += 25
        elif healthy_dex_count == 1:
            score += 8
        if quote_ok_rate_pct >= Decimal("90"):
            score += 10
        elif quote_ok_rate_pct > 0:
            score += 5
        if production_trade_count > 0:
            score += 20
        elif lower_bound_trade_count > 0:
            score += 10
        return min(100, score)

    @staticmethod
    def _classification(
        *,
        configured: bool,
        pair: str,
        score: int,
        healthy_dex_count: int,
        lower_bound_trade_count: int,
        production_trade_count: int,
    ) -> str:
        if not configured:
            return "WATCH_UNCONFIGURED"
        if healthy_dex_count < 2:
            return "BLOCKED_NEEDS_QUOTES"
        if production_trade_count > 0:
            return "ACTIVE_FOCUS"
        if pair == "WETH/USDC" and lower_bound_trade_count > 0:
            return "ACTIVE_FOCUS"
        if score >= 65:
            return "RESEARCH_TARGET"
        return "WATCH"

    @staticmethod
    def _next_action(classification: str, chain: str, pair: str) -> str:
        if classification == "ACTIVE_FOCUS":
            return "Continue paper monitoring and collect execution-cost samples at unchanged production thresholds."
        if classification == "RESEARCH_TARGET":
            return "Add deeper quote/execution evidence before considering paper optimization."
        if classification == "BLOCKED_NEEDS_QUOTES":
            return f"Implement or validate quote providers for {chain} {pair} before treating it as tradeable."
        if classification == "WATCH_UNCONFIGURED":
            return "Keep on watchlist until configured as a supported research pair."
        return "Collect more quote, provider, and replay evidence."

    def _quote_stats(self, rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in rows:
            chain = str(row.get("chain", "")).lower()
            pair = str(row.get("pair", "-")).upper()
            grouped.setdefault((chain, pair), []).append(row)

        stats = {}
        for key, group in grouped.items():
            ok = [row for row in group if str(row.get("status")) == "OK"]
            dexes = sorted({str(row.get("dex")) for row in ok if row.get("dex")})
            ok_rate = Decimal(len(ok)) / Decimal(len(group)) * Decimal("100") if group else Decimal("0")
            stats[key] = {
                "sample_count": len(group),
                "ok_count": len(ok),
                "ok_rate_pct": str(ok_rate.quantize(Decimal("0.0001"))),
                "healthy_dex_count": len(dexes),
                "healthy_dexes": dexes,
            }
        return stats

    def _opportunity_stats(
        self,
        *,
        opportunity_rows: list[dict[str, Any]],
        production_cost_buffer_pct: Decimal,
        paper_buy_threshold_pct: Decimal,
        observed_lower_bound_pct: Decimal | None,
    ) -> dict[tuple[str, str], dict[str, Any]]:
        grouped: dict[tuple[str, str], list[Decimal]] = {}
        for row in opportunity_rows:
            if str(row.get("mode", "REAL")) != "REAL":
                continue
            edge = self._to_decimal(row.get("gross_edge_pct"))
            if edge is None:
                continue
            key = (str(row.get("chain", "")).lower(), str(row.get("pair", "-")).upper())
            grouped.setdefault(key, []).append(edge)

        stats = {}
        production_required_edge = production_cost_buffer_pct + paper_buy_threshold_pct
        for key, edges in grouped.items():
            production_trades = sum(1 for edge in edges if edge >= production_required_edge)
            lower_bound_trades = (
                sum(1 for edge in edges if observed_lower_bound_pct is not None and edge > observed_lower_bound_pct)
                if observed_lower_bound_pct is not None
                else 0
            )
            stats[key] = {
                "real_signal_count": len(edges),
                "avg_gross_edge_pct": str(self._avg(edges).quantize(Decimal("0.0001"))),
                "max_gross_edge_pct": str(max(edges, default=Decimal("0")).quantize(Decimal("0.0001"))),
                "production_trade_count": production_trades,
                "lower_bound_trade_count": lower_bound_trades,
            }
        return stats

    @staticmethod
    def _findings(
        universe: list[dict[str, Any]],
        settings: dict[str, Any],
        provider: dict[str, Any],
    ) -> list[dict[str, str]]:
        findings = []
        active = [row for row in universe if row["classification"] == "ACTIVE_FOCUS"]
        if active:
            focus = active[0]
            findings.append({"severity": "INFO", "message": f"Primary research focus is {focus['chain']} {focus['pair']}."})
        blocked = [row for row in universe if row["classification"] == "BLOCKED_NEEDS_QUOTES"]
        if blocked:
            findings.append({"severity": "ACTION", "message": f"{len(blocked)} configured pair(s) need quote-provider evidence before expansion."})
        if provider.get("overall_status") == "WATCH":
            findings.append({"severity": "WATCH", "message": f"Provider monitor remains WATCH with {provider.get('alert_count', 0)} alert(s)."})
        findings.append({"severity": "INFO", "message": settings["recommendation"]})
        return findings

    @staticmethod
    def _primary_focus(universe: list[dict[str, Any]]) -> dict[str, Any] | None:
        for row in universe:
            if row["classification"] == "ACTIVE_FOCUS":
                return {"chain": row["chain"], "pair": row["pair"], "score": row["score"]}
        return universe[0] if universe else None

    @staticmethod
    def _scenario_summary(row: dict[str, Any] | None) -> dict[str, Any] | None:
        if not row:
            return None
        return {
            "cost_buffer_pct": row.get("cost_buffer_pct"),
            "min_net_edge_pct": row.get("min_net_edge_pct"),
            "notional_usd": row.get("notional_usd"),
            "trade_count": row.get("trade_count"),
            "total_pnl_usd": row.get("total_pnl_usd"),
            "avg_net_edge_pct": row.get("avg_net_edge_pct"),
            "max_drawdown_usd": row.get("max_drawdown_usd"),
        }

    def _best_scenario(self, rows: list[dict[str, Any]]) -> dict[str, Any] | None:
        if not rows:
            return None
        return sorted(
            rows,
            key=lambda row: (
                self._decimal(row.get("total_pnl_usd")),
                self._int(row.get("trade_count")),
                -self._decimal(row.get("max_drawdown_usd")),
            ),
            reverse=True,
        )[0]

    def _markdown(self, payload: dict[str, Any]) -> str:
        focus = payload.get("primary_focus") or {}
        settings = payload["settings_evidence"]
        lines = [
            "# CryptoAI Market Universe Evidence",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Primary focus: `{focus.get('chain', '-')}` `{focus.get('pair', '-')}`",
            f"- Active focus count: `{payload['active_focus_count']}`",
            f"- Research target count: `{payload['research_target_count']}`",
            f"- Blocked count: `{payload['blocked_count']}`",
            f"- Provider status: `{payload['provider_status']}` with `{payload['provider_alert_count']}` alert(s)",
            "",
            "## Settings Evidence",
            "",
            f"- Production cost buffer %: `{settings['production_cost_buffer_pct']}`",
            f"- Production buffer status: `{settings['production_buffer_status']}`",
            f"- Execution-cost confidence: `{settings['execution_cost_confidence']}`",
            f"- Observed cost lower bound %: `{settings['observed_cost_lower_bound_pct']}`",
            f"- Recommendation: {settings['recommendation']}",
            "",
            "## Universe Ranking",
            "",
            "| Class | Chain | Pair | Score | Quote OK % | Healthy DEXs | Real Signals | Prod Trades | Lower-Bound Trades | Next Action |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
        for row in payload["universe"]:
            lines.append(
                f"| {row['classification']} | {row['chain']} | {row['pair']} | {row['score']} | "
                f"{row['quote_ok_rate_pct']} | {row['healthy_dex_count']} | {row['real_signal_count']} | "
                f"{row['production_trade_count']} | {row['lower_bound_trade_count']} | {row['next_action'].replace('|', '/')} |"
            )

        lines += ["", "## Findings", ""]
        for finding in payload["findings"]:
            lines.append(f"- `{finding['severity']}` {finding['message']}")
        lines += ["", "## Notes", ""]
        for note in payload["notes"]:
            lines.append(f"- {note}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _empty_quote_stats() -> dict[str, Any]:
        return {"sample_count": 0, "ok_count": 0, "ok_rate_pct": "0.0000", "healthy_dex_count": 0, "healthy_dexes": []}

    @staticmethod
    def _empty_opportunity_stats() -> dict[str, Any]:
        return {
            "real_signal_count": 0,
            "avg_gross_edge_pct": "0.0000",
            "max_gross_edge_pct": "0.0000",
            "production_trade_count": 0,
            "lower_bound_trade_count": 0,
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
                row.get("cost_buffer_pct"),
                row.get("net_edge_pct"),
                row.get("decision"),
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(row)
        return deduped

    @staticmethod
    def _avg(values: list[Decimal]) -> Decimal:
        if not values:
            return Decimal("0")
        return sum(values, Decimal("0")) / Decimal(len(values))

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
            if value in {None, "", "-"}:
                return Decimal("0")
            return Decimal(str(value))
        except Exception:
            return Decimal("0")

    @staticmethod
    def _int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except Exception:
            return default

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    print(json.dumps(MarketUniverseEvidenceService().generate(), indent=2))


if __name__ == "__main__":
    main()
