from __future__ import annotations

from pathlib import Path
import json
from datetime import datetime


class AnalyticsService:
    """Analytics service for saved and live research data."""

    def __init__(self) -> None:
        self.data_dir = Path("data")
        self.paper_file = self.data_dir / "paper_trades.jsonl"
        self.scan_file = self.data_dir / "scan_history.jsonl"

    def summary(self) -> dict:
        paper_rows = self.recent_paper_trades(limit=5000)
        scan_rows = self.recent_scans(limit=5000)

        total_paper_trades = len(paper_rows)
        total_scans = len(scan_rows)

        estimated_total_profit = 0.0
        profitable = 0

        for row in paper_rows:
            profit = self._safe_float(
                row.get("estimated_profit_usd")
                or row.get("net_profit_usd")
                or row.get("profit_usd")
                or row.get("estimated_net_profit_usd")
                or 0
            )
            estimated_total_profit += profit
            if profit > 0:
                profitable += 1

        win_rate = (profitable / total_paper_trades * 100) if total_paper_trades else 0.0

        return {
            "Total Scans": total_scans,
            "Paper Trades": total_paper_trades,
            "Profitable Trades": profitable,
            "Win Rate %": round(win_rate, 2),
            "Estimated P/L USD": round(estimated_total_profit, 6),
            "Last Updated": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }

    def recent_paper_trades(self, limit: int = 25) -> list[dict]:
        return self._read_jsonl(self.paper_file)[-limit:]

    def recent_scans(self, limit: int = 25) -> list[dict]:
        return self._read_jsonl(self.scan_file)[-limit:]

    def live_scanner_snapshot(self) -> list[dict]:
        """Fallback live snapshot when saved scan history is still empty."""
        try:
            from app.scanner.opportunity_scanner import OpportunityScanner

            rows = []
            for opp in OpportunityScanner().scan_base_gross_opportunities():
                rows.append(
                    {
                        "Chain": getattr(opp, "chain", "-"),
                        "Pair": getattr(opp, "pair", "-"),
                        "Buy DEX": getattr(opp, "best_buy_dex", "-"),
                        "Sell DEX": getattr(opp, "best_sell_dex", "-"),
                        "Buy Price": str(getattr(opp, "buy_price", "")),
                        "Sell Price": str(getattr(opp, "sell_price", "")),
                        "Gross Spread %": str(getattr(opp, "gross_spread_pct", "")),
                    }
                )
            return rows
        except Exception:
            return []

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict]:
        if not path.exists():
            return []

        rows: list[dict] = []
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        except Exception:
            return []

        return rows

    @staticmethod
    def _safe_float(value) -> float:
        try:
            return float(value)
        except Exception:
            return 0.0
