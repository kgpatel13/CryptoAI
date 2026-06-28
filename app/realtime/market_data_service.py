from __future__ import annotations

import asyncio
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal

from app.realtime.binance_ws import BinanceWebSocketClient
from app.realtime.models import MarketTick, RealtimeFeedStatus

try:
    from app.database.db import get_connection, initialize_database
except Exception:
    get_connection = None
    initialize_database = None

try:
    from app.events.event_service import EventBusService
    from app.events.models import EventType
except Exception:
    EventBusService = None
    EventType = None


class RealtimeMarketDataService:
    """Real-time market data orchestration service."""

    def __init__(self) -> None:
        self.binance = BinanceWebSocketClient()

    def snapshot(self, symbol: str = "ethusdt") -> dict:
        """Fetch one real-time tick and return a dashboard-friendly dict.

        This is intentionally one-shot for v2.1 so Streamlit does not spawn
        uncontrolled infinite loops.
        """
        try:
            tick = asyncio.run(self.binance.fetch_one_trade_tick(symbol=symbol))
            self._save_tick(tick)
            self._publish_tick(tick)
            return {
                "source": tick.source,
                "symbol": tick.symbol,
                "connected": True,
                "price_usd": str(tick.price_usd),
                "event_time": tick.event_time,
                "received_at": tick.received_at,
                "message": "Fetched one live WebSocket trade tick.",
            }
        except Exception as exc:
            return {
                "source": "binance_ws",
                "symbol": symbol.upper(),
                "connected": False,
                "price_usd": None,
                "event_time": None,
                "received_at": self._utc_now(),
                "message": str(exc),
            }

    def recent_ticks(self, limit: int = 50) -> list[dict]:
        if get_connection is None or initialize_database is None:
            return []

        try:
            initialize_database()
            self._ensure_tick_table()
            with get_connection() as conn:
                rows = conn.execute(
                    """
                    SELECT source, symbol, price_usd, event_time, received_at
                    FROM market_ticks
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
            return [dict(row) for row in rows]
        except Exception:
            return []

    def _save_tick(self, tick: MarketTick) -> None:
        if get_connection is None or initialize_database is None:
            return

        try:
            initialize_database()
            self._ensure_tick_table()
            with get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO market_ticks
                    (source, symbol, price_usd, event_time, received_at, raw_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tick.source,
                        tick.symbol,
                        str(tick.price_usd),
                        tick.event_time,
                        tick.received_at,
                        str(tick.raw),
                    ),
                )
                conn.commit()
        except Exception:
            return

    @staticmethod
    def _ensure_tick_table() -> None:
        if get_connection is None:
            return

        with get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS market_ticks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    price_usd TEXT NOT NULL,
                    event_time TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    raw_json TEXT NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def _publish_tick(tick: MarketTick) -> None:
        if EventBusService is None or EventType is None:
            return

        try:
            EventBusService().publish(
                event_type=EventType.SYSTEM,
                source="realtime_market_data",
                payload={
                    "message": "Realtime market tick received",
                    "symbol": tick.symbol,
                    "price_usd": str(tick.price_usd),
                    "event_time": tick.event_time,
                },
            )
        except Exception:
            return

    @staticmethod
    def _utc_now() -> str:
        return datetime.utcnow().isoformat(timespec="seconds") + "Z"
