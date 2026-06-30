from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


class ExecutionRealismService:
    """Stress-tests paper opportunities against practical execution constraints.

    This service is intentionally conservative. It does not change production
    buffers, paper thresholds, or risk gates; it creates evidence that says
    whether paper opportunities are realistic enough for shadow/live review.
    """

    CHAIN_GAS_USD = {
        "base": Decimal("0.05"),
        "arbitrum": Decimal("0.10"),
        "optimism": Decimal("0.08"),
        "polygon": Decimal("0.05"),
        "ethereum": Decimal("15.00"),
    }

    MEV_RISK_BUFFER_PCT = {
        "LOW": Decimal("0.02"),
        "MEDIUM": Decimal("0.05"),
        "HIGH": Decimal("0.10"),
    }

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.opportunity_file = self.data_dir / "opportunity_decisions.jsonl"
        self.quote_file = self.data_dir / "quote_diagnostics.jsonl"
        self.portfolio_file = self.data_dir / "paper_portfolio_state.json"
        self.settings_report = self.report_dir / "paper_trading_settings.json"
        self.pool_depth_report = self.report_dir / "pool_depth_ladder.json"
        self.output_json = self.report_dir / "execution_realism.json"
        self.output_md = self.report_dir / "execution_realism.md"

    def generate(self) -> dict[str, Any]:
        opportunities = self._read_jsonl(self.opportunity_file)
        quote_rows = self._read_jsonl(self.quote_file)
        portfolio = self._read_json(self.portfolio_file)
        settings = self._read_json(self.settings_report)
        pool_depth = self._read_json(self.pool_depth_report)

        latest_batch = self._latest_batch(opportunities)
        quote_evidence = self._quote_evidence(quote_rows)
        paper_capital = self._paper_capital_usd(settings, portfolio)
        available_cash = self._decimal(portfolio.get("cash_usd")) or paper_capital
        max_trade = self._max_trade_usd(settings, paper_capital)
        requested_notional = min(paper_capital, available_cash, max_trade)
        rows = [
            self._assess_opportunity(
                row,
                quote_evidence=quote_evidence,
                pool_depth=pool_depth,
                requested_notional_usd=requested_notional,
            )
            for row in latest_batch
        ]

        summary = self._summary(rows, quote_evidence, paper_capital, requested_notional)
        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "paper_capital_usd": str(paper_capital.quantize(Decimal("0.0001"))),
            "requested_notional_usd": str(requested_notional.quantize(Decimal("0.0001"))),
            "overall_status": summary["overall_status"],
            "confidence": summary["confidence"],
            "shadow_ready_count": summary["shadow_ready_count"],
            "live_ready_count": 0,
            "quote_evidence": quote_evidence,
            "opportunities": rows,
            "findings": self._findings(rows, quote_evidence),
            "notes": [
                "Execution Realism is evidence-only and does not change paper BUY thresholds or risk limits.",
                "Without pool-depth evidence, executable size and price impact remain conservative heuristics.",
                "Live trading remains disabled; SHADOW_READY means suitable for deeper paper/shadow analysis only.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _assess_opportunity(
        self,
        row: dict[str, Any],
        *,
        quote_evidence: dict[str, Any],
        pool_depth: dict[str, Any],
        requested_notional_usd: Decimal,
    ) -> dict[str, Any]:
        chain = str(row.get("chain", "base")).lower()
        pair = str(row.get("pair", "-"))
        buy_source = str(row.get("buy_source", row.get("buy_dex", "-")))
        sell_source = str(row.get("sell_source", row.get("sell_dex", "-")))
        gross = self._decimal(row.get("gross_spread_pct") or row.get("gross_edge_pct"))
        configured_cost = self._decimal(row.get("total_cost_buffer_pct") or row.get("cost_buffer_pct")) or Decimal("0.30")
        reported_net = self._decimal(row.get("estimated_net_edge_pct") or row.get("net_edge_pct"))

        route_quotes = self._route_quotes(quote_evidence, chain=chain, pair=pair, buy_source=buy_source, sell_source=sell_source)
        healthy_dex_count = len({quote["dex"] for quote in route_quotes if quote.get("status") == "OK"})
        probe_notional = self._probe_notional_usd(route_quotes, pair=pair)
        pool_route = self._pool_depth_route(pool_depth, chain=chain, pair=pair)
        pool_usable_notional = self._decimal(pool_route.get("max_usable_notional_usd")) if pool_route else None
        if pool_usable_notional is not None and pool_usable_notional > 0:
            executable_notional = min(requested_notional_usd, pool_usable_notional)
            price_impact = (
                self._decimal(pool_route.get("requested_price_impact_pct"))
                or self._decimal(pool_route.get("worst_price_impact_pct"))
                or self._estimated_price_impact_pct(requested_notional_usd, probe_notional)
            )
            depth_model = "POOL_DEPTH_LADDER"
        else:
            executable_notional = min(requested_notional_usd, probe_notional) if probe_notional > 0 else Decimal("0")
            price_impact = self._estimated_price_impact_pct(requested_notional_usd, probe_notional)
            depth_model = "QUOTE_PROBE_HEURISTIC"
        gas_usd = self.CHAIN_GAS_USD.get(chain, Decimal("0.10"))
        gas_pct = (gas_usd / requested_notional_usd * Decimal("100")) if requested_notional_usd > 0 else Decimal("0")
        mev_risk = self._mev_risk(chain=chain, healthy_dex_count=healthy_dex_count)
        mev_buffer = self.MEV_RISK_BUFFER_PCT[mev_risk]
        stress_cost = configured_cost + price_impact + gas_pct + mev_buffer

        if gross is None:
            stress_net = None
        else:
            stress_net = gross - stress_cost

        executable_ratio = executable_notional / requested_notional_usd if requested_notional_usd > 0 else Decimal("0")
        confidence = self._confidence(route_quotes, executable_ratio, pool_route)
        status = self._status(
            source_decision=str(row.get("decision", "-")),
            healthy_dex_count=healthy_dex_count,
            executable_ratio=executable_ratio,
            stress_net_edge_pct=stress_net,
            confidence=confidence,
        )

        return {
            "timestamp": row.get("timestamp"),
            "chain": chain,
            "pair": pair,
            "buy_source": buy_source,
            "sell_source": sell_source,
            "source_decision": row.get("decision"),
            "gross_edge_pct": self._fmt(gross),
            "configured_cost_buffer_pct": self._fmt(configured_cost),
            "reported_net_edge_pct": self._fmt(reported_net),
            "estimated_price_impact_pct": self._fmt(price_impact),
            "estimated_gas_usd": self._fmt(gas_usd),
            "estimated_gas_pct": self._fmt(gas_pct),
            "mev_risk": mev_risk,
            "mev_risk_buffer_pct": self._fmt(mev_buffer),
            "stress_total_cost_pct": self._fmt(stress_cost),
            "stress_net_edge_pct": self._fmt(stress_net),
            "requested_notional_usd": self._fmt_usd(requested_notional_usd),
            "max_executable_notional_usd": self._fmt_usd(executable_notional),
            "executable_ratio_pct": self._fmt(executable_ratio * Decimal("100")),
            "depth_model": depth_model,
            "pool_depth_status": pool_route.get("status") if pool_route else None,
            "confidence": confidence,
            "realism_status": status,
            "reason": self._reason(status, stress_net, executable_ratio, healthy_dex_count, confidence),
        }

    def _quote_evidence(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        latest_timestamp = rows[-1].get("timestamp") if rows else None
        latest_rows = [row for row in rows if row.get("timestamp") == latest_timestamp] if latest_timestamp else []
        if not latest_rows:
            latest_rows = rows[-50:]
        ok = [row for row in latest_rows if str(row.get("status")).upper() == "OK"]
        return {
            "latest_timestamp": latest_timestamp,
            "row_count": len(latest_rows),
            "ok_count": len(ok),
            "healthy_dex_count": len({str(row.get("dex")) for row in ok if row.get("dex")}),
            "healthy_pairs": sorted({str(row.get("pair")) for row in ok if row.get("pair")}),
            "quotes": latest_rows,
        }

    def _route_quotes(self, quote_evidence: dict[str, Any], *, chain: str, pair: str, buy_source: str, sell_source: str) -> list[dict[str, Any]]:
        sources = {buy_source, sell_source}
        return [
            row
            for row in quote_evidence.get("quotes", [])
            if str(row.get("chain", "base")).lower() == chain
            and str(row.get("pair")) == pair
            and str(row.get("dex")) in sources
        ]

    def _probe_notional_usd(self, rows: list[dict[str, Any]], *, pair: str) -> Decimal:
        probes: list[Decimal] = []
        for row in rows:
            amount_in = self._decimal(row.get("amount_in"))
            price = self._decimal(row.get("price"))
            if amount_in is None or amount_in <= 0:
                continue
            if pair.upper().startswith("USDC/") or pair.upper().startswith("USDT/") or pair.upper().startswith("DAI/"):
                probes.append(amount_in)
            elif price is not None and price > 0:
                probes.append(amount_in * price)
        return min(probes) if probes else Decimal("0")

    @staticmethod
    def _estimated_price_impact_pct(requested_notional: Decimal, probe_notional: Decimal) -> Decimal:
        if requested_notional <= 0 or probe_notional <= 0:
            return Decimal("0.25")
        if requested_notional <= probe_notional:
            return Decimal("0.02")
        excess_ratio = (requested_notional / probe_notional) - Decimal("1")
        return min(Decimal("1.00"), Decimal("0.02") + excess_ratio * Decimal("0.15"))

    @staticmethod
    def _mev_risk(*, chain: str, healthy_dex_count: int) -> str:
        if chain == "ethereum":
            return "HIGH"
        if healthy_dex_count < 2:
            return "HIGH"
        return "MEDIUM"

    @staticmethod
    def _confidence(route_quotes: list[dict[str, Any]], executable_ratio: Decimal, pool_route: dict[str, Any] | None = None) -> str:
        if pool_route and pool_route.get("status") == "DEPTH_READY" and executable_ratio >= Decimal("1"):
            return "MEDIUM"
        if len(route_quotes) < 2:
            return "NONE"
        if executable_ratio >= Decimal("1"):
            return "LOW"
        return "LOW"

    @staticmethod
    def _status(*, source_decision: str, healthy_dex_count: int, executable_ratio: Decimal, stress_net_edge_pct: Decimal | None, confidence: str) -> str:
        if healthy_dex_count < 2 or executable_ratio <= 0:
            return "NOT_EXECUTABLE"
        if stress_net_edge_pct is None:
            return "INSUFFICIENT_DATA"
        if stress_net_edge_pct < Decimal("0"):
            return "NEGATIVE_AFTER_STRESS"
        if source_decision != "BUY":
            return "WATCH_ONLY"
        if confidence in {"NONE", "LOW"}:
            return "SHADOW_ONLY"
        return "SHADOW_READY"

    @staticmethod
    def _reason(status: str, stress_net: Decimal | None, executable_ratio: Decimal, healthy_dex_count: int, confidence: str) -> str:
        if status == "NOT_EXECUTABLE":
            return f"Need two healthy route quotes and nonzero executable size; healthy route DEXes={healthy_dex_count}, executable ratio={executable_ratio:.4f}."
        if status == "NEGATIVE_AFTER_STRESS":
            return f"Stress net edge is negative after price-impact/gas/MEV buffers ({stress_net:.4f}%)."
        if status == "WATCH_ONLY":
            return f"Stress model is informational because source decision is not BUY; confidence={confidence}."
        if status == "SHADOW_ONLY":
            return "BUY candidate needs pool-depth/private-routing evidence before shadow/live consideration."
        return "Opportunity passed current realism screen."

    def _summary(self, rows: list[dict[str, Any]], quote_evidence: dict[str, Any], paper_capital: Decimal, requested_notional: Decimal) -> dict[str, Any]:
        shadow_ready = [row for row in rows if row.get("realism_status") == "SHADOW_READY"]
        if not rows:
            status = "NO_OPPORTUNITIES"
            confidence = "NONE"
        elif shadow_ready:
            status = "SHADOW_REVIEW_READY"
            confidence = "MEDIUM"
        elif any(row.get("realism_status") == "SHADOW_ONLY" for row in rows):
            status = "PAPER_ONLY_NEEDS_DEPTH"
            confidence = "LOW"
        else:
            status = "NOT_SHADOW_READY"
            confidence = "LOW" if quote_evidence.get("ok_count", 0) else "NONE"
        return {
            "overall_status": status,
            "confidence": confidence,
            "shadow_ready_count": len(shadow_ready),
            "paper_capital_usd": str(paper_capital),
            "requested_notional_usd": str(requested_notional),
        }

    @staticmethod
    def _findings(rows: list[dict[str, Any]], quote_evidence: dict[str, Any]) -> list[dict[str, str]]:
        findings: list[dict[str, str]] = []
        if not rows:
            findings.append({"severity": "WATCH", "message": "No opportunity decisions are available for realism assessment."})
        if quote_evidence.get("healthy_dex_count", 0) < 2:
            findings.append({"severity": "ACTION", "message": "Need at least two healthy DEX quote venues for real arbitrage realism."})
        if rows and not any(row.get("realism_status") in {"SHADOW_READY", "SHADOW_ONLY"} for row in rows):
            findings.append({"severity": "INFO", "message": "Latest opportunities are not realistic execution candidates after stress checks."})
        if rows and any(row.get("depth_model") == "QUOTE_PROBE_HEURISTIC" for row in rows):
            findings.append({"severity": "ACTION", "message": "Add pool-depth evidence to replace quote-probe executable-size heuristics."})
        if rows and any(row.get("depth_model") == "POOL_DEPTH_LADDER" and row.get("confidence") == "MEDIUM" for row in rows):
            findings.append({"severity": "INFO", "message": "Pool-depth ladder evidence is available for at least one latest opportunity."})
        return findings

    @staticmethod
    def _pool_depth_route(pool_depth: dict[str, Any], *, chain: str, pair: str) -> dict[str, Any]:
        routes = pool_depth.get("routes", []) if isinstance(pool_depth.get("routes"), list) else []
        for row in routes:
            if not isinstance(row, dict):
                continue
            if str(row.get("chain", "base")).lower() == chain and str(row.get("pair")) == pair:
                return row
        return {}

    def _paper_capital_usd(self, settings: dict[str, Any], portfolio: dict[str, Any]) -> Decimal:
        capital = self._decimal(settings.get("paper_capital_usd"))
        if capital is not None and capital > 0:
            return capital
        state_initial = self._decimal(portfolio.get("initial_cash_usd"))
        if state_initial is not None and state_initial > 0:
            return state_initial
        return Decimal("1000")

    def _max_trade_usd(self, settings: dict[str, Any], fallback: Decimal) -> Decimal:
        raw = settings.get("settings", {}).get("paper_capital", {}).get("max_notional_usd_per_trade") if isinstance(settings.get("settings"), dict) else None
        max_trade = self._decimal(raw)
        return max_trade if max_trade is not None and max_trade > 0 else fallback

    @staticmethod
    def _latest_batch(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not rows:
            return []
        latest_timestamp = rows[-1].get("timestamp")
        return [row for row in rows if row.get("timestamp") == latest_timestamp] or rows[-10:]

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows: list[dict[str, Any]] = []
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
    def _decimal(value) -> Decimal | None:
        if value in (None, ""):
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None

    @staticmethod
    def _fmt(value: Decimal | None) -> str | None:
        if value is None:
            return None
        return str(value.quantize(Decimal("0.0001")))

    @staticmethod
    def _fmt_usd(value: Decimal) -> str:
        return str(value.quantize(Decimal("0.0001")))

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# CryptoAI Execution Realism",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Confidence: `{payload['confidence']}`",
            f"- Paper capital USD: `${payload['paper_capital_usd']}`",
            f"- Requested notional USD: `${payload['requested_notional_usd']}`",
            f"- Shadow-ready count: `{payload['shadow_ready_count']}`",
            f"- Live-ready count: `{payload['live_ready_count']}`",
            "",
            "## Latest Opportunity Stress Check",
            "",
            "| Pair | Buy | Sell | Source | Gross % | Reported Net % | Stress Net % | Executable USD | Status | Confidence |",
            "|---|---|---|---|---:|---:|---:|---:|---|---|",
        ]
        for row in payload["opportunities"]:
            lines.append(
                f"| {row['pair']} | {row['buy_source']} | {row['sell_source']} | {row.get('source_decision')} | "
                f"{row.get('gross_edge_pct') or '-'} | {row.get('reported_net_edge_pct') or '-'} | "
                f"{row.get('stress_net_edge_pct') or '-'} | {row.get('max_executable_notional_usd')} | "
                f"{row.get('realism_status')} | {row.get('confidence')} |"
            )
        if not payload["opportunities"]:
            lines.append("| - | - | - | - | - | - | - | - | NO_OPPORTUNITIES | NONE |")

        lines += ["", "## Findings", "", "| Severity | Message |", "|---|---|"]
        for finding in payload["findings"]:
            lines.append(f"| {finding['severity']} | {finding['message']} |")
        if not payload["findings"]:
            lines.append("| OK | No realism findings. |")
        lines += ["", "## Notes", ""]
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    payload = ExecutionRealismService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
