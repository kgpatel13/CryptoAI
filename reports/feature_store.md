# CryptoAI Feature Store Report

Generated: `2026-06-29T12:47:20Z`

## Summary

- Mode: `paper`
- Feature vectors: `279`
- Tradeable or filled: `186`
- Risk/execution rejected: `6`
- Average net edge %: `0.2630`
- Max net edge %: `0.3500`

## Source Counts

- `opportunity_decision`: 109
- `multi_dex_opportunity`: 111
- `paper_order`: 49
- `strategy_signal`: 10

## Decision Counts

- `SKIP`: 60
- `BUY`: 162
- `SKIPPED`: 25
- `FILLED`: 18
- `RISK_REJECTED`: 6
- `WATCH`: 2
- `READY_FOR_PAPER`: 6

## Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 119 |
| USDC/WETH | 119 |

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
