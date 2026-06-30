# CryptoAI v5.9 - Aggressive Paper Execution Profile

## Summary

v5.9 adds an explicit aggressive paper profile for faster evidence collection and larger simulated trade sizing.

This is still paper-only. Live trading remains disabled, the production buffer remains unchanged, and the paper BUY edge threshold remains locked at `0.30%`.

## Added

- `aggressive_paper` settings profile.
- Settings-driven runtime environment export for paper risk and execution services.
- Faster configurable paper loop floor: `15` seconds minimum.
- Saved aggressive paper profile:
  - Loop interval: `30` seconds.
  - Initial paper profile: `1.0` ETH at `$10000`.
  - Max paper notional: `$1000`.
  - Max daily paper trades: `200`.
  - Cooldown: `60` seconds.
  - Max paper daily loss: `$500`.
- Dashboard profile selector.
- Regression tests for aggressive runtime environment export.

## Still Locked

- Live trading stays disabled.
- Production buffer stays `0.30%`.
- Paper BUY threshold stays `0.30%`.
- Duplicate open-position protection stays enabled.
- Kill switch stays enabled.
- Base ETH scope remains the only approved paper launch scope.

## Run

Stop any existing worker with `Ctrl+C`, then restart:

```bash
python -m app.automation.paper_autopilot --loop --use-settings
```

## Rollback

Use the Paper Settings page and click `Reset To Safe Defaults`, or restore the conservative values:

- Loop interval: `300` seconds.
- ETH reference: `$3500`.
- Max paper notional: `$100`.
- Max daily trades: `24`.
- Cooldown: `900` seconds.
- Max daily loss: `$25`.

