# CryptoAI Paper Trading Report

Generated: `2026-06-30T08:03:42Z`

## Summary

- Mode: `paper`
- Live trading: `disabled`
- Opportunity decisions: `1492`
- Total orders: `0`
- Filled orders: `0`
- Skipped orders: `0`
- Rejected orders: `0`
- Portfolio risk rejections: `0`
- Total filled notional USD: `$0`
- Total realized PnL USD: `$0`
- Order-file realized PnL USD: `$0`
- PnL reconciliation: `RECONCILED`
- Paper portfolio cash USD: `$500.00`
- Open paper positions: `0`
- Closed paper positions: `0`
- Avg execution slippage bps: `-`
- Avg execution latency ms: `-`
- Equity USD: `$500.0000`
- Total PnL USD: `$0.0000`
- Total return %: `0.0000`
- Win rate %: `0.0000`
- Max drawdown %: `0.0000`
- Legacy accounting warnings: `0`

## Opportunity Decision Counts

- `BUY`: 535
- `SKIP`: 390
- `WATCH`: 567

## Skip Reasons

- No skipped orders.

## Portfolio Risk Rejection Reasons

- No portfolio risk rejections.

## Execution Quality

- No filled execution-quality records yet.

## Paper Portfolio

- Cash USD: `$500.00`
- Initial cash USD: `$500.00`
- Portfolio realized PnL USD: `$0`
- Open positions: `0`
- Closed positions: `0`
- Daily realized PnL USD: `$0`
- Unrealized PnL USD: `$0.0000`
- Daily filled trades: `0`
- Exposure by chain: `{}`
- Exposure by token: `{}`

## PnL Reconciliation

- Source of truth: `paper_portfolio_state.json`
- Status: `RECONCILED`
- Portfolio realized PnL USD: `$0`
- Order-file realized PnL USD: `$0`
- Difference USD: `$0.0000`
- Note: The active portfolio ledger and paper-order history agree.

## Portfolio Analytics

- Equity USD: `$500.0000`
- Total PnL USD: `$0.0000`
- Total return %: `0.0000`
- Win rate %: `0.0000`
- Profit factor: `N/A`
- Expectancy USD: `$0.0000`
- Max drawdown USD: `$0.0000`
- Max drawdown %: `0.0000`

## Latest Opportunities

| Pair | Net % | Score | Decision | Reason |
|---|---:|---:|---|---|
| WETH/USDC | 0.3090134766069292481369913453 | 61 | BUY | REAL: Real multi-DEX comparison: net edge 0.3090% is above BUY threshold 0.30%. |
| USDC/WETH | 0.0616317488636955489586508439 | 12 | WATCH | REAL: Real multi-DEX comparison: net edge 0.0616% is positive but below BUY threshold. |
| WETH/USDC | 0.3090134766069292481369913453 | 61 | BUY | REAL: Real multi-DEX comparison: net edge 0.3090% is above BUY threshold 0.30%. |
| USDC/WETH | 0.0616317488636955489586508439 | 12 | WATCH | REAL: Real multi-DEX comparison: net edge 0.0616% is positive but below BUY threshold. |
| WETH/USDC | 0.2758309286543639479637863158 | 55 | WATCH | REAL: Real multi-DEX comparison: net edge 0.2758% is positive but below BUY threshold. |
| USDC/WETH | 0.0947438634867620980862116113 | 18 | WATCH | REAL: Real multi-DEX comparison: net edge 0.0947% is positive but below BUY threshold. |
| WETH/USDC | 0.2758309286543639479637863158 | 55 | WATCH | REAL: Real multi-DEX comparison: net edge 0.2758% is positive but below BUY threshold. |
| USDC/WETH | 0.0947438634867620980862116113 | 18 | WATCH | REAL: Real multi-DEX comparison: net edge 0.0947% is positive but below BUY threshold. |
| WETH/USDC | 0.3219793599915975725424335062 | 64 | BUY | REAL: Real multi-DEX comparison: net edge 0.3220% is above BUY threshold 0.30%. |
| USDC/WETH | 0.0485913796847499731004068634 | 9 | SKIP | REAL: Real multi-DEX comparison: net edge 0.0486% is too low after costs. |
| WETH/USDC | 0.3219793599915975725424335062 | 64 | BUY | REAL: Real multi-DEX comparison: net edge 0.3220% is above BUY threshold 0.30%. |
| USDC/WETH | 0.0485913796847499731004068634 | 9 | SKIP | REAL: Real multi-DEX comparison: net edge 0.0486% is too low after costs. |
| WETH/USDC | 0.3045275078748223995885658298 | 60 | BUY | REAL: Real multi-DEX comparison: net edge 0.3045% is above BUY threshold 0.30%. |
| USDC/WETH | 0.0661076247810337682341250338 | 13 | WATCH | REAL: Real multi-DEX comparison: net edge 0.0661% is positive but below BUY threshold. |
| WETH/USDC | 0.3045275078748223995885658298 | 60 | BUY | REAL: Real multi-DEX comparison: net edge 0.3045% is above BUY threshold 0.30%. |
| USDC/WETH | 0.0661076247810337682341250338 | 13 | WATCH | REAL: Real multi-DEX comparison: net edge 0.0661% is positive but below BUY threshold. |
| WETH/USDC | 0.3045275078748223995885658298 | 60 | BUY | REAL: Real multi-DEX comparison: net edge 0.3045% is above BUY threshold 0.30%. |
| USDC/WETH | 0.0661076247810337682341250338 | 13 | WATCH | REAL: Real multi-DEX comparison: net edge 0.0661% is positive but below BUY threshold. |
| WETH/USDC | 0.3045275078748223995885658298 | 60 | BUY | REAL: Real multi-DEX comparison: net edge 0.3045% is above BUY threshold 0.30%. |
| USDC/WETH | 0.0661076247810337682341250338 | 13 | WATCH | REAL: Real multi-DEX comparison: net edge 0.0661% is positive but below BUY threshold. |

## Latest Orders

No paper orders saved yet.

## Notes

- This is simulated paper-trading output only.
- No real wallet or exchange order was used.
- If filled_orders is zero, inspect opportunity_decision_counts and skip_reasons.
- Portfolio cash and realized PnL are reconciled to paper_portfolio_state.json.
- Order-file realized PnL is retained as historical execution evidence and may include rows from earlier paper sessions.
- Rows with legacy_accounting_warning came from pre-repair paper-order records and should not be used for sizing analysis.