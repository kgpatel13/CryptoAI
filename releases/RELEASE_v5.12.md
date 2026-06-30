# CryptoAI v5.12 - Execution Realism Evidence Engine

## Summary

v5.12 adds an evidence-only realism layer between paper profits and any future live-trading decision.

Paper arbitrage can now show impressive results, but this release deliberately asks a harder question:

`Could this paper opportunity realistically be executed at the requested size?`

The answer is reported separately from the existing paper execution engine. It does not change production thresholds, paper BUY thresholds, sizing, or risk gates.

## Added

- `ExecutionRealismService` for stress-checking the latest opportunity decisions against route quote coverage, requested notional, gas, price-impact heuristics, and MEV risk buffers.
- `reports/execution_realism.json` and `reports/execution_realism.md`.
- Mission Control dashboard metrics for realism status, confidence, shadow-ready count, live-ready count, stress net edge, and executable size.
- Report Audit coverage for the new realism reports.
- Paper autopilot integration so realism evidence refreshes after each paper cycle.
- Regression tests for:
  - BUY opportunities remaining `SHADOW_ONLY` when pool-depth evidence is missing.
  - Single-route opportunities being marked `NOT_EXECUTABLE`.
  - Paper autopilot generating realism evidence before report audit.

## Current Interpretation

- `PAPER_ONLY_NEEDS_DEPTH` means paper trading may continue, but the opportunity is not live-ready.
- `SHADOW_ONLY` means the paper BUY candidate needs pool-depth/private-routing evidence before deeper shadow/live review.
- `live_ready_count` remains `0` by design.

## Still Locked

- Live trading remains disabled.
- Paper BUY threshold remains `0.30%`.
- Production cost buffer remains at least `0.30%`.
- This release does not approve real-money trading.

## Next Evidence Gap

The next milestone should replace quote-probe heuristics with real pool-depth evidence:

- pool liquidity/reserve snapshots,
- quote-size ladder tests,
- route-specific slippage curves,
- stale quote detection at execution time,
- replay comparison between quoted edge and realistic executable edge.

