from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from app.execution.models import (
    PaperExecutionBatch,
    PaperOrder,
    PaperOrderSide,
    PaperOrderStatus,
)

try:
    from app.database.db import get_connection, initialize_database
except Exception:
    get_connection = None
    initialize_database = None

try:
    from app.risk.risk_service import RiskService
except Exception:
    RiskService = None

try:
    from app.marketdata.market_service import MarketDataService
except Exception:
    MarketDataService = None


class PaperExecutionService:
    """Simulated execution engine with JSONL + SQLite persistence."""

    def __init__(self) -> None:
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.order_file = self.data_dir / "paper_orders.jsonl"

    def run_once(self) -> PaperExecutionBatch:
        timestamp = self._utc_now()
        assessments = self._load_risk_assessments()
        prices = self._load_prices()

        orders: list[PaperOrder] = []

        for assessment in assessments:
            decision = getattr(assessment, "decision", "")
            decision_value = decision.value if hasattr(decision, "value") else str(decision)

            if decision_value != "APPROVED_FOR_PAPER":
                orders.append(
                    PaperOrder(
                        order_id=str(uuid4())[:8],
                        timestamp=timestamp,
                        strategy_name=str(getattr(assessment, "strategy_name", "Strategy")),
                        chain=str(getattr(assessment, "chain", "-")),
                        pair=str(getattr(assessment, "pair", "-")),
                        side=PaperOrderSide.BUY,
                        notional_usd=Decimal("0"),
                        estimated_edge_pct=self._to_decimal(getattr(assessment, "expected_edge_pct", None)),
                        simulated_fill_price_usd=None,
                        simulated_quantity=None,
                        status=PaperOrderStatus.SKIPPED,
                        reason=f"Risk decision is {decision_value}; paper order not created.",
                    )
                )
                continue

            pair = str(getattr(assessment, "pair", "WETH/USDC"))
            base_symbol = pair.split("/")[0] if "/" in pair else "WETH"
            price = self._price_for(base_symbol, prices)
            notional = self._to_decimal(getattr(assessment, "max_allowed_notional_usd", "0")) or Decimal("0")

            if price <= 0 or notional <= 0:
                orders.append(
                    PaperOrder(
                        order_id=str(uuid4())[:8],
                        timestamp=timestamp,
                        strategy_name=str(getattr(assessment, "strategy_name", "Strategy")),
                        chain=str(getattr(assessment, "chain", "-")),
                        pair=pair,
                        side=PaperOrderSide.BUY,
                        notional_usd=notional,
                        estimated_edge_pct=self._to_decimal(getattr(assessment, "expected_edge_pct", None)),
                        simulated_fill_price_usd=None,
                        simulated_quantity=None,
                        status=PaperOrderStatus.REJECTED,
                        reason="Missing price or notional for simulated fill.",
                    )
                )
                continue

            quantity = notional / price

            orders.append(
                PaperOrder(
                    order_id=str(uuid4())[:8],
                    timestamp=timestamp,
                    strategy_name=str(getattr(assessment, "strategy_name", "Strategy")),
                    chain=str(getattr(assessment, "chain", "-")),
                    pair=pair,
                    side=PaperOrderSide.BUY,
                    notional_usd=notional,
                    estimated_edge_pct=self._to_decimal(getattr(assessment, "expected_edge_pct", None)),
                    simulated_fill_price_usd=price,
                    simulated_quantity=quantity,
                    status=PaperOrderStatus.FILLED,
                    reason="Simulated paper fill created from risk-approved candidate.",
                )
            )

        batch = PaperExecutionBatch(
            timestamp=timestamp,
            total_candidates=len(assessments),
            filled_orders=sum(1 for o in orders if o.status == PaperOrderStatus.FILLED),
            rejected_orders=sum(1 for o in orders if o.status == PaperOrderStatus.REJECTED),
            skipped_orders=sum(1 for o in orders if o.status == PaperOrderStatus.SKIPPED),
            total_notional_usd=sum((o.notional_usd for o in orders if o.status == PaperOrderStatus.FILLED), Decimal("0")),
            orders=orders,
        )

        self._persist_orders_jsonl(orders)
        self._persist_orders_db(orders)
        return batch

    def recent_orders(self, limit: int = 50) -> list[dict]:
        if not self.order_file.exists():
            return []

        rows: list[dict] = []
        for line in self.order_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return rows[-limit:]

    def _load_risk_assessments(self) -> list:
        if RiskService is None:
            return []
        try:
            return RiskService().assess_ranked_signals()
        except Exception:
            return []

    def _load_prices(self) -> dict[str, Decimal]:
        fallback = {
            "ETH": Decimal("3500"),
            "WETH": Decimal("3500"),
            "BTC": Decimal("100000"),
            "WBTC": Decimal("100000"),
            "CBBTC": Decimal("100000"),
            "USDC": Decimal("1"),
        }

        if MarketDataService is None:
            return fallback

        try:
            market_rows = MarketDataService().get_registered_asset_prices()
        except Exception:
            return fallback

        prices = dict(fallback)
        for row in market_rows:
            symbol = str(getattr(row, "symbol", "")).upper()
            price = getattr(row, "usd_price", None)
            if symbol and price is not None:
                prices[symbol] = Decimal(str(price))
                if symbol == "ETH":
                    prices["WETH"] = Decimal(str(price))
                if symbol == "BTC":
                    prices["WBTC"] = Decimal(str(price))
                    prices["CBBTC"] = Decimal(str(price))
        return prices

    def _persist_orders_jsonl(self, orders: list[PaperOrder]) -> None:
        with self.order_file.open("a", encoding="utf-8") as fh:
            for order in orders:
                fh.write(json.dumps(self._serialize_order(order)) + "\n")

    @staticmethod
    def _persist_orders_db(orders: list[PaperOrder]) -> None:
        if initialize_database is None or get_connection is None:
            return

        try:
            initialize_database()
            with get_connection() as conn:
                for order in orders:
                    conn.execute(
                        """
                        INSERT INTO paper_orders
                        (order_id, timestamp, strategy_name, chain, pair, side,
                         notional_usd, estimated_edge_pct, simulated_fill_price_usd,
                         simulated_quantity, status, reason)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            order.order_id,
                            order.timestamp,
                            order.strategy_name,
                            order.chain,
                            order.pair,
                            order.side.value if hasattr(order.side, "value") else str(order.side),
                            str(order.notional_usd),
                            str(order.estimated_edge_pct) if order.estimated_edge_pct is not None else None,
                            str(order.simulated_fill_price_usd) if order.simulated_fill_price_usd is not None else None,
                            str(order.simulated_quantity) if order.simulated_quantity is not None else None,
                            order.status.value if hasattr(order.status, "value") else str(order.status),
                            order.reason,
                        ),
                    )
                conn.commit()
        except Exception:
            return

    @staticmethod
    def _serialize_order(order: PaperOrder) -> dict:
        payload = asdict(order)
        for key, value in list(payload.items()):
            if isinstance(value, Decimal):
                payload[key] = str(value)
            elif hasattr(value, "value"):
                payload[key] = value.value
        return payload

    @staticmethod
    def _price_for(symbol: str, prices: dict[str, Decimal]) -> Decimal:
        normalized = symbol.upper()
        return prices.get(normalized, Decimal("0"))

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _utc_now() -> str:
        return datetime.utcnow().isoformat(timespec="seconds") + "Z"
