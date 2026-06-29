# CryptoAI Replay Diagnostics

Generated: `2026-06-29T17:48:56Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Real signals: `103`
- Synthetic signals: `82`
- Production cost buffer %: `0.30`
- Production trades: `0`
- Production PnL USD: `0.0000`
- Best profitable cost buffer %: `0.20`
- Best profitable trades: `48`
- Best profitable PnL USD: `19.0773`

## Cost Buffer Scenarios

| Cost Buffer % | Signals | Trades | Skipped | PnL USD | Avg Net % | Max Net % |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 103 | 48 | 55 | 19.0773 | 0.0397 | 0.0760 |
| 0.25 | 103 | 16 | 87 | 1.7322 | 0.0108 | 0.0260 |
| 0.30 | 103 | 0 | 103 | 0.0000 | 0.0000 | 0.0000 |
| 0.35 | 103 | 0 | 103 | 0.0000 | 0.0000 | 0.0000 |

## Findings

- `WATCH` Production buffer 0.30% produced 0 trades; buffer 0.20% produced 48 trade(s).
- `ACTION` Collect execution-cost evidence before considering any lower paper threshold.

## Notes

- Replay Diagnostics replays recorded real opportunities only by default.
- It is explanatory research evidence and does not lower risk thresholds automatically.
- Use it to understand whether the replay blocker is caused by cost assumptions, low edge, or missing data.
