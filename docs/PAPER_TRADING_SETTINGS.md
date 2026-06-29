# CryptoAI Paper Trading Settings

v5.7 adds a validated launch profile for continuous paper operation.

The goal is to let CryptoAI run 24/7 with clear parameters while keeping real-money execution locked behind evidence gates.

## Launch Command

```bash
python -m app.operations.paper_settings_service
python -m app.automation.paper_autopilot --loop --use-settings
```

The settings file is:

```text
config/paper_trading_settings.json
```

The generated evidence reports are:

```text
reports/paper_trading_settings.json
reports/paper_trading_settings.md
```

## Default Launch Profile

- Mode: paper only.
- Live trading: disabled.
- Asset focus: ETH.
- Chain: Base.
- Routes: `WETH/USDC`, `USDC/WETH`.
- DEXs: Uniswap V2, Aerodrome, and Uniswap V3.
- Initial paper capital: `1.0` ETH.
- ETH reference price: `$3500`.
- Max paper notional per trade: `$100`.
- Max daily paper trades: `24`.
- Loop interval: `300` seconds.
- Heartbeat interval: `60` seconds.

## Locked Safety Rules

- Production cost buffer must stay at least `0.30%`.
- Paper BUY threshold must stay at least `0.30%`.
- `0.20%` remains research-only evidence, not a paper execution threshold.
- Live trading must remain disabled.
- Duplicate position blocking and kill switch must stay enabled.
- Base ETH scope is the only approved v5.8 paper launch profile.

## About 1 ETH

The `1.0` ETH setting is a paper capital profile and future live capital ceiling. It is not an instruction to spend the full ETH balance on one trade.

For live trading later, the staged plan remains:

1. Paper evidence.
2. Shadow mode.
3. Very small live notional.
4. Gradual increase only if evidence supports it.

## No-Pause Operations

The autopilot can run continuously, but it should not trade every signal blindly. It should act only when quotes, provider health, report audit, ETH coverage, cost evidence, duplicate-position checks, cooldowns, and risk limits pass.

Risk gates are not downtime. They are the control system that keeps 24/7 operation from becoming uncontrolled execution.
