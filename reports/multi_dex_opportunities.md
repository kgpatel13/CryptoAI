# CryptoAI Multi-DEX Opportunity Report

Generated: `2026-06-28T17:36:44Z`

## Quote Health

- Total quotes: `4`
- Healthy quotes: `2`
- Failed/invalid quotes: `2`

## Opportunities

| Mode | Pair | Buy DEX | Sell DEX | Buy Price | Sell Price | Gross % | Cost % | Net % | Decision | Reason |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|
| PAPER_SIMULATED | WETH/USDC | Uniswap V2 | SyntheticPaperVenue | 1558.62981100 | 1568.76090477 | 0.65000000 | 0.30000000 | 0.35000000 | BUY | Paper-simulated opportunity because only one healthy DEX quote exists. Use this only to validate strategy/risk/paper-execution pipeline: net edge 0.3500% is above BUY threshold 0.30%. Not live-tradeable. |
| PAPER_SIMULATED | USDC/WETH | Uniswap V2 | SyntheticPaperVenue | 0.00063475 | 0.00063887 | 0.65000000 | 0.30000000 | 0.35000000 | BUY | Paper-simulated opportunity because only one healthy DEX quote exists. Use this only to validate strategy/risk/paper-execution pipeline: net edge 0.3500% is above BUY threshold 0.30%. Not live-tradeable. |

## Failed / Invalid Quotes

| DEX | Pair | Error |
|---|---|---|
| Aerodrome | WETH/USDC | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row. |
| Aerodrome | USDC/WETH | RPC rate limit while reading Aerodrome quote. Configure BASE_RPC with a private RPC or wait for cache fallback. |

## Interpretation

- Only one DEX is healthy. Real arbitrage is not possible yet; simulated paper mode can validate downstream pipeline.