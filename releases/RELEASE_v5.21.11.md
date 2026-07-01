# CryptoAI v5.21.11 - One-Command Tiny Live Smoke Flow

## Summary

Adds a one-command orchestrator for the capped tiny live smoke flow. The flow reduces manual step confusion while preserving explicit real-money confirmation.

## Changes

- Added `app.execution.tiny_live_smoke_flow_service`.
- Supports `--mode plan` for no-send review.
- Supports `--mode run --confirm LIVE_SMOKE_FLOW_APPROVED` for the gated live smoke sequence.
- The run sequence:
  - regenerates safe reports without a private key,
  - checks the tiny live plan,
  - sends approval only if allowance is insufficient,
  - regenerates transaction simulation after approval,
  - sends the capped one-leg smoke swap only if simulation passes.
- Keeps autonomous live arbitrage disabled.

## Validation

- `python -m unittest tests.test_tiny_live_smoke_flow_service tests.test_tiny_live_pilot_service tests.test_transaction_simulation_service`
- `python -m unittest discover -s tests -p "test_*.py"`

## Live Trading Status

This release improves operator ergonomics for the manual `$20` smoke test. It does not remove real-money confirmation and does not enable continuous live trading.
