from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from datetime import datetime


@dataclass(frozen=True)
class AnalyticsSummary:
    total_scans: int
    total_paper_trades: int
    profitable_paper_trades: int
    estimated_total_profit_usd: float
    last_updated: str


class AnalyticsService:
    """Lightweight analytics service.

    This version is intentionally file-based so the dashboard works without a
    database server. Later we will replace or supplement this with SQLite/Postgres.
    """

    def __init__(self) -> None:
        self.data_dir = Path("data")
        self.paper_file = self.data_dir / "paper_trades.jsonl"
        self.scan_file = self.data_dir / "scan_history.jsonl"

    def summary(self) -> dict:
        paper_rows = self._read_jsonl(self.paper_file)
        scan_rows = self._read_jsonl(self.scan_file)

        total_paper_trades = len(paper_rows)

        estimated_total_profit = 0.0
        profitable = 0

        for row in paper_rows:
            profit = self._safe_float(
                row.get("estimated_profit_usd")
                or row.get("net_profit_usd")
                or row.get("profit_usd")
                or 0
            )
            estimated_total_profit += profit
            if profit > 0:
                profitable += 1

        return {
            "total_scans": len(scan_rows),
            "total_paper_trades": total_paper_trades,
            "profitable_paper_trades": profitable,
            "estimated_total_profit_usd": round(estimated_total_profit, 6),
            "last_updated": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "storage": "file-based JSONL",
        }

    def recent_paper_trades(self, limit: int = 25) -> list[dict]:
        return self._read_jsonl(self.paper_file)[-limit:]

    def recent_scans(self, limit: int = 25) -> list[dict]:
        return self._read_jsonl(self.scan_file)[-limit:]

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
