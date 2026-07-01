# Live Control Center

Generated: `2026-07-01T05:58:08Z`
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
  "usdc_balance": "429.998478",
  "eth_balance": "0.024121785224852599",
  "allowance_sufficient": false,
  "approval_tx_available": true,
  "swap_tx_available": true,
  "smoke_usd": "5",
  "dex": "Uniswap V3",
  "router_address": "0x2626664c2603336E57B271c5C0b26F421741e481",
  "latest_block": 48048070
}
```

## Live Pilot Reconciliation

```json
{
  "overall_status": "LIVE_PILOT_RECONCILED",
  "journal_count": 2,
  "approval_count": 1,
  "swap_count": 1,
  "failed_transaction_count": 0,
  "total_swap_usd": "20.0000",
  "total_gas_used": 190594,
  "current_balances": {
    "ETH": "0.024121785224852599",
    "USDC": "429.998478",
    "WETH": "0.012568442636912582",
    "block_number": "48048070",
    "status": "OK"
  },
  "latest_swap": {
    "block_number": 48044575,
    "dex": "Uniswap V3",
    "gas_used": 135157,
    "mode": "swap",
    "receipt_status": 1,
    "smoke_usd": "20",
    "timestamp": "2026-07-01T04:01:37Z",
    "tx_hash": "376d68575e8e0b9adcea06a10f5ce484daa64f67f78ef241b93512b9ee2bb4ad",
    "wallet_address": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7"
  }
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
  "tiny_live_pilot": "LIVE_PILOT_READY",
  "tiny_live_blocked_checks": 0,
  "provider_monitor": "OK",
  "report_audit_blocking_findings": 0,
  "live_safety": "LIVE_BLOCKED",
  "live_pilot_reconciliation": "LIVE_PILOT_RECONCILED"
}
```

## Blocking Checks

| Source | Check | Severity | Detail |
|---|---|---|---|
| live_readiness | transaction_simulation_passed | ACTION | Transaction Simulation must pass exact calldata and eth_call checks before live review. |

## Notes

- This control center is read-only and never sends live transactions.
- Refreshing safe reports can update wallet, provider, readiness, and simulation evidence, but cannot approve or swap.
- The live-loop command exists as the future continuous entrypoint, but currently refuses autonomous execution.
- Continuous live arbitrage is not available until exact transaction simulation, live readiness, and a real live arbitrage executor pass review.
- The current live-capable path is a manual tiny smoke pilot only.
