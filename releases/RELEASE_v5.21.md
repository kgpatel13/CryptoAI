# v5.21 - Live Autopilot Runner Shell

## Summary

Adds a paper-like live autopilot command that continuously evaluates live execution readiness and journals decisions without sending real transactions.

## Highlights

- Adds `app.execution.live_autopilot`.
- Adds `data/live_autopilot_decisions.jsonl` as the live decision journal.
- Mirrors paper autopilot operations with `--once`, `--loop`, interval control, and a single-instance lock.
- Refuses actual transaction sending until a reviewed live execution adapter exists.
- Refuses live autopilot startup when paper autopilot is already running.
- Adds dashboard command visibility and runtime-file tracking.

## Command

```powershell
python -m app.execution.live_autopilot --loop --interval-seconds 0
```

This is currently a live-readiness runner only. It does not approve, swap, or trade.
