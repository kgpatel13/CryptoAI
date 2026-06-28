from typing import Any

from app.storage.sqlite_store import SQLiteStore


class PaperAnalyticsService:
    def __init__(self) -> None:
        self.store = SQLiteStore()

    def summary(self) -> dict[str, Any]:
        return self.store.get_paper_trade_summary()

    def recent_trades(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.store.get_recent_paper_trades(limit=limit)

    def profit_by_pair(self) -> list[dict[str, Any]]:
        return self.store.get_profit_by_pair()
