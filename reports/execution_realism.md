# CryptoAI Execution Realism

Generated: `2026-07-01T06:04:33Z`

## Summary

- Overall status: `SHADOW_REVIEW_READY`
- Confidence: `MEDIUM`
- Paper capital USD: `$500.0000`
- Requested notional USD: `$500.0000`
- Shadow-ready count: `2`
- Live-ready count: `0`

## Latest Opportunity Stress Check

| Pair | Buy | Sell | Source | Gross % | Reported Net % | Stress Net % | Executable USD | Status | Confidence |
|---|---|---|---|---:|---:|---:|---:|---|---|
| WETH/USDC | Uniswap V2 | Uniswap V3 | SKIP | 0.3000 | 0.0000 | -0.0779 | 500.0000 | NEGATIVE_AFTER_STRESS | MEDIUM |
| USDC/WETH | Uniswap V2 | Uniswap V3 | BUY | 0.6849 | 0.3849 | 0.3136 | 500.0000 | SHADOW_READY | MEDIUM |
| WETH/USDC | Uniswap V2 | Uniswap V3 | SKIP | 0.3000 | 0.0000 | -0.0779 | 500.0000 | NEGATIVE_AFTER_STRESS | MEDIUM |
| USDC/WETH | Uniswap V2 | Uniswap V3 | BUY | 0.6849 | 0.3849 | 0.3136 | 500.0000 | SHADOW_READY | MEDIUM |

## Findings

| Severity | Message |
|---|---|
| INFO | Pool-depth ladder evidence is available for at least one latest opportunity. |

## Notes

- Execution Realism is evidence-only and does not change paper BUY thresholds or risk limits.
- Without pool-depth evidence, executable size and price impact remain conservative heuristics.
- Live trading remains disabled; SHADOW_READY means suitable for deeper paper/shadow analysis only.
