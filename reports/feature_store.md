# CryptoAI Feature Store Report

Generated: `2026-06-30T07:46:42Z`

## Summary

- Mode: `paper`
- Feature vectors: `2072`
- Tradeable or filled: `819`
- Risk/execution rejected: `0`
- Average net edge %: `0.1857`
- Max net edge %: `0.3643`

## Source Counts

- `opportunity_decision`: 928
- `multi_dex_opportunity`: 930
- `paper_order`: 212
- `strategy_signal`: 2

## Decision Counts

- `BUY`: 819
- `SKIP`: 671
- `WATCH`: 370
- `CLOSED`: 93
- `SKIPPED`: 119

## Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 1036 |
| USDC/WETH | 1036 |

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
