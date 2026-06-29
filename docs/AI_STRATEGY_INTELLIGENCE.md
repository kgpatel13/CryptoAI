# CryptoAI AI Strategy Intelligence

## Purpose

AI Strategy Intelligence is the first v5.0 advisory layer. It compares strategies using measured paper evidence and produces explainable recommendations for research, watchlist, or paper optimization.

It does not approve live trading.

## Inputs

- `reports/strategy_center.json`
- `reports/feature_store.json`
- `reports/replay_diagnostics.json`
- `reports/execution_cost_evidence.json`
- `reports/market_universe_evidence.json`
- `reports/quote_coverage_evidence.json`
- `reports/eth_route_architecture.json`
- `reports/eth_market_coverage.json`
- `reports/optimization_report.json`
- `reports/experiment_report.json`
- `reports/provider_monitor.json`
- `reports/paper_report.json`
- `reports/report_audit.json`

## Outputs

- `reports/strategy_intelligence.json`
- `reports/strategy_intelligence.md`

## Recommendations

- `RESEARCH_DISABLED` - strategy is disabled in the registry.
- `HOLD_FIX_OPERATIONS` - provider or audit findings block responsible tuning.
- `CONTINUE_RESEARCH` - experiment evidence still has failing gates.
- `WATCHLIST` - evidence is improving, but more paper data is needed.
- `PAPER_OPTIMIZE_CANDIDATE` - paper evidence is strong enough for walk-forward and optimization review.
- `NEEDS_MORE_DATA` - not enough measured evidence exists.

## Command

```bash
python -m app.ai.strategy_intelligence_service
```

## Safety

The report always sets `promotion_allowed` to `false`. Risk remains the final authority before paper execution, and live trading remains disabled until separate live-readiness gates are implemented and approved.
