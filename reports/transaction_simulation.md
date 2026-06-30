# Transaction Simulation Report

Generated: `2026-06-30T23:30:10Z`
- Overall status: `TX_SIMULATION_ACTION`
- Transaction simulation passed: `False`
- Live trading approval: `False`
- Candidate pair: `-`
- Buy DEX: `-`
- Sell DEX: `-`
- Notional USD: `$-`
- Calldata status: `NOT_BUILT`
- eth_call status: `NOT_RUN`
- Blocked checks: `0`
- Action checks: `6`

## Checks

| Check | Status | Detail |
|---|---|---|
| live_trading_disabled | PASS | Live trading is disabled. |
| kill_switch_enabled | PASS | Live kill switch is enabled. |
| private_key_absent | PASS | Private key is absent. |
| wallet_preflight_ready | ACTION | Wallet Preflight must be ready before transaction simulation review. |
| live_readiness_review_ready | ACTION | Live Readiness Checklist must be review-ready before transaction simulation can pass. |
| shadow_candidate_available | ACTION | No BUY plus SHADOW_READY opportunity is available for simulation. |
| candidate_scope_allowed | PASS | Simulation candidate is Base USDC/WETH scope. |
| routers_configured | PASS | Both route routers are configured. |
| approved_live_dexes | PASS | Simulation candidate DEXes are within the tiny-live allowlist. |
| live_trade_cap_configured | ACTION | Configure a tiny live trade cap before transaction simulation review. |
| exact_calldata_built | ACTION | Exact router calldata was not built for the selected candidate. |
| eth_call_simulation_passed | ACTION | Base eth_call simulation has not passed yet. |

## Intent

```json
{
  "status": "NO_CANDIDATE",
  "calldata_status": "NOT_BUILT",
  "eth_call_status": "NOT_RUN",
  "reason": "No latest BUY plus SHADOW_READY opportunity is available."
}
```

## Notes

- Transaction Simulation is evidence-only and never sends a transaction.
- The gate remains non-passing until exact calldata is built, Base eth_call simulation succeeds for both arbitrage legs, and the surrounding readiness checks pass.
- Private keys must remain absent while developing this report.
