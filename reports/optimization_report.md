# CryptoAI Optimization Report

Generated: `2026-06-29T12:47:25Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Input rows: `146`
- De-duplicated rows: `111`
- Scenarios: `48`
- Include synthetic: `False`

## Best Scenario

- Cost buffer %: `0.20`
- Minimum net edge %: `0.00`
- Notional USD: `1000`
- Trades: `11`
- Total PnL USD: `6.2028`
- Max drawdown USD: `0.0000`

## Scenario Ranking

| Cost % | Min Net % | Notional | Signals | Trades | PnL | Max DD |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 0.00 | 1000 | 29 | 11 | 6.2028 | 0.0000 |
| 0.20 | 0.05 | 1000 | 29 | 7 | 4.8938 | 0.0000 |
| 0.20 | 0.00 | 250 | 29 | 11 | 1.5505 | 0.0000 |
| 0.25 | 0.00 | 1000 | 29 | 7 | 1.3938 | 0.0000 |
| 0.20 | 0.05 | 250 | 29 | 7 | 1.2232 | 0.0000 |
| 0.20 | 0.00 | 100 | 29 | 11 | 0.6200 | 0.0000 |
| 0.20 | 0.05 | 100 | 29 | 7 | 0.4892 | 0.0000 |
| 0.25 | 0.00 | 250 | 29 | 7 | 0.3482 | 0.0000 |
| 0.25 | 0.00 | 100 | 29 | 7 | 0.1392 | 0.0000 |
| 0.20 | 0.10 | 100 | 29 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.10 | 250 | 29 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.10 | 1000 | 29 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 100 | 29 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 250 | 29 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 1000 | 29 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 100 | 29 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 250 | 29 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 1000 | 29 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 100 | 29 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 250 | 29 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 1000 | 29 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 100 | 29 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 250 | 29 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 1000 | 29 | 0 | 0.0000 | 0.0000 |
| 0.30 | 0.00 | 100 | 29 | 0 | 0.0000 | 0.0000 |

## Notes

- Optimization replays recorded opportunities only; it does not fetch markets or execute trades.
- Synthetic paper opportunities are excluded unless include_synthetic is true.
- Results are research evidence, not live-trading approval.
