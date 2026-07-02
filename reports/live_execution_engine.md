# Live Execution Engine

Generated: `2026-07-02T00:56:55Z`
- Overall status: `BLOCKED_ATOMIC_ROUTE_SIMULATION`
- Execution stage: `ATOMIC_ARBITRAGE_ETH_CALL`
- Can send approval: `False`
- Can send smoke swap: `False`
- Can run continuous live: `False`
- Next unblock step: `Atomic route reconciliation status: LOSS_AFTER_ATOMIC_SIMULATION.`

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
  "wallet_preflight_allowed": false,
  "live_review_ready": false,
  "transaction_simulation_passed": false,
  "provider_monitor_ok": true,
  "report_audit_clean": false,
  "tiny_live_pilot_ready": false,
  "allowance_sufficient": false,
  "approval_tx_available": true,
  "swap_tx_available": true,
  "live_safety_report_present": false,
  "live_control_center_present": true,
  "atomic_executor_ready": true,
  "atomic_route_simulation_passed": false
}
```

## Atomic Executor

```json
{
  "enabled": true,
  "address": "0xDB8F6e57861F1aB65812A6B1d64133E244066B0c",
  "address_valid": true,
  "reviewed": true,
  "adapter_selected": true,
  "ready": true
}
```

## Blockers

| Source | Check | Severity | Detail |
|---|---|---|---|
| atomic_live_arbitrage | atomic_route_simulation_passed | BLOCK | Atomic route reconciliation status: LOSS_AFTER_ATOMIC_SIMULATION. |
| live_execution_engine | wallet_preflight_allowed | BLOCK | Wallet preflight is not ready for the isolated Base wallet. |
| live_execution_engine | live_review_ready | BLOCK | Live readiness is not ready: paper/live caps, cost confidence, realism, or audit evidence still need work. |
| live_execution_engine | report_audit_clean | BLOCK | Report audit still has blocking findings. |
| live_execution_engine | tiny_live_pilot_ready | BLOCK | Tiny live pilot plan is blocked. |
| live_execution_engine | transaction_or_atomic_simulation_passed | BLOCK | Either standalone transaction simulation or atomic executor eth_call simulation must pass. |
| live_control_center | wallet_preflight_ready | BLOCK | Wallet preflight must be ready. |
| live_control_center | report_audit_clean | BLOCK | Report audit has blocking findings. |
| live_readiness | report_audit_clean | BLOCK | Report Audit has blocking operational findings. |
| live_readiness | wallet_preflight_ready | ACTION | Wallet Preflight must be ready with an isolated public wallet and tiny-pilot caps. |
| live_readiness | transaction_simulation_passed | ACTION | Transaction Simulation must pass exact calldata and eth_call checks before live review. |
| live_readiness | live_safety_blocked | BLOCK | Live Safety must remain blocked during readiness review. |
| live_readiness | live_feature_off | BLOCK | Live feature flag must remain off until the final reviewed pilot. |
| live_readiness | kill_switch_on | BLOCK | Live and paper kill switches must remain on during readiness review. |
| live_readiness | private_key_absent | BLOCK | Private key must not be configured during readiness review. |
| live_readiness | paper_live_wallet_parity | ACTION | Paper capital should be > $0 and no larger than the configured live wallet ceiling. |
| transaction_simulation | live_trading_disabled | BLOCK | Live trading must remain disabled during transaction simulation development. |
| transaction_simulation | kill_switch_enabled | BLOCK | Live kill switch must remain enabled during transaction simulation development. |
| transaction_simulation | private_key_absent | BLOCK | Private key must not be configured for simulation report generation. |
| transaction_simulation | wallet_preflight_ready | ACTION | Wallet Preflight must be ready before transaction simulation review. |
| transaction_simulation | live_readiness_preconditions_ready | ACTION | Live Readiness Checklist has blocking checks that must be cleared before transaction simulation can pass. |
| transaction_simulation | eth_call_simulation_passed | ACTION | Base eth_call simulation has not passed yet. |
| tiny_live_pilot | wallet_preflight_ready | BLOCK | Wallet preflight must be ready. |
| tiny_live_pilot | report_audit_clean | BLOCK | Report audit has blocking findings. |
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
