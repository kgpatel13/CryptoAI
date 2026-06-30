# CryptoAI v5.11 - Arbitrage Execution Refactor

## Summary

v5.11 fixes paper arbitrage accounting before any further market expansion.

DEX arbitrage is now simulated as an atomic round trip:

1. Buy leg.
2. Sell leg.
3. Cost-buffered net edge.
4. Realized PnL.
5. Immediate `CLOSED` status.
6. Cash returned to the paper ledger immediately.

Arbitrage no longer uses take-profit, stop-loss, or max-hold position lifecycle logic.

## Fixed

- Arbitrage trades no longer remain `OPEN` / `MONITORING`.
- Paper arbitrage does not create long-lived positions.
- Portfolio cash is updated by realized PnL only.
- `cash = initial_cash + realized_pnl` after closed round-trip arbitrage.
- Closed paper orders now include buy DEX, sell DEX, gross edge, cost buffer, net edge, realized PnL, and close reason.
- `paper_report`, `portfolio_analytics`, dashboard, and raw export now read the same closed-order and portfolio-state evidence.
- Saved paper profile restores `max_open_positions = 1` and duplicate-position blocking.

## Still Locked

- Live trading remains disabled.
- Paper BUY threshold remains `0.30%`.
- Production buffer remains at least `0.30%`.
- Full-cash sizing is paper-only and uses available simulated cash without leverage.

## Reset For Fresh Paper Evidence

After this hotfix, old paper runtime files should be archived and active paper state reset before collecting new evidence.

```bash
python -m app.portfolio.repair_portfolio --reset --use-settings
python -m app.reporting.paper_report
python -m app.reporting.report_audit
```

