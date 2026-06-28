# CryptoAI Strategy Center

Generated: `2026-06-28T18:36:53Z`

## Summary

- Mode: `paper`
- Strategy count: `5`
- Active strategies: `1`
- Disabled strategies: `4`

## Strategy Registry & Performance

| Strategy | Enabled | Health | Weight | Orders | Filled | Risk Rejected | Open | Closed | Realized PnL | Win Rate | Avg Slip bps | Avg Latency ms |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DEX Arbitrage Strategy | True | ACTIVE | 1.00 | 43 | 14 | 4 | 2 | 2 | 1.0018 | 100.0000 | 5.0000 | 250.0000 |
| Momentum Strategy | False | DISABLED | 0.70 | 0 | 0 | 0 | 0 | 0 | 0.0000 | None | None | None |
| Mean Reversion Strategy | False | DISABLED | 0.70 | 0 | 0 | 0 | 0 | 0 | 0.0000 | None | None | None |
| Breakout Strategy | False | DISABLED | 0.70 | 0 | 0 | 0 | 0 | 0 | 0.0000 | None | None | None |
| AI Ranked Strategy | False | DISABLED | 0.80 | 0 | 0 | 0 | 0 | 0 | 0.0000 | None | None | None |

## Ranked Signals

| Time | Rank | Strategy | Pair | Action | Confidence | Edge % | Rank Score | Reason |
|---|---:|---|---|---|---:|---:|---:|---|
| 2026-06-28T18:22:32Z | 1 | DEX Arbitrage Strategy | - | WATCH | 0 | None | 10 | Opportunity Explorer: REAL: No healthy quotes available. Fix quote providers/RPC before strategy tuning. |
| 2026-06-28T18:23:10Z | 1 | DEX Arbitrage Strategy | - | WATCH | 0 | None | 10 | Opportunity Explorer: REAL: No healthy quotes available. Fix quote providers/RPC before strategy tuning. |
| 2026-06-28T18:36:53Z | 1 | DEX Arbitrage Strategy | WETH/USDC | READY_FOR_PAPER | 70 | 0.3500 | 90 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |
| 2026-06-28T18:36:53Z | 2 | DEX Arbitrage Strategy | USDC/WETH | READY_FOR_PAPER | 70 | 0.3500 | 90 | Opportunity Explorer BUY: net edge 0.3500% >= threshold 0.30%. |

## Notes

- Strategies produce advisory signals only.
- Risk engine remains final authority before paper or live execution.
- Disabled research strategies are intentionally visible but non-tradeable.