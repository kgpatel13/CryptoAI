# Atomic Live Arbitrage Simulation

Generated: `2026-07-01T18:46:25Z`
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
    "timestamp": "2026-07-01T18:46:17Z",
    "chain": "base",
    "pair": "WETH/USDC",
    "buy_dex": "Uniswap V2",
    "sell_dex": "Uniswap V3",
    "source_decision": "WATCH",
    "realism_status": "WATCH_ONLY",
    "gross_edge_pct": "0.5308",
    "reported_net_edge_pct": "0.2308",
    "stress_net_edge_pct": "0.1527",
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
      "timestamp": "2026-07-01T18:46:17Z",
      "chain": "base",
      "pair": "WETH/USDC",
      "buy_dex": "Uniswap V2",
      "sell_dex": "Uniswap V3",
      "source_decision": "WATCH",
      "realism_status": "WATCH_ONLY",
      "gross_edge_pct": "0.5308",
      "reported_net_edge_pct": "0.2308",
      "stress_net_edge_pct": "0.1527",
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
      "timestamp": "2026-07-01T18:46:17Z",
      "chain": "base",
      "pair": "USDC/WETH",
      "buy_dex": "Uniswap V2",
      "sell_dex": "Uniswap V3",
      "source_decision": "WATCH",
      "realism_status": "WATCH_ONLY",
      "gross_edge_pct": "0.4394",
      "reported_net_edge_pct": "0.1394",
      "stress_net_edge_pct": "0.0682",
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
  ],
  "route_sweep": {
    "enabled": true,
    "strategy": "best_exact_atomic_eth_call",
    "candidate_count": 4,
    "attempt_count": 4,
    "passing_count": 0,
    "selected_attempt": {
      "attempt": 0,
      "status": "SIMULATION_ATTEMPTED",
      "eth_call_status": "FAIL",
      "decoded_error": "ProfitTooLow",
      "amount_in_usdc": "5",
      "simulated_atomic_out_usdc": "4.963158",
      "required_out_usdc": "5.0005",
      "shortfall_usdc": "0.037342",
      "candidate": {
        "timestamp": "2026-07-01T18:46:17Z",
        "pair": "WETH/USDC",
        "buy_dex": "Uniswap V3",
        "sell_dex": "Uniswap V2",
        "variant": "reverse_dex",
        "source_decision": "WATCH",
        "realism_status": "WATCH_ONLY",
        "gross_edge_pct": "0.5308",
        "stress_net_edge_pct": "0.1527"
      },
      "intent": {
        "pair": "WETH/USDC",
        "buy_dex": "Uniswap V3",
        "sell_dex": "Uniswap V2",
        "notional_usd": "5.0000",
        "selection_mode": "ATOMIC_ROUTE_SWEEP_REVERSE_DEX"
      }
    },
    "attempts": [
      {
        "attempt": 1,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T18:46:17Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.5308",
          "stress_net_edge_pct": "0.1527"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5.0000",
          "selection_mode": "TINY_LIVE_REALISM"
        }
      },
      {
        "attempt": 2,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": "4.963158",
        "required_out_usdc": "5.0005",
        "shortfall_usdc": "0.037342",
        "candidate": {
          "timestamp": "2026-07-01T18:46:17Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.5308",
          "stress_net_edge_pct": "0.1527"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5.0000",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_REVERSE_DEX"
        }
      },
      {
        "attempt": 3,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": "4.948182",
        "required_out_usdc": "5.0005",
        "shortfall_usdc": "0.052318",
        "candidate": {
          "timestamp": "2026-07-01T18:46:17Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4394",
          "stress_net_edge_pct": "0.0682"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5.0000",
          "selection_mode": "STANDARD_SHADOW_READY"
        }
      },
      {
        "attempt": 4,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T18:46:17Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4394",
          "stress_net_edge_pct": "0.0682"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5.0000",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_REVERSE_DEX"
        }
      }
    ],
    "selection_rule": "Prefer PASS; otherwise pick the route with the highest simulated atomic USDC output / smallest shortfall."
  }
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
  "deadline": 1782931671,
  "calldata": "0x59b467930000000000000000000000000000000000000000000000000000000000000020000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda029130000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000004c4b4000000000000000000000000000000000000000000000000000000000004c4d3400000000000000000000000000000000000000000000000000000000000001f40000000000000000000000002626664c2603336e57b271c5c0b26f421741e4810000000000000000000000004752ba5dbc23f44d87826276bf6fd6b1c372ad24000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000002a00000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000000006a4560d700000000000000000000000000000000000000000000000000000000000000e404e45aaf000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913000000000000000000000000420000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea450800000000000000000000000000000000000000000000000000000000004c4b40000000000000000000000000000000000000000000000000000aeea2c568d717000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010438ed1739000000000000000000000000000000000000000000000000000aeea2c568d71700000000000000000000000000000000000000000000000000000000004b225300000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000000006a4560d700000000000000000000000000000000000000000000000000000000000000020000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000",
  "calldata_bytes": 1028,
  "swap_legs": [
    {
      "leg": "BUY_WETH",
      "dex": "Uniswap V3",
      "router_type": "v3",
      "router_address": "0x2626664c2603336E57B271c5C0b26F421741e481",
      "token_in": "USDC",
      "token_in_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "token_out": "WETH",
      "token_out_address": "0x4200000000000000000000000000000000000006",
      "amount_in_units": "5000000",
      "amount_out_min_units": "3077132631201559",
      "deadline": 1782931671,
      "calldata": "0x04e45aaf000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913000000000000000000000000420000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea450800000000000000000000000000000000000000000000000000000000004c4b40000000000000000000000000000000000000000000000000000aeea2c568d7170000000000000000000000000000000000000000000000000000000000000000",
      "calldata_bytes": 228,
      "eth_call": {
        "from": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
        "to": "0x2626664c2603336E57B271c5C0b26F421741e481",
        "data": "0x04e45aaf000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913000000000000000000000000420000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea450800000000000000000000000000000000000000000000000000000000004c4b40000000000000000000000000000000000000000000000000000aeea2c568d7170000000000000000000000000000000000000000000000000000000000000000",
        "value": "0x0"
      },
      "route_metadata": {
        "fee_tier": 500,
        "sqrt_price_limit_x96": 0
      },
      "route_reconciliation": {
        "buy_expected_weth": "0.003092595609247798546639641587",
        "buy_min_weth": "0.003077132631201559553906443379",
        "sell_input_source": "buy_min_weth"
      }
    },
    {
      "leg": "SELL_WETH",
      "dex": "Uniswap V2",
      "router_type": "v2",
      "router_address": "0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24",
      "token_in": "WETH",
      "token_in_address": "0x4200000000000000000000000000000000000006",
      "token_out": "USDC",
      "token_out_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "amount_in_units": "3077132631201559",
      "amount_out_min_units": "4923987",
      "deadline": 1782931671,
      "calldata": "0x38ed1739000000000000000000000000000000000000000000000000000aeea2c568d71700000000000000000000000000000000000000000000000000000000004b225300000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000000006a4560d700000000000000000000000000000000000000000000000000000000000000020000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913",
      "calldata_bytes": 260,
      "eth_call": {
        "from": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
        "to": "0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24",
        "data": "0x38ed1739000000000000000000000000000000000000000000000000000aeea2c568d71700000000000000000000000000000000000000000000000000000000004b225300000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000000006a4560d700000000000000000000000000000000000000000000000000000000000000020000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913",
        "value": "0x0"
      },
      "route_metadata": {
        "path": [
          "0x4200000000000000000000000000000000000006",
          "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        ]
      },
      "route_reconciliation": {
        "sell_input_weth": "0.003077132631201559553906443379",
        "sell_expected_usdc": "4.948731004914388015934710210",
        "sell_min_usdc": "4.923987349889816075855036659",
        "atomic_min_usdc": "5.0005"
      }
    }
  ],
  "eth_call": {
    "from": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
    "to": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
    "data": "0x59b467930000000000000000000000000000000000000000000000000000000000000020000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda029130000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000004c4b4000000000000000000000000000000000000000000000000000000000004c4d3400000000000000000000000000000000000000000000000000000000000001f40000000000000000000000002626664c2603336e57b271c5c0b26f421741e4810000000000000000000000004752ba5dbc23f44d87826276bf6fd6b1c372ad24000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000002a00000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000000006a4560d700000000000000000000000000000000000000000000000000000000000000e404e45aaf000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913000000000000000000000000420000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea450800000000000000000000000000000000000000000000000000000000004c4b40000000000000000000000000000000000000000000000000000aeea2c568d717000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010438ed1739000000000000000000000000000000000000000000000000000aeea2c568d71700000000000000000000000000000000000000000000000000000000004b225300000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000000006a4560d700000000000000000000000000000000000000000000000000000000000000020000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000",
    "value": "0x0"
  },
  "eth_call_result": {
    "status": "FAIL",
    "error": "ContractCustomError: ('0x88215f9c00000000000000000000000000000000000000000000000000000000004bbb5600000000000000000000000000000000000000000000000000000000004c4d34', '0x88215f9c00000000000000000000000000000000000000000000000000000000004bbb5600000000000000000000000000000000000000000000000000000000004c4d34')"
  },
  "eth_call_status": "FAIL",
  "eth_call_decoded_error": {
    "name": "ProfitTooLow",
    "amount_out_units": "4963158",
    "required_out_units": "5000500",
    "amount_out_usdc": "4.963158",
    "required_out_usdc": "5.0005",
    "shortfall_usdc": "0.037342",
    "explanation": "Atomic route executed in simulation but did not meet the executor's minimum profitable output."
  },
  "approval_spender": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
  "selected_candidate": {
    "timestamp": "2026-07-01T18:46:17Z",
    "chain": "base",
    "pair": "WETH/USDC",
    "buy_source": "Uniswap V3",
    "sell_source": "Uniswap V2",
    "buy_price": "1616.76489",
    "sell_price": "1608.228048",
    "source_decision": "WATCH",
    "gross_edge_pct": "0.5308",
    "configured_cost_buffer_pct": "0.3000",
    "reported_net_edge_pct": "0.2308",
    "estimated_price_impact_pct": "0.0181",
    "estimated_gas_usd": "0.0500",
    "estimated_gas_pct": "0.0100",
    "mev_risk": "MEDIUM",
    "mev_risk_buffer_pct": "0.0500",
    "stress_total_cost_pct": "0.3781",
    "stress_net_edge_pct": "0.1527",
    "requested_notional_usd": "500.0000",
    "max_executable_notional_usd": "500.0000",
    "executable_ratio_pct": "100.0000",
    "depth_model": "POOL_DEPTH_LADDER",
    "pool_depth_status": "DEPTH_READY",
    "confidence": "MEDIUM",
    "realism_status": "WATCH_ONLY",
    "reason": "Stress model is informational because source decision is not BUY; confidence=MEDIUM.",
    "selection_mode": "ATOMIC_ROUTE_SWEEP_REVERSE_DEX",
    "selection_reason": "Synthetic reverse DEX candidate for exact atomic eth_call sweep.",
    "variant": "reverse_dex",
    "buy_dex": "Uniswap V3",
    "sell_dex": "Uniswap V2"
  },
  "selected_intent": {
    "pair": "WETH/USDC",
    "buy_dex": "Uniswap V3",
    "sell_dex": "Uniswap V2",
    "notional_usd": "5.0000",
    "selection_mode": "ATOMIC_ROUTE_SWEEP_REVERSE_DEX",
    "selection_reason": "Synthetic reverse DEX candidate for exact atomic eth_call sweep."
  },
  "eth_call_success": {},
  "route_sweep": {
    "enabled": true,
    "strategy": "best_exact_atomic_eth_call",
    "candidate_count": 4,
    "attempt_count": 4,
    "passing_count": 0,
    "selected_attempt": {
      "attempt": 0,
      "status": "SIMULATION_ATTEMPTED",
      "eth_call_status": "FAIL",
      "decoded_error": "ProfitTooLow",
      "amount_in_usdc": "5",
      "simulated_atomic_out_usdc": "4.963158",
      "required_out_usdc": "5.0005",
      "shortfall_usdc": "0.037342",
      "candidate": {
        "timestamp": "2026-07-01T18:46:17Z",
        "pair": "WETH/USDC",
        "buy_dex": "Uniswap V3",
        "sell_dex": "Uniswap V2",
        "variant": "reverse_dex",
        "source_decision": "WATCH",
        "realism_status": "WATCH_ONLY",
        "gross_edge_pct": "0.5308",
        "stress_net_edge_pct": "0.1527"
      },
      "intent": {
        "pair": "WETH/USDC",
        "buy_dex": "Uniswap V3",
        "sell_dex": "Uniswap V2",
        "notional_usd": "5.0000",
        "selection_mode": "ATOMIC_ROUTE_SWEEP_REVERSE_DEX"
      }
    },
    "attempts": [
      {
        "attempt": 1,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T18:46:17Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.5308",
          "stress_net_edge_pct": "0.1527"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5.0000",
          "selection_mode": "TINY_LIVE_REALISM"
        }
      },
      {
        "attempt": 2,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": "4.963158",
        "required_out_usdc": "5.0005",
        "shortfall_usdc": "0.037342",
        "candidate": {
          "timestamp": "2026-07-01T18:46:17Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.5308",
          "stress_net_edge_pct": "0.1527"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5.0000",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_REVERSE_DEX"
        }
      },
      {
        "attempt": 3,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": "4.948182",
        "required_out_usdc": "5.0005",
        "shortfall_usdc": "0.052318",
        "candidate": {
          "timestamp": "2026-07-01T18:46:17Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4394",
          "stress_net_edge_pct": "0.0682"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5.0000",
          "selection_mode": "STANDARD_SHADOW_READY"
        }
      },
      {
        "attempt": 4,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T18:46:17Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4394",
          "stress_net_edge_pct": "0.0682"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5.0000",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_REVERSE_DEX"
        }
      }
    ],
    "selection_rule": "Prefer PASS; otherwise pick the route with the highest simulated atomic USDC output / smallest shortfall."
  }
}
```

## Profit Reconciliation

```json
{
  "status": "LOSS_AFTER_ATOMIC_SIMULATION",
  "amount_in_usdc": "5",
  "estimated_gross_out_usdc": "5.026540",
  "estimated_net_out_usdc": "5.011540",
  "estimated_stress_out_usdc": "5.007635",
  "simulated_atomic_out_usdc": "4.963158",
  "required_out_usdc": "5.0005",
  "estimated_stress_net_pct": "0.1527",
  "simulated_atomic_net_pct": "-0.7368",
  "stress_vs_atomic_divergence_pct": "0.8895",
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
