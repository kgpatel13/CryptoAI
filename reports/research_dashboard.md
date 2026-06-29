# CryptoAI Research Dashboard

Generated: `2026-06-29T13:25:17Z`

## Mission Control

- Mode: `paper`
- Live trading: `disabled`
- Portfolio equity USD: `$10002.8220`
- Total PnL USD: `$2.8220`
- Total return %: `0.0282`
- Feature vectors: `303`
- Tradeable or filled records: `180`
- Strategies: `1/5 active`

## Feature Store

- Feature vectors: `303`
- Average net edge %: `0.2194`
- Max net edge %: `0.3500`

### Source Counts

- `opportunity_decision`: 123
- `multi_dex_opportunity`: 125
- `paper_order`: 45
- `strategy_signal`: 10

### Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 134 |
| USDC/WETH | 128 |

## Recent Features

| Time | Source | Pair | Decision | Edge % | Reason |
|---|---|---|---|---:|---|
| 2026-06-29T12:47:14Z | strategy_signal | USDC/WETH | SKIP | -0.1379511013551796416279028826 | Opportunity Explorer SKIP: REAL: Real multi-DEX comparison: net edge -0.1380% is too low after costs. |
| 2026-06-29T12:47:14Z | strategy_signal | WETH/USDC | SKIP | -0.0627867526571790265828422155 | Opportunity Explorer SKIP: REAL: Real multi-DEX comparison: net edge -0.0628% is too low after costs. |
| 2026-06-29T02:29:02Z | strategy_signal | USDC/WETH | READY_FOR_PAPER | 0.3500 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-29T02:29:02Z | strategy_signal | WETH/USDC | READY_FOR_PAPER | 0.3500 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-29T02:22:34Z | strategy_signal | USDC/WETH | READY_FOR_PAPER | 0.3500 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-29T02:22:34Z | strategy_signal | WETH/USDC | READY_FOR_PAPER | 0.3500 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-28T18:36:53Z | strategy_signal | USDC/WETH | READY_FOR_PAPER | 0.3500 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-28T18:36:53Z | strategy_signal | WETH/USDC | READY_FOR_PAPER | 0.3500 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-28T18:23:10Z | strategy_signal | - | WATCH | None | Opportunity Explorer: REAL: No healthy quotes available. Fix quote providers/RPC before strategy tuning. |
| 2026-06-28T18:22:32Z | strategy_signal | - | WATCH | None | Opportunity Explorer: REAL: No healthy quotes available. Fix quote providers/RPC before strategy tuning. |
| 2026-06-29T13:25:00Z | paper_order | USDC/WETH | SKIPPED | -0.1516396104383123414073092587 | Risk decision is WATCHLIST; paper order not created. Expected edge -0.1516% is below paper threshold 0.30%. |
| 2026-06-29T13:25:00Z | paper_order | WETH/USDC | SKIPPED | -0.0488922657387659179562356805 | Risk decision is WATCHLIST; paper order not created. Expected edge -0.0489% is below paper threshold 0.30%. |
| 2026-06-29T02:12:42Z | paper_order | USDC/WETH | FILLED | 0.3500 | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-29T02:12:42Z | paper_order | WETH/USDC | FILLED | 0.3500 | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-29T01:11:32Z | paper_order | USDC/WETH | FILLED | 0.3500 | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-29T01:11:32Z | paper_order | WETH/USDC | FILLED | 0.3500 | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-28T18:37:01Z | paper_order | USDC/WETH | RISK_REJECTED | 0.3500 | Portfolio risk rejected: existing open BUY position for USDC/WETH; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T18:37:01Z | paper_order | WETH/USDC | RISK_REJECTED | 0.3500 | Portfolio risk rejected: existing open BUY position for WETH/USDC; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T18:14:25Z | paper_order | USDC/WETH | RISK_REJECTED | 0.3500 | Portfolio risk rejected: existing open BUY position for USDC/WETH; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T18:14:25Z | paper_order | WETH/USDC | FILLED | 0.3500 | Simulated paper execution completed through professional order lifecycle. |

## Notes

- Research metrics describe observed paper/simulated activity only.
- Do not infer live profitability from synthetic paper opportunities.
- The purpose of v4.0 is to accumulate research-grade data for later backtesting and AI ranking.
