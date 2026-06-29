# CryptoAI Paper Trading Report

Generated: `2026-06-29T23:31:19Z`

## Summary

- Mode: `paper`
- Live trading: `disabled`
- Opportunity decisions: `340`
- Total orders: `67`
- Filled orders: `12`
- Skipped orders: `49`
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

- `SKIP`: 239
- `BUY`: 101

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
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.0609% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.1385% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.0762% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.1234% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.0528% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.1468% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.0503% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.1494% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.0692% is below paper threshold 0.30%.`: 2
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.1305% is below paper threshold 0.30%.`: 2

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
| WETH/USDC | -0.0692445539051405587505678867 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0692% is too low after costs. |
| USDC/WETH | -0.1304730391575905539939033465 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1305% is too low after costs. |
| WETH/USDC | -0.0692445539051405587505678867 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0692% is too low after costs. |
| USDC/WETH | -0.1304730391575905539939033465 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1305% is too low after costs. |
| WETH/USDC | -0.0692445539051405587505678867 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0692% is too low after costs. |
| USDC/WETH | -0.1304730391575905539939033465 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1305% is too low after costs. |
| WETH/USDC | -0.0692445539051405587505678867 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0692% is too low after costs. |
| USDC/WETH | -0.1304730391575905539939033465 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1305% is too low after costs. |
| WETH/USDC | -0.0692445539051405587505678867 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0692% is too low after costs. |
| USDC/WETH | -0.1304730391575905539939033465 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1305% is too low after costs. |
| WETH/USDC | -0.0692445539051405587505678867 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0692% is too low after costs. |
| USDC/WETH | -0.1304730391575905539939033465 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1305% is too low after costs. |
| WETH/USDC | -0.0692445539051405587505678867 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0692% is too low after costs. |
| USDC/WETH | -0.1304730391575905539939033465 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1305% is too low after costs. |
| WETH/USDC | -0.0091654991525793535216386928 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0092% is too low after costs. |
| USDC/WETH | 0.3830010159406717421808796956 | 76 | BUY | REAL: Real multi-DEX comparison: net edge 0.3830% is above BUY threshold 0.30%. |
| WETH/USDC | -0.0091654991525793535216386928 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0092% is too low after costs. |
| USDC/WETH | 0.3830010159406717421808796956 | 76 | BUY | REAL: Real multi-DEX comparison: net edge 0.3830% is above BUY threshold 0.30%. |
| WETH/USDC | -0.0091654991525793535216386928 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0092% is too low after costs. |
| USDC/WETH | 0.3830010159406717421808796956 | 76 | BUY | REAL: Real multi-DEX comparison: net edge 0.3830% is above BUY threshold 0.30%. |

## Latest Orders

| Time | Pair | Status | Notional | Edge % | Slip bps | Quality | Reason |
|---|---|---|---:|---:|---:|---|---|
| 2026-06-29T14:12:10Z | WETH/USDC | SKIPPED | 0 | -0.1128390759035909960434897425 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1128% is below paper threshold 0.30%. |
| 2026-06-29T14:12:10Z | USDC/WETH | SKIPPED | 0 | -0.0882186845516571827872423019 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0882% is below paper threshold 0.30%. |
| 2026-06-29T14:23:16Z | WETH/USDC | SKIPPED | 0 | -0.0491398180386638460061568368 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0491% is below paper threshold 0.30%. |
| 2026-06-29T14:23:16Z | USDC/WETH | SKIPPED | 0 | -0.1520149749886572845258085844 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1520% is below paper threshold 0.30%. |
| 2026-06-29T17:45:15Z | WETH/USDC | SKIPPED | 0 | -0.0552147966416534495753429694 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0552% is below paper threshold 0.30%. |
| 2026-06-29T17:45:15Z | USDC/WETH | SKIPPED | 0 | -0.1441080874515027154139680131 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1441% is below paper threshold 0.30%. |
| 2026-06-29T18:18:08Z | WETH/USDC | SKIPPED | 0 | 0.0111071078041971530481190535 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge 0.0111% is below paper threshold 0.30%. |
| 2026-06-29T18:18:08Z | USDC/WETH | SKIPPED | 0 | -0.2103086317172912901719613480 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.2103% is below paper threshold 0.30%. |
| 2026-06-29T18:46:18Z | WETH/USDC | SKIPPED | 0 | -0.0609390525389801908740345526 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0609% is below paper threshold 0.30%. |
| 2026-06-29T18:46:18Z | USDC/WETH | SKIPPED | 0 | -0.1384958813562056424736350368 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1385% is below paper threshold 0.30%. |
| 2026-06-29T22:59:32Z | WETH/USDC | SKIPPED | 0 | -0.0761681979172122764045773608 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0762% is below paper threshold 0.30%. |
| 2026-06-29T22:59:32Z | USDC/WETH | SKIPPED | 0 | -0.1234196220513873443362474363 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1234% is below paper threshold 0.30%. |
| 2026-06-29T23:16:15Z | WETH/USDC | SKIPPED | 0 | -0.0527630663164861311694971056 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0528% is below paper threshold 0.30%. |
| 2026-06-29T23:16:15Z | USDC/WETH | SKIPPED | 0 | -0.1468393168847037409967392740 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1468% is below paper threshold 0.30%. |
| 2026-06-29T23:20:16Z | WETH/USDC | SKIPPED | 0 | -0.0502761125936736855413982252 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0503% is below paper threshold 0.30%. |
| 2026-06-29T23:20:16Z | USDC/WETH | SKIPPED | 0 | -0.1493647360110745142802275332 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1494% is below paper threshold 0.30%. |
| 2026-06-29T23:25:24Z | WETH/USDC | SKIPPED | 0 | -0.0692445539051405587505678867 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0692% is below paper threshold 0.30%. |
| 2026-06-29T23:25:24Z | USDC/WETH | SKIPPED | 0 | -0.1304730391575905539939033465 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1305% is below paper threshold 0.30%. |
| 2026-06-29T23:26:48Z | WETH/USDC | SKIPPED | 0 | -0.0692445539051405587505678867 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0692% is below paper threshold 0.30%. |
| 2026-06-29T23:26:48Z | USDC/WETH | SKIPPED | 0 | -0.1304730391575905539939033465 | None | None | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1305% is below paper threshold 0.30%. |

## Notes

- This is simulated paper-trading output only.
- No real wallet or exchange order was used.
- If filled_orders is zero, inspect opportunity_decision_counts and skip_reasons.
- Rows with legacy_accounting_warning came from pre-repair paper-order records and should not be used for sizing analysis.