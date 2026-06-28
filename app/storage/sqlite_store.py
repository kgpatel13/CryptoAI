from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class SQLiteStore:
    """Small SQLite persistence layer for CryptoAI historical records."""

    def __init__(self, db_path: str | Path = Path("data") / "cryptoai.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS paper_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp_utc TEXT NOT NULL,
                    chain TEXT NOT NULL,
                    pair TEXT NOT NULL,
                    buy_dex TEXT NOT NULL,
                    sell_dex TEXT NOT NULL,
                    trade_size_usd REAL NOT NULL,
                    estimated_net_profit_usd REAL NOT NULL,
                    estimated_net_profit_pct REAL NOT NULL,
                    status TEXT NOT NULL,
                    reason TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_paper_trades_timestamp
                ON paper_trades(timestamp_utc)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_paper_trades_status
                ON paper_trades(status)
                """
            )

    def insert_paper_trade(self, row: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO paper_trades (
                    timestamp_utc,
                    chain,
                    pair,
                    buy_dex,
                    sell_dex,
                    trade_size_usd,
                    estimated_net_profit_usd,
                    estimated_net_profit_pct,
                    status,
                    reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["timestamp_utc"],
                    row["chain"],
                    row["pair"],
                    row["buy_dex"],
                    row["sell_dex"],
                    float(row["trade_size_usd"]),
                    float(row["estimated_net_profit_usd"]),
                    float(row["estimated_net_profit_pct"]),
                    row["status"],
                    row["reason"],
                ),
            )

    def get_recent_paper_trades(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    timestamp_utc,
                    chain,
                    pair,
                    buy_dex,
                    sell_dex,
                    trade_size_usd,
                    estimated_net_profit_usd,
                    estimated_net_profit_pct,
                    status,
                    reason
                FROM paper_trades
                ORDER BY timestamp_utc DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def get_paper_trade_summary(self) -> dict[str, Any]:
        with self._connect() as conn:
            summary = conn.execute(
                """
                SELECT
                    COUNT(*) AS total_scans,
                    SUM(CASE WHEN status = 'PAPER_EXECUTED' THEN 1 ELSE 0 END) AS paper_executed,
                    SUM(CASE WHEN status = 'PAPER_SKIPPED' THEN 1 ELSE 0 END) AS paper_skipped,
                    COALESCE(SUM(estimated_net_profit_usd), 0) AS total_estimated_net_profit_usd,
                    COALESCE(AVG(estimated_net_profit_usd), 0) AS avg_estimated_net_profit_usd,
                    COALESCE(MAX(estimated_net_profit_usd), 0) AS best_estimated_net_profit_usd,
                    COALESCE(MIN(estimated_net_profit_usd), 0) AS worst_estimated_net_profit_usd
                FROM paper_trades
                """
            ).fetchone()

        return dict(summary)

    def get_profit_by_pair(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    pair,
                    COUNT(*) AS observations,
                    COALESCE(SUM(estimated_net_profit_usd), 0) AS total_estimated_net_profit_usd,
                    COALESCE(AVG(estimated_net_profit_usd), 0) AS avg_estimated_net_profit_usd,
                    COALESCE(MAX(estimated_net_profit_usd), 0) AS best_estimated_net_profit_usd
                FROM paper_trades
                GROUP BY pair
                ORDER BY total_estimated_net_profit_usd DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]
