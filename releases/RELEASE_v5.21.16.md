# v5.21.16 - Atomic Executor Approval Service

## Summary

Adds a dedicated capped USDC approval command for the deployed atomic arbitrage executor.

## Changes

- Added `AtomicExecutorApprovalService`.
- Added read-only plan mode and explicit approve mode.
- Approves USDC to `CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS`, not to a router.
- Requires:
  - `CRYPTOAI_ENABLE_ATOMIC_EXECUTOR_APPROVAL=true`,
  - `CRYPTOAI_LIVE_TRADING_ENABLED=true`,
  - `CRYPTOAI_LIVE_KILL_SWITCH_ENABLED=false`,
  - matching private key and isolated wallet,
  - `--confirm ATOMIC_EXECUTOR_APPROVED`.
- Writes approval evidence to:
  - `reports/atomic_executor_approval.json`
  - `reports/atomic_executor_approval.md`
  - `data/atomic_executor_approvals.jsonl`

## Safety Position

The approval service does not start live trading. It only prepares capped USDC allowance for the reviewed atomic executor.

## Suggested Commit Message

`v5.21.16 - Add atomic executor approval service`
