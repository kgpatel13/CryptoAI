# CryptoAI Execution Cost Evidence

Generated: `2026-06-30T07:46:44Z`

## Summary

- Production cost buffer %: `0.30`
- Paper BUY threshold %: `0.30`
- Buffer status: `INSUFFICIENT_EVIDENCE`
- Confidence: `INSUFFICIENT`
- Observed total cost lower bound %: `None`
- Buffer surplus vs lower bound %: `None`

## Configured Cost Model

- Gas buffer %: `0.08`
- Fee/slippage buffer %: `0.22`
- Total cost buffer %: `0.30`
- Source: `latest_opportunity_decision`

## Paper Execution Evidence

- Filled execution samples: `0`
- Avg slippage bps: `0.0000`
- P95 slippage bps: `0.0000`
- Max slippage bps: `0.0000`
- Avg latency ms: `None`
- P95 latency ms: `None`

## Quote And Provider Evidence

- Quote samples: `6`
- Quote OK rate %: `100.0000`
- Healthy DEX count: `3`
- Avg OK quote latency ms: `0.0700`
- Provider count: `4`
- Avg provider score: `100.0000`

## Replay Cost Evidence

- Real replay signals: `932`
- Max gross edge %: `0.6643`
- Production-buffer trades: `410`
- Production required gross edge %: `0.60`
- Lower-bound cost trades: `0`
- Lower-bound replay PnL USD: `0.0000`

## Findings

- `WATCH` Production buffer assessment is INSUFFICIENT_EVIDENCE with INSUFFICIENT paper-cost confidence.
- `ACTION` Collect more filled paper executions; current slippage sample is 0 and target is 30+.

## Notes

- Execution Cost Evidence measures observed paper/replay/quote evidence only.
- It does not change production cost buffers, risk thresholds, or live-trading eligibility.
- Paper slippage plus configured gas is a measured lower bound, not a complete live execution-cost estimate.
