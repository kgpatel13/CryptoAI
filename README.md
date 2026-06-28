# CryptoAI

Multi-chain AI trading research and paper-execution platform.

## Current Version

**v3.6 — Strategy Framework & Research Platform Foundation**

CryptoAI is currently paper-trading only. Live trading is disabled by default and should remain disabled until long-duration paper validation and live-readiness gates are satisfied.

## Core Flow

```text
Quotes / Market Data
        |
        v
Opportunity Engine
        |
        v
Strategy Framework
        |
        v
AI / Signal Ranking
        |
        v
Risk Engine
        |
        v
Paper Execution Engine
        |
        v
Portfolio Accounting
        |
        v
Analytics / Dashboard
```

## Common Commands

```bash
python -m compileall -q app
python -m unittest discover -s tests -v

python -m app.diagnostics.quote_diagnostics
python -m app.opportunities.multi_dex_opportunity_engine
python -m app.opportunities.opportunity_explorer
python -m app.strategy.strategy_center
python -m app.automation.paper_autopilot --once
python -m app.reporting.paper_report
```

## Strategy Configuration

Strategy enablement is controlled by:

```text
config/strategies.json
```

Only the DEX arbitrage strategy is enabled by default. Research strategies are visible but disabled until their feature pipelines and validation are implemented.

## Documentation

See:

- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/STRATEGY_FRAMEWORK.md`
- `docs/LIVE_READINESS.md`
- `releases/RELEASE_v3.6.md`
