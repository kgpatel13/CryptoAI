from __future__ import annotations

import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from app.strategy.strategy_service import StrategyService


class StrategyPerformanceService:
    """Builds strategy-level performance from paper orders and portfolio state."""

    def __init__(self, data_dir: Path | None = None, report_dir: Path | None = None) -> None:
        self.data_dir = data_dir or Path("data")
        self.report_dir = report_dir or Path("reports")
        self.orders_file = self.data_dir / "paper_orders.jsonl"
        self.portfolio_state_file = self.data_dir / "paper_portfolio_state.json"
        self.report_dir.mkdir(exist_ok=True)

    def snapshot(self) -> dict:
        orders = self._read_jsonl(self.orders_file)
        state = self._read_json(self.portfolio_state_file)
        positions = state.get("positions", []) if isinstance(state.get("positions", []), list) else []
        descriptors = StrategyService(data_dir=self.data_dir).strategy_descriptors()
        ranked_signals = self._read_jsonl(self.data_dir / "strategy_ranked_signals.jsonl")[-20:]
        signal_rows = self._read_jsonl(self.data_dir / "strategy_signals.jsonl")[-50:]

        by_strategy: dict[str, dict] = {}
        for descriptor in descriptors:
            by_strategy[descriptor["name"]] = {
                "strategy_id": descriptor["strategy_id"],
                "strategy_name": descriptor["name"],
                "enabled": descriptor["enabled"],
                "health": descriptor["health"],
                "weight": descriptor["weight"],
                "class_name": descriptor["class_name"],
                "registry_reason": descriptor["reason"],
                "orders": 0,
                "filled_orders": 0,
                "risk_rejected_orders": 0,
                "skipped_orders": 0,
                "open_positions": 0,
                "closed_positions": 0,
                "filled_notional_usd": Decimal("0"),
                "realized_pnl_usd": Decimal("0"),
                "wins": 0,
                "losses": 0,
                "avg_slippage_bps": None,
                "avg_latency_ms": None,
                "last_signal": None,
                "last_order": None,
            }

        for order in orders:
            strategy_name = str(order.get("strategy_name", "UNKNOWN"))
            row = by_strategy.setdefault(strategy_name, self._blank(strategy_name))
            status = str(order.get("status", "UNKNOWN")).upper()
            row["orders"] += 1
            row["last_order"] = order
            if status in {"FILLED", "PARTIAL_FILL"}:
                row["filled_orders"] += 1
                row["filled_notional_usd"] += self._decimal(order.get("filled_notional_usd", order.get("notional_usd", "0")))
            elif status == "RISK_REJECTED":
                row["risk_rejected_orders"] += 1
            elif status == "SKIPPED":
                row["skipped_orders"] += 1

        for pos in positions:
            strategy_name = str(pos.get("strategy_name", "UNKNOWN"))
            row = by_strategy.setdefault(strategy_name, self._blank(strategy_name))
            status = str(pos.get("status", "OPEN")).upper()
            pnl = self._decimal(pos.get("realized_pnl_usd", "0"))
            if status == "CLOSED":
                row["closed_positions"] += 1
                row["realized_pnl_usd"] += pnl
                if pnl > 0:
                    row["wins"] += 1
                elif pnl < 0:
                    row["losses"] += 1
            else:
                row["open_positions"] += 1

        by_name_signal: dict[str, dict] = {}
        for signal in signal_rows:
            by_name_signal[str(signal.get("strategy_name", "UNKNOWN"))] = signal
        for name, signal in by_name_signal.items():
            row = by_strategy.setdefault(name, self._blank(name))
            row["last_signal"] = signal

        for row in by_strategy.values():
            filled_orders = [
                order for order in orders
                if str(order.get("strategy_name")) == row["strategy_name"]
                and str(order.get("status", "")).upper() in {"FILLED", "PARTIAL_FILL"}
            ]
            row["avg_slippage_bps"] = self._avg(filled_orders, "slippage_bps")
            row["avg_latency_ms"] = self._avg(filled_orders, "latency_ms")
            closed = row["closed_positions"]
            row["win_rate_pct"] = self._fmt((Decimal(row["wins"]) / Decimal(closed) * Decimal("100")) if closed else None)
            row["filled_notional_usd"] = self._fmt(row["filled_notional_usd"])
            row["realized_pnl_usd"] = self._fmt(row["realized_pnl_usd"])

        active = [row for row in by_strategy.values() if row.get("enabled")]
        disabled = [row for row in by_strategy.values() if not row.get("enabled")]
        return {
            "mode": "paper",
            "strategy_count": len(by_strategy),
            "active_strategy_count": len(active),
            "disabled_strategy_count": len(disabled),
            "strategies": list(by_strategy.values()),
            "ranked_signals": ranked_signals,
            "notes": [
                "Strategies produce advisory signals only.",
                "Risk engine remains final authority before paper or live execution.",
                "Disabled research strategies are intentionally visible but non-tradeable.",
            ],
        }

    @staticmethod
    def _blank(strategy_name: str) -> dict:
        return {
            "strategy_id": "unknown",
            "strategy_name": strategy_name,
            "enabled": True,
            "health": "ACTIVE",
            "weight": "1.0",
            "class_name": "-",
            "registry_reason": "Discovered from existing orders.",
            "orders": 0,
            "filled_orders": 0,
            "risk_rejected_orders": 0,
            "skipped_orders": 0,
            "open_positions": 0,
            "closed_positions": 0,
            "filled_notional_usd": Decimal("0"),
            "realized_pnl_usd": Decimal("0"),
            "wins": 0,
            "losses": 0,
            "avg_slippage_bps": None,
            "avg_latency_ms": None,
            "last_signal": None,
            "last_order": None,
        }

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict]:
        if not path.exists():
            return []
        rows = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                if isinstance(row, dict):
                    rows.append(row)
            except Exception:
                continue
        return rows

    @staticmethod
    def _read_json(path: Path) -> dict:
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def _decimal(value) -> Decimal:
        try:
            return Decimal(str(value))
        except Exception:
            return Decimal("0")

    @classmethod
    def _avg(cls, rows: list[dict], key: str) -> str | None:
        values = [cls._decimal(row.get(key)) for row in rows if row.get(key) not in {None, "", "-"}]
        if not values:
            return None
        return cls._fmt(sum(values, Decimal("0")) / Decimal(len(values)))

    @staticmethod
    def _fmt(value: Decimal | None) -> str | None:
        if value is None:
            return None
        return str(value.quantize(Decimal("0.0000")))
