# CryptoAI Execution Realism

Generated: `2026-06-30T18:49:08Z`

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
| WETH/USDC | Uniswap V2 | Uniswap V3 | WATCH | 0.3976 | 0.0976 | -0.6625 | 50.0000 | NOT_EXECUTABLE | MEDIUM |
| USDC/WETH | Uniswap V2 | Uniswap V3 | WATCH | 0.5720 | 0.2720 | -0.2856 | 50.0000 | NOT_EXECUTABLE | MEDIUM |

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
