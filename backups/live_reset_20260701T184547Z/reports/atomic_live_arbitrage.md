# Atomic Live Arbitrage Simulation

Generated: `2026-07-01T18:34:05Z`
- Overall status: `ATOMIC_ROUTE_ACTION`
- Atomic route simulation passed: `False`
- Live trading approval: `False`
- Executor: `0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508`
- Executor preflight: `READY`
- eth_call status: `FAIL`
- Route blocker: `ATOMIC_BUILDER_OR_ETH_CALL`
- Profit reconciliation: `LOSS_AFTER_ATOMIC_SIMULATION`
- Blocked checks: `0`
- Action checks: `1`

## Checks

| Check | Status | Detail |
|---|---|---|
| two_leg_candidate_selected | PASS | A two-leg candidate is selected. |
| not_one_leg_smoke | PASS | Route is a two-leg arbitrage candidate. |
| executor_configured | PASS | Atomic executor address is configured. |
| executor_deployed | PASS | Atomic executor bytecode exists on Base. |
| executor_reviewed | PASS | Atomic executor review flag is present. |
| executor_usdc_allowance | PASS | USDC allowance to atomic executor is sufficient or no executable route is ready. |
| atomic_calldata_built | PASS | Atomic executor calldata is built. |
| atomic_eth_call_passed | ACTION | Atomic executor eth_call did not pass. |

## Route Diagnostics

```json
{
  "blocker_type": "ATOMIC_BUILDER_OR_ETH_CALL",
  "next_action": "Inspect atomic_calldata_built and atomic_eth_call_passed details.",
  "transaction_simulation_passed": false,
  "transaction_simulation_status": "TX_SIMULATION_ACTION",
  "simulation_type": "TWO_LEG_ARBITRAGE",
  "selected_candidate_found": true,
  "selected_candidate": {
    "timestamp": "2026-07-01T18:34:02Z",
    "chain": "base",
    "pair": "USDC/WETH",
    "buy_dex": "Uniswap V2",
    "sell_dex": "Uniswap V3",
    "source_decision": "WATCH",
    "realism_status": "WATCH_ONLY",
    "gross_edge_pct": "0.5683",
    "reported_net_edge_pct": "0.2683",
    "stress_net_edge_pct": "0.1971",
    "required_threshold_pct": "0.30",
    "confidence": "MEDIUM",
    "requested_notional_usd": "500.0000",
    "max_executable_notional_usd": "500.0000",
    "executable_ratio_pct": "100.0000",
    "pool_depth_status": "DEPTH_READY",
    "reason": "Stress model is informational because source decision is not BUY; confidence=MEDIUM.",
    "diagnostic_reasons": [
      "source_decision is WATCH, not BUY",
      "realism_status is WATCH_ONLY, not SHADOW_READY",
      "tiny-live eligible; exact atomic eth_call remains the final gate"
    ]
  },
  "latest_opportunity_count": 2,
  "latest_diagnostics_count": 2,
  "buy_candidate_count": 0,
  "shadow_ready_count": 0,
  "tiny_live_eligible_count": 2,
  "latest_opportunities": [
    {
      "timestamp": "2026-07-01T18:34:02Z",
      "chain": "base",
      "pair": "WETH/USDC",
      "buy_dex": "Uniswap V2",
      "sell_dex": "Uniswap V3",
      "source_decision": "WATCH",
      "realism_status": "WATCH_ONLY",
      "gross_edge_pct": "0.4020",
      "reported_net_edge_pct": "0.1020",
      "stress_net_edge_pct": "0.0239",
      "required_threshold_pct": "0.30",
      "confidence": "MEDIUM",
      "requested_notional_usd": "500.0000",
      "max_executable_notional_usd": "500.0000",
      "executable_ratio_pct": "100.0000",
      "pool_depth_status": "DEPTH_READY",
      "reason": "Stress model is informational because source decision is not BUY; confidence=MEDIUM.",
      "diagnostic_reasons": [
        "source_decision is WATCH, not BUY",
        "realism_status is WATCH_ONLY, not SHADOW_READY",
        "tiny-live eligible; exact atomic eth_call remains the final gate"
      ]
    },
    {
      "timestamp": "2026-07-01T18:34:02Z",
      "chain": "base",
      "pair": "USDC/WETH",
      "buy_dex": "Uniswap V2",
      "sell_dex": "Uniswap V3",
      "source_decision": "WATCH",
      "realism_status": "WATCH_ONLY",
      "gross_edge_pct": "0.5683",
      "reported_net_edge_pct": "0.2683",
      "stress_net_edge_pct": "0.1971",
      "required_threshold_pct": "0.30",
      "confidence": "MEDIUM",
      "requested_notional_usd": "500.0000",
      "max_executable_notional_usd": "500.0000",
      "executable_ratio_pct": "100.0000",
      "pool_depth_status": "DEPTH_READY",
      "reason": "Stress model is informational because source decision is not BUY; confidence=MEDIUM.",
      "diagnostic_reasons": [
        "source_decision is WATCH, not BUY",
        "realism_status is WATCH_ONLY, not SHADOW_READY",
        "tiny-live eligible; exact atomic eth_call remains the final gate"
      ]
    }
  ],
  "failed_transaction_simulation_checks": [
    {
      "name": "live_trading_disabled",
      "severity": "BLOCK",
      "detail": "Live trading must remain disabled during transaction simulation development."
    },
    {
      "name": "kill_switch_enabled",
      "severity": "BLOCK",
      "detail": "Live kill switch must remain enabled during transaction simulation development."
    },
    {
      "name": "private_key_absent",
      "severity": "BLOCK",
      "detail": "Private key must not be configured for simulation report generation."
    },
    {
      "name": "wallet_preflight_ready",
      "severity": "ACTION",
      "detail": "Wallet Preflight must be ready before transaction simulation review."
    },
    {
      "name": "live_readiness_preconditions_ready",
      "severity": "ACTION",
      "detail": "Live Readiness Checklist has blocking checks that must be cleared before transaction simulation can pass."
    },
    {
      "name": "eth_call_simulation_passed",
      "severity": "ACTION",
      "detail": "Base eth_call simulation has not passed yet."
    }
  ]
}
```

