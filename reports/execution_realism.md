# CryptoAI Execution Realism

Generated: `2026-06-30T07:52:22Z`

## Summary

- Overall status: `SHADOW_REVIEW_READY`
- Confidence: `MEDIUM`
- Paper capital USD: `$1000.0000`
- Requested notional USD: `$1000.0000`
- Shadow-ready count: `2`
- Live-ready count: `0`

## Latest Opportunity Stress Check

| Pair | Buy | Sell | Source | Gross % | Reported Net % | Stress Net % | Executable USD | Status | Confidence |
|---|---|---|---|---:|---:|---:|---:|---|---|
| WETH/USDC | Uniswap V2 | Uniswap V3 | BUY | 0.6090 | 0.3090 | 0.2137 | 1000.0000 | SHADOW_READY | MEDIUM |
| USDC/WETH | Uniswap V2 | Uniswap V3 | WATCH | 0.3616 | 0.0616 | -0.0188 | 1000.0000 | NEGATIVE_AFTER_STRESS | MEDIUM |
| WETH/USDC | Uniswap V2 | Uniswap V3 | BUY | 0.6090 | 0.3090 | 0.2137 | 1000.0000 | SHADOW_READY | MEDIUM |
| USDC/WETH | Uniswap V2 | Uniswap V3 | WATCH | 0.3616 | 0.0616 | -0.0188 | 1000.0000 | NEGATIVE_AFTER_STRESS | MEDIUM |

## Findings

| Severity | Message |
|---|---|
| INFO | Pool-depth ladder evidence is available for at least one latest opportunity. |

## Notes

- Execution Realism is evidence-only and does not change paper BUY thresholds or risk limits.
- Without pool-depth evidence, executable size and price impact remain conservative heuristics.
- Live trading remains disabled; SHADOW_READY means suitable for deeper paper/shadow analysis only.
