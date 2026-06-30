# Live Control Center

Generated: `2026-06-30T18:47:21Z`
- Overall status: `BLOCKED_LIVE_READINESS`
- Next action: `Continue paper/live-parity evidence; live readiness is not ready.`
- Next command: `python -m app.execution.live_readiness_checklist_service`
- Continuous monitor: `python -m app.execution.live_control_center_service --loop --interval 30`
- Continuous live trading: `NOT_AVAILABLE`

## Wallet

```json
{
  "address": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
  "chain": "base",
  "usdc_balance": "449.998478",
  "eth_balance": "0.024148469750380405",
  "allowance_sufficient": false,
  "approval_tx_available": true,
  "swap_tx_available": true,
  "smoke_usd": "5",
  "dex": "Uniswap V3",
  "router_address": "0x2626664c2603336E57B271c5C0b26F421741e481",
  "latest_block": 48027946
}
```

## Gates

```json
{
  "wallet_preflight": "WALLET_PREP_READY",
  "wallet_preflight_allowed": true,
  "live_readiness": "LIVE_REVIEW_NOT_READY",
  "live_review_ready": false,
  "transaction_simulation": "TX_SIMULATION_ACTION",
  "transaction_simulation_passed": false,
  "tiny_live_pilot": "LIVE_PILOT_BLOCKED",
  "tiny_live_blocked_checks": 3,
  "provider_monitor": "WATCH",
  "report_audit_blocking_findings": 0,
  "live_safety": "LIVE_BLOCKED"
}
```

## Blocking Checks

| Source | Check | Severity | Detail |
|---|---|---|---|
| tiny_live_pilot | live_readiness_ready | BLOCK | Live readiness checklist must be LIVE_REVIEW_READY. |
| tiny_live_pilot | transaction_simulation_passed | BLOCK | Transaction simulation must pass before live pilot. |
| tiny_live_pilot | provider_ok | BLOCK | Provider monitor must be OK. |

## Notes

- This control center is read-only and never sends live transactions.
- Refreshing safe reports can update wallet, provider, readiness, and simulation evidence, but cannot approve or swap.
- Continuous live arbitrage is not available until exact transaction simulation and live readiness pass.
- The current live-capable path is a manual tiny smoke pilot only.
