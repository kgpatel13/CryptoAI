from __future__ import annotations

import asyncio
import json
from datetime import datetime
from decimal import Decimal

try:
    import websockets
except Exception:  # pragma: no cover
    websockets = None

from app.realtime.models import MarketTick


class BinanceWebSocketClient:
    """Binance public WebSocket market data client.

    v2.1 provides the connector and a safe one-message fetch method.
    Later versions can run this continuously in a worker process.
    """

    BASE_URL = "wss://stream.binance.com:9443/ws"

    async def fetch_one_trade_tick(self, symbol: str = "ethusdt", timeout_seconds: int = 8) -> MarketTick:
        if websockets is None:
            raise RuntimeError("websockets package is not installed. Run: pip install websockets")

        stream = f"{symbol.lower()}@trade"
        url = f"{self.BASE_URL}/{stream}"

        async with websockets.connect(url, ping_interval=20, close_timeout=3) as websocket:
            raw_message = await asyncio.wait_for(websocket.recv(), timeout=timeout_seconds)
            payload = json.loads(raw_message)

        price = Decimal(str(payload.get("p", "0")))
        event_ms = payload.get("E")
        event_time = self._ms_to_iso(event_ms) if event_ms else self._utc_now()

        return MarketTick(
            source="binance_ws",
            symbol=symbol.upper(),
            price_usd=price,
            event_time=event_time,
            received_at=self._utc_now(),
            raw=payload,
        )

    @staticmethod
    def _ms_to_iso(ms: int) -> str:
        return datetime.utcfromtimestamp(int(ms) / 1000).isoformat(timespec="milliseconds") + "Z"

    @staticmethod
    def _utc_now() -> str:
        return datetime.utcnow().isoformat(timespec="seconds") + "Z"
