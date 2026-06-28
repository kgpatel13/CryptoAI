# CryptoAI Quote Diagnostics

Generated: `2026-06-28T16:59:30Z`

## Summary

- Total quote diagnostics: `4`
- OK: `2`
- Error: `2`
- Invalid: `0`

## Quote Rows

| Chain | DEX | Pair | Status | Price | Amount Out | Latency ms | Error |
|---|---|---|---|---:|---:|---:|---|
| base | Uniswap V2 | WETH/USDC | OK | 1560.4464 | 1560.4464 | 0.13 |  |
| base | Uniswap V2 | USDC/WETH | OK | 0.000634005859521992706 | 0.634005859521992706 | 0.13 |  |
| base | Aerodrome | WETH/USDC | ERROR | - | - | 0.13 | ConnectionError: HTTPSConnectionPool(host='your-private-base-rpc', port=443): Max retries exceeded with url: / (Caused by NameResolutionError("HTTPSConnection(host='your-private-base-rpc', port=443): Failed to resolve 'your-private-base-rpc' ([Errno 11001] getaddrinfo failed)")) |
| base | Aerodrome | USDC/WETH | ERROR | - | - | 0.13 | ConnectionError: HTTPSConnectionPool(host='your-private-base-rpc', port=443): Max retries exceeded with url: / (Caused by NameResolutionError("HTTPSConnection(host='your-private-base-rpc', port=443): Failed to resolve 'your-private-base-rpc' ([Errno 11001] getaddrinfo failed)")) |

## Interpretation

- Quote layer has at least two valid quotes or a recent healthy snapshot.
- Errors are isolated and should not crash the paper pipeline.