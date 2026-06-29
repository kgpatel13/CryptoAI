# CryptoAI Strategy Intelligence

Generated: `2026-06-29T13:35:07Z`

## Summary

- Mode: `paper`
- Strategies: `5`
- Top recommendation: `CONTINUE_RESEARCH`
- Promotion allowed: `False`
- Provider status: `WATCH`
- Experiment: `RESEARCH_ONLY` with `1` fail / `1` warn
- Report audit findings: `0`

## Strategies

| Strategy | Enabled | Score | Recommendation | Filled | Closed | PnL | Win Rate | Blockers |
|---|---:|---:|---|---:|---:|---:|---:|---|
| DEX Arbitrage Strategy | True | 83 | CONTINUE_RESEARCH | 12 | 8 | 2.8220 | 50.0000 | Live trading is disabled; this is advisory paper intelligence only.; Experiment evidence has 1 failing gate(s).; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |
| Momentum Strategy | False | 30 | RESEARCH_DISABLED | 0 | 0 | 0.0000 | None | Live trading is disabled; this is advisory paper intelligence only.; Strategy is disabled in the strategy registry.; Experiment evidence has 1 failing gate(s).; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |
| Mean Reversion Strategy | False | 30 | RESEARCH_DISABLED | 0 | 0 | 0.0000 | None | Live trading is disabled; this is advisory paper intelligence only.; Strategy is disabled in the strategy registry.; Experiment evidence has 1 failing gate(s).; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |
| Breakout Strategy | False | 30 | RESEARCH_DISABLED | 0 | 0 | 0.0000 | None | Live trading is disabled; this is advisory paper intelligence only.; Strategy is disabled in the strategy registry.; Experiment evidence has 1 failing gate(s).; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |
| AI Ranked Strategy | False | 30 | RESEARCH_DISABLED | 0 | 0 | 0.0000 | None | Live trading is disabled; this is advisory paper intelligence only.; Strategy is disabled in the strategy registry.; Experiment evidence has 1 failing gate(s).; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |

## Next Actions

### DEX Arbitrage Strategy
- Improve replay coverage until default replay produces positive production-buffer trades.

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
