# CryptoAI v5.2 - Execution Cost Evidence Engine

## Executive Summary

v5.2 adds an Execution Cost Evidence Engine to measure whether the unchanged `0.30%` production cost buffer is conservative, accurate, too high, or too low based on paper execution, replay, quote, and provider evidence.

Live trading remains disabled.

## Key Changes

- Added `ExecutionCostEvidenceService`.
- Added `execution_cost_evidence.json` and `execution_cost_evidence.md`.
- Measures paper slippage, latency, quote health, provider health, and replay edge distribution.
- Classifies the production buffer without changing production thresholds.
- Integrated execution cost evidence into Experiment Evidence summaries.
- Integrated execution cost context into Strategy Intelligence next actions.
- Added dashboard controls and metrics for Execution Cost Evidence.
- Added Execution Cost Evidence to Report Audit expected reports.
- Added regression tests for cost lower-bound measurement, too-high classification, and insufficient samples.

## Safety

v5.2 does not change:

- production cost buffer
- paper trading threshold
- risk thresholds
- live-trading eligibility

Paper slippage plus configured gas is treated as a measured lower bound, not as a complete live execution-cost estimate.

## Validation Commands

```bash
python -m app.execution.execution_cost_evidence_service
python -m app.reporting.report_audit
python -m app.backtesting.experiment_service
python -m app.ai.strategy_intelligence_service
python -m app.reporting.report_audit
python -m compileall -q app tests
python -m unittest discover -s tests -v
```

## Git Commit Message

```text
v5.2 - Add execution cost evidence engine
```

## Rollback Instructions

```bash
git revert <v5.2-commit-sha>
```

Generated Execution Cost Evidence reports can be removed and regenerated safely:

```bash
rm -f reports/execution_cost_evidence.json reports/execution_cost_evidence.md
```
