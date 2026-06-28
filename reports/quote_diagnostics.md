# CryptoAI Quote Diagnostics

Generated: `2026-06-28T18:36:54Z`

## Summary

- Total quote diagnostics: `4`
- OK: `2`
- Error: `2`
- Invalid: `0`

## Quote Rows

| Chain | DEX | Pair | Status | Price | Amount Out | Latency ms | Error |
|---|---|---|---|---:|---:|---:|---|
| base | Uniswap V2 | WETH/USDC | OK | 1559.431749 | 1559.431749 | 0.14 |  |
| base | Uniswap V2 | USDC/WETH | OK | 0.000634418607815447198 | 0.634418607815447198 | 0.14 |  |
| base | Aerodrome | WETH/USDC | ERROR | - | - | 0.14 | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row. |
| base | Aerodrome | USDC/WETH | ERROR | - | - | 0.14 | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row. |

## Interpretation

- Quote layer has at least two valid quotes or a recent healthy snapshot.
- Errors are isolated and should not crash the paper pipeline.