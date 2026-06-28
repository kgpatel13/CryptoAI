# CryptoAI v3.5 — Portfolio Analytics & PnL Engine

## Objective

This release adds portfolio analytics on top of the v3.4/v3.4.1 execution and accounting foundation.

The goal is to answer a core production question:

> Is CryptoAI improving or degrading the paper portfolio over time?

## Added

1. Portfolio analytics service.
2. Paper trade journal generation.
3. Daily realized PnL summary.
4. Equity curve calculation.
5. Return percentage calculation.
6. Win/loss/breakeven counts.
7. Win rate.
8. Gross profit and gross loss.
9. Profit factor.
10. Expectancy per closed/PnL trade.
11. Maximum drawdown.
12. Performance by pair.
13. Average execution slippage and latency.
14. `portfolio_analytics.json` and `portfolio_analytics.md` reports.
15. Portfolio Analytics dashboard page.
16. Paper report integration.
17. Unit tests for analytics and drawdown behavior.

## Safety

This release does not enable live trading.

Analytics are generated from existing paper orders and paper portfolio state. No wallet, exchange, or live order path is introduced.

## Validation

Run:

```bash
python -m compileall -q app
python -m unittest discover -s tests -v

python -m app.analytics.pnl_analytics_service
python -m app.reporting.paper_report
python -m app.diagnostics.quote_diagnostics
python -m app.opportunities.multi_dex_opportunity_engine
python -m app.opportunities.opportunity_explorer
python -m app.automation.paper_autopilot --once
python -m app.reporting.paper_report
```

## Expected Result

- Unit tests pass.
- `reports/portfolio_analytics.json` is created.
- `reports/portfolio_analytics.md` is created.
- `reports/paper_report.md` includes a Portfolio Analytics section.
- Dashboard shows the new Portfolio Analytics page.
- Live trading remains disabled.

## Rollback

```bash
git checkout v3.4.1
```
