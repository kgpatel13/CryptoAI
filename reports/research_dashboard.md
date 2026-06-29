# CryptoAI Research Dashboard

Generated: `2026-06-29T01:08:32Z`

## Mission Control

- Mode: `paper`
- Live trading: `disabled`
- Portfolio equity USD: `$10001.4613`
- Total PnL USD: `$1.4613`
- Total return %: `0.0146`
- Feature vectors: `109`
- Tradeable or filled records: `62`
- Strategies: `1/5 active`

## Feature Store

- Feature vectors: `109`
- Average net edge %: `0.3500`
- Max net edge %: `0.3500`

### Source Counts

- `opportunity_decision`: 29
- `multi_dex_opportunity`: 31
- `paper_order`: 45
- `strategy_signal`: 4

### Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 34 |
| USDC/WETH | 34 |

## Recent Features

| Time | Source | Pair | Decision | Edge % | Reason |
|---|---|---|---|---:|---|
| 2026-06-28T18:36:53Z | strategy_signal | USDC/WETH | READY_FOR_PAPER | 0.3500 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-28T18:36:53Z | strategy_signal | WETH/USDC | READY_FOR_PAPER | 0.3500 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-28T18:23:10Z | strategy_signal | - | WATCH | None | Opportunity Explorer: REAL: No healthy quotes available. Fix quote providers/RPC before strategy tuning. |
| 2026-06-28T18:22:32Z | strategy_signal | - | WATCH | None | Opportunity Explorer: REAL: No healthy quotes available. Fix quote providers/RPC before strategy tuning. |
| 2026-06-28T18:37:01Z | paper_order | USDC/WETH | RISK_REJECTED | 0.3500 | Portfolio risk rejected: existing open BUY position for USDC/WETH; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T18:37:01Z | paper_order | WETH/USDC | RISK_REJECTED | 0.3500 | Portfolio risk rejected: existing open BUY position for WETH/USDC; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T18:14:25Z | paper_order | USDC/WETH | RISK_REJECTED | 0.3500 | Portfolio risk rejected: existing open BUY position for USDC/WETH; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T18:14:25Z | paper_order | WETH/USDC | FILLED | 0.3500 | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-28T17:52:15Z | paper_order | USDC/WETH | FILLED | 0.3500 | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-28T17:52:15Z | paper_order | WETH/USDC | RISK_REJECTED | 0.3500 | Portfolio risk rejected: existing open BUY position for WETH/USDC; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T17:36:44Z | paper_order | USDC/WETH | RISK_REJECTED | 0.3500 | Portfolio risk rejected: cooldown active for USDC/WETH BUY (827s/900s). |
| 2026-06-28T17:36:44Z | paper_order | WETH/USDC | RISK_REJECTED | 0.3500 | Portfolio risk rejected: existing open BUY position for WETH/USDC; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T17:22:57Z | paper_order | USDC/WETH | FILLED | 0.3500 | Simulated paper fill created from risk-approved candidate after portfolio risk checks. |
| 2026-06-28T17:22:57Z | paper_order | WETH/USDC | FILLED | 0.3500 | Simulated paper fill created from risk-approved candidate after portfolio risk checks. |
| 2026-06-28T17:02:19Z | paper_order | USDC/WETH | FILLED | 0.3500 | Simulated paper fill created from risk-approved candidate. |
| 2026-06-28T17:02:19Z | paper_order | WETH/USDC | FILLED | 0.3500 | Simulated paper fill created from risk-approved candidate. |
| 2026-06-28T16:59:35Z | paper_order | USDC/WETH | FILLED | 0.3500 | Simulated paper fill created from risk-approved candidate. |
| 2026-06-28T16:59:35Z | paper_order | WETH/USDC | FILLED | 0.3500 | Simulated paper fill created from risk-approved candidate. |
| 2026-06-28T16:59:13Z | paper_order | USDC/WETH | FILLED | 0.3500 | Simulated paper fill created from risk-approved candidate. |
| 2026-06-28T16:59:13Z | paper_order | WETH/USDC | FILLED | 0.3500 | Simulated paper fill created from risk-approved candidate. |

## Notes

- Research metrics describe observed paper/simulated activity only.
- Do not infer live profitability from synthetic paper opportunities.
- The purpose of v4.0 is to accumulate research-grade data for later backtesting and AI ranking.
