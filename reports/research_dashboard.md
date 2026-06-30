# CryptoAI Research Dashboard

Generated: `2026-06-30T02:09:55Z`

## Mission Control

- Mode: `paper`
- Live trading: `disabled`
- Portfolio equity USD: `$-`
- Total PnL USD: `$-`
- Total return %: `-`
- Feature vectors: `44`
- Tradeable or filled records: `0`
- Strategies: `1/5 active`

## Feature Store

- Feature vectors: `44`
- Average net edge %: `0.1852`
- Max net edge %: `0.2599`

### Source Counts

- `opportunity_decision`: 18
- `multi_dex_opportunity`: 20
- `paper_order`: 4
- `strategy_signal`: 2

### Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 22 |
| USDC/WETH | 22 |

## Recent Features

| Time | Source | Pair | Decision | Edge % | Reason |
|---|---|---|---|---:|---|
| 2026-06-30T02:09:55Z | strategy_signal | WETH/USDC | WATCH | 0.1106092052245993244268447881 | Opportunity Explorer WATCH: net edge 0.1106% is positive but below BUY threshold 0.30%. |
| 2026-06-30T02:09:55Z | strategy_signal | USDC/WETH | WATCH | 0.2598556123843567556185077586 | Opportunity Explorer WATCH: net edge 0.2599% is positive but below BUY threshold 0.30%. |
| 2026-06-30T02:09:29Z | paper_order | WETH/USDC | SKIPPED | 0.1106092052245993244268447881 | Risk decision is WATCHLIST; paper order not created. Expected edge 0.1106% is below paper threshold 0.30%. |
| 2026-06-30T02:09:29Z | paper_order | USDC/WETH | SKIPPED | 0.2598556123843567556185077586 | Risk decision is WATCHLIST; paper order not created. Expected edge 0.2599% is below paper threshold 0.30%. |
| 2026-06-30T02:09:25Z | paper_order | WETH/USDC | SKIPPED | 0.1106092052245993244268447881 | Risk decision is WATCHLIST; paper order not created. Expected edge 0.1106% is below paper threshold 0.30%. |
| 2026-06-30T02:09:25Z | paper_order | USDC/WETH | SKIPPED | 0.2598556123843567556185077586 | Risk decision is WATCHLIST; paper order not created. Expected edge 0.2599% is below paper threshold 0.30%. |
| 2026-06-30T02:09:55Z | multi_dex_opportunity | USDC/WETH | WATCH | 0.2598556123843567556185077586 | Real multi-DEX comparison: net edge 0.2599% is positive but below BUY threshold. |
| 2026-06-30T02:09:55Z | multi_dex_opportunity | WETH/USDC | WATCH | 0.1106092052245993244268447881 | Real multi-DEX comparison: net edge 0.1106% is positive but below BUY threshold. |
| 2026-06-30T02:09:53Z | multi_dex_opportunity | USDC/WETH | WATCH | 0.2598556123843567556185077586 | Real multi-DEX comparison: net edge 0.2599% is positive but below BUY threshold. |
| 2026-06-30T02:09:53Z | multi_dex_opportunity | WETH/USDC | WATCH | 0.1106092052245993244268447881 | Real multi-DEX comparison: net edge 0.1106% is positive but below BUY threshold. |
| 2026-06-30T02:09:51Z | multi_dex_opportunity | USDC/WETH | WATCH | 0.2598556123843567556185077586 | Real multi-DEX comparison: net edge 0.2599% is positive but below BUY threshold. |
| 2026-06-30T02:09:51Z | multi_dex_opportunity | WETH/USDC | WATCH | 0.1106092052245993244268447881 | Real multi-DEX comparison: net edge 0.1106% is positive but below BUY threshold. |
| 2026-06-30T02:09:30Z | multi_dex_opportunity | USDC/WETH | WATCH | 0.2598556123843567556185077586 | Real multi-DEX comparison: net edge 0.2599% is positive but below BUY threshold. |
| 2026-06-30T02:09:30Z | multi_dex_opportunity | WETH/USDC | WATCH | 0.1106092052245993244268447881 | Real multi-DEX comparison: net edge 0.1106% is positive but below BUY threshold. |
| 2026-06-30T02:09:29Z | multi_dex_opportunity | USDC/WETH | WATCH | 0.2598556123843567556185077586 | Real multi-DEX comparison: net edge 0.2599% is positive but below BUY threshold. |
| 2026-06-30T02:09:29Z | multi_dex_opportunity | WETH/USDC | WATCH | 0.1106092052245993244268447881 | Real multi-DEX comparison: net edge 0.1106% is positive but below BUY threshold. |
| 2026-06-30T02:09:28Z | multi_dex_opportunity | USDC/WETH | WATCH | 0.2598556123843567556185077586 | Real multi-DEX comparison: net edge 0.2599% is positive but below BUY threshold. |
| 2026-06-30T02:09:28Z | multi_dex_opportunity | WETH/USDC | WATCH | 0.1106092052245993244268447881 | Real multi-DEX comparison: net edge 0.1106% is positive but below BUY threshold. |
| 2026-06-30T02:09:26Z | multi_dex_opportunity | USDC/WETH | WATCH | 0.2598556123843567556185077586 | Real multi-DEX comparison: net edge 0.2599% is positive but below BUY threshold. |
| 2026-06-30T02:09:26Z | multi_dex_opportunity | WETH/USDC | WATCH | 0.1106092052245993244268447881 | Real multi-DEX comparison: net edge 0.1106% is positive but below BUY threshold. |

## Notes

- Research metrics describe observed paper/simulated activity only.
- Do not infer live profitability from synthetic paper opportunities.
- The purpose of v4.0 is to accumulate research-grade data for later backtesting and AI ranking.
