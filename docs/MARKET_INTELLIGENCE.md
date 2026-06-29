# CryptoAI Market Intelligence

## Purpose

Market Intelligence is a v4.1 paper-mode observability layer. It summarizes whether CryptoAI has enough registry and provider evidence to monitor a chain/pair universe responsibly.

It does not approve live trading.

## Inputs

- Chain registry from `app.blockchain.chains`.
- Token registry from `app.registry.tokens`.
- DEX registry from `app.registry.dexes`.
- Configured pairs from `app.registry.pairs`.
- Provider health observations from `data/provider_health.json`.

## Outputs

- `reports/market_intelligence.json`
- `reports/market_intelligence.md`

Market Intelligence feeds `reports/market_universe_evidence.json`, which ranks the configured universe against measured quote, opportunity, optimization, and execution-cost evidence.

## Readiness Score

Readiness combines:

- Registry score: token coverage, DEX coverage, configured pairs, and generated pair candidates.
- Provider score: observed provider-health scores by chain.

Missing provider observations are treated conservatively as incomplete evidence.

Readiness statuses:

- `READY_FOR_PAPER` - enough evidence for paper-mode monitoring.
- `WATCH` - partial readiness; continue collecting evidence.
- `NEEDS_DATA` - registry or provider evidence is insufficient.

## Command

```bash
python -m app.market_intelligence.market_intelligence_service
```

## Safety

Market Intelligence is advisory and observational. Risk Engine remains the final authority before paper execution, and live trading remains disabled.
