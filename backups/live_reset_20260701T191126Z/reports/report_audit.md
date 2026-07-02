# CryptoAI Report Audit

Generated: `2026-07-01T19:06:38Z`

## Summary

- Reports checked: `57`
- Missing: `4`
- Invalid JSON: `0`
- Stale: `38`
- Findings: `42`
- Blocking findings: `14`
- Operational findings: `14`
- Research findings: `24`

## Findings

| Severity | Category | Blocks Shadow | Report | Message |
|---|---|---|---|---|
| WATCH | operational | True | paper_report.json | Report is older than freshness window. |
| WATCH | operational | True | paper_report.md | Report is older than freshness window. |
| WATCH | review | False | paper_run_review.json | Report is older than freshness window. |
| WATCH | review | False | paper_run_review.md | Report is older than freshness window. |
| WARN | operational | True | live_safety.json | Expected report is missing. |
| WARN | operational | True | live_safety.md | Expected report is missing. |
| WATCH | operational | True | portfolio_analytics.json | Report is older than freshness window. |
| WATCH | operational | True | portfolio_analytics.md | Report is older than freshness window. |
| WATCH | research | False | strategy_center.json | Report is older than freshness window. |
| WATCH | research | False | strategy_center.md | Report is older than freshness window. |
| WATCH | research | False | strategy_intelligence.json | Report is older than freshness window. |
| WATCH | research | False | strategy_intelligence.md | Report is older than freshness window. |
| WATCH | research | False | feature_store.json | Report is older than freshness window. |
| WATCH | research | False | feature_store.md | Report is older than freshness window. |
| WATCH | research | False | research_dashboard.json | Report is older than freshness window. |
| WATCH | research | False | research_dashboard.md | Report is older than freshness window. |
| WATCH | research | False | backtest_report.json | Report is older than freshness window. |
| WATCH | research | False | backtest_report.md | Report is older than freshness window. |
| WATCH | research | False | replay_diagnostics.json | Report is older than freshness window. |
| WATCH | research | False | replay_diagnostics.md | Report is older than freshness window. |
| WATCH | operational | True | pool_depth_ladder.json | Report is older than freshness window. |
| WATCH | operational | True | pool_depth_ladder.md | Report is older than freshness window. |
| WARN | operational | True | live_shadow_gate.json | Expected report is missing. |
| WARN | operational | True | live_shadow_gate.md | Expected report is missing. |
| WATCH | operational | True | execution_cost_evidence.json | Report is older than freshness window. |
| WATCH | operational | True | execution_cost_evidence.md | Report is older than freshness window. |
| WATCH | research | False | optimization_report.json | Report is older than freshness window. |
| WATCH | research | False | optimization_report.md | Report is older than freshness window. |
| WATCH | research | False | experiment_report.json | Report is older than freshness window. |
| WATCH | research | False | experiment_report.md | Report is older than freshness window. |
| WATCH | operational | True | market_intelligence.json | Report is older than freshness window. |
| WATCH | operational | True | market_intelligence.md | Report is older than freshness window. |
| WATCH | research | False | market_universe_evidence.json | Report is older than freshness window. |
| WATCH | research | False | market_universe_evidence.md | Report is older than freshness window. |
| WATCH | research | False | quote_coverage_evidence.json | Report is older than freshness window. |
| WATCH | research | False | quote_coverage_evidence.md | Report is older than freshness window. |
| WATCH | research | False | eth_route_architecture.json | Report is older than freshness window. |
| WATCH | research | False | eth_route_architecture.md | Report is older than freshness window. |
| WATCH | research | False | eth_market_coverage.json | Report is older than freshness window. |
| WATCH | research | False | eth_market_coverage.md | Report is older than freshness window. |
| WATCH | review | False | paper_trading_settings.json | Report is older than freshness window. |
| WATCH | review | False | paper_trading_settings.md | Report is older than freshness window. |

## Reports

