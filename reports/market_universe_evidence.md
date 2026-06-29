# CryptoAI Market Universe Evidence

Generated: `2026-06-29T18:18:11Z`

## Summary

- Primary focus: `base` `WETH/USDC`
- Active focus count: `1`
- Research target count: `0`
- Blocked count: `7`
- Provider status: `WATCH` with `2` alert(s)

## Settings Evidence

- Production cost buffer %: `0.30`
- Production buffer status: `CONSERVATIVE`
- Execution-cost confidence: `LOW`
- Observed cost lower bound %: `0.1300`
- Recommendation: Production cost-buffer has positive-after-cost evidence, but paper BUY threshold evidence is still insufficient.

## Universe Ranking

| Class | Chain | Pair | Score | Quote OK % | Healthy DEXs | Real Signals | Prod Trades | Lower-Bound Trades | Next Action |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| ACTIVE_FOCUS | base | WETH/USDC | 83 | 64.2857 | 2 | 56 | 0 | 56 | Continue paper monitoring and collect execution-cost samples at unchanged production thresholds. |
| BLOCKED_NEEDS_QUOTES | polygon | WETH/USDC | 39 | 0.0000 | 0 | 0 | 0 | 0 | Implement or validate quote providers for polygon WETH/USDC before treating it as tradeable. |
| BLOCKED_NEEDS_QUOTES | ethereum | WETH/USDC | 39 | 0.0000 | 0 | 0 | 0 | 0 | Implement or validate quote providers for ethereum WETH/USDC before treating it as tradeable. |
| BLOCKED_NEEDS_QUOTES | arbitrum | WETH/USDC | 39 | 0.0000 | 0 | 0 | 0 | 0 | Implement or validate quote providers for arbitrum WETH/USDC before treating it as tradeable. |
| BLOCKED_NEEDS_QUOTES | base | CBBTC/USDC | 36 | 0.0000 | 0 | 0 | 0 | 0 | Implement or validate quote providers for base CBBTC/USDC before treating it as tradeable. |
| BLOCKED_NEEDS_QUOTES | polygon | WBTC/USDC | 32 | 0.0000 | 0 | 0 | 0 | 0 | Implement or validate quote providers for polygon WBTC/USDC before treating it as tradeable. |
| BLOCKED_NEEDS_QUOTES | ethereum | WBTC/USDC | 32 | 0.0000 | 0 | 0 | 0 | 0 | Implement or validate quote providers for ethereum WBTC/USDC before treating it as tradeable. |
| BLOCKED_NEEDS_QUOTES | arbitrum | WBTC/USDC | 32 | 0.0000 | 0 | 0 | 0 | 0 | Implement or validate quote providers for arbitrum WBTC/USDC before treating it as tradeable. |

## Findings

- `INFO` Primary research focus is base WETH/USDC.
- `ACTION` 7 configured pair(s) need quote-provider evidence before expansion.
- `WATCH` Provider monitor remains WATCH with 2 alert(s).
- `INFO` Production cost-buffer has positive-after-cost evidence, but paper BUY threshold evidence is still insufficient.

## Notes

- Market Universe Evidence ranks research coverage only.
- It does not add live exchange connectivity or change production cost/risk thresholds.
- Base WETH/USDC remains the default focus until other chains have quote-provider evidence.
