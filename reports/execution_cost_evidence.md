# CryptoAI Execution Cost Evidence

Generated: `2026-06-29T18:18:11Z`

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

- Quote samples: `84`
- Quote OK rate %: `64.2857`
- Healthy DEX count: `2`
- Avg OK quote latency ms: `1321.5926`
- Provider count: `4`
- Avg provider score: `69.5000`

## Replay Cost Evidence

- Real replay signals: `112`
- Max gross edge %: `0.3367`
- Production-buffer trades: `0`
- Production required gross edge %: `0.60`
- Lower-bound cost trades: `96`
- Lower-bound replay PnL USD: `81.6780`

## Findings

- `INFO` Production buffer assessment is CONSERVATIVE with LOW paper-cost confidence.
- `ACTION` Collect more filled paper executions; current slippage sample is 6 and target is 30+.
- `WATCH` Replay has trades under measured lower-bound costs but none under the production buffer; do not lower thresholds until gas, fee, and slippage evidence is stronger.

## Notes

- Execution Cost Evidence measures observed paper/replay/quote evidence only.
- It does not change production cost buffers, risk thresholds, or live-trading eligibility.
- Paper slippage plus configured gas is a measured lower bound, not a complete live execution-cost estimate.
