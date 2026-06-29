# CryptoAI Feature Store Report

Generated: `2026-06-29T13:25:17Z`

## Summary

- Mode: `paper`
- Feature vectors: `303`
- Tradeable or filled: `180`
- Risk/execution rejected: `6`
- Average net edge %: `0.2194`
- Max net edge %: `0.3500`

## Source Counts

- `opportunity_decision`: 123
- `multi_dex_opportunity`: 125
- `paper_order`: 45
- `strategy_signal`: 10

## Decision Counts

- `SKIP`: 88
- `BUY`: 162
- `SKIPPED`: 27
- `FILLED`: 12
- `RISK_REJECTED`: 6
- `WATCH`: 2
- `READY_FOR_PAPER`: 6

## Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 134 |
| USDC/WETH | 128 |

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
