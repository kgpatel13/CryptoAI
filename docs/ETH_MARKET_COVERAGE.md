# CryptoAI ETH Market Coverage

## Purpose

ETH Market Coverage turns the "Golden Path" recommendation into a measurable KPI.

Instead of expanding to many assets, CryptoAI now scores how mature ETH coverage is across target chains, DEXs, stablecoin routes, quote evidence, provider health, and execution-cost evidence.

## Golden Path Target

Asset focus:

- ETH / WETH

Stable routes:

- `WETH/USDC`
- `WETH/USDT`
- `WETH/DAI`

Target chains:

- Base
- Ethereum
- Arbitrum
- Optimism
- Polygon

Target venues:

- Base: Uniswap V2, Aerodrome, Uniswap V3
- Ethereum: Uniswap V3, Curve, SushiSwap, Balancer
- Arbitrum: Uniswap V3, Camelot, SushiSwap
- Optimism: Uniswap V3, Velodrome
- Polygon: Uniswap V3, QuickSwap

## Scoring Inputs

- Token registry coverage
- DEX registry coverage
- Implemented quote-provider coverage
- Recent two-DEX quote evidence
- Provider health evidence
- Execution-cost confidence
- ETH route architecture evidence

## Interpretation

Target-only markets are not active markets. A target chain becomes meaningful only after verified registry metadata, provider implementation, route diagnostics, and provider health evidence exist.

ETH should reach high maturity before BTC, blue chips, or long-tail assets are added.

## Command

```bash
python -m app.research.eth_market_coverage_service
```

## Outputs

- `reports/eth_market_coverage.json`
- `reports/eth_market_coverage.md`

## Safety

This report does not change production buffers, risk thresholds, or live-trading eligibility.
