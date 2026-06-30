# v5.19.2 - Live Control Center

## Summary

Adds a read-only Live Control Center for tiny-live pilot preparation.

## Changes

- Added `app.execution.live_control_center_service`.
- Added a continuous read-only monitor command:
  `python -m app.execution.live_control_center_service --loop --interval 30`
- Added a dashboard page for live wallet, readiness, transaction simulation, and tiny pilot status.
- Added regression tests proving the control center does not expose a continuous live trading command.

## Safety

- This release does not enable continuous live trading.
- This release does not bypass live readiness, transaction simulation, or tiny pilot gates.
- The only live-capable path remains the manually confirmed tiny live pilot.
