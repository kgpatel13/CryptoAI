# CryptoAI Quote Diagnostics

Generated: `2026-06-28T15:59:57Z`

## Summary

- Total quote diagnostics: `4`
- OK: `0`
- Error: `4`
- Invalid: `0`

## Quote Rows

| Chain | DEX | Pair | Status | Price | Amount Out | Latency ms | Error |
|---|---|---|---|---:|---:|---:|---|
| base | UniswapV2 | WETH/USDC | ERROR | - | - | 0.65 | UniswapV2QuoteProvider.get_quote() missing 1 required positional argument: 'request' |
| base | Aerodrome | WETH/USDC | ERROR | - | - | 0.65 | AerodromeQuoteProvider.get_quote() missing 1 required positional argument: 'request' |
| base | Aerodrome | USDC/WETH | ERROR | - | - | 0.65 | AerodromeQuoteProvider.get_quote() missing 1 required positional argument: 'request' |
| base | UniswapV2 | USDC/WETH | ERROR | - | - | 0.65 | UniswapV2QuoteProvider.get_quote() missing 1 required positional argument: 'request' |

## Interpretation

- Not enough valid comparable quotes. Opportunity engine cannot create real arbitrage candidates.
- Inspect the `Error` column first. Fix quote collection before tuning strategy thresholds.