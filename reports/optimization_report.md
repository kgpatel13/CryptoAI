# CryptoAI Optimization Report

Generated: `2026-06-29T17:48:56Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Input rows: `236`
- De-duplicated rows: `185`
- Scenarios: `48`
- Include synthetic: `False`

## Best Scenario

- Cost buffer %: `0.20`
- Minimum net edge %: `0.00`
- Notional USD: `1000`
- Trades: `48`
- Total PnL USD: `19.0773`
- Max drawdown USD: `0.0000`

## Scenario Ranking

| Cost % | Min Net % | Notional | Signals | Trades | PnL | Max DD |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 0.00 | 1000 | 103 | 48 | 19.0773 | 0.0000 |
| 0.20 | 0.05 | 1000 | 103 | 16 | 9.7322 | 0.0000 |
| 0.20 | 0.00 | 250 | 103 | 48 | 4.7701 | 0.0000 |
| 0.20 | 0.05 | 250 | 103 | 16 | 2.4331 | 0.0000 |
| 0.20 | 0.00 | 100 | 103 | 48 | 1.9077 | 0.0000 |
| 0.25 | 0.00 | 1000 | 103 | 16 | 1.7322 | 0.0000 |
| 0.20 | 0.05 | 100 | 103 | 16 | 0.9732 | 0.0000 |
| 0.25 | 0.00 | 250 | 103 | 16 | 0.4331 | 0.0000 |
| 0.25 | 0.00 | 100 | 103 | 16 | 0.1732 | 0.0000 |
| 0.20 | 0.10 | 100 | 103 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.10 | 250 | 103 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.10 | 1000 | 103 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 100 | 103 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 250 | 103 | 0 | 0.0000 | 0.0000 |
| 0.20 | 0.20 | 1000 | 103 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 100 | 103 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 250 | 103 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.05 | 1000 | 103 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 100 | 103 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 250 | 103 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.10 | 1000 | 103 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 100 | 103 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 250 | 103 | 0 | 0.0000 | 0.0000 |
| 0.25 | 0.20 | 1000 | 103 | 0 | 0.0000 | 0.0000 |
| 0.30 | 0.00 | 100 | 103 | 0 | 0.0000 | 0.0000 |

## Notes

- Optimization replays recorded opportunities only; it does not fetch markets or execute trades.
- Synthetic paper opportunities are excluded unless include_synthetic is true.
- Results are research evidence, not live-trading approval.
