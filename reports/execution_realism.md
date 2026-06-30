# CryptoAI Execution Realism

Generated: `2026-06-30T17:53:08Z`

## Summary

- Overall status: `NOT_SHADOW_READY`
- Confidence: `NONE`
- Paper capital USD: `$500.0000`
- Requested notional USD: `$50.0000`
- Shadow-ready count: `0`
- Live-ready count: `0`

## Latest Opportunity Stress Check

| Pair | Buy | Sell | Source | Gross % | Reported Net % | Stress Net % | Executable USD | Status | Confidence |
|---|---|---|---|---:|---:|---:|---:|---|---|
| WETH/USDC | Uniswap V2 | Uniswap V3 | WATCH | 0.4228 | 0.1228 | -0.6365 | 50.0000 | NOT_EXECUTABLE | MEDIUM |
| USDC/WETH | Uniswap V2 | Uniswap V3 | WATCH | 0.5467 | 0.2467 | -0.3114 | 50.0000 | NOT_EXECUTABLE | MEDIUM |

## Findings

| Severity | Message |
|---|---|
| ACTION | Need at least two healthy DEX quote venues for real arbitrage realism. |
| INFO | Latest opportunities are not realistic execution candidates after stress checks. |
| INFO | Pool-depth ladder evidence is available for at least one latest opportunity. |

## Notes

- Execution Realism is evidence-only and does not change paper BUY thresholds or risk limits.
- Without pool-depth evidence, executable size and price impact remain conservative heuristics.
- Live trading remains disabled; SHADOW_READY means suitable for deeper paper/shadow analysis only.
