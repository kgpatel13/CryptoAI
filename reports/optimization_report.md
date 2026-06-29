# CryptoAI Optimization Report

Generated: `2026-06-29T22:59:36Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Input rows: `298`
- De-duplicated rows: `229`
- Scenarios: `60`
- Include synthetic: `False`

## Best Scenario

- Cost buffer %: `0.20`
- Minimum net edge %: `0.00`
- Notional USD: `1000`
- Trades: `70`
- Total PnL USD: `33.3502`
- Max drawdown USD: `0.0000`

## Scenario Ranking

| Cost % | Min Net % | Notional | Signals | Trades | PnL | Max DD |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 0.00 | 1000 | 147 | 70 | 33.3502 | 0.0000 |
| 0.20 | 0.05 | 1000 | 147 | 25 | 19.9122 | 0.0000 |
| 0.20 | 0.10 | 1000 | 147 | 9 | 10.1800 | 0.0000 |
| 0.20 | 0.00 | 250 | 147 | 70 | 8.3389 | 0.0000 |
| 0.25 | 0.00 | 1000 | 147 | 25 | 7.4122 | 0.0000 |
| 0.25 | 0.05 | 1000 | 147 | 9 | 5.6800 | 0.0000 |
| 0.20 | 0.05 | 250 | 147 | 25 | 4.9783 | 0.0000 |
| 0.20 | 0.00 | 100 | 147 | 70 | 3.3349 | 0.0000 |
| 0.20 | 0.10 | 250 | 147 | 9 | 2.5452 | 0.0000 |
| 0.20 | 0.05 | 100 | 147 | 25 | 1.9911 | 0.0000 |
| 0.25 | 0.00 | 250 | 147 | 25 | 1.8533 | 0.0000 |
| 0.25 | 0.05 | 250 | 147 | 9 | 1.4202 | 0.0000 |
| 0.30 | 0.00 | 1000 | 147 | 9 | 1.1800 | 0.0000 |
| 0.20 | 0.10 | 100 | 147 | 9 | 1.0179 | 0.0000 |
| 0.25 | 0.00 | 100 | 147 | 25 | 0.7411 | 0.0000 |
| 0.25 | 0.05 | 100 | 147 | 9 | 0.5679 | 0.0000 |
| 0.30 | 0.00 | 250 | 147 | 9 | 0.2952 | 0.0000 |
| 0.30 | 0.00 | 100 | 147 | 9 | 0.1179 | 0.0000 |
| 0.20 | 0.20 | 100 | 147 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 250 | 147 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 1000 | 147 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.30 | 100 | 147 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.30 | 250 | 147 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.30 | 1000 | 147 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 100 | 147 | 0 | 0.0000 | 0.0000 |

## Notes

- Optimization replays recorded opportunities only; it does not fetch markets or execute trades.
- Synthetic paper opportunities are excluded unless include_synthetic is true.
- Results are research evidence, not live-trading approval.
