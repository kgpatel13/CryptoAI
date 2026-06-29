# CryptoAI Feature Store Report

Generated: `2026-06-29T14:12:20Z`

## Summary

- Mode: `paper`
- Feature vectors: `365`
- Tradeable or filled: `180`
- Risk/execution rejected: `6`
- Average net edge %: `0.1582`
- Max net edge %: `0.3500`

## Source Counts

- `opportunity_decision`: 149
- `multi_dex_opportunity`: 151
- `paper_order`: 49
- `strategy_signal`: 16

## Decision Counts

- `SKIP`: 146
- `BUY`: 162
- `SKIPPED`: 31
- `FILLED`: 12
- `RISK_REJECTED`: 6
- `WATCH`: 2
- `READY_FOR_PAPER`: 6

## Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 165 |
| USDC/WETH | 159 |

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
