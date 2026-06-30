# CryptoAI v5.17 - Transaction Simulation Evidence Gate

## Summary

v5.17 adds a transaction-simulation evidence report for the future tiny-live pilot.

The report finds the latest `BUY` plus `SHADOW_READY` paper opportunity, validates Base/USDC/WETH scope, verifies token and router metadata, and creates an unsigned simulation intent. It deliberately does not mark transaction simulation as passed until exact router calldata and Base `eth_call` simulation are implemented for both arbitrage legs.

This release does not enable live trading, store private keys, sign transactions, approve tokens, or send orders.

## Added

- `TransactionSimulationService`.
- `reports/transaction_simulation.json` and `reports/transaction_simulation.md`.
- Risk & Controls dashboard action to generate transaction simulation evidence.
- Reports tab and System Health coverage for transaction simulation outputs.
- Report Audit coverage for transaction simulation reports.
- Live Readiness Checklist now requires transaction simulation evidence before review-ready status.
- Regression tests proving:
  - a valid shadow candidate builds an intent but remains non-passing without calldata and `eth_call`,
  - no candidate is actionable but not falsely passing.

## Current Behavior

- `transaction_simulation_passed` is always `false`.
- `live_trading_approval` is always `false`.
- Exact calldata status remains `NOT_IMPLEMENTED`.
- Base `eth_call` status remains `NOT_RUN`.

## Still Locked

- Live trading remains disabled.
- Live kill switch remains ON during review.
- Private keys remain absent during transaction-simulation development.

## Next

- Configure the isolated wallet public address and tiny-live caps.
- Run live-parity paper trading under the `$50` max trade cap.
- Implement exact router calldata builders and `eth_call` simulation for approved Base routes only.
