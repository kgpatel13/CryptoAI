# Pool Depth Ladder Evidence

Pool Depth Ladder is a paper-mode evidence service for testing whether an apparent arbitrage route is still attractive at larger quote sizes.

It does not execute trades or change risk settings.

## Inputs

- quote providers registered through `QuoteManager`,
- `reports/paper_trading_settings.json`,
- `data/paper_portfolio_state.json`,
- optional DexScreener liquidity evidence.

## Outputs

- `data/quote_size_ladder.jsonl`
- `reports/pool_depth_ladder.json`
- `reports/pool_depth_ladder.md`

## Method

For each Base ETH route, the service requests quotes at increasing USD notionals:

- `100`
- `250`
- `500`
- `1000`
- `2000`

It measures:

- quote success count,
- requested-size price impact,
- worst tested price impact,
- low-impact usable notional,
- healthy DEX count,
- route status.

## Statuses

- `DEPTH_READY`: at least two DEXes quote the requested size with low price impact.
- `DEPTH_WATCH`: requested size is quoteable, but price impact needs review.
- `SIZE_LIMITED`: requested size has high impact; low-impact size is below the desired paper size.
- `INSUFFICIENT_DEPTH`: route lacks enough healthy quote ladders.

## Live Trading Rule

Depth evidence is a gate, not an approval.

Live trading remains blocked until depth evidence, execution-cost evidence, provider health, report audit, risk controls, and staged rollout requirements all pass.

