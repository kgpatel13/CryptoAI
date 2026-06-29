# CryptoAI Feature Store Report

Generated: `2026-06-29T01:08:32Z`

## Summary

- Mode: `paper`
- Feature vectors: `109`
- Tradeable or filled: `62`
- Risk/execution rejected: `6`
- Average net edge %: `0.3500`
- Max net edge %: `0.3500`

## Source Counts

- `opportunity_decision`: 29
- `multi_dex_opportunity`: 31
- `paper_order`: 45
- `strategy_signal`: 4

## Decision Counts

- `SKIP`: 14
- `BUY`: 46
- `SKIPPED`: 25
- `FILLED`: 14
- `RISK_REJECTED`: 6
- `WATCH`: 2
- `READY_FOR_PAPER`: 2

## Top Pairs

| Pair | Count |
|---|---:|
| WETH/USDC | 34 |
| USDC/WETH | 34 |

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