| Report | Category | Exists | Generated | Stale | Size |
|---|---|---|---|---|---:|
| quote_diagnostics.md | review | True | 2026-07-01T19:06:36Z | False | 917 |
| multi_dex_opportunities.md | operational | True | 2026-07-01T19:06:35Z | False | 930 |
| opportunity_explorer.md | operational | True | 2026-07-01T19:06:35Z | False | 511 |
| paper_report.json | operational | True | 2026-07-01T06:07:56Z | True | 182023 |
| paper_report.md | operational | True | 2026-07-01T06:07:56Z | True | 67278 |
| paper_run_review.json | review | True | 2026-07-01T06:07:58Z | True | 2867 |
| paper_run_review.md | review | True | 2026-07-01T06:07:58Z | True | 1922 |
| live_safety.json | operational | False | - | None | 0 |
| live_safety.md | operational | False | - | None | 0 |
| portfolio_analytics.json | operational | True | 2026-07-01T06:07:55Z | True | 69871 |
| portfolio_analytics.md | operational | True | 2026-07-01T06:07:55Z | True | 6137 |
| strategy_center.json | research | True | 2026-06-30T07:46:41Z | True | 6967 |
| strategy_center.md | research | True | 2026-06-30T07:46:41Z | True | 1712 |
| strategy_intelligence.json | research | True | 2026-06-30T07:46:46Z | True | 10599 |
| strategy_intelligence.md | research | True | 2026-06-30T07:46:46Z | True | 4993 |
| feature_store.json | research | True | 2026-06-30T07:46:42Z | True | 1584 |
| feature_store.md | research | True | 2026-06-30T07:46:42Z | True | 1040 |
| research_dashboard.json | research | True | 2026-06-30T07:46:42Z | True | 17995 |
| research_dashboard.md | research | True | 2026-06-30T07:46:42Z | True | 5066 |
| backtest_report.json | research | True | 2026-06-30T07:46:43Z | True | 245879 |
| backtest_report.md | research | True | 2026-06-30T07:46:43Z | True | 9462 |
| replay_diagnostics.json | research | True | 2026-06-30T07:46:44Z | True | 2269 |
| replay_diagnostics.md | research | True | 2026-06-30T07:46:44Z | True | 1258 |
| pool_depth_ladder.json | operational | True | 2026-07-01T16:15:06Z | True | 6947 |
| pool_depth_ladder.md | operational | True | 2026-07-01T16:15:06Z | True | 1719 |
| execution_realism.json | operational | True | 2026-07-01T19:06:36Z | False | 5539 |
| execution_realism.md | operational | True | 2026-07-01T19:06:36Z | False | 1151 |
| live_shadow_gate.json | operational | False | - | None | 0 |
| live_shadow_gate.md | operational | False | - | None | 0 |
| execution_cost_evidence.json | operational | True | 2026-07-01T06:07:56Z | True | 4065 |
| execution_cost_evidence.md | operational | True | 2026-07-01T06:07:56Z | True | 1545 |
| live_readiness_checklist.json | operational | True | 2026-07-01T19:06:37Z | False | 5186 |
| live_readiness_checklist.md | operational | True | 2026-07-01T19:06:37Z | False | 3194 |
| transaction_simulation.json | operational | True | 2026-07-01T19:06:37Z | False | 11699 |
| transaction_simulation.md | operational | True | 2026-07-01T19:06:37Z | False | 8743 |
| optimization_report.json | research | True | 2026-06-30T07:46:43Z | True | 541825 |
| optimization_report.md | research | True | 2026-06-30T07:46:43Z | True | 2210 |
| experiment_report.json | research | True | 2026-06-30T07:46:44Z | True | 9949 |
| experiment_report.md | research | True | 2026-06-30T07:46:44Z | True | 3439 |
| market_intelligence.json | operational | True | 2026-07-01T06:07:56Z | True | 4264 |
| market_intelligence.md | operational | True | 2026-07-01T06:07:56Z | True | 1269 |
| market_universe_evidence.json | research | True | 2026-06-30T07:46:45Z | True | 8885 |
| market_universe_evidence.md | research | True | 2026-06-30T07:46:45Z | True | 2694 |
| quote_coverage_evidence.json | research | True | 2026-06-30T07:46:45Z | True | 16283 |
| quote_coverage_evidence.md | research | True | 2026-06-30T07:46:45Z | True | 2665 |
| eth_route_architecture.json | research | True | 2026-06-30T07:46:45Z | True | 27781 |
| eth_route_architecture.md | research | True | 2026-06-30T07:46:45Z | True | 3986 |
| eth_market_coverage.json | research | True | 2026-06-30T07:46:46Z | True | 8684 |
| eth_market_coverage.md | research | True | 2026-06-30T07:46:46Z | True | 2124 |
| paper_trading_settings.json | review | True | 2026-07-01T05:05:24Z | True | 3989 |
| paper_trading_settings.md | review | True | 2026-07-01T05:05:24Z | True | 2286 |
| wallet_preflight.json | review | True | 2026-07-01T19:06:34Z | False | 3579 |
| wallet_preflight.md | review | True | 2026-07-01T19:06:34Z | False | 2015 |
| tiny_live_pilot.json | review | True | 2026-07-01T18:46:16Z | False | 62234 |
| tiny_live_pilot.md | review | True | 2026-07-01T18:46:16Z | False | 2642 |
| provider_monitor.json | operational | True | 2026-07-01T19:06:34Z | False | 3844 |
| provider_monitor.md | operational | True | 2026-07-01T19:06:34Z | False | 1181 |
