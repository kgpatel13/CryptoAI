# v5.21.4 - Gated Continuous Live Autopilot Path

## Summary

Upgrades the live autopilot from a read-only shell into a fail-closed continuous-live execution path that mirrors paper autopilot control flow.

## Changes

- Adds an injectable live execution adapter interface to `app.execution.live_autopilot`.
- Keeps the default adapter fail-closed until a reviewed atomic live executor is configured.
- Adds a protected continuous-live send branch that requires:
  - `can_run_continuous_live = true` from the Live Execution Engine,
  - `CRYPTOAI_LIVE_AUTOPILOT_SEND_ENABLED=true`,
  - a reviewed execution adapter.
- Journals every live autopilot cycle with the decision and execution result.
- Exposes the future continuous-live command from the Live Execution Engine only when all gates are green.

## Safety

This release does not bypass live-readiness gates, transaction simulation, or the atomic-executor requirement. With the default adapter, even a green engine still refuses live sends until the reviewed adapter is supplied.

## Verification

```powershell
python -m unittest tests.test_live_autopilot tests.test_live_execution_engine_service
python -m unittest discover -s tests
```

## Commit Message

```text
v5.21.4 - Add gated continuous live autopilot path
```
