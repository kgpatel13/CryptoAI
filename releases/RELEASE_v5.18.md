# v5.18 - Exact Calldata and Base eth_call Simulation

## Summary

v5.18 turns the transaction simulation gate from a placeholder into an evidence engine. It builds exact unsigned router calldata for the approved Base USDC/WETH tiny-live scope and runs `eth_call` simulation through the existing RPC provider pool when a `BUY` plus `SHADOW_READY` candidate is available.

This release remains simulation-only. It does not sign transactions, submit transactions, request approvals, store private keys, or approve live trading.

## What Changed

- Added exact calldata generation for two-leg arbitrage simulation:
  - buy leg: `USDC -> WETH`
  - sell leg: `WETH -> USDC`
- Added router-specific calldata builders for:
  - Uniswap V3 SwapRouter02 `exactInputSingle`
  - Aerodrome-style `swapExactTokensForTokens`
  - Uniswap V2-style `swapExactTokensForTokens`
- Added Base `eth_call` simulation with:
  - chain-id verification
  - latest-block evidence
  - latency capture
  - pass/revert/fail status
  - redacted RPC URL evidence
- Added transaction simulation pass/revert regression coverage.

## Safety Constraints

- Live trading remains disabled.
- Live approval remains false.
- Private keys must remain absent.
- The kill switch remains expected on.
- `eth_call` is read/simulation-only and never broadcasts a transaction.

## Expected Baseline Behavior

On a fresh reset with no paper candidate, `transaction_simulation.json` should report:

- `overall_status=TX_SIMULATION_ACTION`
- `transaction_simulation_passed=false`
- `simulation_intent.status=NO_CANDIDATE`
- `calldata_status=NOT_BUILT`
- `eth_call_status=NOT_RUN`

After paper produces a `BUY` plus `SHADOW_READY` candidate, the report should build calldata and attempt Base `eth_call`. A revert is useful evidence and should remain non-passing until the route, wallet state, allowance, balance, and amount limits are ready.

## Tests

- `python -m unittest tests.test_transaction_simulation_service`

## Rollback

Rollback is limited to `app/execution/transaction_simulation_service.py`, `tests/test_transaction_simulation_service.py`, `CHANGELOG.md`, and this release note.
