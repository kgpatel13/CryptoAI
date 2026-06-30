# CryptoAI Feature Store Report

Generated: `2026-06-30T02:54:58Z`

## Summary

- Mode: `paper`
- Feature vectors: `3648`
- Tradeable or filled: `625`
- Risk/execution rejected: `0`
- Average net edge %: `0.1852`
- Max net edge %: `0.3319`

## Source Counts

- `opportunity_decision`: 1638
- `multi_dex_opportunity`: 1640
- `paper_order`: 368
- `strategy_signal`: 2

## Decision Counts

- `WATCH`: 2206
- `BUY`: 625
- `SKIP`: 449
- `SKIPPED`: 301
- `CLOSED`: 67

## Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 1824 |
| USDC/WETH | 1824 |

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
