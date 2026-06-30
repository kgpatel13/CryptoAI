# CryptoAI Paper Trading Settings

v5.10 adds an unbounded paper lab profile for continuous paper stress testing.

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

## Unbounded Paper Lab Profile

The saved runtime profile is currently `unbounded_paper_lab`.

- Mode: paper only.
- Live trading: disabled.
- Asset focus: ETH.
- Chain: Base.
- Routes: `WETH/USDC`, `USDC/WETH`.
- DEXs: Uniswap V2, Aerodrome, and Uniswap V3.
- Initial paper capital: `10.0` ETH.
- ETH reference price: `$10000`.
- Max paper notional per trade: `$100000`.
- Sizing mode: `full_available_cash`.
- Max daily paper trades: `0` for unlimited paper trades.
- Max open positions: `1`.
- Duplicate position blocking: enabled.
- Loop interval: `0` for continuous scan after each cycle completes.
- Heartbeat interval: `60` seconds.
- Cooldown: `0` for no cooldown.
- Max paper daily loss guard: `0` for disabled.
- Report audit and critical-provider launch blocks: disabled for paper lab stress testing.

`0` is a special paper-only value for loop interval, daily trades, open positions, cooldown, and daily-loss stop. It means continuous, unlimited, or disabled depending on the field.

`full_available_cash` means portfolio risk sizes an approved paper trade from the current available simulated cash balance. No leverage or margin is implied.

Arbitrage paper trades are atomic round trips. They must close immediately and should normally leave open positions at `0`.

## Standard Safe Defaults

Resetting the Paper Settings page restores the safer default profile.

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
- Kill switch must stay enabled.
- Base ETH scope is the only approved v5.10 paper launch profile.

## About Paper ETH Capital

The ETH setting is simulated paper capital. It is not an instruction to spend a full real ETH balance on one trade.

For live trading later, the staged plan remains:

1. Paper evidence.
2. Shadow mode.
3. Very small live notional.
4. Gradual increase only if evidence supports it.

## No-Pause Operations

The autopilot can run continuously, but it should not trade every signal blindly. It should act only when quotes, provider health, report audit, ETH coverage, cost evidence, duplicate-position checks, cooldowns, and risk limits pass.

In unbounded paper lab mode, paper throttles are intentionally relaxed so the system can generate higher-volume evidence. Live trading still requires the staged live-readiness process.

## Settings Enforcement

When launched with `--use-settings`, the worker exports paper settings into the Risk and Paper Execution services for that process:

- Paper capital USD.
- Default and max paper notional.
- Risk-per-trade and cash-usage percentages.
- Max daily paper trades.
- Max open positions.
- Cooldown and duplicate signal window.
- Max paper daily loss.
- Paper BUY edge threshold.
- Paper sizing mode.
- Duplicate-position blocking flag.
- Token and chain exposure caps set to the full paper portfolio for the process.
