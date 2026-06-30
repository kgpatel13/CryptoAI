# CryptoAI

Multi-chain AI trading research and paper-execution platform.

## Current Version

**v5.10 - Unbounded Paper Lab Profile**

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
python -m app.automation.paper_autopilot --once
python -m app.reporting.paper_report
python -m app.research.research_report
python -m app.market_intelligence.market_intelligence_service
python -m app.operations.provider_monitor
python -m app.backtesting.backtest_service
python -m app.backtesting.replay_diagnostics_service
python -m app.execution.execution_cost_evidence_service
python -m app.backtesting.optimization_service
python -m app.research.market_universe_evidence_service
python -m app.research.quote_coverage_evidence_service
python -m app.research.eth_route_architecture_service
python -m app.research.eth_market_coverage_service
python -m app.operations.paper_settings_service
python -m app.reporting.report_audit
python -m app.backtesting.experiment_service
python -m app.ai.strategy_intelligence_service
python -m app.reporting.report_audit
python -m app.reporting.legacy_paper_archive --dry-run
python -m app.automation.paper_autopilot --loop --use-settings
python -m app.automation.paper_autopilot --loop --interval-seconds 300 --heartbeat-interval-seconds 60
```

Run `report_audit` once before experiment/AI evidence and once at the end. The first run gives experiment and Strategy Intelligence a fresh audit snapshot; the final run certifies the generated report set.

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
- `reports/market_universe_evidence.json`
- `reports/market_universe_evidence.md`
- `reports/quote_coverage_evidence.json`
- `reports/quote_coverage_evidence.md`
- `reports/eth_route_architecture.json`
- `reports/eth_route_architecture.md`
- `reports/eth_market_coverage.json`
- `reports/eth_market_coverage.md`
- `reports/paper_trading_settings.json`
- `reports/paper_trading_settings.md`
- `reports/backtest_report.json`
- `reports/backtest_report.md`
- `reports/replay_diagnostics.json`
- `reports/replay_diagnostics.md`
- `reports/execution_cost_evidence.json`
- `reports/execution_cost_evidence.md`
- `reports/optimization_report.json`
- `reports/optimization_report.md`
- `reports/experiment_report.json`
- `reports/experiment_report.md`
- `reports/strategy_intelligence.json`
- `reports/strategy_intelligence.md`
- `data/experiments.jsonl`
- `reports/report_audit.json`
- `reports/report_audit.md`

Legacy paper rows that should not count as clean evidence can be archived with:

```bash
python -m app.reporting.legacy_paper_archive --dry-run
python -m app.reporting.legacy_paper_archive
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
- `docs/OPERATIONS.md`
- `docs/MARKET_INTELLIGENCE.md`
- `docs/MARKET_UNIVERSE_EVIDENCE.md`
- `docs/QUOTE_COVERAGE_EVIDENCE.md`
- `docs/ETH_ROUTE_ARCHITECTURE.md`
- `docs/ETH_MARKET_COVERAGE.md`
- `docs/ARCHITECTURE.md`
- `docs/STRATEGY_FRAMEWORK.md`
- `docs/AI_STRATEGY_INTELLIGENCE.md`
- `docs/EXECUTION_COST_EVIDENCE.md`
- `docs/LIVE_READINESS.md`
- `releases/RELEASE_v5.6.md`
