from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from app.execution.arbitrage_execution_engine import ArbitrageExecutionEngine
from app.execution.execution_simulator import ExecutionSimulator
from app.execution.models import PaperExecutionBatch, PaperOrder, PaperOrderSide, PaperOrderStatus
from app.portfolio.accounting import PaperAccounting

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

try:
    from app.risk.portfolio_risk_service import PortfolioRiskService
except Exception:
    PortfolioRiskService = None


class PaperExecutionService:
    """Professional paper execution engine with lifecycle simulation.

    v3.4 keeps live trading disabled and routes every approved candidate through a
    deterministic broker-like simulator before recording a paper position.
    """

    def __init__(
        self,
        data_dir: Path | str = "data",
        portfolio_risk=None,
        execution_simulator: ExecutionSimulator | None = None,
        arbitrage_engine: ArbitrageExecutionEngine | None = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.order_file = self.data_dir / "paper_orders.jsonl"
        self.multi_dex_file = self.data_dir / "multi_dex_opportunities.jsonl"
        self.portfolio_risk = portfolio_risk if portfolio_risk is not None else (PortfolioRiskService() if PortfolioRiskService is not None else None)
        self.execution_simulator = execution_simulator or ExecutionSimulator()
        self.arbitrage_engine = arbitrage_engine or ArbitrageExecutionEngine(data_dir=self.data_dir, execution_simulator=self.execution_simulator)

    def run_once(self) -> PaperExecutionBatch:
        timestamp = self._utc_now()
        assessments = self._load_risk_assessments()
        prices = self._load_prices()
        monitored_positions = 0
        closed_positions = 0

        orders: list[PaperOrder] = []
        for assessment in assessments:
            decision = getattr(assessment, "decision", "")
            decision_value = decision.value if hasattr(decision, "value") else str(decision)
            pair = str(getattr(assessment, "pair", "-"))
            expected_edge = self._to_decimal(getattr(assessment, "expected_edge_pct", None))
            chain = str(getattr(assessment, "chain", "-"))
            strategy_name = str(getattr(assessment, "strategy_name", "Strategy"))

            if decision_value != "APPROVED_FOR_PAPER":
                orders.append(PaperOrder(order_id=str(uuid4())[:8], timestamp=timestamp, strategy_name=strategy_name, chain=chain, pair=pair, side=PaperOrderSide.BUY, notional_usd=Decimal("0"), estimated_edge_pct=expected_edge, simulated_fill_price_usd=None, simulated_quantity=None, status=PaperOrderStatus.SKIPPED, reason=f"Risk decision is {decision_value}; paper order not created. {getattr(assessment, 'reason', '')}"))
                continue

            raw_reference_price = self._fill_price_for(pair, prices)
            requested_notional = self._to_decimal(getattr(assessment, "max_allowed_notional_usd", "0")) or Decimal("0")
            reference_price = PaperAccounting.raw_pair_price_to_base_usd(pair=pair, raw_price=raw_reference_price, prices=prices)

            if reference_price <= 0 or requested_notional <= 0:
                orders.append(PaperOrder(order_id=str(uuid4())[:8], timestamp=timestamp, strategy_name=strategy_name, chain=chain, pair=pair, side=PaperOrderSide.BUY, notional_usd=requested_notional, estimated_edge_pct=expected_edge, simulated_fill_price_usd=None, simulated_quantity=None, status=PaperOrderStatus.REJECTED, reason="Missing fill price or notional for simulated fill."))
                continue

            if self.portfolio_risk is not None:
                portfolio_decision = self.portfolio_risk.assess(chain=chain, pair=pair, side=PaperOrderSide.BUY.value, requested_notional_usd=requested_notional, expected_edge_pct=expected_edge, now=timestamp)
                if not portfolio_decision.approved:
                    orders.append(PaperOrder(order_id=str(uuid4())[:8], timestamp=timestamp, strategy_name=strategy_name, chain=chain, pair=pair, side=PaperOrderSide.BUY, notional_usd=Decimal("0"), estimated_edge_pct=expected_edge, simulated_fill_price_usd=None, simulated_quantity=None, status=PaperOrderStatus.RISK_REJECTED, reason=portfolio_decision.reason))
                    continue
                requested_notional = portfolio_decision.notional_usd

            order = self.arbitrage_engine.execute(
                timestamp=timestamp,
                strategy_name=strategy_name,
                chain=chain,
                pair=pair,
                requested_notional_usd=requested_notional,
                expected_edge_pct=expected_edge,
            )
            orders.append(order)

            if self.portfolio_risk is not None and order.status == PaperOrderStatus.CLOSED and order.notional_usd > 0:
                self.portfolio_risk.record_arbitrage_round_trip(
                    order_id=order.order_id,
                    timestamp=timestamp,
                    strategy_name=strategy_name,
                    chain=chain,
                    pair=pair,
                    notional_usd=order.notional_usd,
                    realized_pnl_usd=order.realized_pnl_usd or Decimal("0"),
                    buy_source=order.buy_source,
                    sell_source=order.sell_source,
                    gross_edge_pct=order.gross_edge_pct,
                    cost_buffer_pct=order.cost_buffer_pct,
                    net_edge_pct=order.net_edge_pct,
                    slippage_bps=order.slippage_bps,
                    latency_ms=order.latency_ms,
                    execution_quality=order.execution_quality,
                )

        filled_statuses = {PaperOrderStatus.CLOSED}
        batch = PaperExecutionBatch(
            timestamp=timestamp,
            total_candidates=len(assessments),
            filled_orders=sum(1 for o in orders if o.status in filled_statuses),
            rejected_orders=sum(1 for o in orders if o.status in {PaperOrderStatus.REJECTED, PaperOrderStatus.CANCELLED, PaperOrderStatus.EXPIRED}),
            skipped_orders=sum(1 for o in orders if o.status in {PaperOrderStatus.SKIPPED, PaperOrderStatus.RISK_REJECTED}),
            total_notional_usd=sum((o.notional_usd for o in orders if o.status in filled_statuses), Decimal("0")),
            orders=orders,
            monitored_positions=monitored_positions,
            closed_positions=closed_positions,
        )
        self._persist_orders_jsonl(orders)
        self._persist_orders_db(orders)
        return batch

    def recent_orders(self, limit: int = 50) -> list[dict]:
        if not self.order_file.exists():
            return []
        rows = []
        for line in self.order_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
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

    def _fill_price_for(self, pair: str, prices: dict[str, Decimal]) -> Decimal:
        latest_opp_price = self._latest_opportunity_buy_price(pair)
        if latest_opp_price > 0:
            return latest_opp_price
        base_symbol = pair.split("/")[0] if "/" in pair else "WETH"
        return self._price_for(base_symbol, prices)

    def _latest_opportunity_buy_price(self, pair: str) -> Decimal:
        if not self.multi_dex_file.exists():
            return Decimal("0")
        try:
            rows = [json.loads(line) for line in self.multi_dex_file.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
            for row in reversed(rows):
                if str(row.get("pair")) == pair and str(row.get("decision")) == "BUY":
                    price = self._to_decimal(row.get("buy_price"))
                    if price is not None and price > 0:
                        return price
        except Exception:
            return Decimal("0")
        return Decimal("0")

    def _load_prices(self) -> dict[str, Decimal]:
        fallback = {"ETH": Decimal("3500"), "WETH": Decimal("3500"), "BTC": Decimal("100000"), "WBTC": Decimal("100000"), "CBBTC": Decimal("100000"), "USDC": Decimal("1")}
        if MarketDataService is None:
            return fallback
        try:
            rows = MarketDataService().get_registered_asset_prices()
        except Exception:
            return fallback
        prices = dict(fallback)
        for row in rows:
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
                    conn.execute("""INSERT INTO paper_orders (order_id, timestamp, strategy_name, chain, pair, side, notional_usd, estimated_edge_pct, simulated_fill_price_usd, simulated_quantity, status, reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (order.order_id, order.timestamp, order.strategy_name, order.chain, order.pair, order.side.value if hasattr(order.side, "value") else str(order.side), str(order.notional_usd), str(order.estimated_edge_pct) if order.estimated_edge_pct is not None else None, str(order.simulated_fill_price_usd) if order.simulated_fill_price_usd is not None else None, str(order.simulated_quantity) if order.simulated_quantity is not None else None, order.status.value if hasattr(order.status, "value") else str(order.status), order.reason))
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
        return prices.get(symbol.upper(), Decimal("0"))

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
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
