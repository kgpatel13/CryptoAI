# CryptoAI Feature Store Report

Generated: `2026-06-29T18:18:09Z`

## Summary

- Mode: `paper`
- Feature vectors: `475`
- Tradeable or filled: `180`
- Risk/execution rejected: `6`
- Average net edge %: `0.0927`
- Max net edge %: `0.3500`

## Source Counts

- `opportunity_decision`: 197
- `multi_dex_opportunity`: 201
- `paper_order`: 55
- `strategy_signal`: 22

## Decision Counts

- `SKIP`: 250
- `BUY`: 162
- `SKIPPED`: 37
- `FILLED`: 12
- `RISK_REJECTED`: 6
- `WATCH`: 2
- `READY_FOR_PAPER`: 6

## Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 220 |
| USDC/WETH | 214 |

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
