# CryptoAI Replay Diagnostics

Generated: `2026-06-30T03:09:38Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Real signals: `1886`
- Synthetic signals: `0`
- Production cost buffer %: `0.30`
- Paper BUY threshold %: `0.30`
- Production trades: `391`
- Production PnL USD: `1270.8025`
- Positive-after-cost signals at production buffer: `1000`
- Best profitable cost buffer %: `0.20`
- Best profitable trades: `1000`
- Best profitable PnL USD: `2852.5283`

## Cost Buffer Scenarios

| Cost Buffer % | Signals | Trades | Skipped | PnL USD | Avg Net % | Max Net % |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 1886 | 1000 | 0 | 2852.5283 | 0.2853 | 0.4322 |
| 0.25 | 1886 | 1000 | 0 | 2352.5283 | 0.2353 | 0.3822 |
| 0.30 | 1886 | 1000 | 0 | 1852.5283 | 0.1853 | 0.3322 |
| 0.35 | 1886 | 697 | 303 | 1386.4051 | 0.1989 | 0.2822 |

## Findings

- `OK` Production buffer 0.30% and paper BUY threshold 0.30% produced 391 replay trade(s).

## Notes

- Replay Diagnostics replays recorded real opportunities only by default.
- It is explanatory research evidence and does not lower risk thresholds automatically.
- Use it to understand whether the replay blocker is caused by cost assumptions, low edge, or missing data.
