# CryptoAI v5.1 - Replay Diagnostics and Evidence Gap Analysis

## Executive Summary

v5.1 improves the main finding from v5.0: default replay still has zero production-buffer trades even though optimization is profitable at lower buffers. This release adds Replay Diagnostics to quantify that gap without lowering risk thresholds automatically.

Live trading remains disabled.

## Key Changes

- Added `ReplayDiagnosticsService`.
- Added `replay_diagnostics.json` and `replay_diagnostics.md`.
- Compared production cost buffer against lower-buffer research scenarios.
- Integrated replay diagnostics into Experiment Evidence summaries.
- Integrated replay diagnostics into Strategy Intelligence blockers and next actions.
- Added dashboard controls and metrics for Replay Diagnostics.
- Added Replay Diagnostics to Report Audit expected reports.
- Added regression test coverage for lower-buffer diagnostic findings.

## Safety

Replay Diagnostics is explanatory only. It does not change risk thresholds, paper thresholds, or live-trading eligibility.

## Validation Commands

```bash
python -m app.backtesting.replay_diagnostics_service
python -m app.reporting.report_audit
python -m app.backtesting.experiment_service
python -m app.ai.strategy_intelligence_service
python -m app.reporting.report_audit
python -m compileall -q app tests
python -m unittest discover -s tests -v
```

## Git Commit Message

```text
v5.1 - Add replay diagnostics for evidence gaps
```

## Rollback Instructions

```bash
git revert <v5.1-commit-sha>
```

Generated Replay Diagnostics reports can be removed and regenerated safely:

```bash
rm -f reports/replay_diagnostics.json reports/replay_diagnostics.md
```
