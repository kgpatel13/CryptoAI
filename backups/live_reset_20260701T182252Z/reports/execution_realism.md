# CryptoAI Execution Realism

Generated: `2026-07-01T18:22:35Z`

## Summary

- Overall status: `NOT_SHADOW_READY`
- Confidence: `LOW`
- Paper capital USD: `$500.0000`
- Requested notional USD: `$500.0000`
- Shadow-ready count: `0`
- Live-ready count: `0`

## Latest Opportunity Stress Check

| Pair | Buy | Sell | Source | Gross % | Reported Net % | Stress Net % | Executable USD | Status | Confidence |
|---|---|---|---|---:|---:|---:|---:|---|---|
| WETH/USDC | Uniswap V2 | Uniswap V3 | WATCH | 0.5551 | 0.2551 | 0.1770 | 500.0000 | WATCH_ONLY | MEDIUM |
| USDC/WETH | Uniswap V2 | Uniswap V3 | WATCH | 0.4150 | 0.1150 | 0.0438 | 500.0000 | WATCH_ONLY | MEDIUM |

## Findings

| Severity | Message |
|---|---|
| INFO | Latest opportunities are not realistic execution candidates after stress checks. |
| INFO | Pool-depth ladder evidence is available for at least one latest opportunity. |

## Notes

- Execution Realism is evidence-only and does not change paper BUY thresholds or risk limits.
- Without pool-depth evidence, executable size and price impact remain conservative heuristics.
- Live trading remains disabled; SHADOW_READY means suitable for deeper paper/shadow analysis only.
