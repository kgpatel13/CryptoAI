# CryptoAI Feature Store Report

Generated: `2026-06-29T02:29:07Z`

## Summary

- Mode: `paper`
- Feature vectors: `213`
- Tradeable or filled: `166`
- Risk/execution rejected: `6`
- Average net edge %: `0.3500`
- Max net edge %: `0.3500`

## Source Counts

- `opportunity_decision`: 77
- `multi_dex_opportunity`: 79
- `paper_order`: 49
- `strategy_signal`: 8

## Decision Counts

- `SKIP`: 14
- `BUY`: 142
- `SKIPPED`: 25
- `FILLED`: 18
- `RISK_REJECTED`: 6
- `WATCH`: 2
- `READY_FOR_PAPER`: 6

## Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 86 |
| USDC/WETH | 86 |

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
