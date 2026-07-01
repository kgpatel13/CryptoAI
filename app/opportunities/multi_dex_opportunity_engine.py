from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from uuid import uuid4


class OpportunityMode(str, Enum):
    REAL = "REAL"
    PAPER_SIMULATED = "PAPER_SIMULATED"


class MultiDexDecision(str, Enum):
    BUY = "BUY"
    WATCH = "WATCH"
    SKIP = "SKIP"


@dataclass(frozen=True)
class MultiDexOpportunity:
    opportunity_id: str
    timestamp: str
    mode: OpportunityMode
    chain: str
    pair: str
    buy_dex: str
    sell_dex: str
    buy_price: Decimal | None
    sell_price: Decimal | None
    gross_edge_pct: Decimal | None
    cost_buffer_pct: Decimal
    net_edge_pct: Decimal | None
    decision: MultiDexDecision
    reason: str


class MultiDexOpportunityEngine:
    """Compares healthy quotes across DEXes.

    If only one DEX is healthy, it creates a clearly-labeled simulated paper
    opportunity to test the downstream strategy/risk/execution path. That
    simulated row is never live-tradeable.
    """

    def __init__(self) -> None:
        self.data_dir = Path("data")
        self.report_dir = Path("reports")
        self.data_dir.mkdir(exist_ok=True)
        self.report_dir.mkdir(exist_ok=True)

        self.output_file = self.data_dir / "multi_dex_opportunities.jsonl"
        self.report_file = self.report_dir / "multi_dex_opportunities.md"

        self.cost_buffer_pct = Decimal("0.30")
        self.buy_threshold_pct = self._env_decimal("CRYPTOAI_MIN_EDGE_FOR_PAPER_PCT", Decimal("0.30"))
        self.watch_threshold_pct = Decimal("0.05")

        # Paper-only synthetic edge to validate downstream execution when only
        # one venue is healthy. Keep this low and clearly labeled.
        self.synthetic_edge_pct = Decimal("0.35")

    def scan(self) -> list[MultiDexOpportunity]:
        quotes = self._load_quotes()
        healthy = [q for q in quotes if self._is_healthy_quote(q)]

        opportunities = self._build_opportunities(healthy, quotes)
        self._persist(opportunities)
        self._write_report(opportunities, quotes)
        return opportunities

    def recent(self, limit: int = 100) -> list[dict]:
        if not self.output_file.exists():
            return []

        rows: list[dict] = []
        for line in self.output_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({"raw": line})
        return rows[-limit:]

    def _load_quotes(self) -> list:
        try:
            from app.cache.quote_cache import quote_cache
            quote_cache.clear()
        except Exception:
            pass

        try:
            from app.quotes.quote_service import QuoteService
            return QuoteService().get_base_quotes()
        except Exception:
            return []

    def _build_opportunities(self, healthy_quotes: list, all_quotes: list) -> list[MultiDexOpportunity]:
        groups: dict[tuple[str, str, str], list] = {}

        for q in healthy_quotes:
            chain = str(getattr(q, "chain", "base"))
            token_in = str(getattr(q, "token_in", "-"))
            token_out = str(getattr(q, "token_out", "-"))
            groups.setdefault((chain, token_in, token_out), []).append(q)

        opportunities: list[MultiDexOpportunity] = []

        for (chain, token_in, token_out), group in groups.items():
            pair = f"{token_in}/{token_out}"
            unique_dexes = {str(getattr(q, "dex", "-")) for q in group}

            if len(group) >= 2 and len(unique_dexes) >= 2:
                opportunities.append(self._real_opportunity(chain, pair, group))
            elif len(group) >= 1:
                opportunities.append(self._paper_simulated_opportunity(chain, pair, group[0]))

        if not opportunities:
            opportunities.append(
                MultiDexOpportunity(
                    opportunity_id=str(uuid4())[:10],
                    timestamp=self._utc_now(),
                    mode=OpportunityMode.REAL,
                    chain="base",
                    pair="-",
                    buy_dex="-",
                    sell_dex="-",
                    buy_price=None,
                    sell_price=None,
                    gross_edge_pct=None,
                    cost_buffer_pct=self.cost_buffer_pct,
                    net_edge_pct=None,
                    decision=MultiDexDecision.SKIP,
                    reason="No healthy quotes available. Fix quote providers/RPC before strategy tuning.",
                )
            )

        return opportunities

    def _real_opportunity(self, chain: str, pair: str, quotes: list) -> MultiDexOpportunity:
        sorted_quotes = sorted(quotes, key=lambda q: self._to_decimal(getattr(q, "price", None)) or Decimal("0"))
        buy_quote = sorted_quotes[0]
        sell_quote = sorted_quotes[-1]

        buy_price = self._to_decimal(getattr(buy_quote, "price", None))
        sell_price = self._to_decimal(getattr(sell_quote, "price", None))

        return self._make_opportunity(
            mode=OpportunityMode.REAL,
            chain=chain,
            pair=pair,
            buy_dex=str(getattr(buy_quote, "dex", "-")),
            sell_dex=str(getattr(sell_quote, "dex", "-")),
            buy_price=buy_price,
            sell_price=sell_price,
            reason_prefix="Real multi-DEX comparison",
        )

    def _paper_simulated_opportunity(self, chain: str, pair: str, quote) -> MultiDexOpportunity:
        buy_price = self._to_decimal(getattr(quote, "price", None))
        if buy_price is None or buy_price <= 0:
            sell_price = None
        else:
            # To create a downstream paper-test opportunity, gross edge must
            # exceed the cost buffer + buy threshold.
            gross_needed = self.cost_buffer_pct + self.synthetic_edge_pct
            sell_price = buy_price * (Decimal("1") + (gross_needed / Decimal("100")))

        return self._make_opportunity(
            mode=OpportunityMode.PAPER_SIMULATED,
            chain=chain,
            pair=pair,
            buy_dex=str(getattr(quote, "dex", "-")),
            sell_dex="SyntheticPaperVenue",
            buy_price=buy_price,
            sell_price=sell_price,
            reason_prefix=(
                "Paper-simulated opportunity because only one healthy DEX quote exists. "
                "Use this only to validate strategy/risk/paper-execution pipeline"
            ),
        )

    def _make_opportunity(
        self,
        mode: OpportunityMode,
        chain: str,
        pair: str,
        buy_dex: str,
        sell_dex: str,
        buy_price: Decimal | None,
        sell_price: Decimal | None,
        reason_prefix: str,
    ) -> MultiDexOpportunity:
        if buy_price is None or sell_price is None or buy_price <= 0:
            gross = None
            net = None
            decision = MultiDexDecision.SKIP
            reason = f"{reason_prefix}: missing or invalid price."
        else:
            gross = ((sell_price - buy_price) / buy_price) * Decimal("100")
            net = gross - self.cost_buffer_pct

            if net >= self.buy_threshold_pct:
                decision = MultiDexDecision.BUY
                reason = f"{reason_prefix}: net edge {net:.4f}% is above BUY threshold {self.buy_threshold_pct}%."
            elif net >= self.watch_threshold_pct:
                decision = MultiDexDecision.WATCH
                reason = f"{reason_prefix}: net edge {net:.4f}% is positive but below BUY threshold."
            else:
                decision = MultiDexDecision.SKIP
                reason = f"{reason_prefix}: net edge {net:.4f}% is too low after costs."

            if mode == OpportunityMode.PAPER_SIMULATED:
                reason += " Not live-tradeable."

        return MultiDexOpportunity(
            opportunity_id=str(uuid4())[:10],
            timestamp=self._utc_now(),
            mode=mode,
            chain=chain,
            pair=pair,
            buy_dex=buy_dex,
            sell_dex=sell_dex,
            buy_price=buy_price,
            sell_price=sell_price,
            gross_edge_pct=gross,
            cost_buffer_pct=self.cost_buffer_pct,
            net_edge_pct=net,
            decision=decision,
            reason=reason,
        )

    @staticmethod
    def _is_healthy_quote(q) -> bool:
        if getattr(q, "error", None):
            return False

        price = MultiDexOpportunityEngine._to_decimal(getattr(q, "price", None))
        amount_out = MultiDexOpportunityEngine._to_decimal(getattr(q, "amount_out", None))
        return price is not None and price > 0 and amount_out is not None and amount_out > 0

    def _persist(self, opportunities: list[MultiDexOpportunity]) -> None:
        with self.output_file.open("a", encoding="utf-8") as fh:
            for opp in opportunities:
                fh.write(json.dumps(self._serialize(opp)) + "\n")

    def _write_report(self, opportunities: list[MultiDexOpportunity], quotes: list) -> None:
        ok_quotes = [q for q in quotes if self._is_healthy_quote(q)]
        error_quotes = [q for q in quotes if not self._is_healthy_quote(q)]

        lines = [
            "# CryptoAI Multi-DEX Opportunity Report",
            "",
            f"Generated: `{self._utc_now()}`",
            "",
            "## Quote Health",
            "",
            f"- Total quotes: `{len(quotes)}`",
            f"- Healthy quotes: `{len(ok_quotes)}`",
            f"- Failed/invalid quotes: `{len(error_quotes)}`",
            "",
            "## Opportunities",
            "",
            "| Mode | Pair | Buy DEX | Sell DEX | Buy Price | Sell Price | Gross % | Cost % | Net % | Decision | Reason |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---|---|",
        ]

        for opp in opportunities:
            lines.append(
                f"| {opp.mode.value} | {opp.pair} | {opp.buy_dex} | {opp.sell_dex} | "
                f"{self._fmt(opp.buy_price)} | {self._fmt(opp.sell_price)} | "
                f"{self._fmt(opp.gross_edge_pct)} | {self._fmt(opp.cost_buffer_pct)} | "
                f"{self._fmt(opp.net_edge_pct)} | {opp.decision.value} | {opp.reason.replace('|', '/')} |"
            )

        lines += [
            "",
            "## Failed / Invalid Quotes",
            "",
            "| DEX | Pair | Error |",
            "|---|---|---|",
        ]

        for q in error_quotes:
            pair = f"{getattr(q, 'token_in', '-')}/{getattr(q, 'token_out', '-')}"
            lines.append(f"| {getattr(q, 'dex', '-')} | {pair} | {str(getattr(q, 'error', '')).replace('|', '/')} |")

        if not error_quotes:
            lines.append("| - | - | None |")

        lines += [
            "",
            "## Interpretation",
            "",
        ]

        if len(ok_quotes) < 2:
            lines.append("- Not enough healthy quotes. Continue fixing providers/RPC.")
        elif len({getattr(q, 'dex', '-') for q in ok_quotes}) < 2:
            lines.append("- Only one DEX is healthy. Real arbitrage is not possible yet; simulated paper mode can validate downstream pipeline.")
        else:
            lines.append("- Multiple DEXes are healthy. Real multi-DEX comparison is possible.")

        self.report_file.write_text("\n".join(lines), encoding="utf-8")

    @classmethod
    def _serialize(cls, opp: MultiDexOpportunity) -> dict:
        raw = asdict(opp)
        for key, value in list(raw.items()):
            if isinstance(value, Decimal):
                raw[key] = str(value)
            elif hasattr(value, "value"):
                raw[key] = value.value
        return raw

    @staticmethod
    def _fmt(value: Decimal | None) -> str:
        if value is None:
            return "-"
        return f"{value:.8f}"

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _env_decimal(name: str, default: Decimal) -> Decimal:
        try:
            return Decimal(os.getenv(name, str(default)))
        except Exception:
            return default

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    rows = MultiDexOpportunityEngine().scan()
    for row in rows:
        print(MultiDexOpportunityEngine._serialize(row))


if __name__ == "__main__":
    main()
