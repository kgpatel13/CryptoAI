# CryptoAI Replay Diagnostics

Generated: `2026-06-30T02:31:59Z`

## Summary

- Source: `data\multi_dex_opportunities.jsonl`
- Real signals: `6`
- Synthetic signals: `0`
- Production cost buffer %: `0.30`
- Paper BUY threshold %: `0.30`
- Production trades: `0`
- Production PnL USD: `0.0000`
- Positive-after-cost signals at production buffer: `6`
- Best profitable cost buffer %: `0.20`
- Best profitable trades: `6`
- Best profitable PnL USD: `17.1225`

## Cost Buffer Scenarios

| Cost Buffer % | Signals | Trades | Skipped | PnL USD | Avg Net % | Max Net % |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 6 | 6 | 0 | 17.1225 | 0.2854 | 0.3177 |
| 0.25 | 6 | 6 | 0 | 14.1225 | 0.2354 | 0.2677 |
| 0.30 | 6 | 6 | 0 | 11.1225 | 0.1854 | 0.2177 |
| 0.35 | 6 | 6 | 0 | 8.1225 | 0.1354 | 0.1677 |

## Findings

- `WATCH` Production buffer 0.30% has 6 positive-after-cost signal(s), but 0 pass the paper BUY threshold 0.30%.
- `ACTION` Collect more execution-cost and closed-paper-trade evidence before considering any threshold change.

## Notes

- Replay Diagnostics replays recorded real opportunities only by default.
- It is explanatory research evidence and does not lower risk thresholds automatically.
- Use it to understand whether the replay blocker is caused by cost assumptions, low edge, or missing data.
