# CryptoAI Feature Store Report

Generated: `2026-06-30T02:31:59Z`

## Summary

- Mode: `paper`
- Feature vectors: `12`
- Tradeable or filled: `0`
- Risk/execution rejected: `0`
- Average net edge %: `0.1854`
- Max net edge %: `0.2177`

## Source Counts

- `opportunity_decision`: 4
- `multi_dex_opportunity`: 6
- `strategy_signal`: 2

## Decision Counts

- `WATCH`: 12

## Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 6 |
| USDC/WETH | 6 |

## Data Quality

- `has_opportunities`: `True`
- `has_orders`: `False`
- `has_strategy_signals`: `True`
- `sqlite_enabled`: `True`
- `jsonl_enabled`: `True`
- `csv_enabled`: `True`

## Notes

- Feature vectors are research inputs, not live-trading approvals.
- Synthetic paper opportunities are labeled and must not be treated as live executable edge.
- Future AI ranking should consume these features only after enough historical outcomes exist.
