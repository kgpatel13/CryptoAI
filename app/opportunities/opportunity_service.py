from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from app.opportunities.models import (
    OpportunityCandidate,
    OpportunityStatus,
    OpportunityType,
)

try:
    from app.scanner.opportunity_scanner import OpportunityScanner
except Exception:
    OpportunityScanner = None

try:
    from app.events.event_service import EventBusService
    from app.events.models import EventType
except Exception:
    EventBusService = None
    EventType = None


class OpportunityService:
    """Normalized opportunity engine.

    v2.2 converts scanner output into opportunity candidates that later
    strategy, AI, risk, and execution modules can evaluate consistently.
    """

    def __init__(self) -> None:
        self.default_cost_buffer_pct = Decimal("0.20")

    def scan(self) -> list[OpportunityCandidate]:
        raw_opportunities = self._load_gross_opportunities()
        candidates: list[OpportunityCandidate] = []

        for raw in raw_opportunities:
            candidate = self._from_gross_opportunity(raw)
            candidates.append(candidate)

        self._publish_scan_event(candidates)
        return candidates

    def _load_gross_opportunities(self) -> list:
        if OpportunityScanner is None:
            return []
        try:
            return OpportunityScanner().scan_base_gross_opportunities()
        except Exception:
            return []

    def _from_gross_opportunity(self, raw) -> OpportunityCandidate:
        chain = str(getattr(raw, "chain", "base"))
        pair = str(getattr(raw, "pair", "-"))
        buy_dex = str(getattr(raw, "best_buy_dex", "-"))
        sell_dex = str(getattr(raw, "best_sell_dex", "-"))
        buy_price = self._to_decimal(getattr(raw, "buy_price", None))
        sell_price = self._to_decimal(getattr(raw, "sell_price", None))
        gross = self._to_decimal(getattr(raw, "gross_spread_pct", None))

        estimated_net = None
        if gross is not None:
            estimated_net = gross - self.default_cost_buffer_pct

        if estimated_net is None:
            status = OpportunityStatus.REJECTED
            reason = "Missing gross spread data."
        elif estimated_net <= 0:
            status = OpportunityStatus.REJECTED
            reason = "Estimated net edge is negative after cost buffer."
        elif estimated_net < Decimal("0.15"):
            status = OpportunityStatus.WATCH
            reason = "Small positive estimated net edge; watch only."
        else:
            status = OpportunityStatus.CANDIDATE
            reason = "Estimated net edge is positive after basic cost buffer."

        return OpportunityCandidate(
            opportunity_id=str(uuid4())[:10],
            opportunity_type=OpportunityType.DEX_ARBITRAGE,
            chain=chain,
            pair=pair,
            source_buy=buy_dex,
            source_sell=sell_dex,
            buy_price=buy_price,
            sell_price=sell_price,
            gross_spread_pct=gross,
            estimated_cost_pct=self.default_cost_buffer_pct,
            estimated_net_edge_pct=estimated_net,
            latency_sensitivity="HIGH",
            liquidity_status="UNKNOWN",
            status=status,
            reason=reason,
        )

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _publish_scan_event(candidates: list[OpportunityCandidate]) -> None:
        if EventBusService is None or EventType is None:
            return

        try:
            EventBusService().publish(
                event_type=EventType.SYSTEM,
                source="opportunity_engine",
                payload={
                    "message": "Opportunity scan completed",
                    "candidate_count": len(candidates),
                    "candidates": [
                        {
                            "id": c.opportunity_id,
                            "type": c.opportunity_type.value,
                            "chain": c.chain,
                            "pair": c.pair,
                            "status": c.status.value,
                            "estimated_net_edge_pct": str(c.estimated_net_edge_pct)
                            if c.estimated_net_edge_pct is not None
                            else None,
                        }
                        for c in candidates
                    ],
                },
            )
        except Exception:
            return
