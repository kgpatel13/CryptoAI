# Atomic Live Arbitrage Simulation

Generated: `2026-07-01T17:29:47Z`
- Overall status: `ATOMIC_ROUTE_ACTION`
- Atomic route simulation passed: `False`
- Live trading approval: `False`
- Executor: `-`
- Executor preflight: `READY`
- eth_call status: `-`
- Route blocker: `NO_TWO_LEG_CANDIDATE`
- Profit reconciliation: `NO_ATOMIC_ROUTE`
- Blocked checks: `1`
- Action checks: `3`

## Checks

| Check | Status | Detail |
|---|---|---|
| two_leg_candidate_selected | ACTION | A BUY plus SHADOW_READY two-leg candidate must be selected. |
| not_one_leg_smoke | BLOCK | Atomic live arbitrage cannot use the one-leg smoke route. |
| executor_configured | PASS | Atomic executor address is configured. |
| executor_deployed | PASS | Atomic executor bytecode exists on Base. |
| executor_reviewed | PASS | Atomic executor review flag is present. |
| executor_usdc_allowance | PASS | USDC allowance to atomic executor is sufficient or no executable route is ready. |
| atomic_calldata_built | ACTION | Atomic executor calldata was not built. |
| atomic_eth_call_passed | ACTION | Atomic executor eth_call did not pass. |

## Route Diagnostics

```json
{
  "blocker_type": "NO_TWO_LEG_CANDIDATE",
  "next_action": "The simulator fell back to one-leg smoke mode because no approved two-leg SHADOW_READY route was selected.",
  "transaction_simulation_passed": false,
  "transaction_simulation_status": "TX_SIMULATION_ACTION",
  "simulation_type": "TINY_LIVE_SMOKE",
  "selected_candidate_found": false,
  "selected_candidate": {},
  "latest_opportunity_count": 2,
  "latest_diagnostics_count": 2,
  "buy_candidate_count": 0,
  "shadow_ready_count": 0,
  "latest_opportunities": [
    {
      "timestamp": "2026-07-01T16:15:06Z",
      "chain": "base",
      "pair": "WETH/USDC",
      "buy_dex": "Uniswap V2",
      "sell_dex": "Uniswap V3",
      "source_decision": "WATCH",
      "realism_status": "WATCH_ONLY",
      "gross_edge_pct": "0.4215",
      "reported_net_edge_pct": "0.1215",
      "stress_net_edge_pct": "0.0434",
      "required_threshold_pct": "0.30",
      "confidence": "MEDIUM",
      "requested_notional_usd": "500.0000",
      "max_executable_notional_usd": "500.0000",
      "executable_ratio_pct": "100.0000",
      "pool_depth_status": "DEPTH_READY",
      "reason": "Stress model is informational because source decision is not BUY; confidence=MEDIUM.",
      "diagnostic_reasons": [
        "source_decision is WATCH, not BUY",
        "realism_status is WATCH_ONLY, not SHADOW_READY"
      ]
    },
    {
      "timestamp": "2026-07-01T16:15:06Z",
      "chain": "base",
      "pair": "USDC/WETH",
      "buy_dex": "Uniswap V2",
      "sell_dex": "Uniswap V3",
      "source_decision": "WATCH",
      "realism_status": "WATCH_ONLY",
      "gross_edge_pct": "0.5473",
      "reported_net_edge_pct": "0.2473",
      "stress_net_edge_pct": "0.1761",
      "required_threshold_pct": "0.30",
      "confidence": "MEDIUM",
      "requested_notional_usd": "500.0000",
      "max_executable_notional_usd": "500.0000",
      "executable_ratio_pct": "100.0000",
      "pool_depth_status": "DEPTH_READY",
      "reason": "Stress model is informational because source decision is not BUY; confidence=MEDIUM.",
      "diagnostic_reasons": [
        "source_decision is WATCH, not BUY",
        "realism_status is WATCH_ONLY, not SHADOW_READY"
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
  "status": "BLOCKED",
  "reason": "Atomic arbitrage requires a two-leg SHADOW_READY arbitrage candidate, not the one-leg smoke route."
}
```

## Profit Reconciliation

```json
{
  "status": "NO_ATOMIC_ROUTE",
  "amount_in_usdc": null,
  "estimated_gross_out_usdc": null,
  "estimated_net_out_usdc": null,
  "estimated_stress_out_usdc": null,
  "simulated_atomic_out_usdc": "0",
  "required_out_usdc": null,
  "estimated_stress_net_pct": "0",
  "simulated_atomic_net_pct": null,
  "stress_vs_atomic_divergence_pct": null,
  "findings": []
}
```

## Notes

- This report is the final evidence gate for atomic live arbitrage.
- It builds one executor transaction and simulates it with eth_call only.
- No transaction is signed or broadcast by this service.
- The wallet must approve USDC to the atomic executor, not just to an individual router.
