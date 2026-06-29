# CryptoAI Experiment Report

Generated: `2026-06-29T12:58:10Z`

## Latest Experiment

- Experiment ID: `8ecb1e84cc66`
- Label: `default-replay-optimization`
- Status: `RESEARCH_ONLY`
- Promotion allowed: `False`
- Gates: `2 pass / 1 warn / 2 fail`
- History count: `2`

## Summary

- backtest_total_signals: `37`
- backtest_trades: `0`
- backtest_pnl_usd: `0.0000`
- optimization_scenarios: `48`
- optimization_best_trades: `15`
- optimization_best_pnl_usd: `7.6008`
- optimization_best_cost_buffer_pct: `0.20`
- provider_status: `CRITICAL`
- provider_alert_count: `4`
- paper_total_pnl_usd: `1.3939`
- audit_finding_count: `2`

## Gates

| Gate | Status | Message |
|---|---|---|
| default_replay_has_positive_trades | FAIL | Default replay did not produce positive production-buffer evidence. Default replay trades=0, pnl_usd=0. |
| optimization_has_minimum_sample | PASS | Best scenario trades=15, pnl_usd=7.6008, min_trades=5. |
| provider_health_not_critical | FAIL | Provider status is CRITICAL with 4 alert(s). |
| paper_pnl_non_negative | PASS | Paper total_pnl_usd=1.3939. |
| report_audit_has_no_findings | WARN | Report audit has 2 finding(s). Review before tuning. |

## Recent Experiments

| Time | ID | Status | Pass | Warn | Fail |
|---|---|---|---:|---:|---:|
| 2026-06-29T12:56:41Z | 2c3933e93ba2 | RESEARCH_ONLY | 2 | 1 | 2 |
| 2026-06-29T12:58:10Z | 8ecb1e84cc66 | RESEARCH_ONLY | 2 | 1 | 2 |

## Notes

- Experiment tracking records research evidence only.
- promotion_allowed is always false until separate live-readiness gates are implemented and approved.
- A PAPER_EVIDENCE_CANDIDATE status is not live-trading approval.
