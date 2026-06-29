# CryptoAI Changelog

## v4.1 - 24/7 Paper Operations Core

- Added Operations Runtime for heartbeat, runtime state, graceful shutdown, uptime tracking, mission summary, and operational metrics.
- Wired continuous `paper_autopilot --loop` through the operations runtime.
- Added Mission Control dashboard visibility for runtime heartbeat and mission summary.
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
