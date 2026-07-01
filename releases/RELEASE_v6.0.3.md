# v6.0.3 - Atomic Profit Reconciliation

## Summary

Added atomic route profit reconciliation so live readiness can explain why a SHADOW_READY opportunity fails the exact executor `eth_call`.

## Changes

- Decode atomic executor `ProfitTooLow` custom errors into USDC amount out, required output, and shortfall.
- Compare opportunity-estimated gross/net/stress output against the exact atomic simulation result.
- Mark atomic executor simulation as the authoritative live gate when the atomic route exists.
- Keep live sends blocked when the executor proves the route is not profitable.

## Validation

- Full regression suite: `178/178` tests passed.
- Latest atomic report shows calldata reached the executor, but the executor correctly rejected the route because simulated output was below the required profitable amount.

