# CryptoAI Execution Cost Evidence

Generated: `2026-06-29T23:31:26Z`

## Summary

- Production cost buffer %: `0.30`
- Paper BUY threshold %: `0.30`
- Buffer status: `CONSERVATIVE`
- Confidence: `LOW`
- Observed total cost lower bound %: `0.1300`
- Buffer surplus vs lower bound %: `0.1700`

## Configured Cost Model

- Gas buffer %: `0.08`
- Fee/slippage buffer %: `0.22`
- Total cost buffer %: `0.30`
- Source: `latest_opportunity_decision`

## Paper Execution Evidence

- Filled execution samples: `6`
- Avg slippage bps: `5.0000`
- P95 slippage bps: `5.0000`
- Max slippage bps: `5.0000`
- Avg latency ms: `250.0000`
- P95 latency ms: `250.0000`

## Quote And Provider Evidence

- Quote samples: `94`
- Quote OK rate %: `68.0851`
- Healthy DEX count: `3`
- Avg OK quote latency ms: `1145.9578`
- Provider count: `5`
- Avg provider score: `76.6000`

## Replay Cost Evidence

- Real replay signals: `188`
- Max gross edge %: `0.6830`
- Production-buffer trades: `5`
- Production required gross edge %: `0.60`
- Lower-bound cost trades: `171`
- Lower-bound replay PnL USD: `164.1083`

## Findings

- `INFO` Production buffer assessment is CONSERVATIVE with LOW paper-cost confidence.
- `ACTION` Collect more filled paper executions; current slippage sample is 6 and target is 30+.

## Notes

- Execution Cost Evidence measures observed paper/replay/quote evidence only.
- It does not change production cost buffers, risk thresholds, or live-trading eligibility.
- Paper slippage plus configured gas is a measured lower bound, not a complete live execution-cost estimate.
