# CryptoAI Experiment Report

Generated: `2026-06-29T14:15:00Z`

## Latest Experiment

- Experiment ID: `17711d33a07b`
- Label: `default-replay-optimization`
- Status: `RESEARCH_ONLY`
- Promotion allowed: `False`
- Gates: `3 pass / 1 warn / 1 fail`
- History count: `7`

## Summary

- backtest_total_signals: `79`
- backtest_trades: `0`
- backtest_pnl_usd: `0.0000`
- optimization_scenarios: `48`
- optimization_best_trades: `36`
- optimization_best_pnl_usd: `13.1480`
- optimization_best_cost_buffer_pct: `0.20`
- provider_status: `WATCH`
- provider_alert_count: `2`
- paper_total_pnl_usd: `2.8220`
- audit_finding_count: `0`

## Replay Diagnostics

- production_cost_buffer_pct: `0.30`
- production_trade_count: `0`
- best_profitable_cost_buffer_pct: `0.20`
- best_profitable_trade_count: `36`
- best_profitable_total_pnl_usd: `13.1480`
- WATCH: Production buffer 0.30% produced 0 trades; buffer 0.20% produced 36 trade(s).
- ACTION: Collect execution-cost evidence before considering any lower paper threshold.

## Gates

| Gate | Status | Message |
|---|---|---|
| default_replay_has_positive_trades | FAIL | Default replay did not produce positive production-buffer evidence. Default replay trades=0, pnl_usd=0. |
| optimization_has_minimum_sample | PASS | Best scenario trades=36, pnl_usd=13.1480, min_trades=5. |
| provider_health_not_critical | WARN | Provider status is WATCH with 2 alert(s). |
| paper_pnl_non_negative | PASS | Paper total_pnl_usd=2.8220. |
| report_audit_has_no_findings | PASS | Report audit has no findings. |

## Recent Experiments

| Time | ID | Status | Pass | Warn | Fail |
|---|---|---|---:|---:|---:|
| 2026-06-29T12:56:41Z | 2c3933e93ba2 | RESEARCH_ONLY | 2 | 1 | 2 |
| 2026-06-29T12:58:10Z | 8ecb1e84cc66 | RESEARCH_ONLY | 2 | 1 | 2 |
| 2026-06-29T13:25:42Z | 6da896c5d39b | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T14:07:59Z | 56a7c49964ba | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T14:08:45Z | 0bee65006c9d | RESEARCH_ONLY | 2 | 2 | 1 |
| 2026-06-29T14:12:38Z | 745bcc6fd902 | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-29T14:15:00Z | 17711d33a07b | RESEARCH_ONLY | 3 | 1 | 1 |

## Notes

- Experiment tracking records research evidence only.
- promotion_allowed is always false until separate live-readiness gates are implemented and approved.
- A PAPER_EVIDENCE_CANDIDATE status is not live-trading approval.
