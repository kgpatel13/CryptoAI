# v5.21.3 - $20 Tiny-Live Parity Profile

## Summary

Raises the live-parity paper trade size from `$5` to `$20` while keeping the first live wallet ceiling and daily loss cap conservative.

## Changes

- Updates the `live_parity_500` paper profile to use `$20` min/max trade notional.
- Keeps the wallet ceiling at `$500`.
- Keeps the max daily loss cap at `$5`.
- Keeps live trading disabled by default.
- Keeps Base-only `WETH/USDC` and `USDC/WETH` scope.

## Why

The `$5` paper profile was useful for safety, but fixed Base gas made the live realism report too pessimistic because gas was about `1%` of the trade size. A `$20` tiny-live profile is still small enough for controlled testing, while giving the execution-realism gate a more realistic chance to evaluate net edge after gas.

## Verification

```powershell
python -m unittest tests.test_paper_settings_service
python -m unittest discover -s tests
```

## Commit Message

```text
v5.21.3 - Move tiny-live parity profile to $20 trades
```
