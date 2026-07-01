# Atomic Live Arbitrage Simulation

Generated: `2026-07-01T05:21:27Z`
- Overall status: `ATOMIC_ROUTE_ACTION`
- Atomic route simulation passed: `False`
- Live trading approval: `False`
- Executor: `-`
- Executor preflight: `READY`
- eth_call status: `-`
- Blocked checks: `1`
- Action checks: `3`

## Checks

| Check | Status | Detail |
|---|---|---|
| two_leg_transaction_simulation_passed | ACTION | Two-leg router calldata simulation must pass first. |
| not_one_leg_smoke | BLOCK | Atomic live arbitrage cannot use the one-leg smoke route. |
| executor_configured | PASS | Atomic executor address is configured. |
| executor_deployed | PASS | Atomic executor bytecode exists on Base. |
| executor_reviewed | PASS | Atomic executor review flag is present. |
| executor_usdc_allowance | PASS | USDC allowance to atomic executor is sufficient or no executable route is ready. |
| atomic_calldata_built | ACTION | Atomic executor calldata was not built. |
| atomic_eth_call_passed | ACTION | Atomic executor eth_call did not pass. |

## Atomic Route

```json
{
  "status": "BLOCKED",
  "reason": "Atomic arbitrage requires a two-leg SHADOW_READY arbitrage candidate, not the one-leg smoke route."
}
```

## Notes

- This report is the final evidence gate for atomic live arbitrage.
- It builds one executor transaction and simulates it with eth_call only.
- No transaction is signed or broadcast by this service.
- The wallet must approve USDC to the atomic executor, not just to an individual router.
