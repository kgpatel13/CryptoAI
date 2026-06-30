# CryptoAI Optimization Report

Generated: `2026-06-30T02:31:59Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Input rows: `6`
- De-duplicated rows: `6`
- Scenarios: `60`
- Include synthetic: `False`

## Best Scenario

- Cost buffer %: `0.20`
- Minimum net edge %: `0.00`
- Notional USD: `1000`
- Trades: `6`
- Total PnL USD: `17.1225`
- Max drawdown USD: `0.0000`

## Scenario Ranking

| Cost % | Min Net % | Notional | Signals | Trades | PnL | Max DD |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 0.00 | 1000 | 6 | 6 | 17.1225 | 0.0000 |
| 0.20 | 0.05 | 1000 | 6 | 6 | 17.1225 | 0.0000 |
| 0.20 | 0.10 | 1000 | 6 | 6 | 17.1225 | 0.0000 |
| 0.20 | 0.20 | 1000 | 6 | 6 | 17.1225 | 0.0000 |
| 0.25 | 0.00 | 1000 | 6 | 6 | 14.1225 | 0.0000 |
| 0.25 | 0.05 | 1000 | 6 | 6 | 14.1225 | 0.0000 |
| 0.25 | 0.10 | 1000 | 6 | 6 | 14.1225 | 0.0000 |
| 0.25 | 0.20 | 1000 | 6 | 6 | 14.1225 | 0.0000 |
| 0.30 | 0.00 | 1000 | 6 | 6 | 11.1225 | 0.0000 |
| 0.30 | 0.05 | 1000 | 6 | 6 | 11.1225 | 0.0000 |
| 0.30 | 0.10 | 1000 | 6 | 6 | 11.1225 | 0.0000 |
| 0.20 | 0.30 | 1000 | 6 | 3 | 9.5313 | 0.0000 |
| 0.35 | 0.00 | 1000 | 6 | 6 | 8.1225 | 0.0000 |
| 0.35 | 0.05 | 1000 | 6 | 6 | 8.1225 | 0.0000 |
| 0.35 | 0.10 | 1000 | 6 | 6 | 8.1225 | 0.0000 |
| 0.30 | 0.20 | 1000 | 6 | 3 | 6.5313 | 0.0000 |
| 0.20 | 0.00 | 250 | 6 | 6 | 4.2807 | 0.0000 |
| 0.20 | 0.05 | 250 | 6 | 6 | 4.2807 | 0.0000 |
| 0.20 | 0.10 | 250 | 6 | 6 | 4.2807 | 0.0000 |
| 0.20 | 0.20 | 250 | 6 | 6 | 4.2807 | 0.0000 |
| 0.25 | 0.00 | 250 | 6 | 6 | 3.5307 | 0.0000 |
| 0.25 | 0.05 | 250 | 6 | 6 | 3.5307 | 0.0000 |
| 0.25 | 0.10 | 250 | 6 | 6 | 3.5307 | 0.0000 |
| 0.25 | 0.20 | 250 | 6 | 6 | 3.5307 | 0.0000 |
| 0.30 | 0.00 | 250 | 6 | 6 | 2.7807 | 0.0000 |

## Notes

- Optimization replays recorded opportunities only; it does not fetch markets or execute trades.
- Synthetic paper opportunities are excluded unless include_synthetic is true.
- Results are research evidence, not live-trading approval.
