# Transaction Simulation Report

Generated: `2026-07-01T05:30:04Z`
- Overall status: `TX_SIMULATION_ACTION`
- Transaction simulation passed: `False`
- Live trading approval: `False`
- Candidate pair: `USDC/WETH`
- Buy DEX: `Uniswap V3`
- Sell DEX: `None`
- Notional USD: `$20.0000`
- Calldata status: `BUILT`
- eth_call status: `REVERT`
- Blocked checks: `0`
- Action checks: `1`

## Checks

| Check | Status | Detail |
|---|---|---|
| live_trading_disabled | PASS | Live trading is disabled. |
| kill_switch_enabled | PASS | Live kill switch is enabled. |
| private_key_absent | PASS | Private key is absent. |
| wallet_preflight_ready | PASS | Wallet Preflight is ready. |
| live_readiness_preconditions_ready | PASS | Live Readiness Checklist has no blocking checks. |
| shadow_candidate_available | PASS | A simulation route is available. |
| candidate_scope_allowed | PASS | Simulation candidate is Base USDC/WETH scope. |
| routers_configured | PASS | Both route routers are configured. |
| approved_live_dexes | PASS | Simulation candidate DEXes are within the tiny-live allowlist. |
| live_trade_cap_configured | PASS | Tiny live trade cap is configured. |
| exact_calldata_built | PASS | Exact router calldata is built. |
| eth_call_simulation_passed | ACTION | Base eth_call simulation has not passed yet. |

## Intent

```json
{
  "status": "SIMULATION_ATTEMPTED",
  "simulation_type": "TINY_LIVE_SMOKE",
  "chain": "base",
  "chain_id": 8453,
  "wallet_address": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
  "pair": "USDC/WETH",
  "buy_dex": "Uniswap V3",
  "sell_dex": null,
  "notional_usd": "20.0000",
  "max_slippage_bps": "50",
  "deadline_seconds": "120",
  "tokens": [
    {
      "symbol": "USDC",
      "address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "decimals": 6,
      "configured": true
    },
    {
      "symbol": "WETH",
      "address": "0x4200000000000000000000000000000000000006",
      "decimals": 18,
      "configured": true
    }
  ],
  "routers": [
    {
      "dex": "Uniswap V3",
      "router_address": "0x2626664c2603336E57B271c5C0b26F421741e481",
      "dex_type": "v3",
      "configured": true
    }
  ],
  "calldata_status": "BUILT",
  "eth_call_status": "REVERT",
  "reason": "No approved two-leg arbitrage candidate is available; simulating the configured one-leg tiny live smoke swap.",
  "swap_legs": [
    {
      "leg": "TINY_LIVE_SMOKE_SWAP",
      "dex": "Uniswap V3",
      "router_type": "v3",
      "router_address": "0x2626664c2603336E57B271c5C0b26F421741e481",
      "token_in": "USDC",
      "token_in_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "token_out": "WETH",
      "token_out_address": "0x4200000000000000000000000000000000000006",
      "amount_in_units": "20000000",
      "amount_out_min_units": "1",
      "deadline": 1782883924,
      "calldata": "0x04e45aaf000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913000000000000000000000000420000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000001f40000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a70000000000000000000000000000000000000000000000000000000001312d0000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000",
      "calldata_bytes": 228,
      "eth_call": {
        "from": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
        "to": "0x2626664c2603336E57B271c5C0b26F421741e481",
        "data": "0x04e45aaf000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913000000000000000000000000420000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000001f40000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a70000000000000000000000000000000000000000000000000000000001312d0000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000",
        "value": "0x0"
      },
      "route_metadata": {
        "fee_tier": 500,
        "sqrt_price_limit_x96": 0
      },
      "eth_call_result": {
        "status": "REVERT",
        "rpc": "Base:rpc1:https://base-rpc.publicnode.com",
        "rpc_url": "https://base-rpc.publicnode.com",
        "latency_ms": 352.74,
        "error": "ContractLogicError: ('execution reverted: STF', '0x08c379a0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000035354460000000000000000000000000000000000000000000000000000000000')"
      }
    }
  ],
  "eth_call_summary": {
    "leg_count": 1,
    "pass_count": 0,
    "revert_count": 1,
    "fail_count": 0
  }
}
```

## Notes

- Transaction Simulation is evidence-only and never sends a transaction.
- The gate remains non-passing until exact calldata is built, Base eth_call simulation succeeds for both arbitrage legs, and the surrounding readiness checks pass.
- Private keys must remain absent while developing this report.
