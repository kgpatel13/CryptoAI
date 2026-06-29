from __future__ import annotations

from typing import Any


class DecisionExplainer:
    """Produces deterministic, auditable explanations for opportunity and order decisions."""

    def explain(self, record: dict[str, Any]) -> dict[str, Any]:
        decision = str(record.get("decision") or record.get("status") or "UNKNOWN").upper()
        reason = str(record.get("reason", ""))
        edge = record.get("estimated_net_edge_pct") or record.get("estimated_edge_pct")
        checks: list[dict[str, Any]] = []

        checks.append({"name": "mode", "passed": True, "detail": "Paper mode only; live execution disabled by default."})

        if edge is not None:
            try:
                checks.append({"name": "net_edge", "passed": float(edge) >= 0, "detail": f"Net/estimated edge: {edge}%"})
            except Exception:
                checks.append({"name": "net_edge", "passed": False, "detail": f"Could not parse edge: {edge}"})
        else:
            checks.append({"name": "net_edge", "passed": False, "detail": "No edge value available."})

        if "PAPER_SIMULATED" in reason:
            checks.append({"name": "live_tradeable", "passed": False, "detail": "Synthetic paper opportunity; not live-tradeable."})
        elif "No healthy quotes" in reason:
            checks.append({"name": "quote_health", "passed": False, "detail": "No healthy quotes were available."})
        else:
            checks.append({"name": "quote_health", "passed": True, "detail": "Quote data was sufficient for paper evaluation."})

        if "risk rejected" in reason.lower() or decision == "RISK_REJECTED":
            checks.append({"name": "risk_engine", "passed": False, "detail": reason})
        else:
            checks.append({"name": "risk_engine", "passed": True, "detail": "No risk rejection present in this record."})

        accepted = decision in {"BUY", "FILLED", "READY_FOR_PAPER"} and all(
            check["passed"] for check in checks if check["name"] not in {"live_tradeable"}
        )
        return {
            "decision": decision,
            "accepted_for_paper": accepted,
            "accepted_for_live": False,
            "summary": self._summary(decision, reason),
            "checks": checks,
            "live_safety_note": "Live trading must remain blocked for stale, simulated, degraded, or risk-rejected data.",
        }

    def _summary(self, decision: str, reason: str) -> str:
        if decision == "RISK_REJECTED":
            return "Rejected by portfolio risk controls."
        if decision == "FILLED":
            return "Paper order filled after passing paper-mode gates."
        if decision == "BUY":
            return "Candidate opportunity approved for paper evaluation."
        if decision == "SKIP":
            return "Opportunity skipped."
        return reason or "Decision explanation unavailable."
