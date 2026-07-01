# CryptoAI v5.21.10 - Tiny Live Smoke Gate Refinement

## Summary

Separates the manual tiny-live smoke-test flow from full autonomous arbitrage readiness so the system can safely progress through preflight, approval, exact smoke-swap simulation, and then one capped smoke swap.

## Changes

- Preserved buy/sell prices in execution-realism evidence for downstream transaction simulation.
- Updated transaction simulation to ignore unsupported live DEX routes and fall back to an exact Uniswap V3 one-leg `USDC -> WETH` smoke-swap simulation.
- Removed the circular dependency where transaction simulation required full live readiness before it could make live readiness pass.
- Allowed manual approval mode after wallet preflight without requiring swap simulation first.
- Allowed manual smoke swap mode only after transaction simulation passes and live readiness has no hard blockers.
- Updated live readiness to recognize historical paper fills at or below the configured tiny live trade cap.
- Isolated live-shadow tests from workspace report state.

## Validation

- `python -m unittest tests.test_transaction_simulation_service tests.test_live_readiness_checklist_service tests.test_tiny_live_pilot_service tests.test_live_shadow_gate_service`
- `python -m unittest discover -s tests -p "test_*.py"`

## Live Trading Status

This release supports a manual capped `$20` one-leg live smoke flow. It does not enable autonomous live arbitrage or `$449` live trading.
