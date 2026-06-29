# CryptoAI Execution Cost Evidence

Generated: `2026-06-29T17:48:56Z`

## Summary

- Production cost buffer %: `0.30`
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

- Quote samples: `80`
- Quote OK rate %: `62.5000`
- Healthy DEX count: `2`
- Avg OK quote latency ms: `1390.7432`
- Provider count: `4`
- Avg provider score: `68.7500`

## Replay Cost Evidence

- Real replay signals: `96`
- Max gross edge %: `0.2760`
- Production-buffer trades: `0`
- Lower-bound cost trades: `88`
- Lower-bound replay PnL USD: `67.0093`

## Findings

- `INFO` Production buffer assessment is CONSERVATIVE with LOW paper-cost confidence.
- `ACTION` Collect more filled paper executions; current slippage sample is 6 and target is 30+.
- `WATCH` Replay has trades under measured lower-bound costs but none under the production buffer; do not lower thresholds until gas, fee, and slippage evidence is stronger.

## Notes

- Execution Cost Evidence measures observed paper/replay/quote evidence only.
- It does not change production cost buffers, risk thresholds, or live-trading eligibility.
- Paper slippage plus configured gas is a measured lower bound, not a complete live execution-cost estimate.
