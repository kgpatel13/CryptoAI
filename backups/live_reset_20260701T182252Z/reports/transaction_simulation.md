# Transaction Simulation Report

Generated: `2026-07-01T18:22:36Z`
- Overall status: `TX_SIMULATION_ACTION`
- Transaction simulation passed: `False`
- Live trading approval: `False`
- Candidate pair: `WETH/USDC`
- Buy DEX: `Uniswap V2`
- Sell DEX: `Uniswap V3`
- Notional USD: `$5.0000`
- Calldata status: `BUILT`
- eth_call status: `REVERT`
- Blocked checks: `3`
- Action checks: `3`

## Checks

| Check | Status | Detail |
|---|---|---|
| live_trading_disabled | BLOCK | Live trading must remain disabled during transaction simulation development. |
| kill_switch_enabled | BLOCK | Live kill switch must remain enabled during transaction simulation development. |
| private_key_absent | BLOCK | Private key must not be configured for simulation report generation. |
| wallet_preflight_ready | ACTION | Wallet Preflight must be ready before transaction simulation review. |
| live_readiness_preconditions_ready | ACTION | Live Readiness Checklist has blocking checks that must be cleared before transaction simulation can pass. |
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
  "chain": "base",
  "chain_id": 8453,
  "wallet_address": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
  "pair": "WETH/USDC",
  "buy_dex": "Uniswap V2",
  "sell_dex": "Uniswap V3",
  "notional_usd": "5.0000",
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
  "calldata_status": "BUILT",
  "eth_call_status": "REVERT",
  "selection_mode": "TINY_LIVE_REALISM",
  "selection_reason": "Selected WATCH candidate because Tiny Live Realism Mode is enabled and stress edge is above the configured tiny-live minimum.",
  "tiny_live_realism_enabled": true,
  "source_decision": "WATCH",
  "realism_status": "WATCH_ONLY",
  "buy_price": "1609.23061",
  "sell_price": "1618.16367",
  "gross_edge_pct": "0.5551",
  "stress_net_edge_pct": "0.1770",
  "swap_legs": [
    {
      "leg": "BUY_WETH",
      "dex": "Uniswap V2",
      "router_type": "v2",
      "router_address": "0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24",
      "token_in": "USDC",
      "token_in_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "token_out": "WETH",
      "token_out_address": "0x4200000000000000000000000000000000000006",
      "amount_in_units": "5000000",
      "amount_out_min_units": "3091539502843535",
      "deadline": 1782930275,
      "calldata": "0x38ed173900000000000000000000000000000000000000000000000000000000004c4b40000000000000000000000000000000000000000000000000000afbbd21e0468f00000000000000000000000000000000000000000000000000000000000000a00000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000000006a455b630000000000000000000000000000000000000000000000000000000000000002000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda029130000000000000000000000004200000000000000000000000000000000000006",
      "calldata_bytes": 260,
      "eth_call": {
        "from": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
        "to": "0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24",
        "data": "0x38ed173900000000000000000000000000000000000000000000000000000000004c4b40000000000000000000000000000000000000000000000000000afbbd21e0468f00000000000000000000000000000000000000000000000000000000000000a00000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000000006a455b630000000000000000000000000000000000000000000000000000000000000002000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda029130000000000000000000000004200000000000000000000000000000000000006",
        "value": "0x0"
      },
      "route_metadata": {
        "path": [
          "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
          "0x4200000000000000000000000000000000000006"
        ]
      },
      "eth_call_result": {
        "status": "REVERT",
        "rpc": "Base:rpc1:https://base-rpc.publicnode.com",
        "rpc_url": "https://base-rpc.publicnode.com",
        "latency_ms": 451.52,
        "error": "ContractLogicError: ('execution reverted: UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT', '0x08c379a00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000002b556e69737761705632526f757465723a20494e53554646494349454e545f4f55545055545f414d4f554e54000000000000000000000000000000000000000000')"
      }
    },
    {
      "leg": "SELL_WETH",
      "dex": "Uniswap V3",
      "router_type": "v3",
      "router_address": "0x2626664c2603336E57B271c5C0b26F421741e481",
      "token_in": "WETH",
      "token_in_address": "0x4200000000000000000000000000000000000006",
      "token_out": "USDC",
      "token_out_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "amount_in_units": "3107074877229684",
      "amount_out_min_units": "5002616",
      "deadline": 1782930275,
      "calldata": "0x04e45aaf0000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000001f40000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000b09de3e590a7400000000000000000000000000000000000000000000000000000000004c55780000000000000000000000000000000000000000000000000000000000000000",
      "calldata_bytes": 228,
      "eth_call": {
        "from": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
        "to": "0x2626664c2603336E57B271c5C0b26F421741e481",
        "data": "0x04e45aaf0000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000001f40000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000b09de3e590a7400000000000000000000000000000000000000000000000000000000004c55780000000000000000000000000000000000000000000000000000000000000000",
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
        "latency_ms": 425.08,
        "error": "ContractLogicError: ('execution reverted: STF', '0x08c379a0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000035354460000000000000000000000000000000000000000000000000000000000')"
      }
    }
  ],
  "eth_call_summary": {
    "leg_count": 2,
    "pass_count": 0,
    "revert_count": 2,
    "fail_count": 0
  }
}
```

## Notes

- Transaction Simulation is evidence-only and never sends a transaction.
- The gate remains non-passing until exact calldata is built, Base eth_call simulation succeeds for both arbitrage legs, and the surrounding readiness checks pass.
- Private keys must remain absent while developing this report.
