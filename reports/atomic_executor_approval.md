# Atomic Executor Approval

Generated: `2026-07-01T05:19:13Z`
- Mode: `plan`
- Overall status: `ATOMIC_APPROVAL_READY`
- Send attempted: `False`
- Blocked checks: `0` / `15`

## Checks

| Check | Status | Detail |
|---|---|---|
| approval_enabled | PASS | Atomic approval flag is enabled or mode is plan. |
| live_feature_flag | PASS | Live trading flag is enabled or mode is plan. |
| kill_switch_off_for_send | PASS | Kill switch is off for send mode or mode is plan. |
| manual_confirmation | PASS | Manual confirmation phrase is present or mode is plan. |
| private_key_available | PASS | Private key is available for send mode or not required. |
| private_key_matches_wallet | PASS | Private key matches isolated wallet or not required. |
| executor_enabled | PASS | Atomic executor enabled flag is set. |
| executor_reviewed | PASS | Atomic executor review flag is set. |
| plan_prepared | PASS | Atomic approval plan is prepared. |
| chain_id_base | PASS | Approval transaction is on Base or not yet prepared. |
| executor_deployed | PASS | Atomic executor bytecode exists. |
| approval_size_cap | PASS | Atomic approval amount is capped. |
| usdc_balance | PASS | USDC balance covers approval amount. |
| approval_needed | PASS | Approval is needed or mode is plan. |
| atomic_report_not_live_approval | PASS | Atomic report is evidence-only. |

## Approval Plan

```json
{
  "wallet_address": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
  "executor_address": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
  "approval_usd": "20",
  "amount_units": "20000000",
  "usdc_balance": "429.998478",
  "usdc_balance_units": "429998478",
  "usdc_allowance": "20",
  "usdc_allowance_units": "20000000",
  "allowance_sufficient": true,
  "chain_id": 8453,
  "latest_block": 48046903,
  "rpc_url": "https://base-rpc.publicnode.com",
  "executor_code_bytes": 6029,
  "approval_tx_available": true,
  "error": null
}
```

## Notes

- Atomic executor approval is a real Base transaction in approve mode.
- It approves a capped USDC amount to the atomic executor, not to a router.
- Approval does not start trading. Atomic route simulation must still pass before live autopilot can send arbitrage.
