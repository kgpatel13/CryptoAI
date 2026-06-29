# CryptoAI v4.1 - 24/7 Paper Operations Core

## Executive Summary

v4.1 starts the Operations Core for long-running paper-mode evidence collection. It adds heartbeat, runtime state, uptime tracking, graceful shutdown, Mission Control summaries, operational metrics, Market Intelligence readiness reporting, Provider Monitoring, and a managed continuous `paper_autopilot --loop`.

Live trading remains disabled.

## Architecture Diagram

```text
Mission Control
        ^
        |
Heartbeat / Runtime State / Metrics / Summary
        ^
        |
Operations Runtime
        |
        v
Provider Monitor + Market Intelligence + Paper Autopilot Loop
        |
        v
SchedulerService.run_once()
        |
        v
Quotes -> Strategy -> AI Ranking -> Risk -> Paper Execution
```

## Modified Files

- `README.md`
- `CHANGELOG.md`
- `docs/ROADMAP.md`
- `docs/OPERATIONS.md`
- `app/automation/paper_autopilot.py`
- `app/dashboard/main_dashboard.py`

## New Files

- `app/operations/__init__.py`
- `app/operations/models.py`
- `app/operations/provider_monitor.py`
- `app/operations/runtime.py`
- `app/market_intelligence/__init__.py`
- `app/market_intelligence/models.py`
- `app/market_intelligence/market_intelligence_service.py`
- `tests/test_operations_runtime.py`
- `tests/test_market_intelligence.py`
- `tests/test_provider_monitor.py`
- `docs/OPERATIONS.md`
- `docs/MARKET_INTELLIGENCE.md`
- `docs/PROVIDER_MONITORING.md`
- `releases/RELEASE_v4.1.md`

## Tests

- Added runtime tests for heartbeat, runtime state, mission summary, operational metrics, failed cycles, and autopilot loop wiring.
- Added Market Intelligence tests for pair generation, readiness scoring, provider-health ingestion, and report creation.
- Added Provider Monitor tests for OK, WATCH, DEGRADED, CRITICAL, stale, and missing-data statuses.

## Documentation

- Added `docs/OPERATIONS.md`.
- Added `docs/MARKET_INTELLIGENCE.md`.
- Added `docs/PROVIDER_MONITORING.md`.
- Updated README commands and current version.
- Updated roadmap for v4.1 through v7.0.
- Updated changelog.

## Validation Commands

```bash
python -m compileall -q app tests
python -m unittest discover -s tests -v
python -m app.operations.provider_monitor
python -m app.market_intelligence.market_intelligence_service
python -m app.automation.paper_autopilot --loop --interval-seconds 300 --heartbeat-interval-seconds 60 --max-cycles 1
```

## Expected Output

- Unit tests pass.
- `data/heartbeat.json` exists.
- `data/runtime_state.json` exists.
- `reports/operational_metrics.json` exists.
- `reports/mission_summary.json` exists.
- `reports/mission_summary.md` exists.
- `reports/market_intelligence.json` exists.
- `reports/market_intelligence.md` exists.
- `reports/provider_monitor.json` exists.
- `reports/provider_monitor.md` exists.
- Mission Control shows paper runtime status when the dashboard is opened.

## Git Commit Message

```text
v4.1 - Add 24/7 paper operations core
```

## Rollback Instructions

```bash
git revert <v4.1-commit-sha>
```

Generated runtime artifacts can be removed safely:

```bash
rm -f data/heartbeat.json data/heartbeat_history.jsonl data/runtime_state.json
rm -f reports/operational_metrics.json reports/mission_summary.json reports/mission_summary.md
rm -f reports/market_intelligence.json reports/market_intelligence.md
rm -f reports/provider_monitor.json reports/provider_monitor.md
```
