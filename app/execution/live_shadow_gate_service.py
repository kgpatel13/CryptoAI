from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


class LiveShadowGateService:
    """Evaluates whether a paper order would be eligible for live-style shadow review.

    This is the missing bridge between profitable paper fills and real-money
    readiness. It deliberately does not require wallet signing or transaction
    simulation; those come after a shadow-eligible candidate exists.
    """

    ELIGIBLE = "SHADOW_ELIGIBLE"
    PAPER_ONLY = "PAPER_ONLY"
    NOT_EVALUATED = "NOT_EVALUATED"

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.output_json = self.report_dir / "live_shadow_gate.json"
        self.output_md = self.report_dir / "live_shadow_gate.md"

    def evaluate_order(self, order: dict[str, Any]) -> dict[str, Any]:
        realism = self._read_json(self.report_dir / "execution_realism.json")
        provider = self._read_json(self.report_dir / "provider_monitor.json")
        cost = self._read_json(self.report_dir / "execution_cost_evidence.json")
        row = self._matching_realism_row(order, realism)
        blockers: list[dict[str, str]] = []

        if str(order.get("status", "")).upper() not in {"CLOSED", "FILLED", "PARTIAL_FILL"}:
            blockers.append(self._blocker("paper_order_not_filled", f"Paper status is {order.get('status', '-')}."))
        if not row:
            blockers.append(self._blocker("missing_execution_realism", "No matching execution-realism row exists for this paper order."))
        else:
            stress_net = self._decimal(row.get("stress_net_edge_pct"))
            if str(row.get("realism_status", "")).upper() != "SHADOW_READY":
                blockers.append(self._blocker("execution_realism_not_shadow_ready", f"Realism status is {row.get('realism_status', '-')}."))
            if stress_net <= Decimal("0"):
                blockers.append(self._blocker("stress_net_not_positive", f"Stress net edge is {stress_net}%."))

        if provider.get("overall_status") != "OK":
            blockers.append(self._blocker("provider_not_ok", f"Provider monitor is {provider.get('overall_status', 'MISSING')}."))
        if str(cost.get("confidence", "")).upper() != "HIGH":
            blockers.append(self._blocker("execution_cost_not_high", f"Execution-cost confidence is {cost.get('confidence', 'MISSING')}."))

        decision = self.ELIGIBLE if not blockers else self.PAPER_ONLY
        return {
            "checked_at": self._utc_now(),
            "paper_decision": "PAPER_BUY" if str(order.get("status", "")).upper() in {"CLOSED", "FILLED", "PARTIAL_FILL"} else "PAPER_SKIP",
            "live_shadow_decision": decision,
            "live_shadow_status": row.get("realism_status") if row else "MISSING",
            "live_shadow_reason": "Paper order passed live-style shadow gates." if decision == self.ELIGIBLE else "; ".join(row["detail"] for row in blockers),
            "live_shadow_stress_net_edge_pct": row.get("stress_net_edge_pct") if row else None,
            "live_shadow_blockers": blockers,
            "matched_realism": row,
        }

    def generate(self) -> dict[str, Any]:
        orders = self._read_jsonl(self.data_dir / "paper_orders.jsonl")
        recent = orders[-200:]
        rows = [self.evaluate_order(order) | {"order_id": order.get("order_id"), "pair": order.get("pair"), "status": order.get("status")} for order in recent]
        eligible = [row for row in rows if row.get("live_shadow_decision") == self.ELIGIBLE]
        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "overall_status": "SHADOW_ELIGIBLE_EVIDENCE" if eligible else "NO_SHADOW_ELIGIBLE_TRADES",
            "recent_order_count": len(rows),
            "shadow_eligible_count": len(eligible),
            "paper_only_count": len(rows) - len(eligible),
            "latest_decisions": rows[-50:],
            "notes": [
                "Live Shadow Gate is paper evidence only; it does not approve live trading.",
                "SHADOW_ELIGIBLE means the paper trade passed live-style evidence gates before wallet/transaction simulation.",
                "Full live trading still requires wallet preflight, exact calldata, eth_call simulation, live safety, and the reviewed live execution adapter.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _matching_realism_row(self, order: dict[str, Any], realism: dict[str, Any]) -> dict[str, Any]:
        rows = realism.get("opportunities", [])
        if not isinstance(rows, list):
            return {}
        chain = str(order.get("chain", "")).lower()
        pair = str(order.get("pair", ""))
        buy = str(order.get("buy_source", ""))
        sell = str(order.get("sell_source", ""))
        for row in rows:
            if (
                str(row.get("chain", "")).lower() == chain
                and str(row.get("pair", "")) == pair
                and str(row.get("buy_source", "")) == buy
                and str(row.get("sell_source", "")) == sell
            ):
                return dict(row)
        for row in rows:
            if str(row.get("chain", "")).lower() == chain and str(row.get("pair", "")) == pair:
                return dict(row)
        return {}

    @staticmethod
    def _blocker(name: str, detail: str) -> dict[str, str]:
        return {"name": name, "severity": "BLOCK", "detail": detail}

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
    def _read_jsonl(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
        return rows

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0")

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# Live Shadow Gate",
            "",
            f"Generated: `{payload['generated_at']}`",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Recent orders: `{payload['recent_order_count']}`",
            f"- Shadow eligible: `{payload['shadow_eligible_count']}`",
            f"- Paper only: `{payload['paper_only_count']}`",
            "",
            "## Latest Decisions",
            "",
            "| Order | Pair | Paper Status | Shadow Decision | Stress Net % | Reason |",
            "|---|---|---|---|---:|---|",
        ]
        for row in payload["latest_decisions"][-25:]:
            reason = str(row.get("live_shadow_reason", "-")).replace("|", "/")
            lines.append(
                f"| {row.get('order_id', '-')} | {row.get('pair', '-')} | {row.get('status', '-')} | "
                f"{row.get('live_shadow_decision', '-')} | {row.get('live_shadow_stress_net_edge_pct', '-')} | {reason} |"
            )
        if not payload["latest_decisions"]:
            lines.append("| - | - | - | - | - | No paper orders found. |")
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    payload = LiveShadowGateService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
