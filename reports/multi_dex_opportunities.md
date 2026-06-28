# CryptoAI Multi-DEX Opportunity Report

Generated: `2026-06-28T16:59:35Z`

## Quote Health

- Total quotes: `4`
- Healthy quotes: `2`
- Failed/invalid quotes: `2`

## Opportunities

| Mode | Pair | Buy DEX | Sell DEX | Buy Price | Sell Price | Gross % | Cost % | Net % | Decision | Reason |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|
| PAPER_SIMULATED | WETH/USDC | Uniswap V2 | SyntheticPaperVenue | 1560.44640000 | 1570.58930160 | 0.65000000 | 0.30000000 | 0.35000000 | BUY | Paper-simulated opportunity because only one healthy DEX quote exists. Use this only to validate strategy/risk/paper-execution pipeline: net edge 0.3500% is above BUY threshold 0.30%. Not live-tradeable. |
| PAPER_SIMULATED | USDC/WETH | Uniswap V2 | SyntheticPaperVenue | 0.00063401 | 0.00063813 | 0.65000000 | 0.30000000 | 0.35000000 | BUY | Paper-simulated opportunity because only one healthy DEX quote exists. Use this only to validate strategy/risk/paper-execution pipeline: net edge 0.3500% is above BUY threshold 0.30%. Not live-tradeable. |

## Failed / Invalid Quotes

| DEX | Pair | Error |
|---|---|---|
| Aerodrome | WETH/USDC | ConnectionError: HTTPSConnectionPool(host='your-private-base-rpc', port=443): Max retries exceeded with url: / (Caused by NameResolutionError("HTTPSConnection(host='your-private-base-rpc', port=443): Failed to resolve 'your-private-base-rpc' ([Errno 11001] getaddrinfo failed)")) |
| Aerodrome | USDC/WETH | ConnectionError: HTTPSConnectionPool(host='your-private-base-rpc', port=443): Max retries exceeded with url: / (Caused by NameResolutionError("HTTPSConnection(host='your-private-base-rpc', port=443): Failed to resolve 'your-private-base-rpc' ([Errno 11001] getaddrinfo failed)")) |

## Interpretation

- Only one DEX is healthy. Real arbitrage is not possible yet; simulated paper mode can validate downstream pipeline.