# CryptoAI v5.7 - 24/7 Paper Launch Settings

## Summary

v5.7 adds a validated paper trading settings layer for 24/7 operations. It lets the dashboard and CLI share one safe launch profile while preserving the current production cost buffer and live-trading lock.

## Added

- `config/paper_trading_settings.json` for dynamic paper launch parameters.
- `PaperSettingsService` for loading, validating, saving, and reporting paper settings.
- Dashboard `Paper Settings` page for editing loop cadence, ETH paper capital, max trade size, daily trade cap, ETH coverage gates, and risk limits.
- `--use-settings` support for `paper_autopilot`.
- `reports/paper_trading_settings.json` and `reports/paper_trading_settings.md`.
- Report Audit coverage for the paper settings reports.
- Regression tests for launch settings validation and safety locks.

## Safety Rules

- Live trading remains disabled.
- The production cost buffer remains `0.30%`.
- The paper BUY threshold remains `0.30%`.
- The `0.20%` buffer remains a research candidate only.
- The v5.7 launch scope is Base ETH routes: `WETH/USDC` and `USDC/WETH`.
- The `1.0` ETH value is a paper capital profile and future live ceiling, not an all-in per-trade size.

## Run

```bash
python -m app.operations.paper_settings_service
python -m app.automation.paper_autopilot --loop --use-settings
```

## Rollback

Remove `config/paper_trading_settings.json`, remove the v5.7 settings service and dashboard page, and use the previous explicit autopilot command:

```bash
python -m app.automation.paper_autopilot --loop --interval-seconds 300 --heartbeat-interval-seconds 60
```

