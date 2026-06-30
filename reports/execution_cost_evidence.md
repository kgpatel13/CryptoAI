# CryptoAI Execution Cost Evidence

Generated: `2026-06-30T18:49:08Z`

## Summary

- Production cost buffer %: `0.30`
- Paper BUY threshold %: `0.30`
- Buffer status: `CONSERVATIVE`
- Confidence: `MEDIUM`
- Observed total cost lower bound %: `0.1300`
- Buffer surplus vs lower bound %: `0.1700`

## Configured Cost Model

- Gas buffer %: `0.08`
- Fee/slippage buffer %: `0.22`
- Total cost buffer %: `0.30`
- Source: `latest_opportunity_decision`

## Paper Execution Evidence

- Filled execution samples: `114`
- Avg slippage bps: `5.0000`
- P95 slippage bps: `5.0000`
- Max slippage bps: `5.0000`
- Avg latency ms: `250.0000`
- P95 latency ms: `250.0000`

## Quote And Provider Evidence

- Quote samples: `0`
- Quote OK rate %: `0.0000`
- Healthy DEX count: `0`
- Avg OK quote latency ms: `None`
- Provider count: `5`
- Avg provider score: `99.6000`

## Replay Cost Evidence

- Real replay signals: `2200`
- Max gross edge %: `0.7839`
- Production-buffer trades: `485`
- Production required gross edge %: `0.60`
- Lower-bound cost trades: `2200`
- Lower-bound replay PnL USD: `7812.3634`

## Findings

- `INFO` Production buffer assessment is CONSERVATIVE with MEDIUM paper-cost confidence.

## Notes

- Execution Cost Evidence measures observed paper/replay/quote evidence only.
- It does not change production cost buffers, risk thresholds, or live-trading eligibility.
- Paper slippage plus configured gas is a measured lower bound, not a complete live execution-cost estimate.
