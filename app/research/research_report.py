from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.research.feature_store import FeatureStoreService
from app.research.models import utc_now


class ResearchReportService:
    """Research dashboard service built on top of the Feature Store."""

    def __init__(self) -> None:
        self.report_dir = Path("reports")
        self.data_dir = Path("data")
        self.report_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

    def generate(self) -> dict[str, Any]:
        feature_summary = FeatureStoreService().build_from_runtime()
        recent = FeatureStoreService().recent_features(limit=25)
        payload = {
            "generated_at": utc_now(),
            "mode": "paper",
            "feature_store": feature_summary,
            "recent_features": recent,
            "mission_control": self._mission_control(feature_summary),
            "notes": [
                "Research metrics describe observed paper/simulated activity only.",
                "Do not infer live profitability from synthetic paper opportunities.",
                "The purpose of v4.0 is to accumulate research-grade data for later backtesting and AI ranking.",
            ],
        }
        (self.report_dir / "research_dashboard.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self._write_markdown(payload)
        return payload

    def _mission_control(self, summary: dict[str, Any]) -> dict[str, Any]:
        paper_report = self._read_json(self.report_dir / "paper_report.json")
        strategy_center = self._read_json(self.report_dir / "strategy_center.json")
        portfolio = paper_report.get("portfolio_analytics", {}) if paper_report else {}
        return {
            "portfolio_equity_usd": portfolio.get("equity_usd", "-"),
            "total_pnl_usd": portfolio.get("total_pnl_usd", "-"),
            "total_return_pct": portfolio.get("total_return_pct", "-"),
            "feature_vectors": summary.get("feature_count", 0),
            "tradeable_or_filled": summary.get("tradeable_or_filled_count", 0),
            "active_strategies": strategy_center.get("active_strategy_count", 0) if strategy_center else 0,
            "strategy_count": strategy_center.get("strategy_count", 0) if strategy_center else 0,
            "mode": "paper",
            "live_trading": "disabled",
        }

    def _write_markdown(self, payload: dict[str, Any]) -> None:
        mc = payload["mission_control"]
        fs = payload["feature_store"]
        lines = [
            "# CryptoAI Research Dashboard",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Mission Control",
            "",
            f"- Mode: `{mc['mode']}`",
            f"- Live trading: `{mc['live_trading']}`",
            f"- Portfolio equity USD: `${mc['portfolio_equity_usd']}`",
            f"- Total PnL USD: `${mc['total_pnl_usd']}`",
            f"- Total return %: `{mc['total_return_pct']}`",
            f"- Feature vectors: `{mc['feature_vectors']}`",
            f"- Tradeable or filled records: `{mc['tradeable_or_filled']}`",
            f"- Strategies: `{mc['active_strategies']}/{mc['strategy_count']} active`",
            "",
            "## Feature Store",
            "",
            f"- Feature vectors: `{fs['feature_count']}`",
            f"- Average net edge %: `{fs['avg_net_edge_pct']}`",
            f"- Max net edge %: `{fs['max_net_edge_pct']}`",
            "",
            "### Source Counts",
            "",
        ]
        for source, count in fs.get("source_counts", {}).items():
            lines.append(f"- `{source}`: {count}")
        lines += ["", "### Top Pairs", "", "| Pair | Count |", "|---|---:|"]
        for row in fs.get("top_pairs", []):
            lines.append(f"| {row.get('pair')} | {row.get('count')} |")
        lines += ["", "## Recent Features", "", "| Time | Source | Pair | Decision | Edge % | Reason |", "|---|---|---|---|---:|---|"]
        for row in payload.get("recent_features", [])[:20]:
            reason = str(row.get("reason", "")).replace("|", "/")[:140]
            lines.append(
                f"| {row.get('created_at', '-')} | {row.get('source', '-')} | {row.get('pair', '-')} | "
                f"{row.get('decision', '-')} | {row.get('estimated_net_edge_pct', '-')} | {reason} |"
            )
        lines += ["", "## Notes", ""]
        for note in payload["notes"]:
            lines.append(f"- {note}")
        (self.report_dir / "research_dashboard.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            return {}


def main() -> None:
    payload = ResearchReportService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
