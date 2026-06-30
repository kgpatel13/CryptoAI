# CryptoAI Market Universe Evidence

Generated: `2026-06-30T02:31:59Z`

## Summary

- Primary focus: `base` `WETH/USDC`
- Active focus count: `0`
- Research target count: `1`
- Blocked count: `7`
- Provider status: `OK` with `0` alert(s)

## Settings Evidence

- Production cost buffer %: `0.30`
- Production buffer status: `INSUFFICIENT_EVIDENCE`
- Execution-cost confidence: `INSUFFICIENT`
- Observed cost lower bound %: `None`
- Recommendation: Production cost-buffer has positive-after-cost evidence, but paper BUY threshold evidence is still insufficient.

## Universe Ranking

| Class | Chain | Pair | Score | Quote OK % | Healthy DEXs | Real Signals | Prod Trades | Lower-Bound Trades | Next Action |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| RESEARCH_TARGET | base | WETH/USDC | 80 | 100.0000 | 3 | 3 | 0 | 0 | Add deeper quote/execution evidence before considering paper optimization. |
| BLOCKED_NEEDS_QUOTES | polygon | WETH/USDC | 39 | 0.0000 | 0 | 0 | 0 | 0 | Implement or validate quote providers for polygon WETH/USDC before treating it as tradeable. |
| BLOCKED_NEEDS_QUOTES | ethereum | WETH/USDC | 39 | 0.0000 | 0 | 0 | 0 | 0 | Implement or validate quote providers for ethereum WETH/USDC before treating it as tradeable. |
| BLOCKED_NEEDS_QUOTES | arbitrum | WETH/USDC | 39 | 0.0000 | 0 | 0 | 0 | 0 | Implement or validate quote providers for arbitrum WETH/USDC before treating it as tradeable. |
| BLOCKED_NEEDS_QUOTES | base | CBBTC/USDC | 38 | 0.0000 | 0 | 0 | 0 | 0 | Implement or validate quote providers for base CBBTC/USDC before treating it as tradeable. |
| BLOCKED_NEEDS_QUOTES | polygon | WBTC/USDC | 32 | 0.0000 | 0 | 0 | 0 | 0 | Implement or validate quote providers for polygon WBTC/USDC before treating it as tradeable. |
| BLOCKED_NEEDS_QUOTES | ethereum | WBTC/USDC | 32 | 0.0000 | 0 | 0 | 0 | 0 | Implement or validate quote providers for ethereum WBTC/USDC before treating it as tradeable. |
| BLOCKED_NEEDS_QUOTES | arbitrum | WBTC/USDC | 32 | 0.0000 | 0 | 0 | 0 | 0 | Implement or validate quote providers for arbitrum WBTC/USDC before treating it as tradeable. |

## Findings

- `ACTION` 7 configured pair(s) need quote-provider evidence before expansion.
- `INFO` Production cost-buffer has positive-after-cost evidence, but paper BUY threshold evidence is still insufficient.

## Notes

- Market Universe Evidence ranks research coverage only.
- It does not add live exchange connectivity or change production cost/risk thresholds.
- Base WETH/USDC remains the default focus until other chains have quote-provider evidence.
