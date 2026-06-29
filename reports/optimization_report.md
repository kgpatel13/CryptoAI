# CryptoAI Optimization Report

Generated: `2026-06-29T14:15:00Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Input rows: `208`
- De-duplicated rows: `161`
- Scenarios: `48`
- Include synthetic: `False`

## Best Scenario

- Cost buffer %: `0.20`
- Minimum net edge %: `0.00`
- Notional USD: `1000`
- Trades: `36`
- Total PnL USD: `13.1480`
- Max drawdown USD: `0.0000`

## Scenario Ranking

| Cost % | Min Net % | Notional | Signals | Trades | PnL | Max DD |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 0.00 | 1000 | 79 | 36 | 13.1480 | 0.0000 |
| 0.20 | 0.05 | 1000 | 79 | 11 | 6.9382 | 0.0000 |
| 0.20 | 0.00 | 250 | 79 | 36 | 3.2874 | 0.0000 |
| 0.20 | 0.05 | 250 | 79 | 11 | 1.7344 | 0.0000 |
| 0.25 | 0.00 | 1000 | 79 | 11 | 1.4382 | 0.0000 |
| 0.20 | 0.00 | 100 | 79 | 36 | 1.3145 | 0.0000 |
| 0.20 | 0.05 | 100 | 79 | 11 | 0.6936 | 0.0000 |
| 0.25 | 0.00 | 250 | 79 | 11 | 0.3594 | 0.0000 |
| 0.25 | 0.00 | 100 | 79 | 11 | 0.1436 | 0.0000 |
| 0.20 | 0.10 | 100 | 79 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.10 | 250 | 79 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.10 | 1000 | 79 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 100 | 79 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 250 | 79 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 1000 | 79 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 100 | 79 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 250 | 79 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 1000 | 79 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 100 | 79 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 250 | 79 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 1000 | 79 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 100 | 79 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 250 | 79 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 1000 | 79 | 0 | 0.0000 | 0.0000 |
| 0.30 | 0.00 | 100 | 79 | 0 | 0.0000 | 0.0000 |

## Notes

- Optimization replays recorded opportunities only; it does not fetch markets or execute trades.
- Synthetic paper opportunities are excluded unless include_synthetic is true.
- Results are research evidence, not live-trading approval.
