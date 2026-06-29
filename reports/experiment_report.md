# CryptoAI Experiment Report

Generated: `2026-06-29T23:31:26Z`

## Latest Experiment

- Experiment ID: `e17d62fc9e0f`
- Label: `default-replay-optimization`
- Status: `WATCHLIST`
- Promotion allowed: `False`
- Gates: `4 pass / 1 warn / 0 fail`
- History count: `19`

## Summary

- backtest_total_signals: `195`
- backtest_trades: `5`
- backtest_pnl_usd: `19.1500`
- optimization_scenarios: `60`
- optimization_best_trades: `99`
- optimization_best_pnl_usd: `68.9755`
- optimization_best_cost_buffer_pct: `0.20`
- provider_status: `WATCH`
- provider_alert_count: `2`
- paper_total_pnl_usd: `2.8220`
- audit_finding_count: `0`
- execution_cost_buffer_status: `CONSERVATIVE`
- execution_cost_confidence: `LOW`
- observed_total_cost_lower_bound_pct: `0.1300`
- market_primary_focus: `base WETH/USDC`
- market_active_focus_count: `1`
- market_blocked_count: `7`
- quote_active_pair_count: `1`
- quote_provider_gap_count: `6`
- quote_gap_count: `1`

## Replay Diagnostics

- production_cost_buffer_pct: `0.30`
- production_trade_count: `5`
- best_profitable_cost_buffer_pct: `0.20`
- best_profitable_trade_count: `99`
- best_profitable_total_pnl_usd: `68.9755`
- OK: Production buffer 0.30% and paper BUY threshold 0.30% produced 5 replay trade(s).

## Execution Cost Evidence

- buffer_status: `CONSERVATIVE`
- confidence: `LOW`
- production_cost_buffer_pct: `0.30`
- observed_total_cost_lower_bound_pct: `0.1300`
- buffer_surplus_vs_lower_bound_pct: `0.1700`
- INFO: Production buffer assessment is CONSERVATIVE with LOW paper-cost confidence.
- ACTION: Collect more filled paper executions; current slippage sample is 6 and target is 30+.

## Market Universe Evidence

- primary_focus: `base WETH/USDC`
- active_focus_count: `1`
- research_target_count: `0`
- blocked_count: `7`
- provider_status: `WATCH`
- provider_alert_count: `2`
- INFO: Primary research focus is base WETH/USDC.
- ACTION: 7 configured pair(s) need quote-provider evidence before expansion.
- WATCH: Provider monitor remains WATCH with 2 alert(s).
- INFO: Production cost-buffer has positive-after-cost evidence, but paper BUY threshold evidence is still insufficient.

## Quote Coverage Evidence

- active_pair_count: `1`
- provider_gap_count: `6`
- quote_gap_count: `1`
- next_target: `base CBBTC/USDC`
- INFO: 1 configured pair(s) have active two-DEX quote evidence.
- ACTION: 7 configured pair(s) still need quote coverage before expansion.
- ACTION: Next targeted quote test: base CBBTC/USDC.
- WATCH: Provider monitor remains WATCH with 2 alert(s).

## Gates

| Gate | Status | Message |
|---|---|---|
| default_replay_has_positive_trades | PASS | Default replay trades=5, pnl_usd=19.1500. |
| optimization_has_minimum_sample | PASS | Best scenario trades=99, pnl_usd=68.9755, min_trades=5. |
| provider_health_not_critical | WARN | Provider status is WATCH with 2 alert(s). |
| paper_pnl_non_negative | PASS | Paper total_pnl_usd=2.8220. |
| report_audit_has_no_findings | PASS | Report audit has no findings. |

## Recent Experiments

| Time | ID | Status | Pass | Warn | Fail |
|---|---|---|---:|---:|---:|
| 2026-06-29T17:48:56Z | 47ebec9a0ff1 | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T18:01:22Z | 9d4ee66aa17c | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T18:03:26Z | 2f673ca40870 | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T18:04:59Z | d56ed9cd2945 | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T18:05:19Z | f4f2f7f812a9 | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T18:16:07Z | 338976846b29 | RESEARCH_ONLY | 2 | 2 | 1 |
| 2026-06-29T18:18:11Z | 82206b3eb776 | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T21:16:03Z | de3bc654289c | RESEARCH_ONLY | 2 | 2 | 1 |
| 2026-06-29T22:59:36Z | f236334b0ef6 | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T23:31:26Z | e17d62fc9e0f | WATCHLIST | 4 | 1 | 0 |

## Notes

- Experiment tracking records research evidence only.
- promotion_allowed is always false until separate live-readiness gates are implemented and approved.
- A PAPER_EVIDENCE_CANDIDATE status is not live-trading approval.
