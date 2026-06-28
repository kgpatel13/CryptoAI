# CryptoAI Real-time Market Data

CryptoAI v2.1 introduces a WebSocket-ready market data layer.

## Goal

Polling APIs are too slow for many trading strategies. Real-time feeds allow CryptoAI to react faster.

## Current implementation

- Binance public WebSocket-compatible client
- Safe fallback snapshot without requiring the dashboard to run a permanent async loop
- SQLite tick storage schema
- Event bus publishing support

## Future versions

- Long-running background worker
- Coinbase WebSocket
- Kraken WebSocket
- Bybit/OKX WebSocket
- DEX event listeners
- Order book depth
- Spread monitors
