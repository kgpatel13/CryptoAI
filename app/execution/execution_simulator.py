from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from app.execution.models import PaperOrderStatus


@dataclass(frozen=True)
class ExecutionSimulationResult:
    order_id: str
    status: PaperOrderStatus
    requested_notional_usd: Decimal
    filled_notional_usd: Decimal
    fill_price_usd: Decimal | None
    quantity: Decimal | None
    slippage_bps: Decimal
    latency_ms: int
    execution_quality: str
    reason: str
    lifecycle_events: list[dict]


class ExecutionSimulator:
    """Deterministic professional paper execution simulator.

    v3.4 intentionally defaults to successful fills so existing paper workflows remain
    stable. Environment variables can make the simulator more conservative for stress
    testing without changing code.
    """

    def __init__(self) -> None:
        self.default_slippage_bps = self._env_decimal("CRYPTOAI_PAPER_SLIPPAGE_BPS", "5")
        self.max_slippage_bps = self._env_decimal("CRYPTOAI_MAX_PAPER_SLIPPAGE_BPS", "35")
        self.latency_ms = self._env_int("CRYPTOAI_PAPER_EXECUTION_LATENCY_MS", 250)
        self.partial_fill_ratio = self._env_decimal("CRYPTOAI_PAPER_PARTIAL_FILL_RATIO", "1.00")
        self.max_order_age_seconds = self._env_int("CRYPTOAI_PAPER_ORDER_MAX_AGE_SECONDS", 30)

    def simulate_entry_order(
        self,
        *,
        timestamp: str,
        pair: str,
        side: str,
        requested_notional_usd: Decimal,
        reference_price_usd: Decimal,
        expected_edge_pct: Decimal | None,
    ) -> ExecutionSimulationResult:
        order_id = str(uuid4())[:8]
        events: list[dict] = []

        self._event(events, timestamp, PaperOrderStatus.NEW, "Order candidate created.")
        self._event(events, timestamp, PaperOrderStatus.VALIDATED, "Portfolio and quote gates passed.")
        self._event(events, timestamp, PaperOrderStatus.SUBMITTED, "Paper order submitted to execution simulator.")
        self._event(events, timestamp, PaperOrderStatus.PENDING, f"Simulated routing latency {self.latency_ms}ms.")

        if requested_notional_usd <= 0:
            self._event(events, timestamp, PaperOrderStatus.REJECTED, "Requested notional is zero.")
            return ExecutionSimulationResult(order_id, PaperOrderStatus.REJECTED, requested_notional_usd, Decimal("0"), None, None, Decimal("0"), self.latency_ms, "REJECTED", "Execution rejected: requested notional is zero.", events)

        if reference_price_usd <= 0:
            self._event(events, timestamp, PaperOrderStatus.REJECTED, "Reference price is unavailable.")
            return ExecutionSimulationResult(order_id, PaperOrderStatus.REJECTED, requested_notional_usd, Decimal("0"), None, None, Decimal("0"), self.latency_ms, "REJECTED", "Execution rejected: missing reference price.", events)

        slippage_bps = self._effective_slippage_bps(expected_edge_pct)
        if slippage_bps > self.max_slippage_bps:
            self._event(events, timestamp, PaperOrderStatus.REJECTED, f"Slippage {slippage_bps}bps exceeds limit {self.max_slippage_bps}bps.")
            return ExecutionSimulationResult(order_id, PaperOrderStatus.REJECTED, requested_notional_usd, Decimal("0"), None, None, slippage_bps, self.latency_ms, "REJECTED", f"Execution rejected: simulated slippage {slippage_bps}bps exceeds limit {self.max_slippage_bps}bps.", events)

        ratio = max(Decimal("0"), min(Decimal("1"), self.partial_fill_ratio))
        if ratio <= 0:
            self._event(events, timestamp, PaperOrderStatus.EXPIRED, "Order expired with no fill.")
            return ExecutionSimulationResult(order_id, PaperOrderStatus.EXPIRED, requested_notional_usd, Decimal("0"), None, None, slippage_bps, self.latency_ms, "EXPIRED", "Execution expired: no simulated liquidity filled the order.", events)

        status = PaperOrderStatus.FILLED if ratio == Decimal("1") else PaperOrderStatus.PARTIAL_FILL
        filled_notional = (requested_notional_usd * ratio).quantize(Decimal("0.0001"))
        price_multiplier = Decimal("1") + (slippage_bps / Decimal("10000")) if side.upper() == "BUY" else Decimal("1") - (slippage_bps / Decimal("10000"))
        fill_price = (reference_price_usd * price_multiplier).quantize(Decimal("0.000000000000000001"))
        quantity = filled_notional / fill_price
        quality = self._quality(slippage_bps, ratio)
        self._event(events, timestamp, status, f"Filled ${filled_notional} at {fill_price} with {slippage_bps}bps simulated slippage.")
        return ExecutionSimulationResult(order_id, status, requested_notional_usd, filled_notional, fill_price, quantity, slippage_bps, self.latency_ms, quality, "Simulated paper execution completed through professional order lifecycle.", events)

    def _effective_slippage_bps(self, expected_edge_pct: Decimal | None) -> Decimal:
        if expected_edge_pct is None:
            return self.default_slippage_bps
        edge_bps = expected_edge_pct * Decimal("100")
        # Conservative model: small edges pay more relative execution penalty.
        if edge_bps < Decimal("20"):
            return max(self.default_slippage_bps, Decimal("15"))
        return self.default_slippage_bps

    @staticmethod
    def _quality(slippage_bps: Decimal, fill_ratio: Decimal) -> str:
        if fill_ratio < Decimal("1"):
            return "PARTIAL"
        if slippage_bps <= Decimal("5"):
            return "GOOD"
        if slippage_bps <= Decimal("20"):
            return "ACCEPTABLE"
        return "POOR"

    @staticmethod
    def _event(events: list[dict], timestamp: str, status: PaperOrderStatus, message: str) -> None:
        events.append({"timestamp": timestamp, "status": status.value, "message": message})

    @staticmethod
    def _env_decimal(name: str, default: str) -> Decimal:
        try:
            return Decimal(os.getenv(name, default))
        except Exception:
            return Decimal(default)

    @staticmethod
    def _env_int(name: str, default: int) -> int:
        try:
            return int(os.getenv(name, str(default)))
        except Exception:
            return default
