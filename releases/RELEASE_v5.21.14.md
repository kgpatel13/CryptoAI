# v5.21.14 - Fail-Closed Atomic Live Adapter Seam

## Summary

Adds the reviewed-adapter boundary required before continuous live arbitrage can be enabled.

## Changes

- Added `AtomicLiveExecutionAdapter` as the future single-transaction live arbitrage execution seam.
- Added live autopilot adapter selection through `CRYPTOAI_LIVE_EXECUTION_ADAPTER=atomic`.
- Strengthened continuous-live readiness so a placeholder address is no longer enough.
- Requires atomic executor enabled flag, valid EVM executor address, explicit review flag, and reviewed adapter selection.
- Keeps live sends fail-closed until the reviewed atomic calldata builder/ABI is implemented.

## Safety Position

This release does not enable autonomous real-money arbitrage. It prevents accidental promotion from tiny smoke swaps to continuous live trading without a reviewed atomic route executor.

## Suggested Commit Message

`v5.21.14 - Add fail-closed atomic live adapter seam`
