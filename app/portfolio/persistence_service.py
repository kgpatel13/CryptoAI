from __future__ import annotations

from datetime import datetime

from app.database.db import get_connection, initialize_database
from app.portfolio.models import PortfolioSnapshot


class PortfolioPersistenceService:
    """SQLite persistence for simulated portfolio snapshots."""

    def __init__(self) -> None:
        initialize_database()

    def save_snapshot(self, snapshot: PortfolioSnapshot) -> int:
        created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"

        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO portfolio_snapshots
                (created_at, portfolio_name, cash_usd, holdings_value_usd,
                 open_positions_value_usd, total_value_usd, realized_pnl_usd,
                 unrealized_pnl_usd, total_pnl_usd, open_positions, closed_positions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    snapshot.portfolio_name,
                    str(snapshot.cash_usd),
                    str(snapshot.holdings_value_usd),
                    str(snapshot.open_positions_value_usd),
                    str(snapshot.total_value_usd),
                    str(snapshot.realized_pnl_usd),
                    str(snapshot.unrealized_pnl_usd),
                    str(snapshot.total_pnl_usd),
                    snapshot.open_positions,
                    snapshot.closed_positions,
                ),
            )
            snapshot_id = int(cur.lastrowid)

            for h in snapshot.holdings:
                conn.execute(
                    """
                    INSERT INTO portfolio_holdings
                    (snapshot_id, chain, symbol, quantity, avg_cost_usd,
                     current_price_usd, market_value_usd, unrealized_pnl_usd,
                     unrealized_pnl_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        snapshot_id,
                        h.chain,
                        h.symbol,
                        str(h.quantity),
                        str(h.avg_cost_usd),
                        str(h.current_price_usd),
                        str(h.market_value_usd),
                        str(h.unrealized_pnl_usd),
                        str(h.unrealized_pnl_pct),
                    ),
                )

            for p in snapshot.positions:
                conn.execute(
                    """
                    INSERT INTO portfolio_positions
                    (snapshot_id, position_id, strategy_name, chain, pair,
                     base_symbol, quote_symbol, quantity, entry_price_usd,
                     current_price_usd, notional_usd, unrealized_pnl_usd,
                     unrealized_pnl_pct, status, opened_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        snapshot_id,
                        p.position_id,
                        p.strategy_name,
                        p.chain,
                        p.pair,
                        p.base_symbol,
                        p.quote_symbol,
                        str(p.quantity),
                        str(p.entry_price_usd),
                        str(p.current_price_usd),
                        str(p.notional_usd),
                        str(p.unrealized_pnl_usd),
                        str(p.unrealized_pnl_pct),
                        p.status.value if hasattr(p.status, "value") else str(p.status),
                        p.opened_at,
                    ),
                )

            conn.commit()
            return snapshot_id

    def recent_snapshots(self, limit: int = 25) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, created_at, portfolio_name, cash_usd, holdings_value_usd,
                       open_positions_value_usd, total_value_usd, realized_pnl_usd,
                       unrealized_pnl_usd, total_pnl_usd, open_positions, closed_positions
                FROM portfolio_snapshots
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def latest_holdings(self, limit: int = 100) -> list[dict]:
        snapshot_id = self._latest_snapshot_id()
        if snapshot_id is None:
            return []

        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT chain, symbol, quantity, avg_cost_usd, current_price_usd,
                       market_value_usd, unrealized_pnl_usd, unrealized_pnl_pct
                FROM portfolio_holdings
                WHERE snapshot_id = ?
                LIMIT ?
                """,
                (snapshot_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def latest_positions(self, limit: int = 100) -> list[dict]:
        snapshot_id = self._latest_snapshot_id()
        if snapshot_id is None:
            return []

        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT position_id, strategy_name, chain, pair, base_symbol,
                       quote_symbol, quantity, entry_price_usd, current_price_usd,
                       notional_usd, unrealized_pnl_usd, unrealized_pnl_pct,
                       status, opened_at
                FROM portfolio_positions
                WHERE snapshot_id = ?
                LIMIT ?
                """,
                (snapshot_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _latest_snapshot_id() -> int | None:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT id FROM portfolio_snapshots
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
        return int(row["id"]) if row else None
