from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


class ExecutionCostEvidenceService:
    """Measures paper/replay cost evidence without changing production thresholds."""

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.paper_orders_file = self.data_dir / "paper_orders.jsonl"
        self.opportunity_file = self.data_dir / "opportunity_decisions.jsonl"
        self.multi_dex_file = self.data_dir / "multi_dex_opportunities.jsonl"
        self.quote_diagnostics_file = self.data_dir / "quote_diagnostics.jsonl"
        self.provider_health_file = self.data_dir / "provider_health.json"
        self.report_json = self.report_dir / "execution_cost_evidence.json"
        self.report_md = self.report_dir / "execution_cost_evidence.md"

    def generate(
        self,
        *,
        production_cost_buffer_pct: Decimal = Decimal("0.30"),
        fallback_gas_buffer_pct: Decimal = Decimal("0.08"),
        fallback_fee_slippage_buffer_pct: Decimal = Decimal("0.22"),
        paper_buy_threshold_pct: Decimal = Decimal("0.30"),
        replay_notional_usd: Decimal = Decimal("1000"),
    ) -> dict[str, Any]:
        orders = self._read_jsonl(self.paper_orders_file)
        opportunities = self._read_jsonl(self.opportunity_file)
        multi_dex_rows = self._dedupe_opportunity_rows(self._read_jsonl(self.multi_dex_file))
        quote_rows = self._read_jsonl(self.quote_diagnostics_file)
        provider_health = self._read_json(self.provider_health_file)

        configured = self._configured_costs(
            opportunities=opportunities,
            production_cost_buffer_pct=production_cost_buffer_pct,
            fallback_gas_buffer_pct=fallback_gas_buffer_pct,
            fallback_fee_slippage_buffer_pct=fallback_fee_slippage_buffer_pct,
        )
        paper = self._paper_execution_evidence(orders)
        quotes = self._quote_evidence(quote_rows)
        providers = self._provider_evidence(provider_health)

        observed_total_lower_bound = None
        if paper["sample_count"]:
            observed_total_lower_bound = (
                self._decimal(configured["gas_buffer_pct"]) + self._decimal(paper["avg_slippage_pct"])
            ).quantize(Decimal("0.0001"))

        replay = self._replay_cost_evidence(
            rows=multi_dex_rows,
            production_cost_buffer_pct=production_cost_buffer_pct,
            paper_buy_threshold_pct=paper_buy_threshold_pct,
            observed_total_lower_bound_pct=observed_total_lower_bound,
            replay_notional_usd=replay_notional_usd,
        )
        assessment = self._assessment(
            production_cost_buffer_pct=production_cost_buffer_pct,
            observed_total_lower_bound_pct=observed_total_lower_bound,
            paper=paper,
            quotes=quotes,
            providers=providers,
            replay=replay,
        )

        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "production_cost_buffer_pct": str(production_cost_buffer_pct),
            "paper_buy_threshold_pct": str(paper_buy_threshold_pct),
            "buffer_status": assessment["buffer_status"],
            "confidence": assessment["confidence"],
            "observed_total_cost_lower_bound_pct": assessment["observed_total_cost_lower_bound_pct"],
            "buffer_surplus_vs_lower_bound_pct": assessment["buffer_surplus_vs_lower_bound_pct"],
            "configured_cost_model": configured,
            "paper_execution_evidence": paper,
            "quote_evidence": quotes,
            "provider_evidence": providers,
            "replay_cost_evidence": replay,
            "assessment": assessment,
            "findings": self._findings(assessment, paper, replay, providers),
            "notes": [
                "Execution Cost Evidence measures observed paper/replay/quote evidence only.",
                "It does not change production cost buffers, risk thresholds, or live-trading eligibility.",
                "Paper slippage plus configured gas is a measured lower bound, not a complete live execution-cost estimate.",
            ],
        }
        self.report_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.report_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _configured_costs(
        self,
        *,
        opportunities: list[dict[str, Any]],
        production_cost_buffer_pct: Decimal,
        fallback_gas_buffer_pct: Decimal,
        fallback_fee_slippage_buffer_pct: Decimal,
    ) -> dict[str, str]:
        latest = next(
            (
                row
                for row in reversed(opportunities)
                if self._to_decimal(row.get("total_cost_buffer_pct")) is not None
            ),
            {},
        )
        gas = self._to_decimal(latest.get("gas_buffer_pct")) or fallback_gas_buffer_pct
        fee_slippage = self._to_decimal(latest.get("fee_slippage_buffer_pct")) or fallback_fee_slippage_buffer_pct
        total = self._to_decimal(latest.get("total_cost_buffer_pct")) or production_cost_buffer_pct
        return {
            "gas_buffer_pct": str(gas),
            "fee_slippage_buffer_pct": str(fee_slippage),
            "total_cost_buffer_pct": str(total),
            "source": "latest_opportunity_decision" if latest else "fallback_defaults",
        }

    def _paper_execution_evidence(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        filled = [
            row
            for row in orders
            if str(row.get("status", "")).upper() in {"FILLED", "PARTIAL_FILL", "CLOSED"}
            and self._to_decimal(row.get("slippage_bps")) is not None
        ]
        slippage_bps = [self._decimal(row.get("slippage_bps")) for row in filled]
        latency_ms = [self._decimal(row.get("latency_ms")) for row in filled if self._to_decimal(row.get("latency_ms")) is not None]
        notionals = [self._decimal(row.get("filled_notional_usd", row.get("notional_usd"))) for row in filled]
        qualities: dict[str, int] = {}
        for row in filled:
            quality = str(row.get("execution_quality") or "UNKNOWN")
            qualities[quality] = qualities.get(quality, 0) + 1

        avg_slippage_bps = self._avg(slippage_bps)
        p95_slippage_bps = self._percentile(slippage_bps, Decimal("0.95"))
        max_slippage_bps = max(slippage_bps, default=Decimal("0"))
        return {
            "sample_count": len(filled),
            "total_filled_notional_usd": str(sum(notionals, Decimal("0")).quantize(Decimal("0.0001"))),
            "avg_slippage_bps": str(avg_slippage_bps.quantize(Decimal("0.0001"))),
            "p95_slippage_bps": str(p95_slippage_bps.quantize(Decimal("0.0001"))),
            "max_slippage_bps": str(max_slippage_bps.quantize(Decimal("0.0001"))),
            "avg_slippage_pct": str((avg_slippage_bps / Decimal("100")).quantize(Decimal("0.0001"))),
            "p95_slippage_pct": str((p95_slippage_bps / Decimal("100")).quantize(Decimal("0.0001"))),
            "max_slippage_pct": str((max_slippage_bps / Decimal("100")).quantize(Decimal("0.0001"))),
            "avg_latency_ms": str(self._avg(latency_ms).quantize(Decimal("0.0001"))) if latency_ms else None,
            "p95_latency_ms": str(self._percentile(latency_ms, Decimal("0.95")).quantize(Decimal("0.0001"))) if latency_ms else None,
            "max_latency_ms": str(max(latency_ms, default=Decimal("0")).quantize(Decimal("0.0001"))) if latency_ms else None,
            "execution_quality_counts": qualities,
        }

    def _quote_evidence(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        recent = rows[-200:]
        ok = [row for row in recent if str(row.get("status")) == "OK"]
        errors = [row for row in recent if str(row.get("status")) == "ERROR"]
        invalid = [row for row in recent if str(row.get("status")) == "INVALID"]
        latencies = [self._decimal(row.get("latency_ms")) for row in ok if self._to_decimal(row.get("latency_ms")) is not None]
        healthy_dexes = sorted({str(row.get("dex")) for row in ok if row.get("dex")})
        ok_rate = Decimal(len(ok)) / Decimal(len(recent)) * Decimal("100") if recent else Decimal("0")
        return {
            "sample_count": len(recent),
            "ok_count": len(ok),
            "error_count": len(errors),
            "invalid_count": len(invalid),
            "ok_rate_pct": str(ok_rate.quantize(Decimal("0.0001"))),
            "healthy_dex_count": len(healthy_dexes),
            "healthy_dexes": healthy_dexes,
            "avg_ok_latency_ms": str(self._avg(latencies).quantize(Decimal("0.0001"))) if latencies else None,
            "p95_ok_latency_ms": str(self._percentile(latencies, Decimal("0.95")).quantize(Decimal("0.0001"))) if latencies else None,
        }

    def _provider_evidence(self, payload: dict[str, Any]) -> dict[str, Any]:
        rows = payload.get("providers", []) if isinstance(payload, dict) else []
        if not isinstance(rows, list):
            rows = []
        latencies = [
            self._decimal(row.get("avg_latency_ms"))
            for row in rows
            if isinstance(row, dict) and self._to_decimal(row.get("avg_latency_ms")) is not None
        ]
        scores = [
            self._decimal(row.get("score"))
            for row in rows
            if isinstance(row, dict) and self._to_decimal(row.get("score")) is not None
        ]
        provider_rows = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            provider_rows.append(
                {
                    "name": row.get("name"),
                    "provider_type": row.get("provider_type"),
                    "chain": row.get("chain"),
                    "success_rate_pct": row.get("success_rate_pct"),
                    "avg_latency_ms": row.get("avg_latency_ms"),
                    "score": row.get("score"),
                    "consecutive_failures": row.get("consecutive_failures"),
                }
            )
        return {
            "provider_count": len(provider_rows),
            "avg_provider_latency_ms": str(self._avg(latencies).quantize(Decimal("0.0001"))) if latencies else None,
            "avg_provider_score": str(self._avg(scores).quantize(Decimal("0.0001"))) if scores else None,
            "providers": provider_rows,
        }

    def _replay_cost_evidence(
        self,
        *,
        rows: list[dict[str, Any]],
        production_cost_buffer_pct: Decimal,
        paper_buy_threshold_pct: Decimal,
        observed_total_lower_bound_pct: Decimal | None,
        replay_notional_usd: Decimal,
    ) -> dict[str, Any]:
        real_rows = [row for row in rows if str(row.get("mode", "REAL")) == "REAL"]
        gross_edges = [
            self._decimal(row.get("gross_edge_pct"))
            for row in real_rows
            if self._to_decimal(row.get("gross_edge_pct")) is not None
        ]
        production_required_edge = production_cost_buffer_pct + paper_buy_threshold_pct
        production_trade_count = sum(1 for edge in gross_edges if edge >= production_required_edge)
        lower_bound_trade_count = 0
        lower_bound_total_pnl = Decimal("0")
        if observed_total_lower_bound_pct is not None:
            for edge in gross_edges:
                net = edge - observed_total_lower_bound_pct
                if net > 0:
                    lower_bound_trade_count += 1
                    lower_bound_total_pnl += replay_notional_usd * net / Decimal("100")
        return {
            "real_signal_count": len(gross_edges),
            "avg_gross_edge_pct": str(self._avg(gross_edges).quantize(Decimal("0.0001"))) if gross_edges else "0.0000",
            "p95_gross_edge_pct": str(self._percentile(gross_edges, Decimal("0.95")).quantize(Decimal("0.0001"))) if gross_edges else "0.0000",
            "max_gross_edge_pct": str(max(gross_edges, default=Decimal("0")).quantize(Decimal("0.0001"))),
            "production_trade_count": production_trade_count,
            "production_required_gross_edge_pct": str(production_required_edge),
            "observed_lower_bound_trade_count": lower_bound_trade_count,
            "observed_lower_bound_total_pnl_usd": str(lower_bound_total_pnl.quantize(Decimal("0.0001"))),
            "replay_notional_usd": str(replay_notional_usd),
        }

    def _assessment(
        self,
        *,
        production_cost_buffer_pct: Decimal,
        observed_total_lower_bound_pct: Decimal | None,
        paper: dict[str, Any],
        quotes: dict[str, Any],
        providers: dict[str, Any],
        replay: dict[str, Any],
    ) -> dict[str, Any]:
        confidence = "INSUFFICIENT"
        if paper["sample_count"] >= 30 and self._decimal(quotes["ok_rate_pct"]) >= Decimal("90"):
            confidence = "HIGH"
        elif paper["sample_count"] >= 10:
            confidence = "MEDIUM"
        elif paper["sample_count"] > 0:
            confidence = "LOW"

        if observed_total_lower_bound_pct is None:
            status = "INSUFFICIENT_EVIDENCE"
            surplus = None
        else:
            surplus_decimal = (production_cost_buffer_pct - observed_total_lower_bound_pct).quantize(Decimal("0.0001"))
            surplus = str(surplus_decimal)
            if surplus_decimal < Decimal("0"):
                status = "TOO_LOW"
            elif surplus_decimal <= Decimal("0.05"):
                status = "ACCURATE"
            elif (
                confidence == "HIGH"
                and surplus_decimal >= Decimal("0.10")
                and replay["production_trade_count"] == 0
                and replay["observed_lower_bound_trade_count"] > 0
            ):
                status = "TOO_HIGH"
            elif surplus_decimal >= Decimal("0.10"):
                status = "CONSERVATIVE"
            else:
                status = "SLIGHTLY_CONSERVATIVE"

        return {
            "buffer_status": status,
            "confidence": confidence,
            "production_cost_buffer_pct": str(production_cost_buffer_pct),
            "observed_total_cost_lower_bound_pct": str(observed_total_lower_bound_pct) if observed_total_lower_bound_pct is not None else None,
            "buffer_surplus_vs_lower_bound_pct": surplus,
            "paper_sample_count": paper["sample_count"],
            "quote_ok_rate_pct": quotes["ok_rate_pct"],
            "avg_provider_score": providers["avg_provider_score"],
            "production_trade_count": replay["production_trade_count"],
            "observed_lower_bound_trade_count": replay["observed_lower_bound_trade_count"],
        }

    @staticmethod
    def _findings(
        assessment: dict[str, Any],
        paper: dict[str, Any],
        replay: dict[str, Any],
        providers: dict[str, Any],
    ) -> list[dict[str, str]]:
        findings: list[dict[str, str]] = []
        status = assessment["buffer_status"]
        confidence = assessment["confidence"]
        findings.append(
            {
                "severity": "INFO" if status in {"CONSERVATIVE", "SLIGHTLY_CONSERVATIVE", "ACCURATE"} else "WATCH",
                "message": f"Production buffer assessment is {status} with {confidence} paper-cost confidence.",
            }
        )
        if status == "TOO_HIGH":
            findings.append(
                {
                    "severity": "WATCH",
                    "message": (
                        "High-confidence lower-bound evidence suggests the production buffer may be too high; "
                        "research a candidate only, without changing production thresholds."
                    ),
                }
            )
        if status == "TOO_LOW":
            findings.append(
                {
                    "severity": "WATCH",
                    "message": "Observed lower-bound cost evidence exceeds the production buffer; keep live trading disabled.",
                }
            )
        if paper["sample_count"] < 30:
            findings.append(
                {
                    "severity": "ACTION",
                    "message": f"Collect more filled paper executions; current slippage sample is {paper['sample_count']} and target is 30+.",
                }
            )
        if replay["production_trade_count"] == 0 and replay["observed_lower_bound_trade_count"] > 0:
            findings.append(
                {
                    "severity": "WATCH",
                    "message": (
                        "Replay has trades under measured lower-bound costs but none under the production buffer; "
                        "do not lower thresholds until gas, fee, and slippage evidence is stronger."
                    ),
                }
            )
        if providers.get("avg_provider_score") is None:
            findings.append({"severity": "WATCH", "message": "Provider cost context is incomplete because provider health evidence is missing."})
        return findings

    def _markdown(self, payload: dict[str, Any]) -> str:
        assessment = payload["assessment"]
        configured = payload["configured_cost_model"]
        paper = payload["paper_execution_evidence"]
        quotes = payload["quote_evidence"]
        providers = payload["provider_evidence"]
        replay = payload["replay_cost_evidence"]
        lines = [
            "# CryptoAI Execution Cost Evidence",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Production cost buffer %: `{payload['production_cost_buffer_pct']}`",
            f"- Paper BUY threshold %: `{payload['paper_buy_threshold_pct']}`",
            f"- Buffer status: `{assessment['buffer_status']}`",
            f"- Confidence: `{assessment['confidence']}`",
            f"- Observed total cost lower bound %: `{assessment['observed_total_cost_lower_bound_pct']}`",
            f"- Buffer surplus vs lower bound %: `{assessment['buffer_surplus_vs_lower_bound_pct']}`",
            "",
            "## Configured Cost Model",
            "",
            f"- Gas buffer %: `{configured['gas_buffer_pct']}`",
            f"- Fee/slippage buffer %: `{configured['fee_slippage_buffer_pct']}`",
            f"- Total cost buffer %: `{configured['total_cost_buffer_pct']}`",
            f"- Source: `{configured['source']}`",
            "",
            "## Paper Execution Evidence",
            "",
            f"- Filled execution samples: `{paper['sample_count']}`",
            f"- Avg slippage bps: `{paper['avg_slippage_bps']}`",
            f"- P95 slippage bps: `{paper['p95_slippage_bps']}`",
            f"- Max slippage bps: `{paper['max_slippage_bps']}`",
            f"- Avg latency ms: `{paper['avg_latency_ms']}`",
            f"- P95 latency ms: `{paper['p95_latency_ms']}`",
            "",
            "## Quote And Provider Evidence",
            "",
            f"- Quote samples: `{quotes['sample_count']}`",
            f"- Quote OK rate %: `{quotes['ok_rate_pct']}`",
            f"- Healthy DEX count: `{quotes['healthy_dex_count']}`",
            f"- Avg OK quote latency ms: `{quotes['avg_ok_latency_ms']}`",
            f"- Provider count: `{providers['provider_count']}`",
            f"- Avg provider score: `{providers['avg_provider_score']}`",
            "",
            "## Replay Cost Evidence",
            "",
            f"- Real replay signals: `{replay['real_signal_count']}`",
            f"- Max gross edge %: `{replay['max_gross_edge_pct']}`",
            f"- Production-buffer trades: `{replay['production_trade_count']}`",
            f"- Production required gross edge %: `{replay['production_required_gross_edge_pct']}`",
            f"- Lower-bound cost trades: `{replay['observed_lower_bound_trade_count']}`",
            f"- Lower-bound replay PnL USD: `{replay['observed_lower_bound_total_pnl_usd']}`",
            "",
            "## Findings",
            "",
        ]
        for finding in payload["findings"]:
            lines.append(f"- `{finding['severity']}` {finding['message']}")
        lines += ["", "## Notes", ""]
        for note in payload["notes"]:
            lines.append(f"- {note}")
        return "\n".join(lines) + "\n"

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
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
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

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
    def _percentile(values: list[Decimal], percentile: Decimal) -> Decimal:
        if not values:
            return Decimal("0")
        ordered = sorted(values)
        index = int((Decimal(len(ordered) - 1) * percentile).to_integral_value(rounding="ROUND_HALF_UP"))
        return ordered[max(0, min(index, len(ordered) - 1))]

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
            return Decimal(str(value))
        except Exception:
            return Decimal("0")

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    print(json.dumps(ExecutionCostEvidenceService().generate(), indent=2))


if __name__ == "__main__":
    main()
