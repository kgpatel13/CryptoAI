# CryptoAI Replay Diagnostics

Generated: `2026-06-30T07:46:44Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Real signals: `932`
- Synthetic signals: `0`
- Production cost buffer %: `0.30`
- Paper BUY threshold %: `0.30`
- Production trades: `410`
- Production PnL USD: `1390.8106`
- Positive-after-cost signals at production buffer: `932`
- Best profitable cost buffer %: `0.20`
- Best profitable trades: `932`
- Best profitable PnL USD: `2663.1442`

## Cost Buffer Scenarios

| Cost Buffer % | Signals | Trades | Skipped | PnL USD | Avg Net % | Max Net % |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 932 | 932 | 0 | 2663.1442 | 0.2857 | 0.4643 |
| 0.25 | 932 | 932 | 0 | 2197.1442 | 0.2357 | 0.4143 |
| 0.30 | 932 | 932 | 0 | 1731.1442 | 0.1857 | 0.3643 |
| 0.35 | 932 | 596 | 336 | 1351.7530 | 0.2268 | 0.3143 |

## Findings

- `OK` Production buffer 0.30% and paper BUY threshold 0.30% produced 410 replay trade(s).

## Notes

- Replay Diagnostics replays recorded real opportunities only by default.
- It is explanatory research evidence and does not lower risk thresholds automatically.
- Use it to understand whether the replay blocker is caused by cost assumptions, low edge, or missing data.
