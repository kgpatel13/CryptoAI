# Tiny Live Pilot

Generated: `2026-06-30T19:16:48Z`
- Mode: `plan`
- Overall status: `LIVE_PILOT_BLOCKED`
- Send attempted: `False`
- Blocked checks: `4` / `18`

## Checks

| Check | Status | Detail |
|---|---|---|
| pilot_enabled | PASS | Tiny live pilot flag is enabled or mode is plan. |
| live_feature_flag | PASS | Live trading flag is enabled or mode is plan. |
| kill_switch_off_for_send | PASS | Kill switch is off for send mode or mode is plan. |
| manual_confirmation | PASS | Manual confirmation phrase is present or mode is plan. |
| private_key_available | PASS | Private key is available for send mode or not required. |
| private_key_matches_wallet | PASS | Private key matches isolated live wallet or not required. |
| no_paper_autopilot_running | PASS | No paper autopilot process is running. |
| wallet_preflight_ready | PASS | Wallet preflight is ready. |
| live_readiness_ready | BLOCK | Live readiness checklist must be LIVE_REVIEW_READY. |
| transaction_simulation_passed | BLOCK | Transaction simulation must pass before live pilot. |
| report_audit_clean | BLOCK | Report audit has blocking findings. |
| provider_ok | BLOCK | Provider monitor must be OK. |
| pilot_plan_prepared | PASS | Tiny live pilot plan is prepared. |
| chain_id_base | PASS | Prepared transaction is on Base or not yet prepared. |
| smoke_size_cap | PASS | Smoke test size is within cap. |
| usdc_balance | PASS | USDC balance covers smoke-test amount. |
| allowance_for_swap | PASS | USDC allowance is sufficient or not needed for this mode. |
| atomic_arbitrage_blocked | PASS | One-leg smoke swap acknowledgement is present or not swapping. |

## Pilot Plan

```json
{
  "smoke_usd": "5",
  "wallet_address": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
  "dex": "Uniswap V3",
  "router_address": "0x2626664c2603336E57B271c5C0b26F421741e481",
  "chain_id": 8453,
  "latest_block": 48028830,
  "rpc_url": "https://base-rpc.publicnode.com",
  "usdc_balance": "449.998478",
  "eth_balance": "0.024148469750380405",
  "allowance_units": "0",
  "allowance_sufficient": false,
  "approval_tx_available": true,
  "swap_tx_available": true,
  "error": null
}
```

## Notes

- Tiny Live Pilot is a manual smoke-test harness, not an autonomous trading loop.
- It supports a capped one-leg USDC->WETH live test only; cross-DEX arbitrage still requires an atomic executor contract before production live trading.
- Never paste a private key into chat. Configure it only in your local environment when intentionally running approve/swap mode.
