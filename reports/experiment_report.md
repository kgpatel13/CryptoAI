# CryptoAI Experiment Report

Generated: `2026-06-29T18:05:19Z`

## Latest Experiment

- Experiment ID: `f4f2f7f812a9`
- Label: `default-replay-optimization`
- Status: `RESEARCH_ONLY`
- Promotion allowed: `False`
- Gates: `3 pass / 1 warn / 1 fail`
- History count: `14`

## Summary

- backtest_total_signals: `105`
- backtest_trades: `0`
- backtest_pnl_usd: `0.0000`
- optimization_scenarios: `60`
- optimization_best_trades: `49`
- optimization_best_pnl_usd: `20.1128`
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

## Replay Diagnostics

- production_cost_buffer_pct: `0.30`
- production_trade_count: `0`
- best_profitable_cost_buffer_pct: `0.20`
- best_profitable_trade_count: `49`
- best_profitable_total_pnl_usd: `20.1128`
- WATCH: Production buffer 0.30% has 1 positive-after-cost signal(s), but 0 pass the paper BUY threshold 0.30%.
- ACTION: Collect more execution-cost and closed-paper-trade evidence before considering any threshold change.

## Execution Cost Evidence

- buffer_status: `CONSERVATIVE`
- confidence: `LOW`
- production_cost_buffer_pct: `0.30`
- observed_total_cost_lower_bound_pct: `0.1300`
- buffer_surplus_vs_lower_bound_pct: `0.1700`
- INFO: Production buffer assessment is CONSERVATIVE with LOW paper-cost confidence.
- ACTION: Collect more filled paper executions; current slippage sample is 6 and target is 30+.
- WATCH: Replay has trades under measured lower-bound costs but none under the production buffer; do not lower thresholds until gas, fee, and slippage evidence is stronger.

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

## Gates

| Gate | Status | Message |
|---|---|---|
| default_replay_has_positive_trades | FAIL | Default replay did not produce positive production-buffer evidence. Default replay trades=0, pnl_usd=0. |
| optimization_has_minimum_sample | PASS | Best scenario trades=49, pnl_usd=20.1128, min_trades=5. |
| provider_health_not_critical | WARN | Provider status is WATCH with 2 alert(s). |
| paper_pnl_non_negative | PASS | Paper total_pnl_usd=2.8220. |
| report_audit_has_no_findings | PASS | Report audit has no findings. |

## Recent Experiments

| Time | ID | Status | Pass | Warn | Fail |
|---|---|---|---:|---:|---:|
| 2026-06-29T14:08:45Z | 0bee65006c9d | RESEARCH_ONLY | 2 | 2 | 1 |
| 2026-06-29T14:12:38Z | 745bcc6fd902 | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T14:15:00Z | 17711d33a07b | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T17:44:52Z | d73ce71a262a | RESEARCH_ONLY | 2 | 2 | 1 |
| 2026-06-29T17:45:21Z | 6dec8e85e081 | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T17:48:56Z | 47ebec9a0ff1 | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T18:01:22Z | 9d4ee66aa17c | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T18:03:26Z | 2f673ca40870 | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T18:04:59Z | d56ed9cd2945 | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T18:05:19Z | f4f2f7f812a9 | RESEARCH_ONLY | 3 | 1 | 1 |

## Notes

- Experiment tracking records research evidence only.
- promotion_allowed is always false until separate live-readiness gates are implemented and approved.
- A PAPER_EVIDENCE_CANDIDATE status is not live-trading approval.
