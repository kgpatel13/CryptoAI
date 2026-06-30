from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.execution.trading_controls_service import TradingControlsService


class LiveSafetyReportService:
    """Evidence report for the future tiny-live pilot safety gate."""

    def __init__(self, report_dir: Path | str = "reports") -> None:
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.output_json = self.report_dir / "live_safety.json"
        self.output_md = self.report_dir / "live_safety.md"

    def generate(self) -> dict[str, Any]:
        status = TradingControlsService().get_status()
        checks = status.get("checks", [])
        blocked = [row for row in checks if not row.get("passed")]
        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "overall_status": "LIVE_BLOCKED" if blocked or not status.get("live_guard_allowed") else "LIVE_GUARD_PASSED",
            "live_guard_allowed": status.get("live_guard_allowed", False),
            "live_guard_reason": status.get("live_guard_reason", "Live trading is blocked by policy."),
            "max_live_wallet_usd": status.get("max_live_wallet_usd"),
            "max_live_trade_usd": status.get("max_live_trade_usd"),
            "max_daily_loss_usd": status.get("max_daily_loss_usd"),
            "blocked_check_count": len(blocked),
            "check_count": len(checks),
            "checks": checks,
            "runtime_status": {key: value for key, value in status.items() if key != "checks"},
            "notes": [
                "Live Safety is a design and evidence gate only; it does not send transactions.",
                "The current platform remains paper/shadow only.",
                "The first real-money pilot should use a dedicated wallet with $500 or less total capital and a smaller per-trade cap.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# Live Safety Report",
            "",
            f"Generated: `{payload['generated_at']}`",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Guard allowed: `{payload['live_guard_allowed']}`",
            f"- Guard reason: `{payload['live_guard_reason']}`",
            f"- Max live wallet USD: `{payload['max_live_wallet_usd']}`",
            f"- Max live trade USD: `{payload['max_live_trade_usd']}`",
            f"- Max daily loss USD: `{payload['max_daily_loss_usd']}`",
            f"- Blocked checks: `{payload['blocked_check_count']}` / `{payload['check_count']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "|---|---|---|",
        ]
        for row in payload["checks"]:
            lines.append(f"| {row['name']} | {row['severity']} | {row['detail']} |")
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    payload = LiveSafetyReportService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
