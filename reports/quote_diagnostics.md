# CryptoAI Quote Diagnostics

Generated: `2026-06-28T17:22:50Z`

## Summary

- Total quote diagnostics: `4`
- OK: `2`
- Error: `2`
- Invalid: `0`

## Quote Rows

| Chain | DEX | Pair | Status | Price | Amount Out | Latency ms | Error |
|---|---|---|---|---:|---:|---:|---|
| base | Uniswap V2 | WETH/USDC | OK | 1561.402082 | 1561.402082 | 1703.70 |  |
| base | Uniswap V2 | USDC/WETH | OK | 0.000633617608836572183 | 0.633617608836572183 | 1703.70 |  |
| base | Aerodrome | WETH/USDC | ERROR | - | - | 1703.70 | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row. |
| base | Aerodrome | USDC/WETH | ERROR | - | - | 1703.70 | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row. |

## Interpretation

- Quote layer has at least two valid quotes or a recent healthy snapshot.
- Errors are isolated and should not crash the paper pipeline.