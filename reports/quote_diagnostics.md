# CryptoAI Quote Diagnostics

Generated: `2026-06-28T18:14:20Z`

## Summary

- Total quote diagnostics: `4`
- OK: `2`
- Error: `2`
- Invalid: `0`

## Quote Rows

| Chain | DEX | Pair | Status | Price | Amount Out | Latency ms | Error |
|---|---|---|---|---:|---:|---:|---|
| base | Uniswap V2 | WETH/USDC | OK | 1559.422345 | 1559.422345 | 2504.54 |  |
| base | Uniswap V2 | USDC/WETH | OK | 0.000634422435562608473 | 0.634422435562608473 | 2504.54 |  |
| base | Aerodrome | WETH/USDC | ERROR | - | - | 2504.54 | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row. |
| base | Aerodrome | USDC/WETH | ERROR | - | - | 2504.54 | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row. |

## Interpretation

- Quote layer has at least two valid quotes or a recent healthy snapshot.
- Errors are isolated and should not crash the paper pipeline.