# CryptoAI Trading Controls

CryptoAI v1.9 introduces safety guardrails before any future live trading module.

## Default posture

Live trading is disabled by default.

```env
CRYPTOAI_LIVE_TRADING_ENABLED=false
CRYPTOAI_PAPER_TRADING_ENABLED=true
CRYPTOAI_REQUIRE_MANUAL_CONFIRMATION=true
CRYPTOAI_MAX_LIVE_TRADE_USD=0
CRYPTOAI_MAX_DAILY_LOSS_USD=0
```

## Important

Do not add a private key to `.env` during research, paper trading, or backtesting.

## Future live trading requirements

Before live trading can be considered:

1. Scanner must be stable.
2. Backtesting must show repeatable edge.
3. Paper trading must show stable simulated performance.
4. Risk engine must enforce position and loss limits.
5. Execution engine must be separately reviewed.
6. Live guard must stay the final mandatory checkpoint.
