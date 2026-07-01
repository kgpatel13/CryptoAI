# v6.0.1 - Atomic Route Builder Diagnostics

## Summary

Adds detailed diagnostics to the atomic live arbitrage report so operators can distinguish market conditions from route-builder/calldata issues.

## Changes

- Added `route_diagnostics` to `atomic_live_arbitrage.json`.
- Reports whether the current blocker is:
  - no two-leg candidate,
  - no BUY signal,
  - realism filter rejection,
  - transaction-simulation selection issue,
  - atomic builder or eth_call failure.
- Includes latest opportunity details:
  - pair,
  - buy/sell DEX,
  - gross edge,
  - reported net edge,
  - stress net edge,
  - threshold,
  - confidence,
  - realism status,
  - rejection reasons.
- Includes failed transaction simulation checks.

## Safety Position

This release does not enable live trading. It improves operator evidence before live trading by making atomic route readiness explainable.

## Suggested Commit Message

`v6.0.1 - Add atomic route builder diagnostics`
