# CryptoAI Research Dashboard

Generated: `2026-06-29T17:45:19Z`

## Mission Control

- Mode: `paper`
- Live trading: `disabled`
- Portfolio equity USD: `$10002.8220`
- Total PnL USD: `$2.8220`
- Total return %: `0.0282`
- Feature vectors: `433`
- Tradeable or filled records: `180`
- Strategies: `1/5 active`

## Feature Store

- Feature vectors: `433`
- Average net edge %: `0.1133`
- Max net edge %: `0.3500`

### Source Counts

- `opportunity_decision`: 179
- `multi_dex_opportunity`: 181
- `paper_order`: 53
- `strategy_signal`: 20

### Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 199 |
| USDC/WETH | 193 |

## Recent Features

| Time | Source | Pair | Decision | Edge % | Reason |
|---|---|---|---|---:|---|
| 2026-06-29T17:45:18Z | strategy_signal | USDC/WETH | SKIP | -0.1441080874515027154139680131 | Opportunity Explorer SKIP: REAL: Real multi-DEX comparison: net edge -0.1441% is too low after costs. |
| 2026-06-29T17:45:18Z | strategy_signal | WETH/USDC | SKIP | -0.0552147966416534495753429694 | Opportunity Explorer SKIP: REAL: Real multi-DEX comparison: net edge -0.0552% is too low after costs. |
| 2026-06-29T14:12:21Z | strategy_signal | USDC/WETH | SKIP | -0.0882186845516571827872423019 | Opportunity Explorer SKIP: REAL: Real multi-DEX comparison: net edge -0.0882% is too low after costs. |
| 2026-06-29T14:12:21Z | strategy_signal | WETH/USDC | SKIP | -0.1128390759035909960434897425 | Opportunity Explorer SKIP: REAL: Real multi-DEX comparison: net edge -0.1128% is too low after costs. |
| 2026-06-29T14:08:37Z | strategy_signal | USDC/WETH | SKIP | -0.0972099073325391546686591745 | Opportunity Explorer SKIP: REAL: Real multi-DEX comparison: net edge -0.0972% is too low after costs. |
| 2026-06-29T14:08:37Z | strategy_signal | WETH/USDC | SKIP | -0.1038540157994195894303357355 | Opportunity Explorer SKIP: REAL: Real multi-DEX comparison: net edge -0.1039% is too low after costs. |
| 2026-06-29T13:34:59Z | strategy_signal | USDC/WETH | SKIP | -0.1475851574587660361695146862 | Opportunity Explorer SKIP: REAL: Real multi-DEX comparison: net edge -0.1476% is too low after costs. |
| 2026-06-29T13:34:59Z | strategy_signal | WETH/USDC | SKIP | -0.0530589499588809716230039761 | Opportunity Explorer SKIP: REAL: Real multi-DEX comparison: net edge -0.0531% is too low after costs. |
| 2026-06-29T13:25:18Z | strategy_signal | USDC/WETH | SKIP | -0.1516396104383123414073092587 | Opportunity Explorer SKIP: REAL: Real multi-DEX comparison: net edge -0.1516% is too low after costs. |
| 2026-06-29T13:25:18Z | strategy_signal | WETH/USDC | SKIP | -0.0488922657387659179562356805 | Opportunity Explorer SKIP: REAL: Real multi-DEX comparison: net edge -0.0489% is too low after costs. |
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

## Notes

- Research metrics describe observed paper/simulated activity only.
- Do not infer live profitability from synthetic paper opportunities.
- The purpose of v4.0 is to accumulate research-grade data for later backtesting and AI ranking.
