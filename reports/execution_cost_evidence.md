# CryptoAI Execution Cost Evidence

Generated: `2026-06-30T15:30:53Z`

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
- Source: `fallback_defaults`

## Paper Execution Evidence

- Filled execution samples: `0`
- Avg slippage bps: `0.0000`
- P95 slippage bps: `0.0000`
- Max slippage bps: `0.0000`
- Avg latency ms: `None`
- P95 latency ms: `None`

## Quote And Provider Evidence

- Quote samples: `0`
- Quote OK rate %: `0.0000`
- Healthy DEX count: `0`
- Avg OK quote latency ms: `None`
- Provider count: `0`
- Avg provider score: `None`

## Replay Cost Evidence

- Real replay signals: `0`
- Max gross edge %: `0.0000`
- Production-buffer trades: `0`
- Production required gross edge %: `0.60`
- Lower-bound cost trades: `0`
- Lower-bound replay PnL USD: `0.0000`

## Findings

- `WATCH` Production buffer assessment is INSUFFICIENT_EVIDENCE with INSUFFICIENT paper-cost confidence.
- `ACTION` Collect more filled paper executions; current slippage sample is 0 and target is 30+.
- `WATCH` Provider cost context is incomplete because provider health evidence is missing.

## Notes

- Execution Cost Evidence measures observed paper/replay/quote evidence only.
- It does not change production cost buffers, risk thresholds, or live-trading eligibility.
- Paper slippage plus configured gas is a measured lower bound, not a complete live execution-cost estimate.
