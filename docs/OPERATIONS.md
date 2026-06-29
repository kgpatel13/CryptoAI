# CryptoAI v4.1 Operations Core

## Executive Summary

v4.1 starts the 24/7 paper operations layer. The goal is reliable long-running paper evidence collection, not live execution.

The operations runtime owns process heartbeat, runtime state, uptime tracking, graceful shutdown, operational metrics, and Mission Control summaries for continuous `paper_autopilot --loop` runs.

## Architecture Diagram

```text
Paper Autopilot CLI
        |
        v
Operations Runtime
        |
SchedulerService.run_once()
        |
        v
Quotes -> Strategy -> AI Ranking -> Risk -> Paper Execution
        |
        v
Provider Monitor + Market Intelligence + Heartbeat/Mission Reports
```

## Runtime Files

- `data/heartbeat.json` - latest process heartbeat.
- `data/heartbeat_history.jsonl` - append-only heartbeat history.
- `data/runtime_state.json` - latest runtime state.
- `reports/operational_metrics.json` - cycle counts, failures, latency, heartbeat count, and status counts.
- `reports/mission_summary.json` - Mission Control machine-readable summary.
- `reports/mission_summary.md` - Mission Control human-readable summary.
- `reports/market_intelligence.json` - chain, token, DEX, pair, provider, and readiness summary.
- `reports/market_intelligence.md` - human-readable Market Intelligence report.
- `reports/provider_monitor.json` - provider status, chain summaries, and alerts.
- `reports/provider_monitor.md` - human-readable Provider Monitor report.
- `reports/backtest_report.json` - multi-DEX replay backtest metrics.
- `reports/backtest_report.md` - human-readable Backtest report.
- `reports/optimization_report.json` - parameter-grid optimization metrics.
- `reports/optimization_report.md` - human-readable Optimization report.
- `reports/experiment_report.json` - experiment evidence gates for replay, optimization, provider health, paper PnL, and report audit.
- `reports/experiment_report.md` - human-readable Experiment report.
- `reports/strategy_intelligence.json` - v5.0 advisory strategy scoring and recommendations.
- `reports/strategy_intelligence.md` - human-readable Strategy Intelligence report.
- `data/experiments.jsonl` - append-only experiment evidence history.
- `reports/report_audit.json` - report freshness, parseability, and warning summary.
- `reports/report_audit.md` - human-readable Report Audit report.
- `data/paper_orders_legacy_archive.jsonl` - archived pre-repair paper rows excluded from clean evidence.

## Commands

Run one cycle:

```bash
python -m app.automation.paper_autopilot --once
```

Generate market intelligence manually:

```bash
python -m app.market_intelligence.market_intelligence_service
```

Generate provider monitoring manually:

```bash
python -m app.diagnostics.quote_diagnostics
python -m app.operations.provider_monitor
```

Provider Monitor reads existing health observations and does not make network calls. Run quote diagnostics or one paper autopilot cycle first when validating provider health.

Generate report audit manually:

```bash
python -m app.reporting.report_audit
```

Archive legacy paper-order rows after reviewing a dry run:

```bash
python -m app.reporting.legacy_paper_archive --dry-run
python -m app.reporting.legacy_paper_archive
```

Generate replay backtest manually:

```bash
python -m app.backtesting.backtest_service
```

Generate optimization manually:

```bash
python -m app.backtesting.optimization_service
```

Record experiment evidence manually:

```bash
python -m app.backtesting.experiment_service
```

Generate strategy intelligence manually:

```bash
python -m app.ai.strategy_intelligence_service
```

Run continuously in paper mode:

```bash
python -m app.automation.paper_autopilot --loop --interval-seconds 300 --heartbeat-interval-seconds 60
```

Bounded validation run:

```bash
python -m app.automation.paper_autopilot --loop --interval-seconds 300 --heartbeat-interval-seconds 60 --max-cycles 2
```

## Safety

- Live trading remains disabled.
- The runtime reports `live_trading_enabled` in Mission Control summaries.
- The paper autopilot still refuses to start when `CRYPTOAI_LIVE_TRADING_ENABLED` is truthy.
- AI ranking remains advisory.
- Risk remains the final authority before paper execution.

## Validation

```bash
python -m compileall -q app tests
python -m unittest discover -s tests -v
python -m app.automation.paper_autopilot --loop --interval-seconds 300 --heartbeat-interval-seconds 60 --max-cycles 1
```

Expected files after a loop run:

```text
data/heartbeat.json
data/heartbeat_history.jsonl
data/runtime_state.json
reports/operational_metrics.json
reports/mission_summary.json
reports/mission_summary.md
reports/market_intelligence.json
reports/market_intelligence.md
reports/provider_monitor.json
reports/provider_monitor.md
reports/backtest_report.json
reports/backtest_report.md
reports/optimization_report.json
reports/optimization_report.md
reports/experiment_report.json
reports/experiment_report.md
reports/strategy_intelligence.json
reports/strategy_intelligence.md
data/experiments.jsonl
reports/report_audit.json
reports/report_audit.md
data/paper_orders_legacy_archive.jsonl
```

## Rollback

Remove the v4.1 operations files and restore the previous `paper_autopilot` loop implementation from the prior release tag or commit. Runtime output files can be deleted safely because they are generated artifacts.
