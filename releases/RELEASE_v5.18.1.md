# v5.18.1 - Paper Autopilot Guard and Readiness Refresh

## Summary

This hotfix protects 24/7 paper evidence from accidental duplicate autopilot processes and keeps live-readiness reports fresh during paper cycles.

## What Changed

- Added an OS-level `SingleInstanceLock` for looped paper autopilot runs.
- Refuses to start a second loop while another paper autopilot lock is active.
- Prints a clean `REFUSED` response instead of a traceback when a duplicate loop is attempted.
- Refreshes these reports during autopilot cycles:
  - execution-cost evidence
  - execution realism
  - wallet preflight
  - live safety
  - transaction simulation
  - live readiness checklist
  - report audit
- Keeps live trading disabled.

## Current Paper Run Finding

The reviewed run is profitable but not shadow/live ready:

- Closed trades: `25`
- Open positions: `0`
- Cash: `$505.7300`
- Realized PnL: `$5.7300`
- Execution realism: `NOT_SHADOW_READY`
- Main blocker: stressed net edge is negative after price-impact, gas, and MEV buffers.

## Tests

- `python -m unittest tests.test_operations_runtime`

## Rollback

Rollback is limited to `app/automation/paper_autopilot.py`, `tests/test_operations_runtime.py`, `CHANGELOG.md`, and this release note.
