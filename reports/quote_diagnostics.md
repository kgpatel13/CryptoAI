# CryptoAI Quote Diagnostics

Generated: `2026-06-28T16:33:47Z`

## Summary

- Total quote diagnostics: `4`
- OK: `2`
- Error: `2`
- Invalid: `0`

## Quote Rows

| Chain | DEX | Pair | Status | Price | Amount Out | Latency ms | Error |
|---|---|---|---|---:|---:|---:|---|
| base | Uniswap V2 | WETH/USDC | OK | 1564.819862 | 1564.819862 | 3743.35 |  |
| base | Uniswap V2 | USDC/WETH | OK | 0.000632232965178056877 | 0.632232965178056877 | 3743.35 |  |
| base | Aerodrome | WETH/USDC | ERROR | - | - | 3743.35 | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row. |
| base | Aerodrome | USDC/WETH | ERROR | - | - | 3743.35 | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row. |

## Interpretation

- Quote layer has at least two valid quotes or a recent healthy snapshot.
- Errors are isolated and should not crash the paper pipeline.