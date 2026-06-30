# CryptoAI Experiment Report

Generated: `2026-06-30T03:09:38Z`

## Latest Experiment

- Experiment ID: `f4d057e9b4c9`
- Label: `default-replay-optimization`
- Status: `WATCHLIST`
- Promotion allowed: `False`
- Gates: `4 pass / 1 warn / 0 fail`
- History count: `3`

## Summary

- backtest_total_signals: `1000`
- backtest_trades: `391`
- backtest_pnl_usd: `1270.8025`
- optimization_scenarios: `60`
- optimization_best_trades: `1000`
- optimization_best_pnl_usd: `2852.5283`
- optimization_best_cost_buffer_pct: `0.20`
- provider_status: `OK`
- provider_alert_count: `0`
- paper_total_pnl_usd: `308.9559`
- audit_finding_count: `21`
- execution_cost_buffer_status: `INSUFFICIENT_EVIDENCE`
- execution_cost_confidence: `INSUFFICIENT`
- observed_total_cost_lower_bound_pct: `None`
- market_primary_focus: `base WETH/USDC`
- market_active_focus_count: `1`
- market_blocked_count: `7`
- quote_active_pair_count: `1`
- quote_provider_gap_count: `6`
- quote_gap_count: `1`

## Replay Diagnostics

- production_cost_buffer_pct: `0.30`
- production_trade_count: `391`
- best_profitable_cost_buffer_pct: `0.20`
- best_profitable_trade_count: `1000`
- best_profitable_total_pnl_usd: `2852.5283`
- OK: Production buffer 0.30% and paper BUY threshold 0.30% produced 391 replay trade(s).

## Execution Cost Evidence

- buffer_status: `INSUFFICIENT_EVIDENCE`
- confidence: `INSUFFICIENT`
- production_cost_buffer_pct: `0.30`
- observed_total_cost_lower_bound_pct: `None`
- buffer_surplus_vs_lower_bound_pct: `None`
- WATCH: Production buffer assessment is INSUFFICIENT_EVIDENCE with INSUFFICIENT paper-cost confidence.
- ACTION: Collect more filled paper executions; current slippage sample is 0 and target is 30+.

## Market Universe Evidence

- primary_focus: `base WETH/USDC`
- active_focus_count: `1`
- research_target_count: `0`
- blocked_count: `7`
- provider_status: `OK`
- provider_alert_count: `0`
- INFO: Primary research focus is base WETH/USDC.
- ACTION: 7 configured pair(s) need quote-provider evidence before expansion.
- INFO: Production cost-buffer has positive-after-cost evidence, but paper BUY threshold evidence is still insufficient.

## Quote Coverage Evidence

- active_pair_count: `1`
- provider_gap_count: `6`
- quote_gap_count: `1`
- next_target: `base CBBTC/USDC`
- INFO: 1 configured pair(s) have active two-DEX quote evidence.
- ACTION: 7 configured pair(s) still need quote coverage before expansion.
- ACTION: Next targeted quote test: base CBBTC/USDC.

## Gates

| Gate | Status | Message |
|---|---|---|
| default_replay_has_positive_trades | PASS | Default replay trades=391, pnl_usd=1270.8025. |
| optimization_has_minimum_sample | PASS | Best scenario trades=1000, pnl_usd=2852.5283, min_trades=5. |
| provider_health_not_critical | PASS | Provider status is OK. |
| paper_pnl_non_negative | PASS | Paper total_pnl_usd=308.9559. |
| report_audit_has_no_findings | WARN | Report audit has 21 finding(s). Review before tuning. |

## Recent Experiments

| Time | ID | Status | Pass | Warn | Fail |
|---|---|---|---:|---:|---:|
| 2026-06-30T02:31:34Z | b767cf7aa548 | RESEARCH_ONLY | 3 | 1 | 1 |
| 2026-06-30T02:31:59Z | 0a281674b47f | RESEARCH_ONLY | 4 | 0 | 1 |
| 2026-06-30T03:09:38Z | f4d057e9b4c9 | WATCHLIST | 4 | 1 | 0 |

## Notes

- Experiment tracking records research evidence only.
- promotion_allowed is always false until separate live-readiness gates are implemented and approved.
- A PAPER_EVIDENCE_CANDIDATE status is not live-trading approval.
