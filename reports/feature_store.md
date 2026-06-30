# CryptoAI Feature Store Report

Generated: `2026-06-30T02:09:56Z`

## Summary

- Mode: `paper`
- Feature vectors: `44`
- Tradeable or filled: `0`
- Risk/execution rejected: `0`
- Average net edge %: `0.1852`
- Max net edge %: `0.2599`

## Source Counts

- `opportunity_decision`: 18
- `multi_dex_opportunity`: 20
- `paper_order`: 4
- `strategy_signal`: 2

## Decision Counts

- `WATCH`: 40
- `SKIPPED`: 4

## Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 22 |
| USDC/WETH | 22 |

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
