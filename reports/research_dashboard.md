# CryptoAI Research Dashboard

Generated: `2026-06-30T02:54:58Z`

## Mission Control

- Mode: `paper`
- Live trading: `disabled`
- Portfolio equity USD: `$1241.3240`
- Total PnL USD: `$241.3240`
- Total return %: `24.1324`
- Feature vectors: `3648`
- Tradeable or filled records: `625`
- Strategies: `1/5 active`

## Feature Store

- Feature vectors: `3648`
- Average net edge %: `0.1852`
- Max net edge %: `0.3319`

### Source Counts

- `opportunity_decision`: 1638
- `multi_dex_opportunity`: 1640
- `paper_order`: 368
- `strategy_signal`: 2

### Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 1824 |
| USDC/WETH | 1824 |

## Recent Features

| Time | Source | Pair | Decision | Edge % | Reason |
|---|---|---|---|---:|---|
| 2026-06-30T02:31:32Z | strategy_signal | USDC/WETH | WATCH | 0.1530375364175635294888288864 | Opportunity Explorer WATCH: net edge 0.1530% is positive but below BUY threshold 0.30%. |
| 2026-06-30T02:31:32Z | strategy_signal | WETH/USDC | WATCH | 0.2177053681626583875876299695 | Opportunity Explorer WATCH: net edge 0.2177% is positive but below BUY threshold 0.30%. |
| 2026-06-30T02:54:56Z | paper_order | USDC/WETH | SKIPPED | 0.0386844834347967972898421171 | Risk decision is WATCHLIST; paper order not created. Expected edge 0.0387% is below paper threshold 0.30%. |
| 2026-06-30T02:54:56Z | paper_order | WETH/USDC | CLOSED | 0.3318728206881047119859398240 | Atomic paper arbitrage round trip completed and closed immediately. |
| 2026-06-30T02:54:49Z | paper_order | USDC/WETH | SKIPPED | 0.0386844834347967972898421171 | Risk decision is WATCHLIST; paper order not created. Expected edge 0.0387% is below paper threshold 0.30%. |
| 2026-06-30T02:54:49Z | paper_order | WETH/USDC | CLOSED | 0.3318728206881047119859398240 | Atomic paper arbitrage round trip completed and closed immediately. |
| 2026-06-30T02:54:43Z | paper_order | USDC/WETH | SKIPPED | 0.0386844834347967972898421171 | Risk decision is WATCHLIST; paper order not created. Expected edge 0.0387% is below paper threshold 0.30%. |
| 2026-06-30T02:54:43Z | paper_order | WETH/USDC | CLOSED | 0.3318728206881047119859398240 | Atomic paper arbitrage round trip completed and closed immediately. |
| 2026-06-30T02:54:36Z | paper_order | USDC/WETH | SKIPPED | 0.0386844834347967972898421171 | Risk decision is WATCHLIST; paper order not created. Expected edge 0.0387% is below paper threshold 0.30%. |
| 2026-06-30T02:54:36Z | paper_order | WETH/USDC | CLOSED | 0.3318728206881047119859398240 | Atomic paper arbitrage round trip completed and closed immediately. |
| 2026-06-30T02:54:28Z | paper_order | USDC/WETH | SKIPPED | 0.0386844834347967972898421171 | Risk decision is WATCHLIST; paper order not created. Expected edge 0.0387% is below paper threshold 0.30%. |
| 2026-06-30T02:54:28Z | paper_order | WETH/USDC | CLOSED | 0.3318728206881047119859398240 | Atomic paper arbitrage round trip completed and closed immediately. |
| 2026-06-30T02:54:21Z | paper_order | USDC/WETH | SKIPPED | 0.0386844834347967972898421171 | Risk decision is WATCHLIST; paper order not created. Expected edge 0.0387% is below paper threshold 0.30%. |
| 2026-06-30T02:54:21Z | paper_order | WETH/USDC | CLOSED | 0.3318728206881047119859398240 | Atomic paper arbitrage round trip completed and closed immediately. |
| 2026-06-30T02:54:15Z | paper_order | USDC/WETH | SKIPPED | 0.0386844834347967972898421171 | Risk decision is WATCHLIST; paper order not created. Expected edge 0.0387% is below paper threshold 0.30%. |
| 2026-06-30T02:54:15Z | paper_order | WETH/USDC | CLOSED | 0.3318728206881047119859398240 | Atomic paper arbitrage round trip completed and closed immediately. |
| 2026-06-30T02:54:09Z | paper_order | USDC/WETH | SKIPPED | 0.0386844834347967972898421171 | Risk decision is WATCHLIST; paper order not created. Expected edge 0.0387% is below paper threshold 0.30%. |
| 2026-06-30T02:54:09Z | paper_order | WETH/USDC | CLOSED | 0.3318728206881047119859398240 | Atomic paper arbitrage round trip completed and closed immediately. |
| 2026-06-30T02:54:01Z | paper_order | USDC/WETH | SKIPPED | 0.0386844834347967972898421171 | Risk decision is WATCHLIST; paper order not created. Expected edge 0.0387% is below paper threshold 0.30%. |
| 2026-06-30T02:54:01Z | paper_order | WETH/USDC | CLOSED | 0.3318728206881047119859398240 | Atomic paper arbitrage round trip completed and closed immediately. |

## Notes

- Research metrics describe observed paper/simulated activity only.
- Do not infer live profitability from synthetic paper opportunities.
- The purpose of v4.0 is to accumulate research-grade data for later backtesting and AI ranking.
