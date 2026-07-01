# Live Execution Engine

Generated: `2026-07-01T05:58:08Z`
- Overall status: `BLOCKED_LIVE_READINESS`
- Execution stage: `LIVE_READINESS`
- Can send approval: `False`
- Can send smoke swap: `False`
- Can run continuous live: `False`
- Next unblock step: `Live readiness is not ready: paper/live caps, cost confidence, realism, or audit evidence still need work.`

## Commands

```json
{
  "safe_live_monitor": "python -m app.execution.live_control_center_service --loop --interval 30",
  "live_execution_monitor": "python -m app.execution.live_execution_engine_service --loop --interval 30",
  "approval": null,
  "smoke_swap": null,
  "continuous_live": null
}
```

## Gates

```json
{
  "wallet_preflight_allowed": true,
  "live_review_ready": false,
  "transaction_simulation_passed": false,
  "provider_monitor_ok": true,
  "report_audit_clean": true,
  "tiny_live_pilot_ready": true,
  "allowance_sufficient": false,
  "approval_tx_available": true,
  "swap_tx_available": true,
  "live_safety_report_present": true,
  "live_control_center_present": true,
  "atomic_executor_ready": true,
  "atomic_route_simulation_passed": false
}
```

## Atomic Executor

```json
{
  "enabled": true,
  "address": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
  "address_valid": true,
  "reviewed": true,
  "adapter_selected": true,
  "ready": true
}
```

## Blockers

| Source | Check | Severity | Detail |
|---|---|---|---|
| live_execution_engine | live_review_ready | BLOCK | Live readiness is not ready: paper/live caps, cost confidence, realism, or audit evidence still need work. |
| live_execution_engine | transaction_simulation_passed | BLOCK | Exact calldata plus Base eth_call transaction simulation has not passed. |
| live_readiness | transaction_simulation_passed | ACTION | Transaction Simulation must pass exact calldata and eth_call checks before live review. |
| transaction_simulation | eth_call_simulation_passed | ACTION | Base eth_call simulation has not passed yet. |
| live_execution_engine | atomic_route_simulation_passed | ACTION | Run python -m app.execution.atomic_arbitrage_execution_service --generate until the atomic executor calldata eth_call passes. |

## Unblock Path

| Step | Name | Detail |
|---|---|---|
| 1 | Live-parity paper profile | Paper max trade and observed fills must stay at or below the live cap, e.g. $20 for the tiny pilot. |
| 2 | Execution evidence | Execution-cost confidence must reach HIGH and execution realism must produce SHADOW_READY opportunities. |
| 3 | Transaction simulation | Build exact Base calldata and pass eth_call for the selected USDC/WETH route. |
| 4 | Manual tiny live pilot | Run approval and one tiny smoke swap only when the engine shows READY_FOR_MANUAL_APPROVAL or READY_FOR_MANUAL_SMOKE_SWAP. |
| 5 | Atomic live executor | Deploy/review the single-transaction arbitrage executor, approve USDC to that executor, and pass the atomic executor eth_call report before continuous live trading is allowed. |

## Notes

- This engine is an execution-readiness state machine. It never signs, approves, swaps, or runs autonomous live arbitrage.
- Manual approval and manual smoke-swap commands appear only when all prerequisite reports permit them.
- Continuous live arbitrage requires a reviewed atomic executor path plus the live autopilot send flag; the current tiny pilot is one-leg smoke testing only.
- Paper profits do not guarantee live profits because live execution can fail from gas, slippage, MEV, reverts, nonce issues, and pool movement.
