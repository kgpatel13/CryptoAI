# CryptoAI Replay Diagnostics

Generated: `2026-06-30T02:09:57Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Real signals: `20`
- Synthetic signals: `0`
- Production cost buffer %: `0.30`
- Paper BUY threshold %: `0.30`
- Production trades: `0`
- Production PnL USD: `0.0000`
- Positive-after-cost signals at production buffer: `20`
- Best profitable cost buffer %: `0.20`
- Best profitable trades: `20`
- Best profitable PnL USD: `57.0470`

## Cost Buffer Scenarios

| Cost Buffer % | Signals | Trades | Skipped | PnL USD | Avg Net % | Max Net % |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 20 | 20 | 0 | 57.0470 | 0.2852 | 0.3599 |
| 0.25 | 20 | 20 | 0 | 47.0470 | 0.2352 | 0.3099 |
| 0.30 | 20 | 20 | 0 | 37.0470 | 0.1852 | 0.2599 |
| 0.35 | 20 | 20 | 0 | 27.0470 | 0.1352 | 0.2099 |

## Findings

- `WATCH` Production buffer 0.30% has 20 positive-after-cost signal(s), but 0 pass the paper BUY threshold 0.30%.
- `ACTION` Collect more execution-cost and closed-paper-trade evidence before considering any threshold change.

## Notes

- Replay Diagnostics replays recorded real opportunities only by default.
- It is explanatory research evidence and does not lower risk thresholds automatically.
- Use it to understand whether the replay blocker is caused by cost assumptions, low edge, or missing data.
