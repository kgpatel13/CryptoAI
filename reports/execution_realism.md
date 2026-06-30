# CryptoAI Execution Realism

Generated: `2026-06-30T03:09:35Z`

## Summary

- Overall status: `NOT_SHADOW_READY`
- Confidence: `LOW`
- Paper capital USD: `$1000.0000`
- Requested notional USD: `$1000.0000`
- Shadow-ready count: `0`
- Live-ready count: `0`

## Latest Opportunity Stress Check

| Pair | Buy | Sell | Source | Gross % | Reported Net % | Stress Net % | Executable USD | Status | Confidence |
|---|---|---|---|---:|---:|---:|---:|---|---|
| WETH/USDC | Uniswap V2 | Uniswap V3 | WATCH | 0.5541 | 0.2541 | -0.0614 | 1000.0000 | NEGATIVE_AFTER_STRESS | LOW |
| USDC/WETH | Uniswap V2 | Uniswap V3 | WATCH | 0.4163 | 0.1163 | -0.1030 | 1000.0000 | NEGATIVE_AFTER_STRESS | LOW |

## Findings

| Severity | Message |
|---|---|
| INFO | Latest opportunities are not realistic execution candidates after stress checks. |

## Notes

- Execution Realism is evidence-only and does not change paper BUY thresholds or risk limits.
- Without pool-depth evidence, executable size and price impact remain conservative heuristics.
- Live trading remains disabled; SHADOW_READY means suitable for deeper paper/shadow analysis only.
