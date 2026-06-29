# CryptoAI Replay Diagnostics

Generated: `2026-06-29T18:18:11Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Real signals: `119`
- Synthetic signals: `82`
- Production cost buffer %: `0.30`
- Paper BUY threshold %: `0.30`
- Production trades: `0`
- Production PnL USD: `0.0000`
- Positive-after-cost signals at production buffer: `8`
- Best profitable cost buffer %: `0.20`
- Best profitable trades: `56`
- Best profitable PnL USD: `28.1462`

## Cost Buffer Scenarios

| Cost Buffer % | Signals | Trades | Skipped | PnL USD | Avg Net % | Max Net % |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 119 | 56 | 63 | 28.1462 | 0.0503 | 0.1367 |
| 0.25 | 119 | 24 | 95 | 6.8011 | 0.0283 | 0.0867 |
| 0.30 | 119 | 8 | 111 | 1.0689 | 0.0134 | 0.0367 |
| 0.35 | 119 | 0 | 119 | 0.0000 | 0.0000 | 0.0000 |

## Findings

- `WATCH` Production buffer 0.30% has 8 positive-after-cost signal(s), but 0 pass the paper BUY threshold 0.30%.
- `ACTION` Collect more execution-cost and closed-paper-trade evidence before considering any threshold change.

## Notes

- Replay Diagnostics replays recorded real opportunities only by default.
- It is explanatory research evidence and does not lower risk thresholds automatically.
- Use it to understand whether the replay blocker is caused by cost assumptions, low edge, or missing data.
