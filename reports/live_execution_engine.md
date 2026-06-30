# Live Execution Engine

Generated: `2026-06-30T19:03:26Z`
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
  "provider_monitor_ok": false,
  "report_audit_clean": true,
  "tiny_live_pilot_ready": false,
  "allowance_sufficient": false,
  "approval_tx_available": false,
  "swap_tx_available": false,
  "live_safety_report_present": true,
  "live_control_center_present": true,
  "atomic_executor_ready": false
}
```

## Blockers

| Source | Check | Severity | Detail |
|---|---|---|---|
| live_execution_engine | live_review_ready | BLOCK | Live readiness is not ready: paper/live caps, cost confidence, realism, or audit evidence still need work. |
| live_execution_engine | transaction_simulation_passed | BLOCK | Exact calldata plus Base eth_call transaction simulation has not passed. |
| live_execution_engine | provider_monitor_ok | BLOCK | Provider monitor must be OK before any live send. |
| live_execution_engine | tiny_live_pilot_ready | BLOCK | Tiny live pilot plan is blocked. |
| live_control_center | live_readiness_ready | BLOCK | Live readiness checklist must be LIVE_REVIEW_READY. |
| live_control_center | transaction_simulation_passed | BLOCK | Transaction simulation must pass before live pilot. |
| live_control_center | provider_ok | BLOCK | Provider monitor must be OK. |
| live_control_center | pilot_plan_prepared | BLOCK | Missing CRYPTOAI_LIVE_WALLET_ADDRESS. |
| live_readiness | paper_shadow_review_ready | ACTION | Paper Run Review must reach REVIEW_READY before live-pilot review. |
| live_readiness | provider_health_ok | BLOCK | Provider Monitor must be OK. |
| live_readiness | execution_cost_confidence | ACTION | Execution-cost evidence confidence must be HIGH. |
| live_readiness | execution_realism_shadow_ready | ACTION | Execution realism must have shadow-ready evidence and zero live-ready approvals. |
| live_readiness | transaction_simulation_passed | ACTION | Transaction Simulation must pass exact calldata and eth_call checks before live review. |
| live_readiness | paper_live_trade_cap_parity | ACTION | Paper max notional and observed fills should be no larger than the configured live trade cap. |
| live_readiness | paper_live_daily_loss_parity | ACTION | Paper daily loss cap should be > $0 and no larger than the configured live daily loss cap. |
| transaction_simulation | live_readiness_review_ready | ACTION | Live Readiness Checklist must be review-ready before transaction simulation can pass. |
| transaction_simulation | shadow_candidate_available | ACTION | No BUY plus SHADOW_READY opportunity is available for simulation. |
| transaction_simulation | exact_calldata_built | ACTION | Exact router calldata was not built for the selected candidate. |
| transaction_simulation | eth_call_simulation_passed | ACTION | Base eth_call simulation has not passed yet. |
| tiny_live_pilot | live_readiness_ready | BLOCK | Live readiness checklist must be LIVE_REVIEW_READY. |
| tiny_live_pilot | transaction_simulation_passed | BLOCK | Transaction simulation must pass before live pilot. |
| tiny_live_pilot | provider_ok | BLOCK | Provider monitor must be OK. |
| tiny_live_pilot | pilot_plan_prepared | BLOCK | Missing CRYPTOAI_LIVE_WALLET_ADDRESS. |
| live_execution_engine | atomic_executor_ready | ACTION | Continuous live arbitrage is blocked until an atomic route executor or equivalent single-transaction execution path is implemented and reviewed. |

## Unblock Path

| Step | Name | Detail |
|---|---|---|
| 1 | Live-parity paper profile | Paper max trade and observed fills must stay at or below the live cap, e.g. $5 for the tiny pilot. |
| 2 | Execution evidence | Execution-cost confidence must reach HIGH and execution realism must produce SHADOW_READY opportunities. |
| 3 | Transaction simulation | Build exact Base calldata and pass eth_call for the selected USDC/WETH route. |
| 4 | Manual tiny live pilot | Run approval and one tiny smoke swap only when the engine shows READY_FOR_MANUAL_APPROVAL or READY_FOR_MANUAL_SMOKE_SWAP. |
| 5 | Atomic live executor | Implement and review single-transaction arbitrage execution before continuous live trading is allowed. |

## Notes

- This engine is an execution-readiness state machine. It never signs, approves, swaps, or runs autonomous live arbitrage.
- Manual approval and manual smoke-swap commands appear only when all prerequisite reports permit them.
- Continuous live arbitrage requires a reviewed atomic executor path; the current tiny pilot is one-leg smoke testing only.
- Paper profits do not guarantee live profits because live execution can fail from gas, slippage, MEV, reverts, nonce issues, and pool movement.
