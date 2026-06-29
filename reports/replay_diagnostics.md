# CryptoAI Replay Diagnostics

Generated: `2026-06-29T22:59:36Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Real signals: `147`
- Synthetic signals: `82`
- Production cost buffer %: `0.30`
- Paper BUY threshold %: `0.30`
- Production trades: `0`
- Production PnL USD: `0.0000`
- Positive-after-cost signals at production buffer: `9`
- Best profitable cost buffer %: `0.20`
- Best profitable trades: `70`
- Best profitable PnL USD: `33.3502`

## Cost Buffer Scenarios

| Cost Buffer % | Signals | Trades | Skipped | PnL USD | Avg Net % | Max Net % |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 147 | 70 | 77 | 33.3502 | 0.0476 | 0.1367 |
| 0.25 | 147 | 25 | 122 | 7.4122 | 0.0296 | 0.0867 |
| 0.30 | 147 | 9 | 138 | 1.1800 | 0.0131 | 0.0367 |
| 0.35 | 147 | 0 | 147 | 0.0000 | 0.0000 | 0.0000 |

## Findings

- `WATCH` Production buffer 0.30% has 9 positive-after-cost signal(s), but 0 pass the paper BUY threshold 0.30%.
- `ACTION` Collect more execution-cost and closed-paper-trade evidence before considering any threshold change.

## Notes

- Replay Diagnostics replays recorded real opportunities only by default.
- It is explanatory research evidence and does not lower risk thresholds automatically.
- Use it to understand whether the replay blocker is caused by cost assumptions, low edge, or missing data.
