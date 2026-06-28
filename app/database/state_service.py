from __future__ import annotations

from app.database.db import get_connection, initialize_database


class StateService:
    """Read-only database summary service for dashboard."""

    def __init__(self) -> None:
        initialize_database()

    def summary(self) -> dict:
        with get_connection() as conn:
            return {
                "events": self._count(conn, "events"),
                "scheduler_runs": self._count(conn, "scheduler_runs"),
                "scheduler_steps": self._count(conn, "scheduler_steps"),
                "paper_orders": self._count(conn, "paper_orders"),
            }

    def recent_scheduler_runs(self, limit: int = 25) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT run_id, started_at, completed_at, status,
                       paper_execution_enabled, total_latency_ms
                FROM scheduler_runs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def recent_paper_orders(self, limit: int = 50) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT order_id, timestamp, strategy_name, chain, pair, side,
                       notional_usd, estimated_edge_pct, simulated_fill_price_usd,
                       simulated_quantity, status, reason
                FROM paper_orders
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _count(conn, table: str) -> int:
        return int(conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"])
