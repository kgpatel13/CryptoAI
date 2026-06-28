from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from app.opportunities.decision_models import OpportunityDecision, TradeDecision

try:
    from app.quotes.quote_service import QuoteService
except Exception:
    QuoteService = None


class OpportunityExplorerService:
    """Explains why opportunities are BUY / WATCH / SKIP.

    v3.0 first uses MultiDexOpportunityEngine output. If that is unavailable,
    it falls back to direct quote comparison.
    """

    def __init__(self) -> None:
        self.data_dir = Path("data")
        self.report_dir = Path("reports")
        self.data_dir.mkdir(exist_ok=True)
        self.report_dir.mkdir(exist_ok=True)
        self.decision_file = self.data_dir / "opportunity_decisions.jsonl"

        self.gas_buffer_pct = Decimal("0.08")
        self.fee_slippage_buffer_pct = Decimal("0.22")
        self.min_buy_net_edge_pct = Decimal("0.30")
        self.watch_net_edge_pct = Decimal("0.05")

    def scan(self) -> list[OpportunityDecision]:
        decisions = self._from_multi_dex_engine()
        if not decisions:
            quotes = self._load_quotes()
            decisions = self._build_decisions_from_quotes(quotes)

        self._persist(decisions)
        self._write_markdown(decisions)
        return decisions

    def recent_decisions(self, limit: int = 100) -> list[dict]:
        if not self.decision_file.exists():
            return []
        rows = []
        for line in self.decision_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return rows[-limit:]

    def _from_multi_dex_engine(self) -> list[OpportunityDecision]:
        try:
            from app.opportunities.multi_dex_opportunity_engine import MultiDexOpportunityEngine
            opportunities = MultiDexOpportunityEngine().scan()
        except Exception:
            return []

        decisions: list[OpportunityDecision] = []

        for opp in opportunities:
            mode = getattr(getattr(opp, "mode", ""), "value", str(getattr(opp, "mode", "")))
            decision_value = getattr(getattr(opp, "decision", ""), "value", str(getattr(opp, "decision", "")))
            net = self._to_decimal(getattr(opp, "net_edge_pct", None))

            if decision_value == "BUY":
                decision = TradeDecision.BUY
            elif decision_value == "WATCH":
                decision = TradeDecision.WATCH
            else:
                decision = TradeDecision.SKIP

            score = self._score(net)

            decisions.append(
                OpportunityDecision(
                    opportunity_id=str(getattr(opp, "opportunity_id", str(uuid4())[:10])),
                    chain=str(getattr(opp, "chain", "base")),
                    pair=str(getattr(opp, "pair", "-")),
                    buy_source=str(getattr(opp, "buy_dex", "-")),
                    sell_source=str(getattr(opp, "sell_dex", "-")),
                    buy_price=self._to_decimal(getattr(opp, "buy_price", None)),
                    sell_price=self._to_decimal(getattr(opp, "sell_price", None)),
                    gross_spread_pct=self._to_decimal(getattr(opp, "gross_edge_pct", None)),
                    gas_buffer_pct=self.gas_buffer_pct,
                    fee_slippage_buffer_pct=self.fee_slippage_buffer_pct,
                    total_cost_buffer_pct=self.gas_buffer_pct + self.fee_slippage_buffer_pct,
                    estimated_net_edge_pct=net,
                    readiness_score=score,
                    decision=decision,
                    reason=f"{mode}: {getattr(opp, 'reason', '')}",
                )
            )

        return decisions

    def _load_quotes(self) -> list:
        if QuoteService is None:
            return []
        try:
            return QuoteService().get_base_quotes()
        except Exception:
            return []

    def _build_decisions_from_quotes(self, quotes: list) -> list[OpportunityDecision]:
        valid_quotes = []
        rejected_count = 0

        for q in quotes:
            price = self._to_decimal(getattr(q, "price", None))
            error = getattr(q, "error", None)
            if price is None or price <= 0 or error:
                rejected_count += 1
                continue
            valid_quotes.append(q)

        groups: dict[tuple[str, str, str], list] = {}
        for q in valid_quotes:
            chain = str(getattr(q, "chain", "base"))
            token_in = str(getattr(q, "token_in", "-"))
            token_out = str(getattr(q, "token_out", "-"))
            groups.setdefault((chain, token_in, token_out), []).append(q)

        decisions: list[OpportunityDecision] = []

        for (chain, token_in, token_out), group in groups.items():
            if len(group) < 2:
                q = group[0]
                decisions.append(
                    self._single_source_decision(
                        chain=chain,
                        pair=f"{token_in}/{token_out}",
                        source=str(getattr(q, "dex", "-")),
                        price=self._to_decimal(getattr(q, "price", None)),
                    )
                )
                continue

            sorted_quotes = sorted(group, key=lambda q: self._to_decimal(getattr(q, "price", None)) or Decimal("0"))
            buy = sorted_quotes[0]
            sell = sorted_quotes[-1]

            decisions.append(
                self._compare_sources(
                    chain=chain,
                    pair=f"{token_in}/{token_out}",
                    buy_source=str(getattr(buy, "dex", "-")),
                    sell_source=str(getattr(sell, "dex", "-")),
                    buy_price=self._to_decimal(getattr(buy, "price", None)),
                    sell_price=self._to_decimal(getattr(sell, "price", None)),
                )
            )

        if not decisions:
            reason = "No comparable valid DEX quotes were available."
            if rejected_count:
                reason += f" Rejected invalid/error quotes: {rejected_count}."
            decisions.append(
                OpportunityDecision(
                    opportunity_id=str(uuid4())[:10],
                    chain="base",
                    pair="-",
                    buy_source="-",
                    sell_source="-",
                    buy_price=None,
                    sell_price=None,
                    gross_spread_pct=None,
                    gas_buffer_pct=self.gas_buffer_pct,
                    fee_slippage_buffer_pct=self.fee_slippage_buffer_pct,
                    total_cost_buffer_pct=self.gas_buffer_pct + self.fee_slippage_buffer_pct,
                    estimated_net_edge_pct=None,
                    readiness_score=0,
                    decision=TradeDecision.SKIP,
                    reason=reason,
                )
            )

        return decisions

    def _single_source_decision(self, chain: str, pair: str, source: str, price: Decimal | None) -> OpportunityDecision:
        return OpportunityDecision(
            opportunity_id=str(uuid4())[:10],
            chain=chain,
            pair=pair,
            buy_source=source,
            sell_source="-",
            buy_price=price,
            sell_price=None,
            gross_spread_pct=None,
            gas_buffer_pct=self.gas_buffer_pct,
            fee_slippage_buffer_pct=self.fee_slippage_buffer_pct,
            total_cost_buffer_pct=self.gas_buffer_pct + self.fee_slippage_buffer_pct,
            estimated_net_edge_pct=None,
            readiness_score=10,
            decision=TradeDecision.SKIP,
            reason="Only one valid quote source was available. Need at least two sources to compare.",
        )

    def _compare_sources(self, chain: str, pair: str, buy_source: str, sell_source: str, buy_price: Decimal | None, sell_price: Decimal | None) -> OpportunityDecision:
        total_cost = self.gas_buffer_pct + self.fee_slippage_buffer_pct

        if buy_price is None or sell_price is None or buy_price <= 0:
            return OpportunityDecision(
                opportunity_id=str(uuid4())[:10],
                chain=chain,
                pair=pair,
                buy_source=buy_source,
                sell_source=sell_source,
                buy_price=buy_price,
                sell_price=sell_price,
                gross_spread_pct=None,
                gas_buffer_pct=self.gas_buffer_pct,
                fee_slippage_buffer_pct=self.fee_slippage_buffer_pct,
                total_cost_buffer_pct=total_cost,
                estimated_net_edge_pct=None,
                readiness_score=0,
                decision=TradeDecision.SKIP,
                reason="Missing or invalid buy/sell price.",
            )

        gross = ((sell_price - buy_price) / buy_price) * Decimal("100")
        net = gross - total_cost
        score = self._score(net)

        if net >= self.min_buy_net_edge_pct:
            decision = TradeDecision.BUY
            reason = f"Estimated net edge {net:.4f}% is above BUY threshold {self.min_buy_net_edge_pct}%."
        elif net >= self.watch_net_edge_pct:
            decision = TradeDecision.WATCH
            reason = f"Estimated net edge {net:.4f}% is positive but below BUY threshold."
        else:
            decision = TradeDecision.SKIP
            reason = f"Estimated net edge {net:.4f}% is too low after cost buffer {total_cost}%."

        return OpportunityDecision(
            opportunity_id=str(uuid4())[:10],
            chain=chain,
            pair=pair,
            buy_source=buy_source,
            sell_source=sell_source,
            buy_price=buy_price,
            sell_price=sell_price,
            gross_spread_pct=gross,
            gas_buffer_pct=self.gas_buffer_pct,
            fee_slippage_buffer_pct=self.fee_slippage_buffer_pct,
            total_cost_buffer_pct=total_cost,
            estimated_net_edge_pct=net,
            readiness_score=score,
            decision=decision,
            reason=reason,
        )

    @staticmethod
    def _score(net_edge: Decimal | None) -> int:
        if net_edge is None:
            return 0
        if net_edge <= 0:
            return 10
        return int(max(0, min(100, net_edge * Decimal("200"))))

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    def _persist(self, decisions: list[OpportunityDecision]) -> None:
        with self.decision_file.open("a", encoding="utf-8") as fh:
            for d in decisions:
                fh.write(json.dumps(self._serialize(d)) + "\n")

    def _write_markdown(self, decisions: list[OpportunityDecision]) -> None:
        path = self.report_dir / "opportunity_explorer.md"
        lines = [
            "# CryptoAI Opportunity Explorer",
            "",
            f"Generated: `{self._utc_now()}`",
            "",
            "| Pair | Buy | Sell | Gross % | Cost % | Net % | Score | Decision | Reason |",
            "|---|---|---|---:|---:|---:|---:|---|---|",
        ]

        for d in decisions:
            lines.append(
                f"| {d.pair} | {d.buy_source} | {d.sell_source} | "
                f"{self._fmt(d.gross_spread_pct)} | {self._fmt(d.total_cost_buffer_pct)} | "
                f"{self._fmt(d.estimated_net_edge_pct)} | {d.readiness_score} | "
                f"{d.decision.value} | {d.reason.replace('|', '/')} |"
            )

        path.write_text("\n".join(lines), encoding="utf-8")

    @classmethod
    def _serialize(cls, d: OpportunityDecision) -> dict:
        raw = asdict(d)
        for key, value in list(raw.items()):
            if isinstance(value, Decimal):
                raw[key] = str(value)
            elif hasattr(value, "value"):
                raw[key] = value.value
        raw["timestamp"] = cls._utc_now()
        return raw

    @staticmethod
    def _fmt(value: Decimal | None) -> str:
        if value is None:
            return "-"
        return f"{value:.4f}"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    decisions = OpportunityExplorerService().scan()
    for d in decisions:
        print(OpportunityExplorerService._serialize(d))


if __name__ == "__main__":
    main()
