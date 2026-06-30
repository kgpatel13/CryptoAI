# CryptoAI Changelog

## v5.15 - Isolated Wallet Preflight

- Added `WalletPreflightService` for preparation-only checks of the future isolated tiny-live wallet.
- Added `wallet_preflight.json` and `wallet_preflight.md`.
- Added Risk & Controls dashboard support for generating and reviewing Wallet Preflight.
- Added Report Audit coverage for wallet preflight reports.
- Validates the Base-only, USDC/WETH, `$450 USDC + $50 ETH gas`, `$500 max wallet` preparation plan without storing keys or sending transactions.
- Kept live trading disabled, kill switch expected ON, private keys absent during preflight, and live approval false.

## v5.14 - Operational Evidence Gate Split

- Added operational, review, and research categories to Report Audit.
- Added blocking, operational, and research finding counts so stale background research remains visible without blocking healthy paper runtime review.
- Updated Paper Run Review and Live Safety to use blocking operational findings instead of total stale-report count.
- Reordered paper autopilot report generation so Report Audit refreshes before Paper Run Review consumes it.
- Reclassified paper settings as a configuration snapshot, not a per-cycle freshness blocker.
- Kept live trading disabled, paper BUY threshold unchanged at `0.30%`, production cost buffer unchanged at `0.30%`, and `$500` paper/live pilot caps intact.

## v5.13 - Pool Depth and Quote-Size Ladder Evidence

- Added `PoolDepthLadderService` to probe Base ETH routes at increasing quote sizes and measure requested-size price impact.
- Added `quote_size_ladder.jsonl`, `pool_depth_ladder.json`, and `pool_depth_ladder.md`.
- Integrated pool-depth evidence into Execution Realism so latest opportunities can use `POOL_DEPTH_LADDER` instead of quote-probe heuristics.
- Added Mission Control, Reports, Replay / Backtesting, Report Audit, and Strategy Intelligence integration for pool-depth status.
- Kept live trading disabled, paper BUY threshold unchanged at `0.30%`, and production cost buffer unchanged at `0.30%`.
- Added regression tests for depth-ready routes, size-limited routes, and depth-aware realism promotion.

## v5.12 - Execution Realism Evidence Engine

- Added `ExecutionRealismService` to stress-check paper opportunities against route quote coverage, requested notional, gas, price-impact heuristics, and MEV risk buffers.
- Added `execution_realism.json` and `execution_realism.md` reports.
- Integrated Execution Realism into Mission Control, report views, Report Audit, and paper autopilot report generation.
- Added conservative statuses such as `PAPER_ONLY_NEEDS_DEPTH`, `SHADOW_ONLY`, `NEGATIVE_AFTER_STRESS`, and `NOT_EXECUTABLE`.
- Kept live trading disabled, paper BUY threshold unchanged at `0.30%`, and production cost buffer unchanged at `0.30%`.
- Added regression tests for shadow-only BUY candidates, non-executable single-route opportunities, and autopilot report ordering.

## v5.11 - Arbitrage Execution Refactor

- Added a dedicated paper `ArbitrageExecutionEngine` so DEX arbitrage is simulated as an atomic buy/sell round trip.
- Changed paper arbitrage fills to persist as immediately `CLOSED` orders with buy venue, sell venue, gross edge, cost buffer, net edge, realized PnL, and exit value.
- Stopped routing arbitrage fills through TP/SL/max-hold position lifecycle logic.
- Added portfolio ledger support for closed arbitrage trades that updates cash by realized PnL without creating open positions.
- Updated reports and analytics so `paper_report`, `portfolio_analytics`, dashboard, and raw exports use the same closed-order/portfolio-state source of truth.
- Restored `max_open_positions = 1` and duplicate-position blocking for the saved paper profile.
- Added regression tests for immediate close, no open arbitrage positions, no cash/PnL explosion, report consistency, and full-cash sizing without leverage.

## v5.10 - Unbounded Paper Lab Profile

- Added an explicit `unbounded_paper_lab` profile for stress-testing 24/7 paper execution with larger simulated capital.
- Allowed paper-only `0` values for unlimited daily trades, unlimited open positions, no cooldown, and disabled paper daily-loss stop.
- Allowed `0` loop interval for continuous paper scanning where the next cycle starts immediately after the prior cycle completes.
- Added `full_available_cash` paper sizing so approved paper trades can request the configured max trade size and then use available portfolio cash as the final cap.
- Added dashboard controls for duplicate-position blocking and widened the paper capital/notional input ranges.
- Wired unbounded settings into Portfolio Risk so zero-valued paper throttles are actually disabled during `--use-settings` runs.
- Kept live trading disabled, stale-live quotes blocked, kill switch enabled, and paper BUY threshold locked at `0.30%`.
- Added regression coverage for the unbounded settings export and zero-limit risk behavior.

## v5.9 - Aggressive Paper Execution Profile

