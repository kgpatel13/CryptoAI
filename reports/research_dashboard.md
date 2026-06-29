# CryptoAI Research Dashboard

Generated: `2026-06-29T02:29:07Z`

## Mission Control

- Mode: `paper`
- Live trading: `disabled`
- Portfolio equity USD: `$10001.3939`
- Total PnL USD: `$1.3939`
- Total return %: `0.0139`
- Feature vectors: `213`
- Tradeable or filled records: `166`
- Strategies: `1/5 active`

## Feature Store

- Feature vectors: `213`
- Average net edge %: `0.3500`
- Max net edge %: `0.3500`

### Source Counts

- `opportunity_decision`: 77
- `multi_dex_opportunity`: 79
- `paper_order`: 49
- `strategy_signal`: 8

### Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 86 |
| USDC/WETH | 86 |

## Recent Features

| Time | Source | Pair | Decision | Edge % | Reason |
|---|---|---|---|---:|---|
| 2026-06-29T02:29:02Z | strategy_signal | USDC/WETH | READY_FOR_PAPER | 0.3500 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-29T02:29:02Z | strategy_signal | WETH/USDC | READY_FOR_PAPER | 0.3500 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-29T02:22:34Z | strategy_signal | USDC/WETH | READY_FOR_PAPER | 0.3500 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-29T02:22:34Z | strategy_signal | WETH/USDC | READY_FOR_PAPER | 0.3500 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-28T18:36:53Z | strategy_signal | USDC/WETH | READY_FOR_PAPER | 0.3500 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-28T18:36:53Z | strategy_signal | WETH/USDC | READY_FOR_PAPER | 0.3500 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-28T18:23:10Z | strategy_signal | - | WATCH | None | Opportunity Explorer: REAL: No healthy quotes available. Fix quote providers/RPC before strategy tuning. |
| 2026-06-28T18:22:32Z | strategy_signal | - | WATCH | None | Opportunity Explorer: REAL: No healthy quotes available. Fix quote providers/RPC before strategy tuning. |
| 2026-06-29T02:12:42Z | paper_order | USDC/WETH | FILLED | 0.3500 | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-29T02:12:42Z | paper_order | WETH/USDC | FILLED | 0.3500 | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-29T01:11:32Z | paper_order | USDC/WETH | FILLED | 0.3500 | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-29T01:11:32Z | paper_order | WETH/USDC | FILLED | 0.3500 | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-28T18:37:01Z | paper_order | USDC/WETH | RISK_REJECTED | 0.3500 | Portfolio risk rejected: existing open BUY position for USDC/WETH; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T18:37:01Z | paper_order | WETH/USDC | RISK_REJECTED | 0.3500 | Portfolio risk rejected: existing open BUY position for WETH/USDC; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T18:14:25Z | paper_order | USDC/WETH | RISK_REJECTED | 0.3500 | Portfolio risk rejected: existing open BUY position for USDC/WETH; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T18:14:25Z | paper_order | WETH/USDC | FILLED | 0.3500 | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-28T17:52:15Z | paper_order | USDC/WETH | FILLED | 0.3500 | Simulated paper execution completed through professional order lifecycle. |
| 2026-06-28T17:52:15Z | paper_order | WETH/USDC | RISK_REJECTED | 0.3500 | Portfolio risk rejected: existing open BUY position for WETH/USDC; reuse/monitor the open position instead of adding duplicate exposure. |
| 2026-06-28T17:36:44Z | paper_order | USDC/WETH | RISK_REJECTED | 0.3500 | Portfolio risk rejected: cooldown active for USDC/WETH BUY (827s/900s). |
| 2026-06-28T17:36:44Z | paper_order | WETH/USDC | RISK_REJECTED | 0.3500 | Portfolio risk rejected: existing open BUY position for WETH/USDC; reuse/monitor the open position instead of adding duplicate exposure. |

## Notes

- Research metrics describe observed paper/simulated activity only.
- Do not infer live profitability from synthetic paper opportunities.
- The purpose of v4.0 is to accumulate research-grade data for later backtesting and AI ranking.
