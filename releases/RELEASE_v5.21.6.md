# v5.21.6 - Paper Live-Shadow Enforcement Hotfix

Date: 30-Jun-2026

## Summary

Hardens live-parity paper trading so a paper arbitrage fill cannot be recorded unless it has an explicit live-shadow verdict.

## Changes

- Fixed paper autopilot single-instance detection by importing the missing JSON module.
- Centralized strict live-shadow enforcement inside paper execution.
- Converts any strict-mode closed paper fill without `SHADOW_ELIGIBLE` into a zero-notional `SKIPPED` order.
- Marks normal risk-threshold skips as `NOT_EVALUATED` instead of leaving dashboard/report rows ambiguous.
- Added regression coverage for missing shadow verdicts and risk-skip shadow labeling.

## Verification

- `python -m unittest tests.test_live_shadow_gate_service tests.test_paper_settings_service tests.test_paper_run_review`
- `python -m unittest discover -s tests -p "test_*.py"`

Both passes completed successfully with 153 total tests.
