# Atomic Live Arbitrage Simulation

Generated: `2026-07-02T00:56:55Z`
- Overall status: `ATOMIC_ROUTE_ACTION`
- Atomic route simulation passed: `False`
- Live trading approval: `False`
- Executor: `0xDB8F6e57861F1aB65812A6B1d64133E244066B0c`
- Executor preflight: `READY`
- eth_call status: `FAIL`
- Route blocker: `ATOMIC_BUILDER_OR_ETH_CALL`
- Profit reconciliation: `LOSS_AFTER_ATOMIC_SIMULATION`
- Near pass: `False`
- Generation elapsed ms: `33264`
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
    "timestamp": "2026-07-02T00:56:23Z",
    "chain": "base",
    "pair": "WETH/USDC",
    "buy_dex": "Uniswap V2",
    "sell_dex": "Uniswap V3",
    "source_decision": "BUY",
    "realism_status": "SHADOW_READY",
    "gross_edge_pct": "0.6802",
    "reported_net_edge_pct": "0.3802",
    "stress_net_edge_pct": "0.3021",
    "required_threshold_pct": "0.30",
    "confidence": "MEDIUM",
    "requested_notional_usd": "500.0000",
    "max_executable_notional_usd": "500.0000",
    "executable_ratio_pct": "100.0000",
    "pool_depth_status": "DEPTH_READY",
    "reason": "Opportunity passed current realism screen.",
    "diagnostic_reasons": [
      "tiny-live eligible; exact atomic eth_call remains the final gate"
    ]
  },
  "latest_opportunity_count": 2,
  "latest_diagnostics_count": 2,
  "buy_candidate_count": 1,
  "shadow_ready_count": 1,
  "tiny_live_eligible_count": 1,
  "latest_opportunities": [
    {
      "timestamp": "2026-07-02T00:56:23Z",
      "chain": "base",
      "pair": "WETH/USDC",
      "buy_dex": "Uniswap V2",
      "sell_dex": "Uniswap V3",
      "source_decision": "BUY",
      "realism_status": "SHADOW_READY",
      "gross_edge_pct": "0.6802",
      "reported_net_edge_pct": "0.3802",
      "stress_net_edge_pct": "0.3021",
      "required_threshold_pct": "0.30",
      "confidence": "MEDIUM",
      "requested_notional_usd": "500.0000",
      "max_executable_notional_usd": "500.0000",
      "executable_ratio_pct": "100.0000",
      "pool_depth_status": "DEPTH_READY",
      "reason": "Opportunity passed current realism screen.",
      "diagnostic_reasons": [
        "tiny-live eligible; exact atomic eth_call remains the final gate"
      ]
    },
    {
      "timestamp": "2026-07-02T00:56:23Z",
      "chain": "base",
      "pair": "USDC/WETH",
      "buy_dex": "Uniswap V2",
      "sell_dex": "Uniswap V3",
      "source_decision": "SKIP",
      "realism_status": "NEGATIVE_AFTER_STRESS",
      "gross_edge_pct": "0.2902",
      "reported_net_edge_pct": "-0.0098",
      "stress_net_edge_pct": "-0.0810",
      "required_threshold_pct": "0.30",
      "confidence": "MEDIUM",
      "requested_notional_usd": "500.0000",
      "max_executable_notional_usd": "500.0000",
      "executable_ratio_pct": "100.0000",
      "pool_depth_status": "DEPTH_READY",
      "reason": "Stress net edge is negative after price-impact/gas/MEV buffers (-0.0810%).",
      "diagnostic_reasons": [
        "source_decision is SKIP, not BUY",
        "realism_status is NEGATIVE_AFTER_STRESS, not SHADOW_READY",
        "stress_net_edge_pct is negative"
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
    "strategy": "best_exact_atomic_eth_call_notional_venue_sweep",
    "candidate_count": 16,
    "attempt_count": 16,
    "passing_count": 0,
    "sweep_config": {
      "notionals_usd": [
        "1",
        "2"
      ],
      "venues": [
        "Uniswap V2",
        "Uniswap V3",
        "Aerodrome"
      ],
      "venue_sweep_enabled": true,
      "leg_slippage_bps_list": [
        "1",
        "2"
      ],
      "legacy_single_leg_slippage_bps": "50"
    },
    "selected_attempt": {
      "attempt": 0,
      "status": "SIMULATION_ATTEMPTED",
      "eth_call_status": "FAIL",
      "decoded_error": "RouterRevert",
      "amount_in_usdc": "1",
      "simulated_atomic_out_usdc": null,
      "required_out_usdc": "1.0001",
      "shortfall_usdc": null,
      "candidate": {
        "timestamp": "2026-07-02T00:56:23Z",
        "pair": "WETH/USDC",
        "buy_dex": "Uniswap V3",
        "sell_dex": "Uniswap V2",
        "variant": "reverse_dex",
        "source_decision": "BUY",
        "realism_status": "SHADOW_READY",
        "gross_edge_pct": "0.6802",
        "stress_net_edge_pct": "0.3021",
        "sweep_notional_usd": "1",
        "sweep_leg_slippage_bps": "1",
        "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
      },
      "intent": {
        "pair": "WETH/USDC",
        "buy_dex": "Uniswap V3",
        "sell_dex": "Uniswap V2",
        "notional_usd": "1",
        "max_slippage_bps": "1",
        "sweep_leg_slippage_bps": "1",
        "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
      }
    },
    "attempts": [
      {
        "attempt": 1,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 2,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 3,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 4,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 5,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 6,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 7,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 8,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 9,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 10,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 11,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 12,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 13,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 14,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 15,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 16,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      }
    ],
    "selection_rule": "Prefer PASS; otherwise pick the route with the highest simulated atomic USDC output / smallest shortfall across candidate, venue, and notional variants."
  }
}
```

## Atomic Route

```json
{
  "status": "SIMULATION_ATTEMPTED",
  "chain": "base",
  "chain_id": 8453,
  "executor_address": "0xDB8F6e57861F1aB65812A6B1d64133E244066B0c",
  "wallet_address": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
  "token_in": "USDC",
  "token_mid": "WETH",
  "token_out": "USDC",
  "amount_in_units": "1000000",
  "min_amount_out_units": "1000100",
  "min_profit_units": "100",
  "min_profit_bps": "1",
  "tiny_live_realism_enabled": true,
  "executor_version": "v2",
  "patch_sell_amount_in": true,
  "sell_amount_in_offset": "4",
  "deadline": 1782953880,
  "calldata": "0x56d1b32c0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda029130000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000f424000000000000000000000000000000000000000000000000000000000000f42a400000000000000000000000000000000000000000000000000000000000000640000000000000000000000002626664c2603336e57b271c5c0b26f421741e4810000000000000000000000004752ba5dbc23f44d87826276bf6fd6b1c372ad2400000000000000000000000000000000000000000000000000000000000001c000000000000000000000000000000000000000000000000000000000000002e00000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000000006a45b7980000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000e404e45aaf000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913000000000000000000000000420000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000db8f6e57861f1ab65812a6b1d64133e244066b0c00000000000000000000000000000000000000000000000000000000000f4240000000000000000000000000000000000000000000000000000237955f57343c000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010438ed1739000000000000000000000000000000000000000000000000000237955f57343c00000000000000000000000000000000000000000000000000000000000f271500000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000db8f6e57861f1ab65812a6b1d64133e244066b0c000000000000000000000000000000000000000000000000000000006a45b79800000000000000000000000000000000000000000000000000000000000000020000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000",
  "calldata_bytes": 1092,
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
      "amount_in_units": "1000000",
      "amount_out_min_units": "624064642626620",
      "deadline": 1782953880,
      "calldata": "0x04e45aaf000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913000000000000000000000000420000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000db8f6e57861f1ab65812a6b1d64133e244066b0c00000000000000000000000000000000000000000000000000000000000f4240000000000000000000000000000000000000000000000000000237955f57343c0000000000000000000000000000000000000000000000000000000000000000",
      "calldata_bytes": 228,
      "eth_call": {
        "from": "0xDB8F6e57861F1aB65812A6B1d64133E244066B0c",
        "to": "0x2626664c2603336E57B271c5C0b26F421741e481",
        "data": "0x04e45aaf000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913000000000000000000000000420000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000db8f6e57861f1ab65812a6b1d64133e244066b0c00000000000000000000000000000000000000000000000000000000000f4240000000000000000000000000000000000000000000000000000237955f57343c0000000000000000000000000000000000000000000000000000000000000000",
        "value": "0x0"
      },
      "route_metadata": {
        "fee_tier": 500,
        "sqrt_price_limit_x96": 0
      },
      "route_reconciliation": {
        "buy_expected_weth": "0.0006241270553321538530311501863",
        "buy_min_weth": "0.0006240646426266206376458470713",
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
      "amount_in_units": "624064642626620",
      "amount_out_min_units": "993045",
      "deadline": 1782953880,
      "calldata": "0x38ed1739000000000000000000000000000000000000000000000000000237955f57343c00000000000000000000000000000000000000000000000000000000000f271500000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000db8f6e57861f1ab65812a6b1d64133e244066b0c000000000000000000000000000000000000000000000000000000006a45b79800000000000000000000000000000000000000000000000000000000000000020000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913",
      "calldata_bytes": 260,
      "eth_call": {
        "from": "0xDB8F6e57861F1aB65812A6B1d64133E244066B0c",
        "to": "0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24",
        "data": "0x38ed1739000000000000000000000000000000000000000000000000000237955f57343c00000000000000000000000000000000000000000000000000000000000f271500000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000db8f6e57861f1ab65812a6b1d64133e244066b0c000000000000000000000000000000000000000000000000000000006a45b79800000000000000000000000000000000000000000000000000000000000000020000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913",
        "value": "0x0"
      },
      "route_metadata": {
        "path": [
          "0x4200000000000000000000000000000000000006",
          "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        ]
      },
      "route_reconciliation": {
        "sell_input_weth": "0.0006240646426266206376458470713",
        "sell_expected_usdc": "0.9931445938532632255905793523",
        "sell_min_usdc": "0.9930452793938778992680202944",
        "atomic_min_usdc": "1.0001"
      }
    }
  ],
  "eth_call": {
    "from": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
    "to": "0xDB8F6e57861F1aB65812A6B1d64133E244066B0c",
    "data": "0x56d1b32c0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda029130000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000f424000000000000000000000000000000000000000000000000000000000000f42a400000000000000000000000000000000000000000000000000000000000000640000000000000000000000002626664c2603336e57b271c5c0b26f421741e4810000000000000000000000004752ba5dbc23f44d87826276bf6fd6b1c372ad2400000000000000000000000000000000000000000000000000000000000001c000000000000000000000000000000000000000000000000000000000000002e00000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000000006a45b7980000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000e404e45aaf000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913000000000000000000000000420000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000db8f6e57861f1ab65812a6b1d64133e244066b0c00000000000000000000000000000000000000000000000000000000000f4240000000000000000000000000000000000000000000000000000237955f57343c000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010438ed1739000000000000000000000000000000000000000000000000000237955f57343c00000000000000000000000000000000000000000000000000000000000f271500000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000db8f6e57861f1ab65812a6b1d64133e244066b0c000000000000000000000000000000000000000000000000000000006a45b79800000000000000000000000000000000000000000000000000000000000000020000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000",
    "value": "0x0"
  },
  "eth_call_result": {
    "status": "FAIL",
    "elapsed_ms": 198,
    "error": "ContractCustomError: ('0xff9fa5950000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000006408c379a000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000013546f6f206c6974746c652072656365697665640000000000000000000000000000000000000000000000000000000000000000000000000000000000', '0xff9fa595000000000000000000000000000000000000000000000000000000000000002000000"
  },
  "eth_call_status": "FAIL",
  "eth_call_decoded_error": {
    "name": "RouterRevert",
    "selector": "0xff9fa595",
    "reason": "Too little received",
    "raw": "0xff9fa5950000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000006408c379a000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000013546f6f206c6974746c652072656365697665640000000000000000000000000000000000000000000000000000000000000000000000000000000000"
  },
  "approval_spender": "0xDB8F6e57861F1aB65812A6B1d64133E244066B0c",
  "selected_candidate": {
    "timestamp": "2026-07-02T00:56:23Z",
    "chain": "base",
    "pair": "WETH/USDC",
    "buy_source": "Uniswap V3",
    "sell_source": "Uniswap V2",
    "buy_price": "1602.237864",
    "sell_price": "1591.413014",
    "source_decision": "BUY",
    "gross_edge_pct": "0.6802",
    "configured_cost_buffer_pct": "0.3000",
    "reported_net_edge_pct": "0.3802",
    "estimated_price_impact_pct": "0.0181",
    "estimated_gas_usd": "0.0500",
    "estimated_gas_pct": "0.0100",
    "mev_risk": "MEDIUM",
    "mev_risk_buffer_pct": "0.0500",
    "stress_total_cost_pct": "0.3781",
    "stress_net_edge_pct": "0.3021",
    "requested_notional_usd": "1",
    "max_executable_notional_usd": "500.0000",
    "executable_ratio_pct": "100.0000",
    "depth_model": "POOL_DEPTH_LADDER",
    "pool_depth_status": "DEPTH_READY",
    "confidence": "MEDIUM",
    "realism_status": "SHADOW_READY",
    "reason": "Opportunity passed current realism screen.",
    "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE",
    "variant": "reverse_dex",
    "buy_dex": "Uniswap V3",
    "sell_dex": "Uniswap V2",
    "selection_reason": "Tight leg-slippage exact atomic eth_call sweep candidate.",
    "sweep_notional_usd": "1",
    "sweep_leg_slippage_bps": "1"
  },
  "selected_intent": {
    "pair": "WETH/USDC",
    "buy_dex": "Uniswap V3",
    "sell_dex": "Uniswap V2",
    "notional_usd": "1",
    "max_slippage_bps": "1",
    "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE",
    "selection_reason": "Tight leg-slippage exact atomic eth_call sweep candidate."
  },
  "v2_route_patch": {
    "enabled": true,
    "patch_sell_amount_in": true,
    "sell_amount_in_offset": "4",
    "sell_router_type": "v2",
    "sell_dex": "Uniswap V2",
    "explanation": "V2 patches sell calldata amountIn to the actual tokenMid balance received after leg 1."
  },
  "eth_call_success": {},
  "route_sweep": {
    "enabled": true,
    "strategy": "best_exact_atomic_eth_call_notional_venue_sweep",
    "candidate_count": 16,
    "attempt_count": 16,
    "passing_count": 0,
    "sweep_config": {
      "notionals_usd": [
        "1",
        "2"
      ],
      "venues": [
        "Uniswap V2",
        "Uniswap V3",
        "Aerodrome"
      ],
      "venue_sweep_enabled": true,
      "leg_slippage_bps_list": [
        "1",
        "2"
      ],
      "legacy_single_leg_slippage_bps": "50"
    },
    "selected_attempt": {
      "attempt": 0,
      "status": "SIMULATION_ATTEMPTED",
      "eth_call_status": "FAIL",
      "decoded_error": "RouterRevert",
      "amount_in_usdc": "1",
      "simulated_atomic_out_usdc": null,
      "required_out_usdc": "1.0001",
      "shortfall_usdc": null,
      "candidate": {
        "timestamp": "2026-07-02T00:56:23Z",
        "pair": "WETH/USDC",
        "buy_dex": "Uniswap V3",
        "sell_dex": "Uniswap V2",
        "variant": "reverse_dex",
        "source_decision": "BUY",
        "realism_status": "SHADOW_READY",
        "gross_edge_pct": "0.6802",
        "stress_net_edge_pct": "0.3021",
        "sweep_notional_usd": "1",
        "sweep_leg_slippage_bps": "1",
        "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
      },
      "intent": {
        "pair": "WETH/USDC",
        "buy_dex": "Uniswap V3",
        "sell_dex": "Uniswap V2",
        "notional_usd": "1",
        "max_slippage_bps": "1",
        "sweep_leg_slippage_bps": "1",
        "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
      }
    },
    "attempts": [
      {
        "attempt": 1,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 2,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 3,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 4,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 5,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 6,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 7,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 8,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 9,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 10,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 11,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 12,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 13,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 14,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 15,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 16,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-02T00:56:23Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "BUY",
          "realism_status": "SHADOW_READY",
          "gross_edge_pct": "0.6802",
          "stress_net_edge_pct": "0.3021",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      }
    ],
    "selection_rule": "Prefer PASS; otherwise pick the route with the highest simulated atomic USDC output / smallest shortfall across candidate, venue, and notional variants."
  }
}
```

## Profit Reconciliation

```json
{
  "status": "LOSS_AFTER_ATOMIC_SIMULATION",
  "amount_in_usdc": "1",
  "estimated_gross_out_usdc": "1.006802",
  "estimated_net_out_usdc": "1.003802",
  "estimated_stress_out_usdc": "1.003021",
  "simulated_atomic_out_usdc": "0",
  "required_out_usdc": "1.0001",
  "output_delta_usdc": "-1",
  "shortfall_to_required_usdc": "1.0001",
  "near_pass": false,
  "near_pass_threshold_usdc": "0.001",
  "estimated_stress_net_pct": "0.3021",
  "simulated_atomic_net_pct": "-100.0000",
  "stress_vs_atomic_divergence_pct": "100.3021",
  "findings": [
    "Atomic eth_call shows the selected route loses money after real router execution.",
    "Opportunity stress estimate and atomic eth_call differ by more than 0.10 percentage points.",
    "Atomic simulation used live trade cap while opportunity evidence was assessed at a larger paper notional."
  ]
}
```

## Performance Metrics

```json
{
  "generation_elapsed_ms": 33264,
  "route_sweep_attempt_count": 16,
  "selected_eth_call_elapsed_ms": 198
}
```

## Notes

- This report is the final evidence gate for atomic live arbitrage.
- It builds one executor transaction and simulates it with eth_call only.
- No transaction is signed or broadcast by this service.
- The wallet must approve USDC to the atomic executor, not just to an individual router.
