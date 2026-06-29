from __future__ import annotations

import sqlite3
from pathlib import Path
from types import TracebackType


DB_PATH = Path("data") / "cryptoai.db"


class ManagedConnection(sqlite3.Connection):
    """SQLite connection that closes when used as a context manager.

    Python's built-in sqlite3.Connection context manager commits or rolls back,
    but it does not close the file handle on __exit__. On Windows that can leave
    temp test databases locked until garbage collection, which breaks cleanup.
    This subclass preserves normal sqlite transaction behavior and closes the
    connection deterministically when used as `with get_connection() as conn:`.
    """

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        result = super().__exit__(exc_type, exc_value, traceback)
        self.close()
        return result


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH, factory=ManagedConnection)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                event_type TEXT NOT NULL,
                source TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scheduler_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                status TEXT NOT NULL,
                paper_execution_enabled INTEGER NOT NULL,
                total_latency_ms REAL NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scheduler_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                step_name TEXT NOT NULL,
                status TEXT NOT NULL,
                items_processed INTEGER NOT NULL,
                latency_ms REAL NOT NULL,
                message TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS paper_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                chain TEXT NOT NULL,
                pair TEXT NOT NULL,
                side TEXT NOT NULL,
                notional_usd TEXT NOT NULL,
                estimated_edge_pct TEXT,
                simulated_fill_price_usd TEXT,
                simulated_quantity TEXT,
                status TEXT NOT NULL,
                reason TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                portfolio_name TEXT NOT NULL,
                cash_usd TEXT NOT NULL,
                holdings_value_usd TEXT NOT NULL,
                open_positions_value_usd TEXT NOT NULL,
                total_value_usd TEXT NOT NULL,
                realized_pnl_usd TEXT NOT NULL,
                unrealized_pnl_usd TEXT NOT NULL,
                total_pnl_usd TEXT NOT NULL,
                open_positions INTEGER NOT NULL,
                closed_positions INTEGER NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio_holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER NOT NULL,
                chain TEXT NOT NULL,
                symbol TEXT NOT NULL,
                quantity TEXT NOT NULL,
                avg_cost_usd TEXT NOT NULL,
                current_price_usd TEXT NOT NULL,
                market_value_usd TEXT NOT NULL,
                unrealized_pnl_usd TEXT NOT NULL,
                unrealized_pnl_pct TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER NOT NULL,
                position_id TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                chain TEXT NOT NULL,
                pair TEXT NOT NULL,
                base_symbol TEXT NOT NULL,
                quote_symbol TEXT NOT NULL,
                quantity TEXT NOT NULL,
                entry_price_usd TEXT NOT NULL,
                current_price_usd TEXT NOT NULL,
                notional_usd TEXT NOT NULL,
                unrealized_pnl_usd TEXT NOT NULL,
                unrealized_pnl_pct TEXT NOT NULL,
                status TEXT NOT NULL,
                opened_at TEXT NOT NULL
            )
            """
        )

        conn.commit()
