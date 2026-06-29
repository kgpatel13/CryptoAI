# CryptoAI Changelog

## v5.1 - Replay Diagnostics and Evidence Gap Analysis

- Added Replay Diagnostics report for explaining why production-buffer replay has zero trades.
- Compared production cost buffer against lower-buffer research scenarios without automatically relaxing risk.
- Integrated replay diagnostics into Experiment Evidence and Strategy Intelligence next actions.
- Added dashboard metrics and report view for Replay Diagnostics.
- Added Replay Diagnostics to Report Audit expected outputs.
- Added regression tests for lower-buffer diagnostic findings.

## v5.0 - AI Strategy Intelligence

- Added measured Strategy Intelligence report for strategy-level scoring and recommendations.
- Combined Strategy Center, Feature Store, Optimization, Experiment, Provider Monitor, Paper Report, and Report Audit evidence.
- Added conservative recommendations: research, watchlist, operations hold, and paper optimization candidate.
- Added dashboard tab for AI Strategy Intelligence review.
- Added Strategy Intelligence to Report Audit expected outputs.
- Added regression tests for clean evidence and experiment-failure behavior.

## v4.4 - Provider Health Hardening

- Moved paper autopilot operations reports after quote/workflow refresh so Provider Monitor reports on fresh health evidence.
- Split provider current status from rolling score status for recovering providers.
- Downgraded unhealthy optional backup RPCs to WATCH when required same-chain RPC coverage is fresh and healthy.
- Treated fresh successful low-score providers as WATCH recovery instead of persistent DEGRADED.
- Added legacy paper-order archive utility for pre-repair inverse-pair rows.
- Updated experiment gates so provider WATCH remains a warning, not a pass.
- Refreshed reports with zero audit findings and no legacy paper accounting warnings.

## v4.3 - Experiment Evidence Tracking

- Added experiment evidence tracking for replay, optimization, provider health, paper PnL, and report audit gates.
- Added `experiment_report.json`, `experiment_report.md`, and append-only `data/experiments.jsonl` history.
- Added dashboard controls and metrics for recording and reviewing experiment evidence.
- Added experiment regression tests for research-only and paper-evidence-candidate states.

## v4.2 - Replay, Backtesting, Optimization

- Started v4.2 replay/backtesting foundation.
- Added multi-DEX opportunity replay backtest with real-vs-synthetic filtering.
- Added `backtest_report.json` and `backtest_report.md` outputs.
- Added parameter-grid Optimization report for cost buffer, minimum net edge, and notional scenarios.
- Added Replay / Backtesting dashboard tab for backtest and optimization review.
- Added backtest regression tests for real opportunity replay and explicit synthetic inclusion.

## v4.1 - 24/7 Paper Operations Core

- Added Operations Runtime for heartbeat, runtime state, graceful shutdown, uptime tracking, mission summary, and operational metrics.
- Wired continuous `paper_autopilot --loop` through the operations runtime.
- Added Mission Control dashboard visibility for runtime heartbeat and mission summary.
- Added Market Intelligence report for chain, DEX, token, pair, provider-health, and readiness scoring.
- Added Provider Monitor report for stale, degraded, and critical provider observations.
- Added Report Audit report for freshness, parseability, critical status, and legacy accounting review.
- Added operations regression tests with deterministic fake cycle runners.
- Added v4.1 operations documentation and release notes.

## v4.0 - Quant Research Platform

- Added Feature Store with JSONL, CSV, and SQLite exports.
- Added Research Dashboard report and dashboard page.
- Added Mission Control dashboard page.
- Added deterministic decision explainability helper.
- Added research documentation and v4.0 release notes.
- Added regression tests for feature vectors, exports, and explainability.

## v3.6 - Strategy Framework & Research Platform Foundation

- Added strategy registry and configuration.
- Added ranked strategy signals and signal persistence.
- Added strategy-level performance report and Strategy Center dashboard page.
- Added research placeholders for momentum, mean reversion, breakout, and AI-ranked strategies.
- Added docs for roadmap, architecture, strategy framework, and live readiness.

## v3.5 - Portfolio Analytics & PnL Engine

- Added portfolio analytics and PnL service.
- Added daily PnL, equity curve, return %, max drawdown, win rate, profit factor, and expectancy.
- Added trade journal and performance-by-pair analytics.
- Added `portfolio_analytics.json` and `portfolio_analytics.md`.
- Integrated analytics into paper report.
- Added Portfolio Analytics dashboard page.
- Added analytics regression tests.

## v3.4.1 - Paper Accounting & Execution Integrity Hotfix

- Added canonical USD accounting for paper positions.
- Fixed inverse-pair accounting for routes such as USDC/WETH.
- Prevented raw quote-unit quantity explosions from corrupting cash/PnL.
- Added automatic legacy paper portfolio state repair.
- Added `python -m app.portfolio.repair_portfolio` repair/reset utility.
- Added accounting regression tests; unit test count increased to 17.

## v3.4 - Professional Execution Engine

- Added broker-like paper execution simulator.
- Added order lifecycle events.
- Added simulated slippage, latency, partial fills, and execution quality.
- Added take-profit, stop-loss, and max-hold-time paper position monitoring.
- Strengthened duplicate exposure control by blocking same-pair open positions by default.
- Enhanced paper reports with execution analytics and PnL fields.
- Expanded unit tests to 12 tests.

## v3.3 - Intelligent Portfolio & Risk Engine

- Added paper cash tracking.
- Added dynamic position sizing.
- Added open position tracking.
- Added daily trade limit, exposure limits, duplicate signal checks, and cooldown controls.
- Added paper portfolio reporting.

## v3.2 - Resilience Layer

- Added RPC failover, retry policy, circuit breakers, provider health, quote freshness, and paper/live safety gates.

## v3.1 - Resilient Quotes + Risk Approval

- Added resilient quote handling and paper risk approval improvements.
