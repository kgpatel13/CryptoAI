# Live Control Center

Generated: `2026-07-01T18:22:40Z`
- Overall status: `BLOCKED_WALLET_PREFLIGHT`
- Next action: `Run wallet preflight in safe mode until it is WALLET_PREP_READY.`
- Next command: `python -m app.execution.wallet_preflight_service`
- Continuous monitor: `python -m app.execution.live_control_center_service --loop --interval 30`
- Continuous live command: `python -m app.execution.live_control_center_service --live-loop --interval 30`
- Continuous live status: `NOT_AVAILABLE_UNTIL_LIVE_EXECUTOR`

## Wallet

```json
{
  "address": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
  "chain": "base",
  "usdc_balance": "429.998478",
  "eth_balance": "0.024121785224852599",
  "allowance_sufficient": false,
  "approval_tx_available": true,
  "swap_tx_available": true,
  "smoke_usd": "5",
  "dex": "Uniswap V3",
  "router_address": "0x2626664c2603336E57B271c5C0b26F421741e481",
  "latest_block": 48070406
}
```

## Live Pilot Reconciliation

```json
{
  "overall_status": "NO_LIVE_PILOT_JOURNAL",
  "journal_count": 0,
  "approval_count": 0,
  "swap_count": 0,
  "failed_transaction_count": 0,
  "total_swap_usd": "0.0000",
  "total_gas_used": 0,
  "current_balances": {
    "ETH": "0.024121785224852599",
    "USDC": "429.998478",
    "WETH": "0.012568442636912582",
    "block_number": "48070405",
    "status": "OK"
  },
  "latest_swap": null
}
```

## Gates

```json
{
  "wallet_preflight": "WALLET_PREP_ACTION",
  "wallet_preflight_allowed": false,
  "live_readiness": "LIVE_REVIEW_NOT_READY",
  "live_review_ready": false,
  "transaction_simulation": "TX_SIMULATION_ACTION",
  "transaction_simulation_passed": false,
  "tiny_live_pilot": "LIVE_PILOT_BLOCKED",
  "tiny_live_blocked_checks": 2,
  "provider_monitor": "OK",
  "report_audit_blocking_findings": 14,
  "live_safety": "-",
  "live_pilot_reconciliation": "NO_LIVE_PILOT_JOURNAL"
}
```

## Blocking Checks

| Source | Check | Severity | Detail |
|---|---|---|---|
| tiny_live_pilot | wallet_preflight_ready | BLOCK | Wallet preflight must be ready. |
| tiny_live_pilot | report_audit_clean | BLOCK | Report audit has blocking findings. |

## Notes

- This control center is read-only and never sends live transactions.
- Refreshing safe reports can update wallet, provider, readiness, and simulation evidence, but cannot approve or swap.
- The live-loop command exists as the future continuous entrypoint, but currently refuses autonomous execution.
- Continuous live arbitrage is not available until exact transaction simulation, live readiness, and a real live arbitrage executor pass review.
- The current live-capable path is a manual tiny smoke pilot only.
