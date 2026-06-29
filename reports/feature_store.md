# CryptoAI Feature Store Report

Generated: `2026-06-29T17:45:19Z`

## Summary

- Mode: `paper`
- Feature vectors: `433`
- Tradeable or filled: `180`
- Risk/execution rejected: `6`
- Average net edge %: `0.1133`
- Max net edge %: `0.3500`

## Source Counts

- `opportunity_decision`: 179
- `multi_dex_opportunity`: 181
- `paper_order`: 53
- `strategy_signal`: 20

## Decision Counts

- `SKIP`: 210
- `BUY`: 162
- `SKIPPED`: 35
- `FILLED`: 12
- `RISK_REJECTED`: 6
- `WATCH`: 2
- `READY_FOR_PAPER`: 6

## Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 199 |
| USDC/WETH | 193 |

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
