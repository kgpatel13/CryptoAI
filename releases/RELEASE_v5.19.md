# v5.19 - Tiny Live Pilot Harness

## Summary

v5.19 adds the first guarded live execution harness. It is deliberately limited to a manual, tiny Base USDC->WETH smoke test so the project can validate real wallet, approval, signing, gas, receipt, and balance behavior before attempting any production live strategy.

This is not autonomous live arbitrage. Cross-DEX arbitrage remains blocked until an atomic executor contract exists.

## What Changed

- Added `TinyLivePilotService`.
- Added reports:
  - `reports/tiny_live_pilot.json`
  - `reports/tiny_live_pilot.md`
- Added live pilot journal:
  - `data/live_pilot_orders.jsonl`
- Added modes:
  - `plan`: prepare and report only; never signs or sends.
  - `approve`: sends only a capped USDC approval after all gates and manual confirmation pass.
  - `swap`: sends only a one-leg USDC->WETH smoke swap after all gates, allowance, and explicit one-leg acknowledgement pass.
- Added dashboard integration under Risk & Controls and Reports.
- Added Report Audit coverage for the tiny live pilot report.

## Hard Gates

Approve/swap mode requires:

- `CRYPTOAI_ENABLE_TINY_LIVE_PILOT=true`
- `CRYPTOAI_LIVE_TRADING_ENABLED=true`
- `CRYPTOAI_LIVE_KILL_SWITCH_ENABLED=false`
- `CRYPTOAI_PRIVATE_KEY` configured locally and matching `CRYPTOAI_LIVE_WALLET_ADDRESS`
- no paper autopilot process running
- wallet preflight ready
- live readiness checklist ready
- transaction simulation passed
- provider monitor OK
- report audit has zero blocking findings
- smoke size <= `$10`
- manual confirmation phrase: `LIVE_PILOT_APPROVED`

Swap mode additionally requires:

- sufficient USDC allowance
- `CRYPTOAI_ALLOW_ONE_LEG_SMOKE_SWAP=true`

## Safety Notes

- Never paste the private key into chat or commit it to files.
- The first live test should be `$5` or less.
- A one-leg smoke swap may lose money from spread, slippage, and gas. It is only an infrastructure test.
- Production arbitrage still requires an atomic executor or equivalent atomic route before live profit-seeking trading.

## Tests

- `python -m unittest tests.test_tiny_live_pilot_service`

## Rollback

Rollback is limited to:

- `app/execution/tiny_live_pilot_service.py`
- `tests/test_tiny_live_pilot_service.py`
- `app/dashboard/main_dashboard.py`
- `app/reporting/report_audit.py`
- `CHANGELOG.md`
- this release note
