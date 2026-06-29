# CryptoAI Paper Trading Report

Generated: `2026-06-29T18:18:09Z`

## Summary

- Mode: `paper`
- Live trading: `disabled`
- Opportunity decisions: `250`
- Total orders: `55`
- Filled orders: `12`
- Skipped orders: `37`
- Rejected orders: `0`
- Portfolio risk rejections: `6`
- Total filled notional USD: `$1225.0697`
- Paper portfolio cash USD: `$10002.8220`
- Open paper positions: `0`
- Closed paper positions: `8`
- Avg execution slippage bps: `5.0000`
- Avg execution latency ms: `250.0000`
- Equity USD: `$10002.8220`
- Total PnL USD: `$2.8220`
- Total return %: `0.0282`
- Win rate %: `80.0000`
- Max drawdown %: `0.0000`
- Legacy accounting warnings: `0`

## Opportunity Decision Counts

- `SKIP`: 152
- `BUY`: 98

## Skip Reasons

- `Risk decision is WATCHLIST; paper order not created.`: 25
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.0489% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.1516% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.1039% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.0972% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.1128% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.0882% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.0491% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.1520% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.0552% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.1441% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge 0.0111% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.2103% is below paper threshold 0.30%.`: 1

## Portfolio Risk Rejection Reasons

- `Portfolio risk rejected: existing open BUY position for WETH/USDC; reuse/monitor the open position instead of adding duplicate exposure.`: 3
- `Portfolio risk rejected: cooldown active for USDC/WETH BUY (827s/900s).`: 1
- `Portfolio risk rejected: existing open BUY position for USDC/WETH; reuse/monitor the open position instead of adding duplicate exposure.`: 2

## Execution Quality

- `UNKNOWN`: 6
- `GOOD`: 6

## Paper Portfolio

- Cash USD: `$10002.8220`
- Initial cash USD: `$10000`
- Open positions: `0`
- Closed positions: `8`
- Daily realized PnL USD: `$1.8202`
- Unrealized PnL USD: `$0.0000`
- Daily filled trades: `4`
- Exposure by chain: `{}`
- Exposure by token: `{}`

## Portfolio Analytics

- Equity USD: `$10002.8220`
- Total PnL USD: `$2.8220`
- Total return %: `0.0282`
- Win rate %: `80.0000`
- Profit factor: `103.2464`
- Expectancy USD: `$0.5644`
- Max drawdown USD: `$0.0000`
- Max drawdown %: `0.0000`

### Daily PnL

| Date | Trades | Filled Notional | Realized PnL | Cumulative PnL | Daily Return % |
|---|---:|---:|---:|---:|---:|
| 2026-06-28 | 8 | 825.0135 | 2.8220 | 2.8220 | 0.0282 |
| 2026-06-29 | 4 | 400.0562 | 0.0000 | 2.8220 | 0.0000 |

### Performance by Pair

| Pair | Trades | Filled Notional | Realized PnL | Win Rate % |
|---|---:|---:|---:|---:|
| USDC/WETH | 3 | 300.0316 | 0.3500 | 100.0000 |
| WETH/USDC | 9 | 925.0381 | 2.4720 | 75.0000 |

## Latest Opportunities

| Pair | Net % | Score | Decision | Reason |
|---|---:|---:|---|---|
| WETH/USDC | 0.0035451216502074820379041918 | 0 | SKIP | REAL: Real multi-DEX comparison: net edge 0.0035% is too low after costs. |
| USDC/WETH | -0.2026491309744196552680145815 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.2026% is too low after costs. |
| WETH/USDC | 0.0366812934780021846957308582 | 7 | SKIP | REAL: Real multi-DEX comparison: net edge 0.0367% is too low after costs. |
| USDC/WETH | -0.2360492311516206765453592314 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.2360% is too low after costs. |
| WETH/USDC | 0.0366812934780021846957308582 | 7 | SKIP | REAL: Real multi-DEX comparison: net edge 0.0367% is too low after costs. |
| USDC/WETH | -0.2360492311516206765453592314 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.2360% is too low after costs. |
| WETH/USDC | 0.0111071078041971530481190535 | 2 | SKIP | REAL: Real multi-DEX comparison: net edge 0.0111% is too low after costs. |
| USDC/WETH | -0.2103086317172912901719613480 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.2103% is too low after costs. |
| WETH/USDC | 0.0111071078041971530481190535 | 2 | SKIP | REAL: Real multi-DEX comparison: net edge 0.0111% is too low after costs. |
| USDC/WETH | -0.2103086317172912901719613480 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.2103% is too low after costs. |
| WETH/USDC | 0.0111071078041971530481190535 | 2 | SKIP | REAL: Real multi-DEX comparison: net edge 0.0111% is too low after costs. |
| USDC/WETH | -0.2103086317172912901719613480 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.2103% is too low after costs. |
| WETH/USDC | 0.0111071078041971530481190535 | 2 | SKIP | REAL: Real multi-DEX comparison: net edge 0.0111% is too low after costs. |
| USDC/WETH | -0.2103086317172912901719613480 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.2103% is too low after costs. |
| WETH/USDC | 0.0111071078041971530481190535 | 2 | SKIP | REAL: Real multi-DEX comparison: net edge 0.0111% is too low after costs. |
| USDC/WETH | -0.2103086317172912901719613480 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.2103% is too low after costs. |
| WETH/USDC | 0.0111071078041971530481190535 | 2 | SKIP | REAL: Real multi-DEX comparison: net edge 0.0111% is too low after costs. |
| USDC/WETH | -0.2103086317172912901719613480 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.2103% is too low after costs. |
| WETH/USDC | 0.0111071078041971530481190535 | 2 | SKIP | REAL: Real multi-DEX comparison: net edge 0.0111% is too low after costs. |
| USDC/WETH | -0.2103086317172912901719613480 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.2103% is too low after costs. |

## Latest Orders

| Time | Pair | Status | Notional | Edge % | Slip bps | Quality | Reason |
|---|---|---|---:|---:|---:|---|---|
| 2026-06-28T18:14:25Z | WETH/USDC | FILLED | 100.0100 | 0.3500 | 5 | GOOD | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-28T18:14:25Z | USDC/WETH | RISK_REJECTED | 0 | 0.3500 | None | None | Portfolio risk rejected: existing open BUY position for USDC/WETH; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T18:37:01Z | WETH/USDC | RISK_REJECTED | 0 | 0.3500 | None | None | Portfolio risk rejected: existing open BUY position for WETH/USDC; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T18:37:01Z | USDC/WETH | RISK_REJECTED | 0 | 0.3500 | None | None | Portfolio risk rejected: existing open BUY position for USDC/WETH; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-29T01:11:32Z | WETH/USDC | FILLED | 100.0142 | 0.3500 | 5 | GOOD | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-29T01:11:32Z | USDC/WETH | FILLED | 100.0142 | 0.3500 | 5 | GOOD | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-29T02:12:42Z | WETH/USDC | FILLED | 100.0139 | 0.3500 | 5 | GOOD | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-29T02:12:42Z | USDC/WETH | FILLED | 100.0139 | 0.3500 | 5 | GOOD | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-29T13:25:00Z | WETH/USDC | SKIPPED | 0 | -0.0488922657387659179562356805 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0489% is below paper threshold 0.30%. |
| 2026-06-29T13:25:00Z | USDC/WETH | SKIPPED | 0 | -0.1516396104383123414073092587 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1516% is below paper threshold 0.30%. |
| 2026-06-29T14:08:22Z | WETH/USDC | SKIPPED | 0 | -0.1038540157994195894303357355 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1039% is below paper threshold 0.30%. |
| 2026-06-29T14:08:22Z | USDC/WETH | SKIPPED | 0 | -0.0972099073325391546686591745 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0972% is below paper threshold 0.30%. |
| 2026-06-29T14:12:10Z | WETH/USDC | SKIPPED | 0 | -0.1128390759035909960434897425 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1128% is below paper threshold 0.30%. |
| 2026-06-29T14:12:10Z | USDC/WETH | SKIPPED | 0 | -0.0882186845516571827872423019 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0882% is below paper threshold 0.30%. |
| 2026-06-29T14:23:16Z | WETH/USDC | SKIPPED | 0 | -0.0491398180386638460061568368 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0491% is below paper threshold 0.30%. |
| 2026-06-29T14:23:16Z | USDC/WETH | SKIPPED | 0 | -0.1520149749886572845258085844 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1520% is below paper threshold 0.30%. |
| 2026-06-29T17:45:15Z | WETH/USDC | SKIPPED | 0 | -0.0552147966416534495753429694 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0552% is below paper threshold 0.30%. |
| 2026-06-29T17:45:15Z | USDC/WETH | SKIPPED | 0 | -0.1441080874515027154139680131 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1441% is below paper threshold 0.30%. |
| 2026-06-29T18:18:08Z | WETH/USDC | SKIPPED | 0 | 0.0111071078041971530481190535 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge 0.0111% is below paper threshold 0.30%. |
| 2026-06-29T18:18:08Z | USDC/WETH | SKIPPED | 0 | -0.2103086317172912901719613480 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.2103% is below paper threshold 0.30%. |

## Notes

- This is simulated paper-trading output only.
- No real wallet or exchange order was used.
- If filled_orders is zero, inspect opportunity_decision_counts and skip_reasons.
- Rows with legacy_accounting_warning came from pre-repair paper-order records and should not be used for sizing analysis.