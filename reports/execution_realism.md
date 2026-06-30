# CryptoAI Execution Realism

Generated: `2026-06-30T19:36:37Z`

## Summary

- Overall status: `NOT_SHADOW_READY`
- Confidence: `NONE`
- Paper capital USD: `$500.0000`
- Requested notional USD: `$5.0000`
- Shadow-ready count: `0`
- Live-ready count: `0`

## Latest Opportunity Stress Check

| Pair | Buy | Sell | Source | Gross % | Reported Net % | Stress Net % | Executable USD | Status | Confidence |
|---|---|---|---|---:|---:|---:|---:|---|---|
| WETH/USDC | Uniswap V2 | Uniswap V3 | BUY | 0.7820 | 0.4820 | -1.1911 | 5.0000 | NOT_EXECUTABLE | MEDIUM |
| USDC/WETH | Uniswap V2 | Uniswap V3 | SKIP | 0.1964 | -0.1036 | -1.5694 | 5.0000 | NOT_EXECUTABLE | MEDIUM |
| WETH/USDC | Uniswap V2 | Uniswap V3 | BUY | 0.7820 | 0.4820 | -1.1911 | 5.0000 | NOT_EXECUTABLE | MEDIUM |
| USDC/WETH | Uniswap V2 | Uniswap V3 | SKIP | 0.1964 | -0.1036 | -1.5694 | 5.0000 | NOT_EXECUTABLE | MEDIUM |

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
