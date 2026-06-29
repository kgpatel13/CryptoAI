# CryptoAI Strategy Intelligence

Generated: `2026-06-29T23:31:37Z`

## Summary

- Mode: `paper`
- Strategies: `5`
- Top recommendation: `WATCHLIST`
- Promotion allowed: `False`
- Provider status: `WATCH`
- Experiment: `WATCHLIST` with `0` fail / `1` warn
- Report audit findings: `0`
- Replay production trades: `5` at `0.30` cost buffer
- Replay best profitable buffer: `0.20` with `99` trade(s)
- Execution cost status: `CONSERVATIVE` with `LOW` confidence
- Observed cost lower bound %: `0.1300`
- Market primary focus: `base WETH/USDC`
- Market universe: `1` active / `0` research / `7` blocked
- Quote coverage: `1` active / `1` quote-test gaps / `6` provider gaps
- Next quote target: `base CBBTC/USDC`
- ETH route decision: `KEEP_0_30_PRODUCTION_RESEARCH_0_20`
- ETH route buffers: production `0.30` / candidate `0.20`
- ETH route promotion gates: `4/8`
- ETH market coverage: `52` / `ETH_COVERAGE_EARLY`
- ETH configured chains: `4/5` with `2` quote-ready route(s)

## Strategies

| Strategy | Enabled | Score | Recommendation | Filled | Closed | PnL | Win Rate | Blockers |
|---|---:|---:|---|---:|---:|---:|---:|---|
| DEX Arbitrage Strategy | True | 100 | WATCHLIST | 12 | 8 | 2.8220 | 50.0000 | Live trading is disabled; this is advisory paper intelligence only.; ETH route evidence keeps 0.20% buffer research-only; production buffer remains 0.30%.; ETH Golden Path market coverage is still below developing maturity.; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |
| Momentum Strategy | False | 51 | RESEARCH_DISABLED | 0 | 0 | 0.0000 | None | Live trading is disabled; this is advisory paper intelligence only.; Strategy is disabled in the strategy registry.; ETH route evidence keeps 0.20% buffer research-only; production buffer remains 0.30%.; ETH Golden Path market coverage is still below developing maturity.; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |
| Mean Reversion Strategy | False | 51 | RESEARCH_DISABLED | 0 | 0 | 0.0000 | None | Live trading is disabled; this is advisory paper intelligence only.; Strategy is disabled in the strategy registry.; ETH route evidence keeps 0.20% buffer research-only; production buffer remains 0.30%.; ETH Golden Path market coverage is still below developing maturity.; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |
| Breakout Strategy | False | 51 | RESEARCH_DISABLED | 0 | 0 | 0.0000 | None | Live trading is disabled; this is advisory paper intelligence only.; Strategy is disabled in the strategy registry.; ETH route evidence keeps 0.20% buffer research-only; production buffer remains 0.30%.; ETH Golden Path market coverage is still below developing maturity.; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |
| AI Ranked Strategy | False | 51 | RESEARCH_DISABLED | 0 | 0 | 0.0000 | None | Live trading is disabled; this is advisory paper intelligence only.; Strategy is disabled in the strategy registry.; ETH route evidence keeps 0.20% buffer research-only; production buffer remains 0.30%.; ETH Golden Path market coverage is still below developing maturity.; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |

## Next Actions

### DEX Arbitrage Strategy
- Continue paper cycles and collect more closed-trade evidence before tuning risk upward.

### Momentum Strategy
- Keep disabled until its feature pipeline and validation tests are implemented.

### Mean Reversion Strategy
- Keep disabled until its feature pipeline and validation tests are implemented.

### Breakout Strategy
- Keep disabled until its feature pipeline and validation tests are implemented.

### AI Ranked Strategy
- Keep disabled until its feature pipeline and validation tests are implemented.

## Notes

- Strategy Intelligence is advisory and paper-only.
- Risk engine remains the final authority before paper execution.
- promotion_allowed is always false until dedicated live-readiness gates are implemented and approved.
