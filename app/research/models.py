from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


@dataclass(frozen=True)
class FeatureVector:
    """Research-ready representation of an opportunity, signal, or execution context."""

    feature_id: str
    created_at: str
    source: str
    chain: str = "-"
    pair: str = "-"
    strategy_id: str = "arbitrage"
    mode: str = "paper"
    buy_source: str = "-"
    sell_source: str = "-"
    buy_price: str | None = None
    sell_price: str | None = None
    gross_spread_pct: str | None = None
    gas_buffer_pct: str | None = None
    fee_slippage_buffer_pct: str | None = None
    total_cost_buffer_pct: str | None = None
    estimated_net_edge_pct: str | None = None
    readiness_score: int = 0
    decision: str = "UNKNOWN"
    reason: str = ""
    confidence_score: int = 0
    rank_score: int = 0
    quote_health_score: int = 0
    risk_status: str = "UNKNOWN"
    execution_quality: str | None = None
    slippage_bps: str | None = None
    latency_ms: str | None = None
    realized_pnl_usd: str | None = None
    hour_utc: int = 0
    weekday_utc: int = 0
    tags: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_opportunity(cls, row: dict[str, Any], source: str = "opportunity") -> "FeatureVector":
        created_at = str(row.get("timestamp") or row.get("created_at") or utc_now())
        parsed = _parse_dt(created_at)
        decision = str(row.get("decision", "UNKNOWN"))
        readiness = _int(row.get("readiness_score", row.get("score", 0)))
        net_edge = row.get("estimated_net_edge_pct", row.get("net_pct", row.get("net_edge_pct")))
        confidence = readiness if decision.upper() in {"BUY", "READY_FOR_PAPER"} else min(readiness, 25)
        tags = []
        reason = str(row.get("reason", ""))
        if "PAPER_SIMULATED" in reason:
            tags.append("paper_simulated")
        if "Not live-tradeable" in reason or "not live" in reason.lower():
            tags.append("not_live_tradeable")
        if decision.upper() == "SKIP":
            tags.append("skipped")
        if decision.upper() == "BUY":
            tags.append("candidate")

        return cls(
            feature_id=f"fv_{uuid4().hex[:12]}",
            created_at=created_at,
            source=source,
            chain=str(row.get("chain", "base")),
            pair=str(row.get("pair", "-")),
            strategy_id=str(row.get("strategy_id", "arbitrage")),
            mode=str(row.get("mode", "paper")),
            buy_source=str(row.get("buy_source", row.get("buy", "-"))),
            sell_source=str(row.get("sell_source", row.get("sell", "-"))),
            buy_price=_optional_str(row.get("buy_price")),
            sell_price=_optional_str(row.get("sell_price")),
            gross_spread_pct=_optional_str(row.get("gross_spread_pct", row.get("gross_pct"))),
            gas_buffer_pct=_optional_str(row.get("gas_buffer_pct")),
            fee_slippage_buffer_pct=_optional_str(row.get("fee_slippage_buffer_pct")),
            total_cost_buffer_pct=_optional_str(row.get("total_cost_buffer_pct", row.get("cost_pct"))),
            estimated_net_edge_pct=_optional_str(net_edge),
            readiness_score=readiness,
            decision=decision,
            reason=reason,
            confidence_score=confidence,
            rank_score=readiness + (20 if decision.upper() == "BUY" else 0),
            quote_health_score=100 if row.get("buy_price") and row.get("sell_price") else 0,
            risk_status="PENDING",
            hour_utc=parsed.hour,
            weekday_utc=parsed.weekday(),
            tags=tags,
            raw=row,
        )

    @classmethod
    def from_order(cls, row: dict[str, Any], source: str = "paper_order") -> "FeatureVector":
        created_at = str(row.get("timestamp") or utc_now())
        parsed = _parse_dt(created_at)
        status = str(row.get("status", "UNKNOWN")).upper()
        tags = ["order"]
        if status == "FILLED":
            tags.append("filled")
        if status == "RISK_REJECTED":
            tags.append("risk_rejected")
        return cls(
            feature_id=f"fv_{uuid4().hex[:12]}",
            created_at=created_at,
            source=source,
            chain=str(row.get("chain", "base")),
            pair=str(row.get("pair", "-")),
            strategy_id=str(row.get("strategy_id", "arbitrage")),
            mode="paper",
            estimated_net_edge_pct=_optional_str(row.get("estimated_edge_pct")),
            decision=status,
            reason=str(row.get("reason", "")),
            confidence_score=70 if status == "FILLED" else 0,
            rank_score=80 if status == "FILLED" else 10,
            risk_status="REJECTED" if status == "RISK_REJECTED" else "APPROVED" if status == "FILLED" else status,
            execution_quality=_optional_str(row.get("execution_quality")),
            slippage_bps=_optional_str(row.get("slippage_bps")),
            latency_ms=_optional_str(row.get("latency_ms")),
            realized_pnl_usd=_optional_str(row.get("realized_pnl_usd")),
            hour_utc=parsed.hour,
            weekday_utc=parsed.weekday(),
            tags=tags,
            raw=row,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _int(value: Any) -> int:
    try:
        if value is None:
            return 0
        return int(Decimal(str(value)))
    except Exception:
        return 0


def _parse_dt(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return datetime.utcnow()
