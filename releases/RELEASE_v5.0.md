# CryptoAI v5.0 - AI Strategy Intelligence

## Executive Summary

v5.0 starts AI Strategy Intelligence as a measured, advisory layer above the existing strategy/research foundation. It scores strategies from current paper evidence, optimization results, experiment gates, provider health, and report audit status.

Live trading remains disabled.

## Key Changes

- Added `StrategyIntelligenceService`.
- Added `strategy_intelligence.json` and `strategy_intelligence.md`.
- Added dashboard page for AI Strategy Intelligence.
- Added Strategy Intelligence to Report Audit expected reports.
- Added deterministic scoring factors, blockers, recommendations, and next actions.
- Added regression tests for clean evidence and experiment-failure behavior.

## Recommendation States

- `RESEARCH_DISABLED`
- `HOLD_FIX_OPERATIONS`
- `CONTINUE_RESEARCH`
- `WATCHLIST`
- `PAPER_OPTIMIZE_CANDIDATE`
- `NEEDS_MORE_DATA`

## Validation Commands

```bash
python -m app.ai.strategy_intelligence_service
python -m app.reporting.report_audit
python -m compileall -q app tests
python -m unittest discover -s tests -v
```

## Git Commit Message

```text
v5.0 - Add AI strategy intelligence foundation
```

## Rollback Instructions

```bash
git revert <v5.0-commit-sha>
```

Generated Strategy Intelligence reports can be removed and regenerated safely:

```bash
rm -f reports/strategy_intelligence.json reports/strategy_intelligence.md
```
