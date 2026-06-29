# CryptoAI v4.1 Operations Core

## Executive Summary

v4.1 starts the 24/7 paper operations layer. The goal is reliable long-running paper evidence collection, not live execution.

The operations runtime owns process heartbeat, runtime state, uptime tracking, graceful shutdown, operational metrics, and Mission Control summaries for continuous `paper_autopilot --loop` runs.

## Architecture Diagram

```text
Paper Autopilot CLI
        |
        v
Operations Runtime
        |
        +--> Heartbeat
        +--> Runtime State
        +--> Operational Metrics
        +--> Mission Summary
        |
        v
SchedulerService.run_once()
        |
        v
Quotes -> Strategy -> AI Ranking -> Risk -> Paper Execution
```

## Runtime Files

- `data/heartbeat.json` - latest process heartbeat.
- `data/heartbeat_history.jsonl` - append-only heartbeat history.
- `data/runtime_state.json` - latest runtime state.
- `reports/operational_metrics.json` - cycle counts, failures, latency, heartbeat count, and status counts.
- `reports/mission_summary.json` - Mission Control machine-readable summary.
- `reports/mission_summary.md` - Mission Control human-readable summary.

## Commands

Run one cycle:

```bash
python -m app.automation.paper_autopilot --once
```

Run continuously in paper mode:

```bash
python -m app.automation.paper_autopilot --loop --interval-seconds 300 --heartbeat-interval-seconds 60
```

Bounded validation run:

```bash
python -m app.automation.paper_autopilot --loop --interval-seconds 300 --heartbeat-interval-seconds 60 --max-cycles 2
```

## Safety

- Live trading remains disabled.
- The runtime reports `live_trading_enabled` in Mission Control summaries.
- The paper autopilot still refuses to start when `CRYPTOAI_LIVE_TRADING_ENABLED` is truthy.
- AI ranking remains advisory.
- Risk remains the final authority before paper execution.

## Validation

```bash
python -m compileall -q app tests
python -m unittest discover -s tests -v
python -m app.automation.paper_autopilot --loop --interval-seconds 300 --heartbeat-interval-seconds 60 --max-cycles 1
```

Expected files after a loop run:

```text
data/heartbeat.json
data/heartbeat_history.jsonl
data/runtime_state.json
reports/operational_metrics.json
reports/mission_summary.json
reports/mission_summary.md
```

## Rollback

Remove the v4.1 operations files and restore the previous `paper_autopilot` loop implementation from the prior release tag or commit. Runtime output files can be deleted safely because they are generated artifacts.
