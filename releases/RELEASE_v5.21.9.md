# CryptoAI v5.21.9 - Live-Parity Paper Duplicate Signal Guard

## Summary

Adds a live-parity paper guard that blocks repeated identical arbitrage snapshots within a configurable time window before they can inflate paper PnL or live-shadow evidence.

## Changes

- Added `CRYPTOAI_ARBITRAGE_SIGNAL_FINGERPRINT_WINDOW_SECONDS` support to portfolio risk.
- Added a 60-second arbitrage signal fingerprint guard to the `live_parity_500` paper profile.
- Updated the live-parity profile to use a paper-only `$500` notional probe against a `$500` wallet ceiling.
- Persisted arbitrage signal fingerprint and signal timestamp into the paper order journal for audit review.
- Added regression coverage for repeated arbitrage snapshot rejection, paper settings export, and portfolio risk duplicate detection.

## Validation

- `python -m unittest tests.test_arbitrage_execution_engine tests.test_portfolio_risk_service tests.test_paper_settings_service`
- `python -m unittest discover -s tests -p "test_*.py"`
- Two-cycle live-parity paper probe confirmed one `$500` shadow-eligible close followed by duplicate `RISK_REJECTED` within the 60-second window.

## Live Trading Status

Live trading remains disabled. This release improves paper/live evidence quality but does not approve autonomous real-money execution.
