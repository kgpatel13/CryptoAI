# Live Control Center

Generated: `2026-07-01T03:57:12Z`
- Overall status: `BLOCKED_LIVE_READINESS`
- Next action: `Continue paper/live-parity evidence; live readiness is not ready.`
- Next command: `python -m app.execution.live_readiness_checklist_service`
- Continuous monitor: `python -m app.execution.live_control_center_service --loop --interval 30`
- Continuous live command: `python -m app.execution.live_control_center_service --live-loop --interval 30`
- Continuous live status: `NOT_AVAILABLE_UNTIL_LIVE_EXECUTOR`

## Wallet

```json
{
  "address": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
  "chain": "base",
  "usdc_balance": "449.998478",
  "eth_balance": "0.024147637570439412",
  "allowance_sufficient": true,
  "approval_tx_available": true,
  "swap_tx_available": true,
  "smoke_usd": "20",
  "dex": "Uniswap V3",
  "router_address": "0x2626664c2603336E57B271c5C0b26F421741e481",
  "latest_block": 48044442
}
```

## Gates

```json
{
  "wallet_preflight": "WALLET_PREP_READY",
  "wallet_preflight_allowed": true,
  "live_readiness": "LIVE_REVIEW_NOT_READY",
  "live_review_ready": false,
  "transaction_simulation": "TX_SIMULATION_READY",
  "transaction_simulation_passed": true,
  "tiny_live_pilot": "LIVE_PILOT_READY",
  "tiny_live_blocked_checks": 0,
  "provider_monitor": "OK",
  "report_audit_blocking_findings": 0,
  "live_safety": "LIVE_BLOCKED"
}
```

## Blocking Checks

| Source | Check | Severity | Detail |
|---|---|---|---|
| live_readiness | execution_realism_shadow_ready | ACTION | Execution realism must have shadow-ready evidence and zero live-ready approvals. |

## Notes

- This control center is read-only and never sends live transactions.
- Refreshing safe reports can update wallet, provider, readiness, and simulation evidence, but cannot approve or swap.
- The live-loop command exists as the future continuous entrypoint, but currently refuses autonomous execution.
- Continuous live arbitrage is not available until exact transaction simulation, live readiness, and a real live arbitrage executor pass review.
- The current live-capable path is a manual tiny smoke pilot only.
