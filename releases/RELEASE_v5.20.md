# v5.20 - Live Execution Engine

## Summary

Adds a read-only Live Execution Engine that turns wallet, readiness, transaction simulation, tiny-live pilot, provider, and audit reports into one live-operation state machine.

## Highlights

- Adds `app.execution.live_execution_engine_service`.
- Produces `reports/live_execution_engine.json` and `reports/live_execution_engine.md`.
- Shows whether manual approval, manual tiny smoke swap, or continuous live arbitrage is allowed.
- Blocks continuous live arbitrage until a reviewed atomic executor path exists.
- Adds dashboard integration under Live Control Center plus runtime file tracking.
- Adds regression tests proving the engine is read-only and keeps live automation blocked unless all gates are green.

## Commands

```powershell
python -m app.execution.live_execution_engine_service
python -m app.execution.live_execution_engine_service --loop --interval 30
```

The loop is a monitor only. It does not sign, approve, swap, or trade.