## Atomic Route

```json
{
  "status": "SIMULATION_ATTEMPTED",
  "chain": "base",
  "chain_id": 8453,
  "executor_address": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
  "wallet_address": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
  "token_in": "USDC",
  "token_mid": "WETH",
  "token_out": "USDC",
  "amount_in_units": "5000000",
  "min_amount_out_units": "5000500",
  "min_profit_units": "500",
  "min_profit_bps": "1",
  "tiny_live_realism_enabled": true,
  "deadline": 1782930934,
  "calldata": "0x59b467930000000000000000000000000000000000000000000000000000000000000020000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda029130000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000004c4b4000000000000000000000000000000000000000000000000000000000004c4d3400000000000000000000000000000000000000000000000000000000000001f40000000000000000000000004752ba5dbc23f44d87826276bf6fd6b1c372ad240000000000000000000000002626664c2603336e57b271c5c0b26f421741e481000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000002c00000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000000006a455df6000000000000000000000000000000000000000000000000000000000000010438ed173900000000000000000000000000000000000000000000000000000000004c4b40000000000000000000000000000000000000000000000000000adf6b82fc184100000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000000006a455df60000000000000000000000000000000000000000000000000000000000000002000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000042000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e404e45aaf0000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000adf6b82fc184100000000000000000000000000000000000000000000000000000000004b1b27000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
  "calldata_bytes": 1028,
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
      "amount_out_min_units": "3060402619160641",
      "deadline": 1782930934,
      "calldata": "0x38ed173900000000000000000000000000000000000000000000000000000000004c4b40000000000000000000000000000000000000000000000000000adf6b82fc184100000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000000006a455df60000000000000000000000000000000000000000000000000000000000000002000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda029130000000000000000000000004200000000000000000000000000000000000006",
      "calldata_bytes": 260,
      "eth_call": {
        "from": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
        "to": "0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24",
        "data": "0x38ed173900000000000000000000000000000000000000000000000000000000004c4b40000000000000000000000000000000000000000000000000000adf6b82fc184100000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000000006a455df60000000000000000000000000000000000000000000000000000000000000002000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda029130000000000000000000000004200000000000000000000000000000000000006",
        "value": "0x0"
      },
      "route_metadata": {
        "path": [
          "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
          "0x4200000000000000000000000000000000000006"
        ]
      },
      "route_reconciliation": {
        "buy_expected_weth": "0.0030757815267946149800000",
        "buy_min_weth": "0.0030604026191606419051000000",
        "sell_input_source": "buy_min_weth"
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
      "amount_in_units": "3060402619160641",
      "amount_out_min_units": "4922151",
      "deadline": 1782930934,
      "calldata": "0x04e45aaf0000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000adf6b82fc184100000000000000000000000000000000000000000000000000000000004b1b270000000000000000000000000000000000000000000000000000000000000000",
      "calldata_bytes": 228,
      "eth_call": {
        "from": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
        "to": "0x2626664c2603336E57B271c5C0b26F421741e481",
        "data": "0x04e45aaf0000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000adf6b82fc184100000000000000000000000000000000000000000000000000000000004b1b270000000000000000000000000000000000000000000000000000000000000000",
        "value": "0x0"
      },
      "route_metadata": {
        "fee_tier": 500,
        "sqrt_price_limit_x96": 0
      },
      "route_reconciliation": {
        "sell_input_weth": "0.0030604026191606419051000000",
        "sell_expected_usdc": "4.946885508621931950629995190",
        "sell_min_usdc": "4.922151081078822290876845214",
        "atomic_min_usdc": "5.0005"
      }
    }
  ],
  "eth_call": {
    "from": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
    "to": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
    "data": "0x59b467930000000000000000000000000000000000000000000000000000000000000020000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda029130000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000004c4b4000000000000000000000000000000000000000000000000000000000004c4d3400000000000000000000000000000000000000000000000000000000000001f40000000000000000000000004752ba5dbc23f44d87826276bf6fd6b1c372ad240000000000000000000000002626664c2603336e57b271c5c0b26f421741e481000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000002c00000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000000006a455df6000000000000000000000000000000000000000000000000000000000000010438ed173900000000000000000000000000000000000000000000000000000000004c4b40000000000000000000000000000000000000000000000000000adf6b82fc184100000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000000006a455df60000000000000000000000000000000000000000000000000000000000000002000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000042000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e404e45aaf0000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000adf6b82fc184100000000000000000000000000000000000000000000000000000000004b1b27000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "value": "0x0"
  },
  "eth_call_result": {
    "status": "FAIL",
    "error": "ContractCustomError: ('0x88215f9c00000000000000000000000000000000000000000000000000000000004b680900000000000000000000000000000000000000000000000000000000004c4d34', '0x88215f9c00000000000000000000000000000000000000000000000000000000004b680900000000000000000000000000000000000000000000000000000000004c4d34')"
  },
  "eth_call_status": "FAIL",
  "eth_call_decoded_error": {
    "name": "ProfitTooLow",
    "amount_out_units": "4941833",
    "required_out_units": "5000500",
    "amount_out_usdc": "4.941833",
    "required_out_usdc": "5.0005",
    "shortfall_usdc": "0.058667",
    "explanation": "Atomic route executed in simulation but did not meet the executor's minimum profitable output."
  },
  "approval_spender": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508"
}
```

## Profit Reconciliation

```json
{
  "status": "LOSS_AFTER_ATOMIC_SIMULATION",
  "amount_in_usdc": "5",
  "estimated_gross_out_usdc": "5.028415",
  "estimated_net_out_usdc": "5.013415",
  "estimated_stress_out_usdc": "5.009855",
  "simulated_atomic_out_usdc": "4.941833",
  "required_out_usdc": "5.0005",
  "estimated_stress_net_pct": "0.1971",
  "simulated_atomic_net_pct": "-1.1633",
  "stress_vs_atomic_divergence_pct": "1.3604",
  "findings": [
    "Atomic eth_call shows the selected route loses money after real router execution.",
    "Opportunity stress estimate and atomic eth_call differ by more than 0.10 percentage points.",
    "Atomic simulation used live trade cap while opportunity evidence was assessed at a larger paper notional.",
    "Executor profit guard is working; do not send live until atomic eth_call passes."
  ]
}
```

## Notes

- This report is the final evidence gate for atomic live arbitrage.
- It builds one executor transaction and simulates it with eth_call only.
- No transaction is signed or broadcast by this service.
- The wallet must approve USDC to the atomic executor, not just to an individual router.
