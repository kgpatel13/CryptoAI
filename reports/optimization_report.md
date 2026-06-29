# CryptoAI Optimization Report

Generated: `2026-06-29T18:18:11Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Input rows: `260`
- De-duplicated rows: `201`
- Scenarios: `60`
- Include synthetic: `False`

## Best Scenario

- Cost buffer %: `0.20`
- Minimum net edge %: `0.00`
- Notional USD: `1000`
- Trades: `56`
- Total PnL USD: `28.1462`
- Max drawdown USD: `0.0000`

## Scenario Ranking

| Cost % | Min Net % | Notional | Signals | Trades | PnL | Max DD |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 0.00 | 1000 | 119 | 56 | 28.1462 | 0.0000 |
| 0.20 | 0.05 | 1000 | 119 | 24 | 18.8011 | 0.0000 |
| 0.20 | 0.10 | 1000 | 119 | 8 | 9.0689 | 0.0000 |
| 0.20 | 0.00 | 250 | 119 | 56 | 7.0375 | 0.0000 |
| 0.25 | 0.00 | 1000 | 119 | 24 | 6.8011 | 0.0000 |
| 0.25 | 0.05 | 1000 | 119 | 8 | 5.0689 | 0.0000 |
| 0.20 | 0.05 | 250 | 119 | 24 | 4.7005 | 0.0000 |
| 0.20 | 0.00 | 100 | 119 | 56 | 2.8145 | 0.0000 |
| 0.20 | 0.10 | 250 | 119 | 8 | 2.2674 | 0.0000 |
| 0.20 | 0.05 | 100 | 119 | 24 | 1.8800 | 0.0000 |
| 0.25 | 0.00 | 250 | 119 | 24 | 1.7005 | 0.0000 |
| 0.25 | 0.05 | 250 | 119 | 8 | 1.2674 | 0.0000 |
| 0.30 | 0.00 | 1000 | 119 | 8 | 1.0689 | 0.0000 |
| 0.20 | 0.10 | 100 | 119 | 8 | 0.9068 | 0.0000 |
| 0.25 | 0.00 | 100 | 119 | 24 | 0.6800 | 0.0000 |
| 0.25 | 0.05 | 100 | 119 | 8 | 0.5068 | 0.0000 |
| 0.30 | 0.00 | 250 | 119 | 8 | 0.2674 | 0.0000 |
| 0.30 | 0.00 | 100 | 119 | 8 | 0.1068 | 0.0000 |
| 0.20 | 0.20 | 100 | 119 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 250 | 119 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 1000 | 119 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.30 | 100 | 119 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.30 | 250 | 119 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.30 | 1000 | 119 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 100 | 119 | 0 | 0.0000 | 0.0000 |

## Notes

- Optimization replays recorded opportunities only; it does not fetch markets or execute trades.
- Synthetic paper opportunities are excluded unless include_synthetic is true.
- Results are research evidence, not live-trading approval.
