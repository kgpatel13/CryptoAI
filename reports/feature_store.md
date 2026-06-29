# CryptoAI Feature Store Report

Generated: `2026-06-29T23:31:22Z`

## Summary

- Mode: `paper`
- Feature vectors: `639`
- Tradeable or filled: `190`
- Risk/execution rejected: `6`
- Average net edge %: `0.0495`
- Max net edge %: `0.3830`

## Source Counts

- `opportunity_decision`: 269
- `multi_dex_opportunity`: 277
- `paper_order`: 67
- `strategy_signal`: 26

## Decision Counts

- `SKIP`: 392
- `BUY`: 171
- `SKIPPED`: 49
- `FILLED`: 12
- `RISK_REJECTED`: 6
- `WATCH`: 2
- `READY_FOR_PAPER`: 7

## Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 302 |
| USDC/WETH | 296 |

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
