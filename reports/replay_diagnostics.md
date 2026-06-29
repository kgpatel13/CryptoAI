# CryptoAI Replay Diagnostics

Generated: `2026-06-29T23:31:26Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Real signals: `195`
- Synthetic signals: `82`
- Production cost buffer %: `0.30`
- Paper BUY threshold %: `0.30`
- Production trades: `5`
- Production PnL USD: `19.1500`
- Positive-after-cost signals at production buffer: `14`
- Best profitable cost buffer %: `0.20`
- Best profitable trades: `99`
- Best profitable PnL USD: `68.9755`

## Cost Buffer Scenarios

| Cost Buffer % | Signals | Trades | Skipped | PnL USD | Avg Net % | Max Net % |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 195 | 99 | 96 | 68.9755 | 0.0697 | 0.4830 |
| 0.25 | 195 | 35 | 160 | 31.1037 | 0.0889 | 0.4330 |
| 0.30 | 195 | 14 | 181 | 20.3300 | 0.1452 | 0.3830 |
| 0.35 | 195 | 5 | 190 | 16.6500 | 0.3330 | 0.3330 |

## Findings

- `OK` Production buffer 0.30% and paper BUY threshold 0.30% produced 5 replay trade(s).

## Notes

- Replay Diagnostics replays recorded real opportunities only by default.
- It is explanatory research evidence and does not lower risk thresholds automatically.
- Use it to understand whether the replay blocker is caused by cost assumptions, low edge, or missing data.
