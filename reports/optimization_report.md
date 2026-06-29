# CryptoAI Optimization Report

Generated: `2026-06-29T18:05:19Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Input rows: `240`
- De-duplicated rows: `187`
- Scenarios: `60`
- Include synthetic: `False`

## Best Scenario

- Cost buffer %: `0.20`
- Minimum net edge %: `0.00`
- Notional USD: `1000`
- Trades: `49`
- Total PnL USD: `20.1128`
- Max drawdown USD: `0.0000`

## Scenario Ranking

| Cost % | Min Net % | Notional | Signals | Trades | PnL | Max DD |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 0.00 | 1000 | 105 | 49 | 20.1128 | 0.0000 |
| 0.20 | 0.05 | 1000 | 105 | 17 | 10.7677 | 0.0000 |
| 0.20 | 0.00 | 250 | 105 | 49 | 5.0290 | 0.0000 |
| 0.20 | 0.05 | 250 | 105 | 17 | 2.6920 | 0.0000 |
| 0.25 | 0.00 | 1000 | 105 | 17 | 2.2677 | 0.0000 |
| 0.20 | 0.00 | 100 | 105 | 49 | 2.0112 | 0.0000 |
| 0.20 | 0.05 | 100 | 105 | 17 | 1.0767 | 0.0000 |
| 0.20 | 0.10 | 1000 | 105 | 1 | 1.0355 | 0.0000 |
| 0.25 | 0.00 | 250 | 105 | 17 | 0.5670 | 0.0000 |
| 0.25 | 0.05 | 1000 | 105 | 1 | 0.5355 | 0.0000 |
| 0.20 | 0.10 | 250 | 105 | 1 | 0.2589 | 0.0000 |
| 0.25 | 0.00 | 100 | 105 | 17 | 0.2267 | 0.0000 |
| 0.25 | 0.05 | 250 | 105 | 1 | 0.1339 | 0.0000 |
| 0.20 | 0.10 | 100 | 105 | 1 | 0.1035 | 0.0000 |
| 0.25 | 0.05 | 100 | 105 | 1 | 0.0535 | 0.0000 |
| 0.30 | 0.00 | 1000 | 105 | 1 | 0.0355 | 0.0000 |
| 0.30 | 0.00 | 250 | 105 | 1 | 0.0089 | 0.0000 |
| 0.30 | 0.00 | 100 | 105 | 1 | 0.0035 | 0.0000 |
| 0.20 | 0.20 | 100 | 105 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 250 | 105 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 1000 | 105 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.30 | 100 | 105 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.30 | 250 | 105 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.30 | 1000 | 105 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 100 | 105 | 0 | 0.0000 | 0.0000 |

## Notes

- Optimization replays recorded opportunities only; it does not fetch markets or execute trades.
- Synthetic paper opportunities are excluded unless include_synthetic is true.
- Results are research evidence, not live-trading approval.
