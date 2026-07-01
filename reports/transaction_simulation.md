# Transaction Simulation Report

Generated: `2026-07-01T01:29:36Z`
- Overall status: `TX_SIMULATION_ACTION`
- Transaction simulation passed: `False`
- Live trading approval: `False`
- Candidate pair: `WETH/USDC`
- Buy DEX: `Uniswap V2`
- Sell DEX: `Uniswap V3`
- Notional USD: `$500.0000`
- Calldata status: `BLOCKED`
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
| shadow_candidate_available | PASS | A BUY plus SHADOW_READY opportunity is available. |
| candidate_scope_allowed | PASS | Simulation candidate is Base USDC/WETH scope. |
| routers_configured | PASS | Both route routers are configured. |
| approved_live_dexes | ACTION | Simulation candidate uses a DEX outside the tiny-live allowlist. |
| live_trade_cap_configured | ACTION | Configure a tiny live trade cap before transaction simulation review. |
| exact_calldata_built | ACTION | Exact router calldata was not built for the selected candidate. |
| eth_call_simulation_passed | ACTION | Base eth_call simulation has not passed yet. |

## Intent

```json
{
  "status": "INTENT_READY",
  "chain": "base",
  "chain_id": 8453,
  "wallet_address": null,
  "pair": "WETH/USDC",
  "buy_dex": "Uniswap V2",
  "sell_dex": "Uniswap V3",
  "notional_usd": "500.0000",
  "max_slippage_bps": "50",
  "deadline_seconds": "120",
  "tokens": [
    {
      "symbol": "WETH",
      "address": "0x4200000000000000000000000000000000000006",
      "decimals": 18,
      "configured": true
    },
    {
      "symbol": "USDC",
      "address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "decimals": 6,
      "configured": true
    }
  ],
  "routers": [
    {
      "dex": "Uniswap V2",
      "router_address": "0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24",
      "dex_type": "v2",
      "configured": true
    },
    {
      "dex": "Uniswap V3",
      "router_address": "0x2626664c2603336E57B271c5C0b26F421741e481",
      "dex_type": "v3",
      "configured": true
    }
  ],
  "calldata_status": "BLOCKED",
  "eth_call_status": "NOT_RUN",
  "reason": "A valid isolated wallet address is required."
}
```

## Notes

- Transaction Simulation is evidence-only and never sends a transaction.
- The gate remains non-passing until exact calldata is built, Base eth_call simulation succeeds for both arbitrage legs, and the surrounding readiness checks pass.
- Private keys must remain absent while developing this report.
