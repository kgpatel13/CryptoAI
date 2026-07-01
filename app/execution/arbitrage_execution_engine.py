from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from app.execution.execution_simulator import ExecutionSimulator
from app.execution.models import PaperOrder, PaperOrderSide, PaperOrderStatus


@dataclass(frozen=True)
class ArbitrageOpportunityContext:
    opportunity_id: str | None
    timestamp: str | None
    pair: str
    buy_source: str
    sell_source: str
    buy_price: Decimal | None
    sell_price: Decimal | None
    gross_edge_pct: Decimal | None
    cost_buffer_pct: Decimal
    net_edge_pct: Decimal | None
    reason: str


class ArbitrageExecutionEngine:
    """Paper-only atomic arbitrage execution.

    Arbitrage is modeled as a round trip, not as a position. A successful
    simulation returns a CLOSED order with realized PnL already computed.
    """

    def __init__(
        self,
        data_dir: str | Path = "data",
        execution_simulator: ExecutionSimulator | None = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.opportunity_file = self.data_dir / "opportunity_decisions.jsonl"
        self.execution_simulator = execution_simulator or ExecutionSimulator()

    def execute(
        self,
        *,
        timestamp: str,
        strategy_name: str,
        chain: str,
        pair: str,
        requested_notional_usd: Decimal,
        expected_edge_pct: Decimal | None,
    ) -> PaperOrder:
        context = self.latest_context(pair) or self._fallback_context(pair, expected_edge_pct)
        reference_price = context.buy_price or Decimal("1")

        entry = self.execution_simulator.simulate_entry_order(
            timestamp=timestamp,
            pair=pair,
            side=PaperOrderSide.BUY.value,
            requested_notional_usd=requested_notional_usd,
            reference_price_usd=reference_price,
            expected_edge_pct=context.net_edge_pct if context.net_edge_pct is not None else expected_edge_pct,
        )

        if entry.status not in {PaperOrderStatus.FILLED, PaperOrderStatus.PARTIAL_FILL}:
            return PaperOrder(
                order_id=entry.order_id,
                timestamp=timestamp,
                strategy_name=strategy_name,
                chain=chain,
                pair=pair,
                side=PaperOrderSide.BUY,
                notional_usd=Decimal("0"),
                requested_notional_usd=entry.requested_notional_usd,
                filled_notional_usd=entry.filled_notional_usd,
                estimated_edge_pct=expected_edge_pct,
                simulated_fill_price_usd=entry.fill_price_usd,
                simulated_quantity=entry.quantity,
                status=entry.status,
                reason=entry.reason,
                execution_type="ARBITRAGE_ROUND_TRIP",
                buy_source=context.buy_source,
                sell_source=context.sell_source,
                buy_price_usd=context.buy_price,
                sell_price_usd=context.sell_price,
                gross_edge_pct=context.gross_edge_pct,
                cost_buffer_pct=context.cost_buffer_pct,
                net_edge_pct=context.net_edge_pct,
                slippage_bps=entry.slippage_bps,
                latency_ms=entry.latency_ms,
                execution_quality=entry.execution_quality,
                lifecycle_events=entry.lifecycle_events,
            )

        net_edge = context.net_edge_pct if context.net_edge_pct is not None else (expected_edge_pct or Decimal("0"))
        realized_pnl = self._q(entry.filled_notional_usd * net_edge / Decimal("100"))
        exit_value = self._q(entry.filled_notional_usd + realized_pnl)
        order_id = entry.order_id or str(uuid4())[:8]
        events = list(entry.lifecycle_events)
        events.append(
            {
                "timestamp": timestamp,
                "status": "SELL_LEG",
                "message": f"Paper arbitrage sell leg simulated on {context.sell_source}.",
            }
        )
        events.append(
            {
                "timestamp": timestamp,
                "status": "CLOSED",
                "message": f"Atomic paper arbitrage round trip closed with realized PnL ${realized_pnl}.",
            }
        )

        return PaperOrder(
            order_id=order_id,
            timestamp=timestamp,
            strategy_name=strategy_name,
            chain=chain,
            pair=pair,
            side=PaperOrderSide.BUY,
            notional_usd=entry.filled_notional_usd,
            requested_notional_usd=entry.requested_notional_usd,
            filled_notional_usd=entry.filled_notional_usd,
            estimated_edge_pct=expected_edge_pct,
            simulated_fill_price_usd=entry.fill_price_usd,
            simulated_quantity=entry.quantity,
            status=PaperOrderStatus.CLOSED,
            reason="Atomic paper arbitrage round trip completed and closed immediately.",
            execution_type="ARBITRAGE_ROUND_TRIP",
            buy_source=context.buy_source,
            sell_source=context.sell_source,
            buy_price_usd=context.buy_price,
            sell_price_usd=context.sell_price,
            gross_edge_pct=context.gross_edge_pct,
            cost_buffer_pct=context.cost_buffer_pct,
            net_edge_pct=net_edge,
            realized_pnl_usd=realized_pnl,
            exit_value_usd=exit_value,
            slippage_bps=entry.slippage_bps,
            latency_ms=entry.latency_ms,
            execution_quality=entry.execution_quality,
            lifecycle_events=events,
        )

    def latest_context(self, pair: str) -> ArbitrageOpportunityContext | None:
        if not self.opportunity_file.exists():
            return None
        try:
            rows = [
                json.loads(line)
                for line in self.opportunity_file.read_text(encoding="utf-8", errors="replace").splitlines()
                if line.strip()
            ]
        except Exception:
            return None

        for row in reversed(rows):
            if str(row.get("pair")) != pair:
                continue
            if str(row.get("decision", "")).upper() != "BUY":
                continue
            return ArbitrageOpportunityContext(
                opportunity_id=str(row.get("opportunity_id")) if row.get("opportunity_id") is not None else None,
                timestamp=str(row.get("timestamp")) if row.get("timestamp") is not None else None,
                pair=pair,
                buy_source=str(row.get("buy_source", "-")),
                sell_source=str(row.get("sell_source", "-")),
                buy_price=self._decimal_or_none(row.get("buy_price")),
                sell_price=self._decimal_or_none(row.get("sell_price")),
                gross_edge_pct=self._decimal_or_none(row.get("gross_spread_pct")),
                cost_buffer_pct=self._decimal(row.get("total_cost_buffer_pct", "0.30")),
                net_edge_pct=self._decimal_or_none(row.get("estimated_net_edge_pct")),
                reason=str(row.get("reason", "")),
            )
        return None

    @staticmethod
    def _fallback_context(pair: str, expected_edge_pct: Decimal | None) -> ArbitrageOpportunityContext:
        return ArbitrageOpportunityContext(
            opportunity_id=None,
            timestamp=None,
            pair=pair,
            buy_source="-",
            sell_source="-",
            buy_price=Decimal("1"),
            sell_price=None,
            gross_edge_pct=expected_edge_pct,
            cost_buffer_pct=Decimal("0.30"),
            net_edge_pct=expected_edge_pct,
            reason="No matching opportunity context found; used risk edge as fallback.",
        )

    @staticmethod
    def _decimal(value) -> Decimal:
        try:
            return Decimal(str(value))
        except Exception:
            return Decimal("0")

    @classmethod
    def _decimal_or_none(cls, value) -> Decimal | None:
        if value is None:
            return None
        parsed = cls._decimal(value)
        return parsed

    @staticmethod
    def _q(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.0000"))

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
