# CryptoAI Replay Diagnostics

Generated: `2026-06-29T14:15:00Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Real signals: `79`
- Synthetic signals: `82`
- Production cost buffer %: `0.30`
- Production trades: `0`
- Production PnL USD: `0.0000`
- Best profitable cost buffer %: `0.20`
- Best profitable trades: `36`
- Best profitable PnL USD: `13.1480`

## Cost Buffer Scenarios

| Cost Buffer % | Signals | Trades | Skipped | PnL USD | Avg Net % | Max Net % |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 79 | 36 | 43 | 13.1480 | 0.0365 | 0.0701 |
| 0.25 | 79 | 11 | 68 | 1.4382 | 0.0131 | 0.0201 |
| 0.30 | 79 | 0 | 79 | 0.0000 | 0.0000 | 0.0000 |
| 0.35 | 79 | 0 | 79 | 0.0000 | 0.0000 | 0.0000 |

## Findings

- `WATCH` Production buffer 0.30% produced 0 trades; buffer 0.20% produced 36 trade(s).
- `ACTION` Collect execution-cost evidence before considering any lower paper threshold.

## Notes

- Replay Diagnostics replays recorded real opportunities only by default.
- It is explanatory research evidence and does not lower risk thresholds automatically.
- Use it to understand whether the replay blocker is caused by cost assumptions, low edge, or missing data.
