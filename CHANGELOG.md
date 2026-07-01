# v6.2 - Live Route Refresh Fix

## Fixed

- Live readiness no longer relies on old `atomic_live_arbitrage.json`.
- Atomic candidate selection now rejects stale candidates using `CRYPTOAI_ATOMIC_MAX_CANDIDATE_AGE_SECONDS`.
- Transaction simulation now refreshes quote/opportunity/realism evidence before selecting a live atomic route.
- Atomic live adapter regenerates the atomic route report before send.
- Atomic send flag is checked before any send attempt.

## Safety

- No live safety gates were weakened.
- No profit thresholds were reduced.
- No transaction is sent unless current-cycle atomic eth_call passes.
