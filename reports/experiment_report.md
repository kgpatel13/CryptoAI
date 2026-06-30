# CryptoAI Experiment Report

Generated: `2026-06-30T07:46:44Z`

## Latest Experiment

- Experiment ID: `f3192caaf9a2`
- Label: `default-replay-optimization`
- Status: `WATCHLIST`
- Promotion allowed: `False`
- Gates: `4 pass / 1 warn / 0 fail`
- History count: `1`

## Summary

- backtest_total_signals: `930`
- backtest_trades: `410`
- backtest_pnl_usd: `1390.8106`
- optimization_scenarios: `60`
- optimization_best_trades: `930`
- optimization_best_pnl_usd: `2657.3781`
- optimization_best_cost_buffer_pct: `0.20`
- provider_status: `OK`
- provider_alert_count: `0`
- paper_total_pnl_usd: `370.8424`
- audit_finding_count: `27`
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
- production_trade_count: `410`
- best_profitable_cost_buffer_pct: `0.20`
- best_profitable_trade_count: `932`
- best_profitable_total_pnl_usd: `2663.1442`
- OK: Production buffer 0.30% and paper BUY threshold 0.30% produced 410 replay trade(s).

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
| default_replay_has_positive_trades | PASS | Default replay trades=410, pnl_usd=1390.8106. |
| optimization_has_minimum_sample | PASS | Best scenario trades=930, pnl_usd=2657.3781, min_trades=5. |
| provider_health_not_critical | PASS | Provider status is OK. |
| paper_pnl_non_negative | PASS | Paper total_pnl_usd=370.8424. |
| report_audit_has_no_findings | WARN | Report audit has 27 finding(s). Review before tuning. |

## Recent Experiments

| Time | ID | Status | Pass | Warn | Fail |
|---|---|---|---:|---:|---:|
| 2026-06-30T07:46:44Z | f3192caaf9a2 | WATCHLIST | 4 | 1 | 0 |

## Notes

- Experiment tracking records research evidence only.
- promotion_allowed is always false until separate live-readiness gates are implemented and approved.
- A PAPER_EVIDENCE_CANDIDATE status is not live-trading approval.