- Added an explicit `aggressive_paper` settings profile for faster paper evidence collection.
- Reduced the configurable paper loop floor from 60 seconds to 15 seconds; the saved aggressive profile uses 30 seconds.
- Wired `paper_autopilot --use-settings` into runtime environment variables so paper capital, max notional, daily trade cap, cooldown, and daily loss settings are enforced by Risk and Paper Execution.
- Increased saved aggressive paper profile to 1 ETH at a `$10000` reference, `$1000` max paper notional, 200 daily paper trades, 60-second cooldown, and `$500` paper daily loss guard.
- Kept live trading disabled, duplicate open-position protection enabled, kill switch enabled, and paper BUY threshold locked at `0.30%`.
- Added regression coverage for aggressive paper runtime environment export.

## v5.8 - Verified Base Uniswap V3 Quote Provider

- Added a Base Uniswap V3 QuoterV2 quote provider for `WETH/USDC` and `USDC/WETH` diagnostics.
- Verified Base Uniswap V3 Factory, SwapRouter02, and QuoterV2 deployment addresses against official Uniswap deployment documentation.
- Wired Uniswap V3 into QuoteService, QuoteManager, Quote Coverage Evidence, ETH Route Architecture, ETH Market Coverage, and Paper Settings.
- Expanded the Base ETH paper launch profile from two DEX venues to three while keeping live trading disabled.
- Kept production cost buffer and paper BUY threshold unchanged at `0.30%`.
- Added regression tests for Uniswap V3 address constants, registry wiring, provider support, and paper settings coverage.

## v5.7 - 24/7 Paper Launch Settings

- Added validated paper launch settings for continuous 24/7 paper operation.
- Added a dashboard Paper Settings page for loop cadence, 1 ETH paper profile, max trade size, daily trade cap, ETH coverage gates, and risk limits.
- Added `paper_autopilot --use-settings` so CLI runs share the same validated settings as the dashboard.
- Added settings reports and Report Audit integration.
- Kept live trading disabled, production cost buffer at `0.30%`, and paper BUY threshold at `0.30%`.
- Added regression tests for settings validation and safety locks.

## v5.6 - ETH Golden Path Market Coverage

- Added ETH Market Coverage report for scoring target-vs-evidence maturity before expanding beyond ETH.
- Added the Golden Path coverage target across Base, Ethereum, Arbitrum, Optimism, and Polygon without pretending unimplemented markets are active.
- Added Mission Control and Market Intelligence dashboard KPIs for ETH coverage score, status, target chains, and quote-ready routes.
- Integrated ETH coverage into Strategy Intelligence and Report Audit.
- Added regression tests to prevent fake market coverage and require two-DEX quote readiness.

## v5.5 - ETH Route Architecture & Buffer Candidate Evidence

- Added ETH Route Architecture report for focusing Base `WETH/USDC` and `USDC/WETH` before wider market expansion.
- Compared `0.20%` research-buffer candidate evidence against the unchanged `0.30%` production buffer.
- Added explicit promotion gates so a lower buffer cannot graduate without high-confidence execution-cost, quote, provider, paper, and audit evidence.
- Documented the real-money execution architecture for future v6 live-readiness work without enabling live trading.
- Added dashboard, Report Audit, operations docs, roadmap, release notes, and regression tests for the route architecture evidence.

## v5.4 - Quote Coverage Expansion Evidence

- Added Quote Coverage Evidence report for ranking configured pair, DEX, router, provider, and recent quote coverage.
- Identified Base `WETH/USDC` as the only active two-DEX quoted pair and Base `CBBTC/USDC` as the next targeted quote test.
- Added quote coverage context to Strategy Intelligence and dashboard Market Intelligence views.
- Added Quote Coverage Evidence to Report Audit expected reports.
- Corrected the Base Aerodrome registry router to match the quote provider contract constant.
- Added regression tests for quote coverage classification and registry/provider address consistency.

## v5.3 - Market Universe and Settings Evidence

- Added Market Universe Evidence report for ranking configured chain/pair/DEX coverage from measured quote, provider, opportunity, optimization, and execution-cost evidence.
- Classified pairs as active focus, research targets, quote-provider blocked, or watchlist without changing production thresholds.
- Added research-only settings evidence so lower-buffer optimization can be reviewed without changing the `0.30%` production buffer.
- Clarified replay diagnostics so production trades require both production cost buffer and paper BUY threshold.
- Integrated universe evidence into Strategy Intelligence, dashboard, Report Audit, docs, and release notes.
- Added regression tests for active-focus ranking and quote-provider blocking.

## v5.2 - Execution Cost Evidence Engine

- Added Execution Cost Evidence report for measuring observed paper slippage, quote latency, provider health, and replay edge distribution.
- Classified the unchanged `0.30%` production cost buffer as conservative, accurate, too high, too low, or insufficient based on measured evidence.
- Integrated execution cost evidence into Experiment Evidence, Strategy Intelligence, dashboard, and Report Audit.
- Added dashboard controls and report views for Execution Cost Evidence.
- Added regression tests for lower-bound cost measurement, too-high classification, and insufficient sample handling.

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
