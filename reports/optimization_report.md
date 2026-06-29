# CryptoAI Optimization Report

Generated: `2026-06-29T13:25:42Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Input rows: `166`
- De-duplicated rows: `127`
- Scenarios: `48`
- Include synthetic: `False`

## Best Scenario

- Cost buffer %: `0.20`
- Minimum net edge %: `0.00`
- Notional USD: `1000`
- Trades: `19`
- Total PnL USD: `9.6452`
- Max drawdown USD: `0.0000`

## Scenario Ranking

| Cost % | Min Net % | Notional | Signals | Trades | PnL | Max DD |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 0.00 | 1000 | 45 | 19 | 9.6452 | 0.0000 |
| 0.20 | 0.05 | 1000 | 45 | 11 | 6.9382 | 0.0000 |
| 0.20 | 0.00 | 250 | 45 | 19 | 2.4111 | 0.0000 |
| 0.20 | 0.05 | 250 | 45 | 11 | 1.7344 | 0.0000 |
| 0.25 | 0.00 | 1000 | 45 | 11 | 1.4382 | 0.0000 |
| 0.20 | 0.00 | 100 | 45 | 19 | 0.9642 | 0.0000 |
| 0.20 | 0.05 | 100 | 45 | 11 | 0.6936 | 0.0000 |
| 0.25 | 0.00 | 250 | 45 | 11 | 0.3594 | 0.0000 |
| 0.25 | 0.00 | 100 | 45 | 11 | 0.1436 | 0.0000 |
| 0.20 | 0.10 | 100 | 45 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.10 | 250 | 45 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.10 | 1000 | 45 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 100 | 45 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 250 | 45 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 1000 | 45 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 100 | 45 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 250 | 45 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 1000 | 45 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 100 | 45 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 250 | 45 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 1000 | 45 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 100 | 45 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 250 | 45 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 1000 | 45 | 0 | 0.0000 | 0.0000 |
| 0.30 | 0.00 | 100 | 45 | 0 | 0.0000 | 0.0000 |

## Notes

- Optimization replays recorded opportunities only; it does not fetch markets or execute trades.
- Synthetic paper opportunities are excluded unless include_synthetic is true.
- Results are research evidence, not live-trading approval.
