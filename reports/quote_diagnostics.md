# CryptoAI Quote Diagnostics

Generated: `2026-06-28T16:09:38Z`

## Summary

- Total quote diagnostics: `4`
- OK: `2`
- Error: `2`
- Invalid: `0`

## Quote Rows

| Chain | DEX | Pair | Status | Price | Amount Out | Latency ms | Error |
|---|---|---|---|---:|---:|---:|---|
| base | Uniswap V2 | USDC/WETH | OK | 0.000629644594857841211 | 0.629644594857841211 | 642.25 |  |
| base | Uniswap V2 | WETH/USDC | OK | 1571.249171 | 1571.249171 | 642.25 |  |
| base | Aerodrome | USDC/WETH | ERROR | - | - | 642.25 | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row. |
| base | Aerodrome | WETH/USDC | ERROR | - | - | 642.25 | RPC rate limit while reading Aerodrome quote. Add a private Base RPC or wait for cache refresh. |

## Interpretation

- Quote layer has at least two valid quotes. Opportunity Explorer should be able to compare prices.