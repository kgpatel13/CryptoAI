# Transaction Simulation Report

Generated: `2026-07-02T00:56:25Z`
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
  "selection_mode": "STANDARD_SHADOW_READY",
  "selection_reason": null,
  "tiny_live_realism_enabled": true,
  "source_decision": "BUY",
  "realism_status": "SHADOW_READY",
  "buy_price": "1591.413014",
  "sell_price": "1602.237864",
  "gross_edge_pct": "0.6802",
  "stress_net_edge_pct": "0.3021",
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
      "amount_out_min_units": "3126152643112669",
      "deadline": 1782953904,
      "calldata": "0x38ed173900000000000000000000000000000000000000000000000000000000004c4b40000000000000000000000000000000000000000000000000000b1b3821ce6edd00000000000000000000000000000000000000000000000000000000000000a00000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000000006a45b7b00000000000000000000000000000000000000000000000000000000000000002000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda029130000000000000000000000004200000000000000000000000000000000000006",
      "calldata_bytes": 260,
      "eth_call": {
        "from": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
        "to": "0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24",
        "data": "0x38ed173900000000000000000000000000000000000000000000000000000000004c4b40000000000000000000000000000000000000000000000000000b1b3821ce6edd00000000000000000000000000000000000000000000000000000000000000a00000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000000006a45b7b00000000000000000000000000000000000000000000000000000000000000002000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda029130000000000000000000000004200000000000000000000000000000000000006",
        "value": "0x0"
      },
      "route_metadata": {
        "path": [
          "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
          "0x4200000000000000000000000000000000000006"
        ]
      },
      "route_reconciliation": {
        "buy_expected_weth": "0.003141861952877054956646219810",
        "buy_min_weth": "0.003126152643112669681862988711",
        "sell_input_source": "buy_min_weth"
      },
      "eth_call_result": {
        "status": "REVERT",
        "elapsed_ms": 345,
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
      "amount_in_units": "3126152643112669",
      "amount_out_min_units": "4983795",
      "deadline": 1782953904,
      "calldata": "0x04e45aaf0000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000001f40000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000b1b3821ce6edd00000000000000000000000000000000000000000000000000000000004c0bf30000000000000000000000000000000000000000000000000000000000000000",
      "calldata_bytes": 228,
      "eth_call": {
        "from": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
        "to": "0x2626664c2603336E57B271c5C0b26F421741e481",
        "data": "0x04e45aaf0000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000001f40000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000b1b3821ce6edd00000000000000000000000000000000000000000000000000000000004c0bf30000000000000000000000000000000000000000000000000000000000000000",
        "value": "0x0"
      },
      "route_metadata": {
        "fee_tier": 500,
        "sqrt_price_limit_x96": 0
      },
      "route_reconciliation": {
        "sell_input_weth": "0.003126152643112669681862988711",
        "sell_expected_usdc": "5.008840133438798182405714573",
        "sell_min_usdc": "4.983795932771604191493686000",
        "atomic_min_usdc": null
      },
      "eth_call_result": {
        "status": "REVERT",
        "elapsed_ms": 205,
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
