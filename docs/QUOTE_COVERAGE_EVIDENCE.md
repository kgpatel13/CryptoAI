# CryptoAI Quote Coverage Evidence

## Purpose

Quote Coverage Evidence ranks configured chain, pair, and DEX coverage before expanding paper trading beyond the currently evidenced market.

It answers:

- Which configured pairs have at least two recent OK DEX quotes.
- Which pairs have implemented providers but still need route quote tests.
- Which chains need verified router metadata and quote-provider implementation.
- Which provider target should be tested next.

It does not approve live trading or change risk, paper, or cost thresholds.

## Inputs

- Chain, DEX, token, and pair registries.
- `data/quote_diagnostics.jsonl`
- `reports/provider_monitor.json`

## Outputs

- `reports/quote_coverage_evidence.json`
- `reports/quote_coverage_evidence.md`

## Current Interpretation

Base `WETH/USDC` is the primary configured pair with active quote evidence. v5.8 adds a verified Base Uniswap V3 quote provider so diagnostics can move from two-venue evidence toward sustained three-venue evidence.

Base `CBBTC/USDC` remains a later targeted quote test. The immediate priority is keeping ETH focused while collecting Uniswap V2, Aerodrome, and Uniswap V3 quote diagnostics for `WETH/USDC` and `USDC/WETH`.

Ethereum, Arbitrum, and Polygon expansion still needs verified router metadata and quote-provider implementation before those markets should be treated as tradeable evidence.

## Command

```bash
python -m app.research.quote_coverage_evidence_service
```

## Safety

A configured pair is not tradeable evidence until at least two DEXes have recent OK quotes for the same route. Missing quote coverage should block expansion, not encourage threshold changes.
