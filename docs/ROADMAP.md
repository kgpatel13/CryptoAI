# CryptoAI Roadmap

## Completed

- v3.1 - Resilient quotes and paper risk approval.
- v3.2 - Resilience layer: RPC failover, provider health, circuit breakers, cache safety.
- v3.3 - Intelligent portfolio and risk engine.
- v3.4 - Professional paper execution engine.
- v3.4.1 - Paper accounting hotfix for inverse pairs.
- v3.5 - Portfolio analytics and PnL engine.
- v3.6 - Strategy framework and research platform foundation.
- v4.0 - Quant research platform foundation.
- v4.1 - 24/7 operations, Mission Control runtime state, heartbeat, scheduler loop, and operational metrics.
- v4.2 - Replay engine, backtesting, and strategy optimization foundation.
- v4.3 - Experiment evidence tracking, replay/optimization gates, and walk-forward validation preparation.
- v4.4 - Provider health hardening, clean report evidence gates, and legacy paper evidence archive.
- v5.0 - AI Strategy Intelligence, measured strategy scoring, and advisory paper optimization recommendations.
- v5.1 - Replay Diagnostics and evidence gap analysis for production-buffer replay blockers.
- v5.2 - Execution Cost Evidence Engine for measuring whether the current production cost buffer is conservative, accurate, too high, or too low.
- v5.3 - Market Universe and Settings Evidence for ranking which chain/pair/DEX surfaces are actually ready for paper monitoring.
- v5.4 - Quote Coverage Expansion Evidence for ranking quote-provider, router, and route-test gaps before adding more markets.
- v5.5 - ETH Route Architecture and Buffer Candidate Evidence for focusing Base WETH/USDC and USDC/WETH, documenting real-money controls, and keeping 0.20% as a gated research candidate.
- v5.6 - ETH Golden Path Market Coverage for scoring ETH market maturity across target chains, DEXs, stables, quote evidence, provider health, and execution-cost confidence.
- v5.7 - 24/7 Paper Launch Settings for dashboard-managed paper parameters, 1 ETH paper capital profile, validated launch command, and unchanged safety thresholds.
- v5.8 - Verified Base Uniswap V3 Quote Provider for three-venue Base ETH quote diagnostics and market coverage evidence.
- v5.9 - Aggressive Paper Execution Profile for faster 24/7 paper scans, larger simulated notional, settings-driven risk sizing, and unchanged core safety gates.

## Current

- v5.10 - Unbounded Paper Lab Profile for high-capital paper stress testing, zero-valued paper throttles, and unchanged live-trading locks.

## Next

- v5.11 - Market regime awareness, adaptive confidence, and walk-forward explainability.
- v6.0 - Live trading candidate with dedicated wallet, secure signing, smart contract executor, kill switch, and progressive rollout.
- v7.0 - Multi-exchange, multi-account, and cloud deployment expansion.

## Live Trading Gate

Live trading should remain disabled until the platform has objective evidence:

- 60-90 days stable paper trading.
- Positive risk-adjusted paper performance.
- High-confidence execution-cost evidence.
- Active market universe evidence beyond a single narrow venue set, unless explicitly approved for a narrow launch.
- No accounting reconciliation issues.
- No critical unresolved provider failures.
- Risk-engine violations resolved.
- Strategy metrics statistically meaningful.
