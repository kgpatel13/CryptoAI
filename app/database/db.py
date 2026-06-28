from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path("data") / "cryptoai.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
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

        conn.commit()
