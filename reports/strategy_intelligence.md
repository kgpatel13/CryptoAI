# CryptoAI Strategy Intelligence

Generated: `2026-06-29T14:15:05Z`

## Summary

- Mode: `paper`
- Strategies: `5`
- Top recommendation: `CONTINUE_RESEARCH`
- Promotion allowed: `False`
- Provider status: `WATCH`
- Experiment: `RESEARCH_ONLY` with `1` fail / `1` warn
- Report audit findings: `0`
- Replay production trades: `0` at `0.30` cost buffer
- Replay best profitable buffer: `0.20` with `36` trade(s)

## Strategies

| Strategy | Enabled | Score | Recommendation | Filled | Closed | PnL | Win Rate | Blockers |
|---|---:|---:|---|---:|---:|---:|---:|---|
| DEX Arbitrage Strategy | True | 84 | CONTINUE_RESEARCH | 12 | 8 | 2.8220 | 50.0000 | Live trading is disabled; this is advisory paper intelligence only.; Experiment evidence has 1 failing gate(s).; Production replay has 0 trades while lower cost-buffer diagnostics are profitable.; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |
| Momentum Strategy | False | 31 | RESEARCH_DISABLED | 0 | 0 | 0.0000 | None | Live trading is disabled; this is advisory paper intelligence only.; Strategy is disabled in the strategy registry.; Experiment evidence has 1 failing gate(s).; Production replay has 0 trades while lower cost-buffer diagnostics are profitable.; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |
| Mean Reversion Strategy | False | 31 | RESEARCH_DISABLED | 0 | 0 | 0.0000 | None | Live trading is disabled; this is advisory paper intelligence only.; Strategy is disabled in the strategy registry.; Experiment evidence has 1 failing gate(s).; Production replay has 0 trades while lower cost-buffer diagnostics are profitable.; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |
| Breakout Strategy | False | 31 | RESEARCH_DISABLED | 0 | 0 | 0.0000 | None | Live trading is disabled; this is advisory paper intelligence only.; Strategy is disabled in the strategy registry.; Experiment evidence has 1 failing gate(s).; Production replay has 0 trades while lower cost-buffer diagnostics are profitable.; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |
| AI Ranked Strategy | False | 31 | RESEARCH_DISABLED | 0 | 0 | 0.0000 | None | Live trading is disabled; this is advisory paper intelligence only.; Strategy is disabled in the strategy registry.; Experiment evidence has 1 failing gate(s).; Production replay has 0 trades while lower cost-buffer diagnostics are profitable.; Closed paper-trade sample is below the 10-trade minimum for strategy confidence. |

## Next Actions

### DEX Arbitrage Strategy
- Keep production buffer unchanged; collect execution-cost evidence to prove whether 0.20% is realistic.

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
