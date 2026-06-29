# CryptoAI v5.3 - Market Universe and Settings Evidence

## Executive Summary

v5.3 adds a Market Universe Evidence layer that ranks chain/pair/DEX coverage and research-only settings from measured evidence.

The current best focus remains Base `WETH/USDC`. Other configured chains and pairs are treated as expansion candidates until quote-provider and provider-health evidence exists.

Live trading remains disabled.

## Key Changes

- Added `MarketUniverseEvidenceService`.
- Added `market_universe_evidence.json` and `market_universe_evidence.md`.
- Classified configured pairs as active focus, research target, blocked by missing quotes, or watchlist.
- Added research-only settings evidence from optimization and execution-cost reports.
- Clarified replay diagnostics so production trades require both the production cost buffer and the paper BUY threshold.
- Integrated market universe evidence into Strategy Intelligence next actions.
- Integrated market universe evidence into Experiment Evidence.
- Added dashboard generation, metrics, tables, and report display.
- Added Market Universe Evidence to Report Audit expected reports.
- Added docs and regression tests.

## Safety

v5.3 does not change:

- production cost buffer
- paper trading threshold
- risk thresholds
- live-trading eligibility

Lower-buffer settings remain research-only until high-confidence execution-cost evidence, stable replay results, clean provider health, and larger paper samples support a reviewed change.

## Validation Commands

```bash
python -m app.market_intelligence.market_intelligence_service
python -m app.operations.provider_monitor
python -m app.backtesting.backtest_service
python -m app.backtesting.replay_diagnostics_service
python -m app.execution.execution_cost_evidence_service
python -m app.backtesting.optimization_service
python -m app.research.market_universe_evidence_service
python -m app.reporting.report_audit
python -m app.backtesting.experiment_service
python -m app.ai.strategy_intelligence_service
python -m app.reporting.report_audit
python -m compileall -q app tests
python -m unittest discover -s tests -v
```

## Git Commit Message

```text
v5.3 - Add market universe and settings evidence
```

## Rollback Instructions

```bash
git revert <v5.3-commit-sha>
```

Generated Market Universe Evidence reports can be removed and regenerated safely:

```bash
rm -f reports/market_universe_evidence.json reports/market_universe_evidence.md
```
