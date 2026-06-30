# CryptoAI Feature Store Report

Generated: `2026-06-30T03:09:39Z`

## Summary

- Mode: `paper`
- Feature vectors: `4192`
- Tradeable or filled: `783`
- Risk/execution rejected: `0`
- Average net edge %: `0.1852`
- Max net edge %: `0.3322`

## Source Counts

- `opportunity_decision`: 1884
- `multi_dex_opportunity`: 1886
- `paper_order`: 418
- `strategy_signal`: 4

## Decision Counts

- `WATCH`: 2384
- `BUY`: 783
- `SKIP`: 607
- `SKIPPED`: 335
- `CLOSED`: 83

## Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 2096 |
| USDC/WETH | 2096 |

## Data Quality

- `has_opportunities`: `True`
- `has_orders`: `True`
- `has_strategy_signals`: `True`
- `sqlite_enabled`: `True`
- `jsonl_enabled`: `True`
- `csv_enabled`: `True`

## Notes

- Feature vectors are research inputs, not live-trading approvals.
- Synthetic paper opportunities are labeled and must not be treated as live executable edge.
- Future AI ranking should consume these features only after enough historical outcomes exist.
