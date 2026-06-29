# CryptoAI Replay Diagnostics

Generated: `2026-06-29T18:05:19Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Real signals: `105`
- Synthetic signals: `82`
- Production cost buffer %: `0.30`
- Paper BUY threshold %: `0.30`
- Production trades: `0`
- Production PnL USD: `0.0000`
- Positive-after-cost signals at production buffer: `1`
- Best profitable cost buffer %: `0.20`
- Best profitable trades: `49`
- Best profitable PnL USD: `20.1128`

## Cost Buffer Scenarios

| Cost Buffer % | Signals | Trades | Skipped | PnL USD | Avg Net % | Max Net % |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 105 | 49 | 56 | 20.1128 | 0.0410 | 0.1035 |
| 0.25 | 105 | 17 | 88 | 2.2677 | 0.0133 | 0.0535 |
| 0.30 | 105 | 1 | 104 | 0.0355 | 0.0035 | 0.0035 |
| 0.35 | 105 | 0 | 105 | 0.0000 | 0.0000 | 0.0000 |

## Findings

- `WATCH` Production buffer 0.30% has 1 positive-after-cost signal(s), but 0 pass the paper BUY threshold 0.30%.
- `ACTION` Collect more execution-cost and closed-paper-trade evidence before considering any threshold change.

## Notes

- Replay Diagnostics replays recorded real opportunities only by default.
- It is explanatory research evidence and does not lower risk thresholds automatically.
- Use it to understand whether the replay blocker is caused by cost assumptions, low edge, or missing data.
