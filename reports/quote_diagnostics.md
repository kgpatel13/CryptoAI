# CryptoAI Quote Diagnostics

Generated: `2026-06-28T17:36:38Z`

## Summary

- Total quote diagnostics: `4`
- OK: `2`
- Error: `2`
- Invalid: `0`

## Quote Rows

| Chain | DEX | Pair | Status | Price | Amount Out | Latency ms | Error |
|---|---|---|---|---:|---:|---:|---|
| base | Uniswap V2 | WETH/USDC | OK | 1558.629811 | 1558.629811 | 3044.47 |  |
| base | Uniswap V2 | USDC/WETH | OK | 0.000634745190804857799 | 0.634745190804857799 | 3044.47 |  |
| base | Aerodrome | WETH/USDC | ERROR | - | - | 3044.47 | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row. |
| base | Aerodrome | USDC/WETH | ERROR | - | - | 3044.47 | RPC rate limit while reading Aerodrome quote. Configure BASE_RPC with a private RPC or wait for cache fallback. |

## Interpretation

- Quote layer has at least two valid quotes or a recent healthy snapshot.
- Errors are isolated and should not crash the paper pipeline.