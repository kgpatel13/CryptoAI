# CryptoAI v5.13 - Pool Depth and Quote-Size Ladder Evidence

## Summary

v5.13 adds route-depth evidence so paper profits can be reviewed against executable size, not just top-of-book quotes.

This release does not change live trading, paper BUY thresholds, production cost buffers, or risk limits.

## Added

- `PoolDepthLadderService` for probing Base ETH routes at increasing quote sizes.
- `data/quote_size_ladder.jsonl` for raw ladder observations.
- `reports/pool_depth_ladder.json` and `reports/pool_depth_ladder.md`.
- Mission Control depth metrics:
  - depth status,
  - confidence,
  - depth-ready routes,
  - requested paper size.
- Dashboard action to run Pool Depth Ladder from Replay / Backtesting.
- Report Audit coverage for pool-depth ladder outputs.
- Strategy Intelligence context for pool-depth status and ready-route count.
- Execution Realism integration so realism can use `POOL_DEPTH_LADDER` instead of only `QUOTE_PROBE_HEURISTIC`.

## Current Evidence

The current Base ETH ladder is available but still watchlist:

- Pool-depth status: `DEPTH_EVIDENCE_WATCH`
- Confidence: `LOW`
- Depth-ready routes: `0`
- Watch routes: `2`
- Requested paper size: `$1000`

Execution Realism now marks the latest opportunities as `NOT_SHADOW_READY` because stress net edge is negative after depth-aware price impact, gas, MEV, and the unchanged `0.30%` buffer.

## Still Locked

- Live trading remains disabled.
- Paper BUY threshold remains `0.30%`.
- Production cost buffer remains at least `0.30%`.
- `DEPTH_WATCH` is not a live-trading approval.

## Next

Use the ladder evidence to tune research, not production:

- collect more ladder samples over different market conditions,
- compare requested size versus low-impact usable size,
- identify which DEX contributes most route impact,
- add route-specific sizing recommendations,
- keep real-money trading blocked until depth evidence reaches stable `DEPTH_READY`.

