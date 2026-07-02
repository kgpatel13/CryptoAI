# Atomic Live Arbitrage Simulation

Generated: `2026-07-01T19:31:27Z`
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
    "timestamp": "2026-07-01T19:30:03Z",
    "chain": "base",
    "pair": "WETH/USDC",
    "buy_dex": "Uniswap V2",
    "sell_dex": "Uniswap V3",
    "source_decision": "WATCH",
    "realism_status": "WATCH_ONLY",
    "gross_edge_pct": "0.4951",
    "reported_net_edge_pct": "0.1951",
    "stress_net_edge_pct": "0.1170",
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
      "timestamp": "2026-07-01T19:30:03Z",
      "chain": "base",
      "pair": "WETH/USDC",
      "buy_dex": "Uniswap V2",
      "sell_dex": "Uniswap V3",
      "source_decision": "WATCH",
      "realism_status": "WATCH_ONLY",
      "gross_edge_pct": "0.4951",
      "reported_net_edge_pct": "0.1951",
      "stress_net_edge_pct": "0.1170",
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
      "timestamp": "2026-07-01T19:30:03Z",
      "chain": "base",
      "pair": "USDC/WETH",
      "buy_dex": "Uniswap V2",
      "sell_dex": "Uniswap V3",
      "source_decision": "WATCH",
      "realism_status": "WATCH_ONLY",
      "gross_edge_pct": "0.4755",
      "reported_net_edge_pct": "0.1755",
      "stress_net_edge_pct": "0.1043",
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
    "strategy": "best_exact_atomic_eth_call_notional_venue_sweep",
    "candidate_count": 48,
    "attempt_count": 48,
    "passing_count": 0,
    "sweep_config": {
      "notionals_usd": [
        "1",
        "2",
        "5"
      ],
      "venues": [
        "Uniswap V2",
        "Uniswap V3",
        "Aerodrome"
      ],
      "venue_sweep_enabled": true,
      "leg_slippage_bps_list": [
        "1",
        "2",
        "5",
        "10",
        "25",
        "50"
      ],
      "legacy_single_leg_slippage_bps": "300"
    },
    "selected_attempt": {
      "attempt": 0,
      "status": "SIMULATION_ATTEMPTED",
      "eth_call_status": "FAIL",
      "decoded_error": "ProfitTooLow",
      "amount_in_usdc": "1",
      "simulated_atomic_out_usdc": "0.995186",
      "required_out_usdc": "1.0001",
      "shortfall_usdc": "0.004914",
      "candidate": {
        "timestamp": "2026-07-01T19:30:03Z",
        "pair": "USDC/WETH",
        "buy_dex": "Aerodrome",
        "sell_dex": "Uniswap V3",
        "variant": "venue:Aerodrome->Uniswap V3",
        "source_decision": "WATCH",
        "realism_status": "WATCH_ONLY",
        "gross_edge_pct": "0.4755",
        "stress_net_edge_pct": "0.1043",
        "sweep_notional_usd": "1",
        "sweep_leg_slippage_bps": "1",
        "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
      },
      "intent": {
        "pair": "USDC/WETH",
        "buy_dex": "Aerodrome",
        "sell_dex": "Uniswap V3",
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
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5",
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
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 5,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 6,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5",
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
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 8,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 9,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 10,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 11,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 12,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 13,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 14,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 15,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 16,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 17,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 18,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 19,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 20,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 21,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 22,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 23,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
      },
      {
        "attempt": 24,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 25,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 26,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 27,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": "4.975712",
        "required_out_usdc": "5.0005",
        "shortfall_usdc": "0.024788",
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 28,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 29,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 30,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 31,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": "0.995142",
        "required_out_usdc": "1.0001",
        "shortfall_usdc": "0.004958",
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 32,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": "1.990285",
        "required_out_usdc": "2.0002",
        "shortfall_usdc": "0.009915",
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 33,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": "4.975712",
        "required_out_usdc": "5.0005",
        "shortfall_usdc": "0.024788",
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 34,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 35,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 36,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 37,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 38,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 39,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 40,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 41,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 42,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 43,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 44,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 45,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 46,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": "0.995186",
        "required_out_usdc": "1.0001",
        "shortfall_usdc": "0.004914",
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 47,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": "1.990373",
        "required_out_usdc": "2.0002",
        "shortfall_usdc": "0.009827",
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 48,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": "4.975932",
        "required_out_usdc": "5.0005",
        "shortfall_usdc": "0.024568",
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5",
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
  "executor_address": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
  "wallet_address": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
  "token_in": "USDC",
  "token_mid": "WETH",
  "token_out": "USDC",
  "amount_in_units": "1000000",
  "min_amount_out_units": "1000100",
  "min_profit_units": "100",
  "min_profit_bps": "1",
  "tiny_live_realism_enabled": true,
  "deadline": 1782934373,
  "calldata": "0x59b467930000000000000000000000000000000000000000000000000000000000000020000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda029130000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000f424000000000000000000000000000000000000000000000000000000000000f42a40000000000000000000000000000000000000000000000000000000000000064000000000000000000000000cf77a3ba9a5ca399b7c97c74d54e5b1beb874e430000000000000000000000002626664c2603336e57b271c5c0b26f421741e481000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000003000000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000000006a456b650000000000000000000000000000000000000000000000000000000000000144cac88ea900000000000000000000000000000000000000000000000000000000000f424000000000000000000000000000000000000000000000000000022f6adbf79c2900000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000000006a456b650000000000000000000000000000000000000000000000000000000000000001000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000042000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000000000000000000000000000420dd381b31aef6683db6b902084cb0ffece40da0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e404e45aaf0000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea450800000000000000000000000000000000000000000000000000022f6adbf79c2900000000000000000000000000000000000000000000000000000000000f2efc000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
  "calldata_bytes": 1092,
  "swap_legs": [
    {
      "leg": "BUY_WETH",
      "dex": "Aerodrome",
      "router_type": "solidly",
      "router_address": "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43",
      "token_in": "USDC",
      "token_in_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "token_out": "WETH",
      "token_out_address": "0x4200000000000000000000000000000000000006",
      "amount_in_units": "1000000",
      "amount_out_min_units": "615085956897833",
      "deadline": 1782934373,
      "calldata": "0xcac88ea900000000000000000000000000000000000000000000000000000000000f424000000000000000000000000000000000000000000000000000022f6adbf79c2900000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000000006a456b650000000000000000000000000000000000000000000000000000000000000001000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000042000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000000000000000000000000000420dd381b31aef6683db6b902084cb0ffece40da",
      "calldata_bytes": 324,
      "eth_call": {
        "from": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
        "to": "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43",
        "data": "0xcac88ea900000000000000000000000000000000000000000000000000000000000f424000000000000000000000000000000000000000000000000000022f6adbf79c2900000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000000006a456b650000000000000000000000000000000000000000000000000000000000000001000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000042000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000000000000000000000000000420dd381b31aef6683db6b902084cb0ffece40da",
        "value": "0x0"
      },
      "route_metadata": {
        "stable": false,
        "factory": "0x420dd381b31aef6683db6b902084cb0ffece40da"
      },
      "route_reconciliation": {
        "buy_expected_weth": "0.000615147471644998149",
        "buy_min_weth": "0.0006150859568978336491851",
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
      "amount_in_units": "615085956897833",
      "amount_out_min_units": "995068",
      "deadline": 1782934373,
      "calldata": "0x04e45aaf0000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea450800000000000000000000000000000000000000000000000000022f6adbf79c2900000000000000000000000000000000000000000000000000000000000f2efc0000000000000000000000000000000000000000000000000000000000000000",
      "calldata_bytes": 228,
      "eth_call": {
        "from": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
        "to": "0x2626664c2603336E57B271c5C0b26F421741e481",
        "data": "0x04e45aaf0000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea450800000000000000000000000000000000000000000000000000022f6adbf79c2900000000000000000000000000000000000000000000000000000000000f2efc0000000000000000000000000000000000000000000000000000000000000000",
        "value": "0x0"
      },
      "route_metadata": {
        "fee_tier": 500,
        "sqrt_price_limit_x96": 0
      },
      "route_reconciliation": {
        "sell_input_weth": "0.0006150859568978336491851",
        "sell_expected_usdc": "0.9951678076399642933247161321",
        "sell_min_usdc": "0.9950682908592002968953836605",
        "atomic_min_usdc": "1.0001"
      }
    }
  ],
  "eth_call": {
    "from": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
    "to": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
    "data": "0x59b467930000000000000000000000000000000000000000000000000000000000000020000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda029130000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000f424000000000000000000000000000000000000000000000000000000000000f42a40000000000000000000000000000000000000000000000000000000000000064000000000000000000000000cf77a3ba9a5ca399b7c97c74d54e5b1beb874e430000000000000000000000002626664c2603336e57b271c5c0b26f421741e481000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000003000000000000000000000000003e4e81ec69a073f157c6945c41e5c36fda7579a7000000000000000000000000000000000000000000000000000000006a456b650000000000000000000000000000000000000000000000000000000000000144cac88ea900000000000000000000000000000000000000000000000000000000000f424000000000000000000000000000000000000000000000000000022f6adbf79c2900000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea4508000000000000000000000000000000000000000000000000000000006a456b650000000000000000000000000000000000000000000000000000000000000001000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000042000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000000000000000000000000000420dd381b31aef6683db6b902084cb0ffece40da0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e404e45aaf0000000000000000000000004200000000000000000000000000000000000006000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda0291300000000000000000000000000000000000000000000000000000000000001f4000000000000000000000000f714213aec4d8dd3c95b209f5f5193c8c9ea450800000000000000000000000000000000000000000000000000022f6adbf79c2900000000000000000000000000000000000000000000000000000000000f2efc000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "value": "0x0"
  },
  "eth_call_result": {
    "status": "FAIL",
    "error": "ContractCustomError: ('0x88215f9c00000000000000000000000000000000000000000000000000000000000f2f7200000000000000000000000000000000000000000000000000000000000f42a4', '0x88215f9c00000000000000000000000000000000000000000000000000000000000f2f7200000000000000000000000000000000000000000000000000000000000f42a4')"
  },
  "eth_call_status": "FAIL",
  "eth_call_decoded_error": {
    "name": "ProfitTooLow",
    "amount_out_units": "995186",
    "required_out_units": "1000100",
    "amount_out_usdc": "0.995186",
    "required_out_usdc": "1.0001",
    "shortfall_usdc": "0.004914",
    "explanation": "Atomic route executed in simulation but did not meet the executor's minimum profitable output."
  },
  "approval_spender": "0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508",
  "selected_candidate": {
    "timestamp": "2026-07-01T19:30:03Z",
    "chain": "base",
    "pair": "USDC/WETH",
    "buy_source": "Aerodrome",
    "sell_source": "Uniswap V3",
    "buy_price": "0.000615147471644998149",
    "sell_price": "0.000618072602606094203",
    "source_decision": "WATCH",
    "gross_edge_pct": "0.4755",
    "configured_cost_buffer_pct": "0.3000",
    "reported_net_edge_pct": "0.1755",
    "estimated_price_impact_pct": "0.0112",
    "estimated_gas_usd": "0.0500",
    "estimated_gas_pct": "0.0100",
    "mev_risk": "MEDIUM",
    "mev_risk_buffer_pct": "0.0500",
    "stress_total_cost_pct": "0.3712",
    "stress_net_edge_pct": "0.1043",
    "requested_notional_usd": "1",
    "max_executable_notional_usd": "500.0000",
    "executable_ratio_pct": "100.0000",
    "depth_model": "POOL_DEPTH_LADDER",
    "pool_depth_status": "DEPTH_READY",
    "confidence": "MEDIUM",
    "realism_status": "WATCH_ONLY",
    "reason": "Stress model is informational because source decision is not BUY; confidence=MEDIUM.",
    "variant": "venue:Aerodrome->Uniswap V3",
    "buy_dex": "Aerodrome",
    "sell_dex": "Uniswap V3",
    "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE",
    "selection_reason": "Tight leg-slippage exact atomic eth_call sweep candidate.",
    "sweep_notional_usd": "1",
    "sweep_leg_slippage_bps": "1"
  },
  "selected_intent": {
    "pair": "USDC/WETH",
    "buy_dex": "Aerodrome",
    "sell_dex": "Uniswap V3",
    "notional_usd": "1",
    "max_slippage_bps": "1",
    "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE",
    "selection_reason": "Tight leg-slippage exact atomic eth_call sweep candidate."
  },
  "eth_call_success": {},
  "route_sweep": {
    "enabled": true,
    "strategy": "best_exact_atomic_eth_call_notional_venue_sweep",
    "candidate_count": 48,
    "attempt_count": 48,
    "passing_count": 0,
    "sweep_config": {
      "notionals_usd": [
        "1",
        "2",
        "5"
      ],
      "venues": [
        "Uniswap V2",
        "Uniswap V3",
        "Aerodrome"
      ],
      "venue_sweep_enabled": true,
      "leg_slippage_bps_list": [
        "1",
        "2",
        "5",
        "10",
        "25",
        "50"
      ],
      "legacy_single_leg_slippage_bps": "300"
    },
    "selected_attempt": {
      "attempt": 0,
      "status": "SIMULATION_ATTEMPTED",
      "eth_call_status": "FAIL",
      "decoded_error": "ProfitTooLow",
      "amount_in_usdc": "1",
      "simulated_atomic_out_usdc": "0.995186",
      "required_out_usdc": "1.0001",
      "shortfall_usdc": "0.004914",
      "candidate": {
        "timestamp": "2026-07-01T19:30:03Z",
        "pair": "USDC/WETH",
        "buy_dex": "Aerodrome",
        "sell_dex": "Uniswap V3",
        "variant": "venue:Aerodrome->Uniswap V3",
        "source_decision": "WATCH",
        "realism_status": "WATCH_ONLY",
        "gross_edge_pct": "0.4755",
        "stress_net_edge_pct": "0.1043",
        "sweep_notional_usd": "1",
        "sweep_leg_slippage_bps": "1",
        "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
      },
      "intent": {
        "pair": "USDC/WETH",
        "buy_dex": "Aerodrome",
        "sell_dex": "Uniswap V3",
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
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5",
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
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 5,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 6,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5",
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
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 8,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 9,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 10,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 11,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 12,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 13,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 14,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 15,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 16,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 17,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 18,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 19,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 20,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 21,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 22,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
        "attempt": 23,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
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
      },
      {
        "attempt": 24,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4951",
          "stress_net_edge_pct": "0.1170",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "WETH/USDC",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 25,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 26,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 27,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": "4.975712",
        "required_out_usdc": "5.0005",
        "shortfall_usdc": "0.024788",
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "original",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 28,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 29,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 30,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterRevert",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "reverse_dex",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 31,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": "0.995142",
        "required_out_usdc": "1.0001",
        "shortfall_usdc": "0.004958",
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 32,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": "1.990285",
        "required_out_usdc": "2.0002",
        "shortfall_usdc": "0.009915",
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 33,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": "4.975712",
        "required_out_usdc": "5.0005",
        "shortfall_usdc": "0.024788",
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Uniswap V2->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 34,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 35,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 36,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V2->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V2",
          "sell_dex": "Aerodrome",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 37,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 38,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 39,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Uniswap V3->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 40,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 41,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 42,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": null,
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "variant": "venue:Uniswap V3->Aerodrome",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Uniswap V3",
          "sell_dex": "Aerodrome",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 43,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "1.0001",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 44,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "2.0002",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 45,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "RouterInsufficientOutputAmount",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": null,
        "required_out_usdc": "5.0005",
        "shortfall_usdc": null,
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "variant": "venue:Aerodrome->Uniswap V2",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V2",
          "notional_usd": "5",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 46,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "1",
        "simulated_atomic_out_usdc": "0.995186",
        "required_out_usdc": "1.0001",
        "shortfall_usdc": "0.004914",
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "notional_usd": "1",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 47,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "2",
        "simulated_atomic_out_usdc": "1.990373",
        "required_out_usdc": "2.0002",
        "shortfall_usdc": "0.009827",
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "2",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "notional_usd": "2",
          "max_slippage_bps": "1",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        }
      },
      {
        "attempt": 48,
        "status": "SIMULATION_ATTEMPTED",
        "eth_call_status": "FAIL",
        "decoded_error": "ProfitTooLow",
        "amount_in_usdc": "5",
        "simulated_atomic_out_usdc": "4.975932",
        "required_out_usdc": "5.0005",
        "shortfall_usdc": "0.024568",
        "candidate": {
          "timestamp": "2026-07-01T19:30:03Z",
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "variant": "venue:Aerodrome->Uniswap V3",
          "source_decision": "WATCH",
          "realism_status": "WATCH_ONLY",
          "gross_edge_pct": "0.4755",
          "stress_net_edge_pct": "0.1043",
          "sweep_notional_usd": "5",
          "sweep_leg_slippage_bps": "1",
          "selection_mode": "ATOMIC_ROUTE_SWEEP_LEG_SLIPPAGE"
        },
        "intent": {
          "pair": "USDC/WETH",
          "buy_dex": "Aerodrome",
          "sell_dex": "Uniswap V3",
          "notional_usd": "5",
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
  "estimated_gross_out_usdc": "1.004951",
  "estimated_net_out_usdc": "1.001951",
  "estimated_stress_out_usdc": "1.001170",
  "simulated_atomic_out_usdc": "0.995186",
  "required_out_usdc": "1.0001",
  "estimated_stress_net_pct": "0.1170",
  "simulated_atomic_net_pct": "-0.4814",
  "stress_vs_atomic_divergence_pct": "0.5984",
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
