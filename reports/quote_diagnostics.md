# CryptoAI Quote Diagnostics

Generated: `2026-06-29T02:28:42Z`

## Summary

- Total quote diagnostics: `4`
- OK: `2`
- Error: `2`
- Invalid: `0`

## Quote Rows

| Chain | DEX | Pair | Status | Price | Amount Out | Latency ms | Error |
|---|---|---|---|---:|---:|---:|---|
| base | Uniswap V2 | WETH/USDC | OK | 1558.809981 | 1558.809981 | 3926.31 |  |
| base | Uniswap V2 | USDC/WETH | OK | 0.000634671980564107288 | 0.634671980564107288 | 3926.31 |  |
| base | Aerodrome | WETH/USDC | ERROR | - | - | 3926.31 | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row. |
| base | Aerodrome | USDC/WETH | ERROR | - | - | 3926.31 | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row. |

## Interpretation

- Quote layer has valid quote rows but fewer than two healthy DEX venues. Real arbitrage needs another venue, but simulated paper validation may still run.
- Errors are isolated and should not crash the paper pipeline.