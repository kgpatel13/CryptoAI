# CryptoAI Paper Trading Report

Generated: `2026-06-29T13:25:08Z`

## Summary

- Mode: `paper`
- Live trading: `disabled`
- Opportunity decisions: `156`
- Total orders: `45`
- Filled orders: `12`
- Skipped orders: `27`
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

- `SKIP`: 58
- `BUY`: 98

## Skip Reasons

- `Risk decision is WATCHLIST; paper order not created.`: 25
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.0489% is below paper threshold 0.30%.`: 1
- `Risk decision is WATCHLIST; paper order not created. Expected edge -0.1516% is below paper threshold 0.30%.`: 1

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
| WETH/USDC | -0.0627867526571790265828422155 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0628% is too low after costs. |
| USDC/WETH | -0.1379511013551796416279028826 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1380% is too low after costs. |
| WETH/USDC | -0.0627867526571790265828422155 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0628% is too low after costs. |
| USDC/WETH | -0.1379511013551796416279028826 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1380% is too low after costs. |
| WETH/USDC | -0.0627867526571790265828422155 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0628% is too low after costs. |
| USDC/WETH | -0.1379511013551796416279028826 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1380% is too low after costs. |
| WETH/USDC | -0.0673149713862384432978766197 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0673% is too low after costs. |
| USDC/WETH | -0.1334677807305146655124903447 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1335% is too low after costs. |
| WETH/USDC | -0.0673149713862384432978766197 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0673% is too low after costs. |
| USDC/WETH | -0.1334677807305146655124903447 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1335% is too low after costs. |
| WETH/USDC | -0.0488922657387659179562356805 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0489% is too low after costs. |
| USDC/WETH | -0.1516396104383123414073092587 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1516% is too low after costs. |
| WETH/USDC | -0.0488922657387659179562356805 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0489% is too low after costs. |
| USDC/WETH | -0.1516396104383123414073092587 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1516% is too low after costs. |
| WETH/USDC | -0.0488922657387659179562356805 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0489% is too low after costs. |
| USDC/WETH | -0.1516396104383123414073092587 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1516% is too low after costs. |
| WETH/USDC | -0.0488922657387659179562356805 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0489% is too low after costs. |
| USDC/WETH | -0.1516396104383123414073092587 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1516% is too low after costs. |
| WETH/USDC | -0.0488922657387659179562356805 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.0489% is too low after costs. |
| USDC/WETH | -0.1516396104383123414073092587 | 10 | SKIP | REAL: Real multi-DEX comparison: net edge -0.1516% is too low after costs. |

## Latest Orders

| Time | Pair | Status | Notional | Edge % | Slip bps | Quality | Reason |
|---|---|---|---:|---:|---:|---|---|
| 2026-06-28T16:34:07Z | WETH/USDC | FILLED | 105.0000 | 0.3500 | - | - | Simulated paper fill created from risk-approved candidate. |
| 2026-06-28T16:42:36Z | WETH/USDC | FILLED | 105.0000 | 0.3500 | - | - | Simulated paper fill created from risk-approved candidate. |
| 2026-06-28T16:59:13Z | WETH/USDC | FILLED | 105.0000 | 0.3500 | - | - | Simulated paper fill created from risk-approved candidate. |
| 2026-06-28T16:59:35Z | WETH/USDC | FILLED | 105.0000 | 0.3500 | - | - | Simulated paper fill created from risk-approved candidate. |
| 2026-06-28T17:02:19Z | WETH/USDC | FILLED | 105.0000 | 0.3500 | - | - | Simulated paper fill created from risk-approved candidate. |
| 2026-06-28T17:22:57Z | WETH/USDC | FILLED | 100.0000 | 0.3500 | - | - | Simulated paper fill created from risk-approved candidate after portfolio risk checks. |
| 2026-06-28T17:36:44Z | WETH/USDC | RISK_REJECTED | 0 | 0.3500 | None | None | Portfolio risk rejected: existing open BUY position for WETH/USDC; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T17:36:44Z | USDC/WETH | RISK_REJECTED | 0 | 0.3500 | None | None | Portfolio risk rejected: cooldown active for USDC/WETH BUY (827s/900s). |
| 2026-06-28T17:52:15Z | WETH/USDC | RISK_REJECTED | 0 | 0.3500 | None | None | Portfolio risk rejected: existing open BUY position for WETH/USDC; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T17:52:15Z | USDC/WETH | FILLED | 100.0035 | 0.3500 | 5 | GOOD | Simulated paper execution completed through professional order lifecycle. |
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

## Notes

- This is simulated paper-trading output only.
- No real wallet or exchange order was used.
- If filled_orders is zero, inspect opportunity_decision_counts and skip_reasons.
- Rows with legacy_accounting_warning came from pre-repair paper-order records and should not be used for sizing analysis.