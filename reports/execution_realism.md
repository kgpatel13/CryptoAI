# CryptoAI Execution Realism

Generated: `2026-06-30T02:54:57Z`

## Summary

- Overall status: `PAPER_ONLY_NEEDS_DEPTH`
- Confidence: `LOW`
- Paper capital USD: `$1000.0000`
- Requested notional USD: `$1000.0000`
- Shadow-ready count: `0`
- Live-ready count: `0`

## Latest Opportunity Stress Check

| Pair | Buy | Sell | Source | Gross % | Reported Net % | Stress Net % | Executable USD | Status | Confidence |
|---|---|---|---|---:|---:|---:|---:|---|---|
| WETH/USDC | Uniswap V2 | Uniswap V3 | BUY | 0.6319 | 0.3319 | 0.2569 | 1000.0000 | SHADOW_ONLY | LOW |
| USDC/WETH | Uniswap V2 | Uniswap V3 | SKIP | 0.3387 | 0.0387 | -0.0363 | 1000.0000 | NEGATIVE_AFTER_STRESS | LOW |

## Findings

| Severity | Message |
|---|---|
| ACTION | Add pool-depth evidence to replace quote-probe executable-size heuristics. |

## Notes

- Execution Realism is evidence-only and does not change paper BUY thresholds or risk limits.
- Without pool-depth evidence, executable size and price impact remain conservative heuristics.
- Live trading remains disabled; SHADOW_READY means suitable for deeper paper/shadow analysis only.
