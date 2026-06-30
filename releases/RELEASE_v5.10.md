# CryptoAI v5.10 - Unbounded Paper Lab Profile

## Summary

v5.10 adds a paper-only stress-test profile that removes the paper throttles Kamlesh wanted to relax for continuous 24/7 simulation.

Live trading remains disabled. The production buffer and paper BUY threshold remain locked at `0.30%`.

## What Changed

- Added `unbounded_paper_lab` as a launch profile.
- Set simulated paper capital to `10.0` ETH at a `$10000` reference value.
- Set the saved paper loop interval to `0`, meaning continuous scan after each cycle completes.
- Set max paper notional to `$100000` per trade.
- Added `full_available_cash` paper sizing so approved paper trades can request the configured max trade size and portfolio cash becomes the final cap.
- Allowed `0` to mean unlimited daily paper trades.
- Allowed `0` to mean unlimited open paper positions.
- Allowed `0` to mean no paper cooldown.
- Allowed `0` to mean disabled paper daily-loss stop.
- Allowed duplicate-position blocking, report-audit launch blocking, and critical-provider launch blocking to be toggled off for paper lab runs.
- Wired these settings into the runtime environment used by `paper_autopilot --use-settings`.
- Updated Portfolio Risk so zero-valued paper limits are honored.
- Added regression tests for unbounded settings and zero-limit risk behavior.

## Still Locked

- Live trading is disabled.
- Stale live quotes are blocked.
- Kill switch stays enabled.
- Production cost buffer cannot be below `0.30%`.
- Paper BUY threshold cannot be below `0.30%`.
- The active paper market remains Base ETH: `WETH/USDC` and `USDC/WETH`.

## Launch Command

```bash
python -m app.automation.paper_autopilot --loop --use-settings
```
