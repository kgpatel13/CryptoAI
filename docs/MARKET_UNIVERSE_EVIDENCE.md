# CryptoAI Market Universe Evidence

## Purpose

Market Universe Evidence ranks the configured chain, pair, and DEX universe using measured paper evidence.

It answers:

- Which markets are active focus candidates now.
- Which markets are configured but blocked by missing quote-provider evidence.
- Which lower-buffer settings are promising for research only.
- Whether expansion beyond Base WETH/USDC is evidence-backed.

It does not change production cost buffers, risk thresholds, paper thresholds, or live-trading eligibility.

## Inputs

- `reports/market_intelligence.json`
- `reports/provider_monitor.json`
- `reports/optimization_report.json`
- `reports/execution_cost_evidence.json`
- `reports/quote_coverage_evidence.json`
- `data/quote_diagnostics.jsonl`
- `data/multi_dex_opportunities.jsonl`

## Outputs

- `reports/market_universe_evidence.json`
- `reports/market_universe_evidence.md`

## Classifications

- `ACTIVE_FOCUS` - enough quote and opportunity evidence to keep monitoring in paper mode.
- `RESEARCH_TARGET` - promising registry/provider surface but still needs deeper evidence.
- `BLOCKED_NEEDS_QUOTES` - configured pair is not tradeable evidence yet because fewer than two healthy DEX quotes exist.
- `WATCH_UNCONFIGURED` - discovered candidate is not configured as a supported research pair.
- `WATCH` - keep collecting evidence.

## Current Interpretation

Base `WETH/USDC` is the default research focus because it has real quote evidence across Uniswap V2 and Aerodrome. Other configured chains and pairs remain expansion candidates until quote providers and provider-health evidence exist for those venues.

Use Quote Coverage Evidence to identify the next route/provider target before expanding the active universe.

## Command

```bash
python -m app.research.market_universe_evidence_service
```

## Safety

Lower-buffer optimization remains research-only. The production `0.30%` buffer stays unchanged until execution-cost confidence, replay stability, provider health, and paper performance all support a reviewed change.

Production-trade evidence means a signal clears both the production cost buffer and the paper BUY threshold. Positive-after-cost signals below the BUY threshold remain diagnostics only.
