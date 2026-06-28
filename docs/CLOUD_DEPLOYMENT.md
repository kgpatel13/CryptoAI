# CryptoAI Cloud Deployment

CryptoAI v2.3 adds cloud deployment foundations for paper trading.

## Recommended free/low-cost setup

### Dashboard
Use Streamlit Community Cloud or Render free web service for the dashboard.

### Paper autopilot worker
Use Render worker/cron or a low-cost always-on service. Free web services can sleep, so they are not ideal for reliable 24/7 loops.

## Environment variables

Safe paper-trading defaults:

```env
CRYPTOAI_LIVE_TRADING_ENABLED=false
CRYPTOAI_PAPER_TRADING_ENABLED=true
CRYPTOAI_REQUIRE_MANUAL_CONFIRMATION=true
CRYPTOAI_MAX_LIVE_TRADE_USD=0
CRYPTOAI_MAX_DAILY_LOSS_USD=0
CRYPTOAI_AUTOPILOT_INTERVAL_SECONDS=300
CRYPTOAI_AUTOPILOT_ENABLE_PAPER_EXECUTION=true
```

## 1 ETH paper mode

This does not require real ETH. You can simulate a paper portfolio sized around 1 ETH by setting:

```env
CRYPTOAI_PAPER_STARTING_ETH=1
```

The current engine still treats portfolio values in USD internally. Future versions can add full multi-asset ledgers.

## Do not deploy secrets yet

Do not set:

```env
CRYPTOAI_PRIVATE_KEY=
```

until live trading code exists, has been reviewed, and has strong safeguards.
