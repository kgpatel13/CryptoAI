# CryptoAI Optimization Report

Generated: `2026-06-29T12:58:10Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Input rows: `154`
- De-duplicated rows: `119`
- Scenarios: `48`
- Include synthetic: `False`

## Best Scenario

- Cost buffer %: `0.20`
- Minimum net edge %: `0.00`
- Notional USD: `1000`
- Trades: `15`
- Total PnL USD: `7.6008`
- Max drawdown USD: `0.0000`

## Scenario Ranking

| Cost % | Min Net % | Notional | Signals | Trades | PnL | Max DD |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 0.00 | 1000 | 37 | 15 | 7.6008 | 0.0000 |
| 0.20 | 0.05 | 1000 | 37 | 7 | 4.8938 | 0.0000 |
| 0.20 | 0.00 | 250 | 37 | 15 | 1.8999 | 0.0000 |
| 0.25 | 0.00 | 1000 | 37 | 7 | 1.3938 | 0.0000 |
| 0.20 | 0.05 | 250 | 37 | 7 | 1.2232 | 0.0000 |
| 0.20 | 0.00 | 100 | 37 | 15 | 0.7598 | 0.0000 |
| 0.20 | 0.05 | 100 | 37 | 7 | 0.4892 | 0.0000 |
| 0.25 | 0.00 | 250 | 37 | 7 | 0.3482 | 0.0000 |
| 0.25 | 0.00 | 100 | 37 | 7 | 0.1392 | 0.0000 |
| 0.20 | 0.10 | 100 | 37 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.10 | 250 | 37 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.10 | 1000 | 37 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 100 | 37 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 250 | 37 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 1000 | 37 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 100 | 37 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 250 | 37 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 1000 | 37 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 100 | 37 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 250 | 37 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 1000 | 37 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 100 | 37 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 250 | 37 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 1000 | 37 | 0 | 0.0000 | 0.0000 |
| 0.30 | 0.00 | 100 | 37 | 0 | 0.0000 | 0.0000 |

## Notes

- Optimization replays recorded opportunities only; it does not fetch markets or execute trades.
- Synthetic paper opportunities are excluded unless include_synthetic is true.
- Results are research evidence, not live-trading approval.
