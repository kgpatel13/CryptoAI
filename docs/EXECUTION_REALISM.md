# Execution Realism Evidence

Execution Realism is a paper-mode evidence layer for deciding whether profitable-looking paper arbitrage is realistic enough for shadow review.

It does not place trades, approve live trading, or change thresholds.

## Inputs

- `data/opportunity_decisions.jsonl`
- `data/quote_diagnostics.jsonl`
- `data/paper_portfolio_state.json`
- `reports/paper_trading_settings.json`
- `reports/pool_depth_ladder.json` when available

## Outputs

- `reports/execution_realism.json`
- `reports/execution_realism.md`

## Realism Model

For the latest opportunity batch, the service measures:

- requested paper notional,
- route quote availability,
- healthy DEX count,
- quote-probe executable size,
- estimated price impact,
- chain gas cost,
- MEV risk buffer,
- stress total cost,
- stress net edge.

When Pool Depth Ladder evidence exists, Execution Realism uses `POOL_DEPTH_LADDER`.
Otherwise, it falls back to the intentionally conservative `QUOTE_PROBE_HEURISTIC`.

## Statuses

- `NOT_EXECUTABLE`: fewer than two healthy route quotes or no executable size evidence.
- `NEGATIVE_AFTER_STRESS`: gross edge disappears after gas, price-impact, and MEV buffers.
- `WATCH_ONLY`: source opportunity was not a BUY.
- `SHADOW_ONLY`: paper BUY exists, but confidence is not high enough for live review.
- `SHADOW_READY`: reserved for future higher-confidence depth evidence.

## Live Trading Rule

`SHADOW_ONLY` and `PAPER_ONLY_NEEDS_DEPTH` are not live approvals.

Live trading remains blocked until pool-depth evidence, execution-cost confidence, provider health, paper stability, audit cleanliness, and rollout controls all pass dedicated gates.
