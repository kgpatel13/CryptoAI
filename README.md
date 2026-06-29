# CryptoAI

Multi-chain AI trading research and paper-execution platform.

## Current Version

**v4.1 - 24/7 Paper Operations Core**

CryptoAI is currently paper-trading only. Live trading is disabled by default and should remain disabled until long-duration paper validation and live-readiness gates are satisfied.

## Leadership

- Project Owner: Kamlesh Patel
- Primary Architect: ChatGPT GPT-5.5

## Core Principles

1. Reliability over speed.
2. Research before AI.
3. AI advises, Risk decides.
4. Data before opinions.
5. Never break existing architecture.
6. Everything measurable.
7. Everything tested.
8. Everything documented.
9. Everything rollback friendly.
10. Live trading only after sufficient paper evidence.

## Core Flow

```text
24/7 Operations / Mission Control
        |
        v
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
python -m app.market_intelligence.market_intelligence_service
python -m app.operations.provider_monitor
python -m app.reporting.report_audit
python -m app.automation.paper_autopilot --once
python -m app.automation.paper_autopilot --loop --interval-seconds 300 --heartbeat-interval-seconds 60
python -m app.reporting.paper_report
```

The continuous paper autopilot publishes:

- `data/heartbeat.json`
- `data/heartbeat_history.jsonl`
- `data/runtime_state.json`
- `reports/mission_summary.json`
- `reports/mission_summary.md`
- `reports/operational_metrics.json`
- `reports/market_intelligence.json`
- `reports/market_intelligence.md`
- `reports/provider_monitor.json`
- `reports/provider_monitor.md`
- `reports/report_audit.json`
- `reports/report_audit.md`

## Strategy Configuration

Strategy enablement is controlled by:

```text
config/strategies.json
```

Only the DEX arbitrage strategy is enabled by default. Research strategies are visible but disabled until their feature pipelines and validation are implemented.

## Documentation

See:

- `docs/ROADMAP.md`
- `docs/OPERATIONS.md`
- `docs/MARKET_INTELLIGENCE.md`
- `docs/ARCHITECTURE.md`
- `docs/STRATEGY_FRAMEWORK.md`
- `docs/LIVE_READINESS.md`
- `releases/RELEASE_v4.1.md`
