from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from app.strategy.performance_service import StrategyPerformanceService
from app.strategy.strategy_service import StrategyService


class StrategyCenterService:
    """Generates the v3.6 Strategy Center report."""

    def __init__(self, data_dir: Path | None = None, report_dir: Path | None = None) -> None:
        self.data_dir = data_dir or Path("data")
        self.report_dir = report_dir or Path("reports")
        self.report_dir.mkdir(exist_ok=True)

    def generate(self) -> dict:
        # Generate fresh signals/ranks so the report reflects current registry state.
        try:
            StrategyService(data_dir=self.data_dir).ranked_signals()
        except Exception:
            pass
        snapshot = StrategyPerformanceService(self.data_dir, self.report_dir).snapshot()
        report = {"generated_at": self._utc_now(), **snapshot}
        self._write_json(report)
        self._write_markdown(report)
        return report

    def _write_json(self, report: dict) -> None:
        (self.report_dir / "strategy_center.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    def _write_markdown(self, report: dict) -> None:
        lines = [
            "# CryptoAI Strategy Center",
            "",
            f"Generated: `{report['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Mode: `{report.get('mode', 'paper')}`",
            f"- Strategy count: `{report.get('strategy_count', 0)}`",
            f"- Active strategies: `{report.get('active_strategy_count', 0)}`",
            f"- Disabled strategies: `{report.get('disabled_strategy_count', 0)}`",
            "",
            "## Strategy Registry & Performance",
            "",
            "| Strategy | Enabled | Health | Weight | Orders | Filled | Risk Rejected | Open | Closed | Realized PnL | Win Rate | Avg Slip bps | Avg Latency ms |",
            "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for row in report.get("strategies", []):
            lines.append(
                f"| {row.get('strategy_name', '-')} | {row.get('enabled', '-')} | {row.get('health', '-')} | "
                f"{row.get('weight', '-')} | {row.get('orders', 0)} | {row.get('filled_orders', 0)} | "
                f"{row.get('risk_rejected_orders', 0)} | {row.get('open_positions', 0)} | {row.get('closed_positions', 0)} | "
                f"{row.get('realized_pnl_usd', '-')} | {row.get('win_rate_pct', '-')} | "
                f"{row.get('avg_slippage_bps', '-')} | {row.get('avg_latency_ms', '-')} |"
            )
        lines += ["", "## Ranked Signals", ""]
        ranked = report.get("ranked_signals", [])[-20:]
        if ranked:
            lines.append("| Time | Rank | Strategy | Pair | Action | Confidence | Edge % | Rank Score | Reason |")
            lines.append("|---|---:|---|---|---|---:|---:|---:|---|")
            for row in ranked:
                reason = str(row.get("reason", "-")).replace("|", "/")
                lines.append(
                    f"| {row.get('timestamp', '-')} | {row.get('rank', '-')} | {row.get('strategy_name', '-')} | "
                    f"{row.get('pair', '-')} | {row.get('action', '-')} | {row.get('confidence_score', '-')} | "
                    f"{row.get('expected_edge_pct', '-')} | {row.get('rank_score', '-')} | {reason} |"
                )
        else:
            lines.append("- No ranked signals yet. Run paper autopilot or strategy center once.")
        lines += ["", "## Notes", ""]
        for note in report.get("notes", []):
            lines.append(f"- {note}")
        (self.report_dir / "strategy_center.md").write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    report = StrategyCenterService().generate()
    print(json.dumps({"generated_at": report["generated_at"], "strategies": report.get("strategy_count", 0), "active": report.get("active_strategy_count", 0)}, indent=2))


if __name__ == "__main__":
    main()
