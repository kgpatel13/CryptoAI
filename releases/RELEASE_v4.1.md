# CryptoAI v4.1 - 24/7 Paper Operations Core

## Executive Summary

v4.1 starts the Operations Core for long-running paper-mode evidence collection. It adds heartbeat, runtime state, uptime tracking, graceful shutdown, Mission Control summaries, operational metrics, and a managed continuous `paper_autopilot --loop`.

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
Paper Autopilot Loop
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
- `app/automation/paper_autopilot.py`
- `app/dashboard/main_dashboard.py`

## New Files

- `app/operations/__init__.py`
- `app/operations/models.py`
- `app/operations/runtime.py`
- `tests/test_operations_runtime.py`
- `docs/OPERATIONS.md`
- `releases/RELEASE_v4.1.md`

## Tests

- Added runtime tests for heartbeat, runtime state, mission summary, operational metrics, failed cycles, and autopilot loop wiring.

## Documentation

- Added `docs/OPERATIONS.md`.
- Updated README commands and current version.
- Updated roadmap for v4.1 through v7.0.
- Updated changelog.

## Validation Commands

```bash
python -m compileall -q app tests
python -m unittest discover -s tests -v
python -m app.automation.paper_autopilot --loop --interval-seconds 300 --heartbeat-interval-seconds 60 --max-cycles 1
```

## Expected Output

- Unit tests pass.
- `data/heartbeat.json` exists.
- `data/runtime_state.json` exists.
- `reports/operational_metrics.json` exists.
- `reports/mission_summary.json` exists.
- `reports/mission_summary.md` exists.
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
```
