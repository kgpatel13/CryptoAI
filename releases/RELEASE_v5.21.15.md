# v5.21.15 - Atomic Live Arbitrage Executor Path

## Summary

Adds the final atomic-arbitrage execution path required before continuous live trading can be considered.

## Changes

- Added `contracts/CryptoAIAtomicArbitrageExecutor.sol`.
- Added `AtomicArbitrageExecutionService` to build one executor transaction from a two-leg Base USDC/WETH route.
- Rebuilds swap leg calldata with the executor contract as recipient so profit can be checked inside one transaction.
- Adds atomic executor `eth_call` evidence report:
  - `reports/atomic_live_arbitrage.json`
  - `reports/atomic_live_arbitrage.md`
- Updates the live adapter to require the atomic route report before sending.
- Adds a second explicit send flag: `CRYPTOAI_ATOMIC_EXECUTOR_SEND_ENABLED=true`.
- Updates live execution readiness so continuous live requires:
  - reviewed atomic executor config,
  - passing router calldata simulation,
  - passing atomic executor eth_call simulation.

## Safety Position

This release provides the software path for atomic live arbitrage, but it still requires an externally deployed and reviewed executor contract address. The system remains blocked until the exact deployed executor transaction passes `eth_call`.

## Suggested Commit Message

`v5.21.15 - Add atomic live arbitrage executor path`
