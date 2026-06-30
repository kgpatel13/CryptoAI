# CryptoAI Execution Cost Evidence

Generated: `2026-06-30T08:23:13Z`

## Summary

- Production cost buffer %: `0.30`
- Paper BUY threshold %: `0.30`
- Buffer status: `CONSERVATIVE`
- Confidence: `HIGH`
- Observed total cost lower bound %: `0.1300`
- Buffer surplus vs lower bound %: `0.1700`

## Configured Cost Model

- Gas buffer %: `0.08`
- Fee/slippage buffer %: `0.22`
- Total cost buffer %: `0.30`
- Source: `latest_opportunity_decision`

## Paper Execution Evidence

- Filled execution samples: `40`
- Avg slippage bps: `5.0000`
- P95 slippage bps: `5.0000`
- Max slippage bps: `5.0000`
- Avg latency ms: `250.0000`
- P95 latency ms: `250.0000`

## Quote And Provider Evidence

- Quote samples: `6`
- Quote OK rate %: `100.0000`
- Healthy DEX count: `3`
- Avg OK quote latency ms: `0.0700`
- Provider count: `4`
- Avg provider score: `100.0000`

## Replay Cost Evidence

- Real replay signals: `1636`
- Max gross edge %: `0.6643`
- Production-buffer trades: `639`
- Production required gross edge %: `0.60`
- Lower-bound cost trades: `1636`
- Lower-bound replay PnL USD: `5818.3967`

## Findings

- `INFO` Production buffer assessment is CONSERVATIVE with HIGH paper-cost confidence.

## Notes

- Execution Cost Evidence measures observed paper/replay/quote evidence only.
- It does not change production cost buffers, risk thresholds, or live-trading eligibility.
- Paper slippage plus configured gas is a measured lower bound, not a complete live execution-cost estimate.
