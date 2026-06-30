from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import uuid4

try:
    from app.providers.dexscreener_provider import DexScreenerProvider
except Exception:
    DexScreenerProvider = None

try:
    from app.quotes.models import DexQuote, QuoteRequest
    from app.quotes.quote_manager import QuoteManager
except Exception:
    DexQuote = None
    QuoteRequest = None
    QuoteManager = None

try:
    from app.registry.dexes import get_dexes_for_chain
except Exception:
    get_dexes_for_chain = None


class PoolDepthLadderService:
    """Builds paper-mode quote-size ladder evidence for executable depth.

    This service is research-only. It probes progressively larger quote sizes
    and reports whether apparent arbitrage edge survives realistic sizing.
    It does not alter paper execution, cost buffers, or live-trading locks.
    """

    DEFAULT_NOTIONAL_STEPS = (Decimal("100"), Decimal("250"), Decimal("500"), Decimal("1000"), Decimal("2000"))
    TARGET_ROUTES = (
        ("base", "WETH", "USDC"),
        ("base", "USDC", "WETH"),
    )
    GOOD_IMPACT_PCT = Decimal("0.15")
    WATCH_IMPACT_PCT = Decimal("0.50")

    def __init__(
        self,
        data_dir: Path | str = "data",
        report_dir: Path | str = "reports",
        quote_manager: Any | None = None,
        dexscreener: Any | None = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.quote_manager = quote_manager
        self.dexscreener = dexscreener
        self.output_json = self.report_dir / "pool_depth_ladder.json"
        self.output_md = self.report_dir / "pool_depth_ladder.md"
        self.ladder_file = self.data_dir / "quote_size_ladder.jsonl"
        self.settings_report = self.report_dir / "paper_trading_settings.json"
        self.portfolio_file = self.data_dir / "paper_portfolio_state.json"

    def generate(self) -> dict[str, Any]:
        generated_at = self._utc_now()
        batch_id = str(uuid4())[:10]
        reference_price = self._eth_reference_usd()
        requested_notional = self._requested_notional_usd()
        notional_steps = self._notional_steps(requested_notional)
        dexes = self._dex_names()

        liquidity = self._liquidity_evidence()
        ladder_rows = self._quote_ladder(
            generated_at=generated_at,
            batch_id=batch_id,
            dexes=dexes,
            notional_steps=notional_steps,
            reference_price=reference_price,
        )
        self._annotate_price_impact(ladder_rows)
        self._append_ladder_rows(ladder_rows)

        routes = self._route_summaries(ladder_rows, liquidity, requested_notional)
        summary = self._summary(routes, ladder_rows)
        payload = {
            "generated_at": generated_at,
            "mode": "paper",
            "batch_id": batch_id,
            "overall_status": summary["overall_status"],
            "confidence": summary["confidence"],
            "route_count": len(routes),
            "depth_ready_route_count": summary["depth_ready_route_count"],
            "watch_route_count": summary["watch_route_count"],
            "notional_steps_usd": [self._fmt_usd(value) for value in notional_steps],
            "requested_notional_usd": self._fmt_usd(requested_notional),
            "eth_reference_usd": self._fmt_usd(reference_price),
            "quote_row_count": len(ladder_rows),
            "ok_quote_row_count": sum(1 for row in ladder_rows if row["status"] == "OK"),
            "liquidity_evidence": liquidity,
            "routes": routes,
            "findings": self._findings(routes, ladder_rows, liquidity),
            "notes": [
                "Pool-depth ladder evidence is research-only and does not change trade thresholds.",
                "Quote-size ladder impact is measured from provider quotes at increasing notional sizes.",
                "Live trading remains disabled; DEPTH_READY is not a live-trading approval.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _quote_ladder(
        self,
        *,
        generated_at: str,
        batch_id: str,
        dexes: list[str],
        notional_steps: list[Decimal],
        reference_price: Decimal,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        manager = self._quote_manager()
        if manager is None or QuoteRequest is None:
            return [
                {
                    "timestamp": generated_at,
                    "batch_id": batch_id,
                    "chain": "base",
                    "dex": "-",
                    "pair": "-",
                    "notional_usd": "0.0000",
                    "amount_in": "0",
                    "amount_out": None,
                    "effective_price_usd": None,
                    "price_impact_pct": None,
                    "status": "ERROR",
                    "error": "QuoteManager is not available.",
                }
            ]

        for chain, token_in, token_out in self.TARGET_ROUTES:
            pair = f"{token_in}/{token_out}"
            for dex in dexes:
                for notional in notional_steps:
                    amount_in = self._amount_in_for_notional(token_in, notional, reference_price)
                    request = QuoteRequest(chain=chain, dex=dex, token_in=token_in, token_out=token_out, amount_in=amount_in)
                    quote = self._safe_quote(manager, request)
                    rows.append(
                        self._row_from_quote(
                            quote=quote,
                            timestamp=generated_at,
                            batch_id=batch_id,
                            pair=pair,
                            notional=notional,
                            reference_price=reference_price,
                        )
                    )
        return rows

    @staticmethod
    def _safe_quote(manager: Any, request: Any) -> Any:
        try:
            return manager.get_quote(request)
        except Exception as exc:
            return {
                "chain": request.chain,
                "dex": request.dex,
                "token_in": request.token_in,
                "token_out": request.token_out,
                "amount_in": request.amount_in,
                "amount_out": None,
                "price": None,
                "error": f"{type(exc).__name__}: {exc}",
            }

    def _row_from_quote(
        self,
        *,
        quote: Any,
        timestamp: str,
        batch_id: str,
        pair: str,
        notional: Decimal,
        reference_price: Decimal,
    ) -> dict[str, Any]:
        chain = str(self._attr(quote, "chain", "base"))
        dex = str(self._attr(quote, "dex", "-"))
        token_in = str(self._attr(quote, "token_in", pair.split("/", 1)[0]))
        token_out = str(self._attr(quote, "token_out", pair.split("/", 1)[1]))
        amount_in = self._decimal(self._attr(quote, "amount_in", None))
        amount_out = self._decimal(self._attr(quote, "amount_out", None))
        error = self._attr(quote, "error", None)
        effective_price = self._effective_price_usd(
            token_in=token_in,
            token_out=token_out,
            amount_in=amount_in,
            amount_out=amount_out,
            reference_price=reference_price,
        )
        status = "OK" if amount_in and amount_out and amount_out > 0 and effective_price and not error else "ERROR"
        return {
            "timestamp": timestamp,
            "batch_id": batch_id,
            "chain": chain,
            "dex": dex,
            "pair": pair,
            "token_in": token_in,
            "token_out": token_out,
            "notional_usd": self._fmt_usd(notional),
            "amount_in": str(amount_in) if amount_in is not None else None,
            "amount_out": str(amount_out) if amount_out is not None else None,
            "effective_price_usd": self._fmt(effective_price),
            "price_impact_pct": None,
            "status": status,
            "error": str(error)[:300] if error else "",
        }

    def _annotate_price_impact(self, rows: list[dict[str, Any]]) -> None:
        baselines: dict[tuple[str, str, str], Decimal] = {}
        for row in rows:
            if row["status"] != "OK":
                continue
            key = (row["chain"], row["dex"], row["pair"])
            price = self._decimal(row.get("effective_price_usd"))
            if price is not None and price > 0 and key not in baselines:
                baselines[key] = price

        for row in rows:
            price = self._decimal(row.get("effective_price_usd"))
            baseline = baselines.get((row["chain"], row["dex"], row["pair"]))
            if price is None or baseline is None or baseline <= 0:
                row["price_impact_pct"] = None
                continue
            if row["pair"].upper().startswith("WETH/"):
                impact = max(Decimal("0"), (baseline - price) / baseline * Decimal("100"))
            else:
                impact = max(Decimal("0"), (price - baseline) / baseline * Decimal("100"))
            row["price_impact_pct"] = self._fmt(impact)

    def _route_summaries(
        self,
        rows: list[dict[str, Any]],
        liquidity: dict[str, Any],
        requested_notional: Decimal,
    ) -> list[dict[str, Any]]:
        routes: list[dict[str, Any]] = []
        pairs = sorted({row["pair"] for row in rows if row.get("pair") and row.get("pair") != "-"})
        for pair in pairs:
            pair_rows = [row for row in rows if row.get("pair") == pair]
            notional_values = sorted({self._decimal(row.get("notional_usd")) for row in pair_rows if self._decimal(row.get("notional_usd")) is not None})
            max_usable = Decimal("0")
            for notional in notional_values:
                ok_at_size = []
                for row in pair_rows:
                    impact = self._decimal(row.get("price_impact_pct"))
                    if (
                        self._decimal(row.get("notional_usd")) == notional
                        and row.get("status") == "OK"
                        and impact is not None
                        and impact <= self.GOOD_IMPACT_PCT
                    ):
                        ok_at_size.append(row)
                if len({row["dex"] for row in ok_at_size}) >= 2:
                    max_usable = notional

            dex_rows = []
            worst_tested_impact = Decimal("0")
            ok_dexes: set[str] = set()
            requested_impacts: list[tuple[str, Decimal]] = []
            for dex in sorted({row["dex"] for row in pair_rows if row.get("dex") != "-"}):
                rows_for_dex = [row for row in pair_rows if row.get("dex") == dex]
                ok_rows = [row for row in rows_for_dex if row["status"] == "OK"]
                impacts = [self._decimal(row.get("price_impact_pct")) for row in ok_rows]
                impacts = [value for value in impacts if value is not None]
                dex_worst = max(impacts) if impacts else None
                if dex_worst is not None:
                    worst_tested_impact = max(worst_tested_impact, dex_worst)
                requested_row = self._best_row_at_or_below_requested(ok_rows, requested_notional)
                requested_impact = self._decimal(requested_row.get("price_impact_pct")) if requested_row else None
                if requested_impact is not None:
                    requested_impacts.append((dex, requested_impact))
                if ok_rows:
                    ok_dexes.add(dex)
                dex_rows.append(
                    {
                        "dex": dex,
                        "ok_count": len(ok_rows),
                        "tested_count": len(rows_for_dex),
                        "max_tested_notional_usd": self._fmt_usd(max((self._decimal(row.get("notional_usd")) or Decimal("0")) for row in rows_for_dex)),
                        "worst_price_impact_pct": self._fmt(dex_worst),
                        "liquidity_usd": self._fmt_usd(self._liquidity_for(liquidity, dex, pair)),
                    }
                )

            executable_requested = sorted(
                [(dex, impact) for dex, impact in requested_impacts if impact <= self.GOOD_IMPACT_PCT],
                key=lambda item: item[1],
            )
            selected_depth_venues = executable_requested[:2]
            selected_requested_impact = max((impact for _dex, impact in selected_depth_venues), default=None)
            requested_worst_impact = max((impact for _dex, impact in requested_impacts), default=Decimal("999"))
            if len(ok_dexes) < 2:
                status = "INSUFFICIENT_DEPTH"
                confidence = "LOW"
            elif max_usable >= requested_notional and len(selected_depth_venues) >= 2 and selected_requested_impact is not None:
                status = "DEPTH_READY"
                confidence = "MEDIUM"
            elif requested_worst_impact <= self.WATCH_IMPACT_PCT:
                status = "DEPTH_WATCH"
                confidence = "LOW"
            else:
                status = "SIZE_LIMITED"
                confidence = "LOW"

            routes.append(
                {
                    "chain": "base",
                    "pair": pair,
                    "status": status,
                    "confidence": confidence,
                    "healthy_dex_count": len(ok_dexes),
                    "requested_notional_usd": self._fmt_usd(requested_notional),
                    "max_usable_notional_usd": self._fmt_usd(max_usable),
                    "requested_price_impact_pct": self._fmt(selected_requested_impact if selected_requested_impact is not None else requested_worst_impact if requested_worst_impact != Decimal("999") else None),
                    "worst_requested_price_impact_pct": self._fmt(requested_worst_impact if requested_worst_impact != Decimal("999") else None),
                    "worst_price_impact_pct": self._fmt(worst_tested_impact),
                    "selected_depth_venues": [
                        {"dex": dex, "requested_price_impact_pct": self._fmt(impact)}
                        for dex, impact in selected_depth_venues
                    ],
                    "dexes": dex_rows,
                    "reason": self._route_reason(status, pair, max_usable, requested_notional, selected_requested_impact or requested_worst_impact),
                }
            )
        return routes

    def _liquidity_evidence(self) -> dict[str, Any]:
        provider = self._dexscreener()
        if provider is None:
            return {"source": "unavailable", "pair_count": 0, "pairs": [], "error": "DexScreenerProvider is not available."}
        try:
            pairs = provider.get_base_major_pairs()
        except Exception as exc:
            return {"source": "dexscreener", "pair_count": 0, "pairs": [], "error": f"{type(exc).__name__}: {exc}"}

        rows = []
        for pair in pairs[:20]:
            liquidity_usd = self._decimal((pair.get("liquidity") or {}).get("usd")) if isinstance(pair, dict) else None
            rows.append(
                {
                    "chain": str(pair.get("chainId", "")),
                    "dex_id": str(pair.get("dexId", "")),
                    "pair_address": str(pair.get("pairAddress", "")),
                    "base_token": str((pair.get("baseToken") or {}).get("symbol", "")),
                    "quote_token": str((pair.get("quoteToken") or {}).get("symbol", "")),
                    "liquidity_usd": self._fmt_usd(liquidity_usd or Decimal("0")),
                    "volume_h24_usd": self._fmt_usd(self._decimal((pair.get("volume") or {}).get("h24")) or Decimal("0")),
                }
            )
        return {"source": "dexscreener", "pair_count": len(rows), "pairs": rows, "error": ""}

    @staticmethod
    def _summary(routes: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
        ready = [route for route in routes if route["status"] == "DEPTH_READY"]
        watch = [route for route in routes if route["status"] in {"DEPTH_WATCH", "SIZE_LIMITED"}]
        ok_rows = [row for row in rows if row.get("status") == "OK"]
        if ready:
            status = "DEPTH_EVIDENCE_READY"
            confidence = "MEDIUM"
        elif watch:
            status = "DEPTH_EVIDENCE_WATCH"
            confidence = "LOW"
        elif ok_rows:
            status = "DEPTH_EVIDENCE_INSUFFICIENT"
            confidence = "LOW"
        else:
            status = "DEPTH_EVIDENCE_UNAVAILABLE"
            confidence = "NONE"
        return {
            "overall_status": status,
            "confidence": confidence,
            "depth_ready_route_count": len(ready),
            "watch_route_count": len(watch),
        }

    def _findings(self, routes: list[dict[str, Any]], rows: list[dict[str, Any]], liquidity: dict[str, Any]) -> list[dict[str, str]]:
        findings: list[dict[str, str]] = []
        if not any(row.get("status") == "OK" for row in rows):
            findings.append({"severity": "ACTION", "message": "No quote-size ladder rows succeeded; provider/RPC evidence is unavailable."})
        if liquidity.get("error"):
            findings.append({"severity": "WATCH", "message": f"Pool liquidity lookup unavailable: {liquidity['error']}"})
        if routes and not any(route["status"] == "DEPTH_READY" for route in routes):
            findings.append({"severity": "ACTION", "message": "No route has medium-confidence depth evidence at requested paper size."})
        if any(route["status"] == "SIZE_LIMITED" for route in routes):
            findings.append({"severity": "WATCH", "message": "At least one route is size-limited by quote ladder price impact."})
        return findings

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# CryptoAI Pool Depth Ladder",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Confidence: `{payload['confidence']}`",
            f"- Requested notional USD: `${payload['requested_notional_usd']}`",
            f"- ETH reference USD: `${payload['eth_reference_usd']}`",
            f"- Quote rows: `{payload['ok_quote_row_count']}/{payload['quote_row_count']}`",
            f"- Depth-ready routes: `{payload['depth_ready_route_count']}`",
            "",
            "## Routes",
            "",
            "| Pair | Status | Confidence | DEXes | Max Usable USD | Best-Two Requested Impact % | Worst Requested Impact % | Worst Tested Impact % | Reason |",
            "|---|---|---|---:|---:|---:|---:|---:|---|",
        ]
        for route in payload["routes"]:
            lines.append(
                f"| {route['pair']} | {route['status']} | {route['confidence']} | {route['healthy_dex_count']} | "
                f"{route['max_usable_notional_usd']} | {route.get('requested_price_impact_pct') or '-'} | "
                f"{route.get('worst_requested_price_impact_pct') or '-'} | {route['worst_price_impact_pct']} | {route['reason']} |"
            )
        if not payload["routes"]:
            lines.append("| - | DEPTH_EVIDENCE_UNAVAILABLE | NONE | 0 | 0.0000 | - | No route evidence. |")
        lines += ["", "## DEX Detail", "", "| Pair | DEX | OK | Tested | Max Tested USD | Worst Impact % | Liquidity USD |", "|---|---|---:|---:|---:|---:|---:|"]
        for route in payload["routes"]:
            for dex in route["dexes"]:
                lines.append(
                    f"| {route['pair']} | {dex['dex']} | {dex['ok_count']} | {dex['tested_count']} | "
                    f"{dex['max_tested_notional_usd']} | {dex['worst_price_impact_pct'] or '-'} | {dex['liquidity_usd']} |"
                )
        lines += ["", "## Findings", "", "| Severity | Message |", "|---|---|"]
        for finding in payload["findings"]:
            lines.append(f"| {finding['severity']} | {finding['message']} |")
        if not payload["findings"]:
            lines.append("| OK | No pool-depth ladder findings. |")
        lines += ["", "## Notes", ""]
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    def _quote_manager(self) -> Any | None:
        if self.quote_manager is not None:
            return self.quote_manager
        if QuoteManager is None:
            return None
        try:
            self.quote_manager = QuoteManager()
            return self.quote_manager
        except Exception:
            return None

    def _dexscreener(self) -> Any | None:
        if self.dexscreener is not None:
            return self.dexscreener
        if DexScreenerProvider is None:
            return None
        try:
            self.dexscreener = DexScreenerProvider()
            return self.dexscreener
        except Exception:
            return None

    def _dex_names(self) -> list[str]:
        manager = self._quote_manager()
        providers = getattr(manager, "providers", []) if manager is not None else []
        names = [str(getattr(provider, "dex", "")) for provider in providers if str(getattr(provider, "chain", "")).lower() == "base" and getattr(provider, "dex", "")]
        if names:
            return names
        if get_dexes_for_chain is None:
            return ["Uniswap V2", "Aerodrome", "Uniswap V3"]
        return [dex.name for dex in get_dexes_for_chain("base") if dex.router_address]

    def _eth_reference_usd(self) -> Decimal:
        settings = self._read_json(self.settings_report)
        value = settings.get("settings", {}).get("paper_capital", {}).get("eth_reference_usd") if isinstance(settings.get("settings"), dict) else None
        return self._decimal(value) or Decimal("1000")

    def _requested_notional_usd(self) -> Decimal:
        settings = self._read_json(self.settings_report)
        portfolio = self._read_json(self.portfolio_file)
        configured = None
        if isinstance(settings.get("settings"), dict):
            configured = settings["settings"].get("paper_capital", {}).get("max_notional_usd_per_trade")
        max_trade = self._decimal(configured)
        cash = self._decimal(portfolio.get("cash_usd"))
        capital = self._decimal(settings.get("paper_capital_usd"))
        candidates = [value for value in (max_trade, cash, capital) if value is not None and value > 0]
        return min(candidates) if candidates else Decimal("1000")

    def _notional_steps(self, requested_notional: Decimal) -> list[Decimal]:
        env = os.getenv("CRYPTOAI_DEPTH_LADDER_NOTIONALS_USD", "")
        values: list[Decimal] = []
        if env:
            for raw in env.split(","):
                parsed = self._decimal(raw.strip())
                if parsed is not None and parsed > 0:
                    values.append(parsed)
        if not values:
            values = list(self.DEFAULT_NOTIONAL_STEPS)
        if requested_notional > 0 and requested_notional not in values:
            values.append(requested_notional)
        return sorted(set(values))

    @staticmethod
    def _amount_in_for_notional(token_in: str, notional: Decimal, reference_price: Decimal) -> Decimal:
        if token_in.upper() == "WETH":
            return (notional / reference_price).quantize(Decimal("0.0000000001"))
        return notional

    @staticmethod
    def _effective_price_usd(*, token_in: str, token_out: str, amount_in: Decimal | None, amount_out: Decimal | None, reference_price: Decimal) -> Decimal | None:
        if amount_in is None or amount_out is None or amount_in <= 0 or amount_out <= 0:
            return None
        if token_in.upper() == "WETH" and token_out.upper() in {"USDC", "USDT", "DAI"}:
            return amount_out / amount_in
        if token_in.upper() in {"USDC", "USDT", "DAI"} and token_out.upper() == "WETH":
            return amount_in / amount_out
        return reference_price

    def _liquidity_for(self, liquidity: dict[str, Any], dex: str, pair: str) -> Decimal:
        best = Decimal("0")
        dex_key = dex.lower().replace(" ", "")
        tokens = set(pair.upper().split("/"))
        for row in liquidity.get("pairs", []):
            if not isinstance(row, dict):
                continue
            row_tokens = {str(row.get("base_token", "")).upper(), str(row.get("quote_token", "")).upper()}
            if not tokens.issubset(row_tokens):
                continue
            dex_id = str(row.get("dex_id", "")).lower().replace("-", "").replace("_", "")
            if "aerodrome" in dex_key and "aerodrome" not in dex_id:
                continue
            if "uniswap" in dex_key and "uniswap" not in dex_id:
                continue
            best = max(best, self._decimal(row.get("liquidity_usd")) or Decimal("0"))
        return best

    @staticmethod
    def _route_reason(status: str, pair: str, max_usable: Decimal, requested: Decimal, worst_impact: Decimal) -> str:
        if status == "DEPTH_READY":
            return f"{pair} has at least two healthy DEX ladders at requested size with worst impact {worst_impact:.4f}%."
        if status == "DEPTH_WATCH":
            return f"{pair} has two DEX ladders at requested size, but price impact needs review."
        if status == "SIZE_LIMITED":
            return f"{pair} requested size has high impact; low-impact usable size is ${max_usable:.4f} versus requested ${requested:.4f}."
        return f"{pair} needs at least two healthy DEX quote ladders with low impact."

    @classmethod
    def _best_row_at_or_below_requested(cls, rows: list[dict[str, Any]], requested: Decimal) -> dict[str, Any] | None:
        eligible = [
            row
            for row in rows
            if (cls._decimal(row.get("notional_usd")) or Decimal("0")) <= requested
        ]
        if not eligible:
            return None
        return max(eligible, key=lambda row: cls._decimal(row.get("notional_usd")) or Decimal("0"))

    def _append_ladder_rows(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        with self.ladder_file.open("a", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row) + "\n")

    @staticmethod
    def _attr(value: Any, name: str, default: Any) -> Any:
        if isinstance(value, dict):
            return value.get(name, default)
        return getattr(value, name, default)

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
    def _decimal(value: Any) -> Decimal | None:
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
        return str(value.quantize(Decimal("0.0000")))

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    payload = PoolDepthLadderService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
