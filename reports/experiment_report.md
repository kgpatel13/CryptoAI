# CryptoAI Experiment Report

Generated: `2026-06-30T02:09:57Z`

## Latest Experiment

- Experiment ID: `4dc404bddb51`
- Label: `default-replay-optimization`
- Status: `RESEARCH_ONLY`
- Promotion allowed: `False`
- Gates: `3 pass / 1 warn / 1 fail`
- History count: `1`

## Summary

- backtest_total_signals: `20`
- backtest_trades: `0`
- backtest_pnl_usd: `0.0000`
- optimization_scenarios: `60`
- optimization_best_trades: `20`
- optimization_best_pnl_usd: `57.0470`
- optimization_best_cost_buffer_pct: `0.20`
- provider_status: `OK`
- provider_alert_count: `0`
- paper_total_pnl_usd: `None`
- audit_finding_count: `0`
- execution_cost_buffer_status: `INSUFFICIENT_EVIDENCE`
- execution_cost_confidence: `INSUFFICIENT`
- observed_total_cost_lower_bound_pct: `None`
- market_primary_focus: `base WETH/USDC`
- market_active_focus_count: `0`
- market_blocked_count: `7`
- quote_active_pair_count: `1`
- quote_provider_gap_count: `6`
- quote_gap_count: `1`

## Replay Diagnostics

- production_cost_buffer_pct: `0.30`
- production_trade_count: `0`
- best_profitable_cost_buffer_pct: `0.20`
- best_profitable_trade_count: `20`
- best_profitable_total_pnl_usd: `57.0470`
- WATCH: Production buffer 0.30% has 20 positive-after-cost signal(s), but 0 pass the paper BUY threshold 0.30%.
- ACTION: Collect more execution-cost and closed-paper-trade evidence before considering any threshold change.

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
- active_focus_count: `0`
- research_target_count: `1`
- blocked_count: `7`
- provider_status: `OK`
- provider_alert_count: `0`
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
| default_replay_has_positive_trades | FAIL | Default replay did not produce positive production-buffer evidence. Default replay trades=0, pnl_usd=0. |
| optimization_has_minimum_sample | PASS | Best scenario trades=20, pnl_usd=57.0470, min_trades=5. |
| provider_health_not_critical | PASS | Provider status is OK. |
| paper_pnl_non_negative | WARN | Paper PnL is unavailable. |
| report_audit_has_no_findings | PASS | Report audit has no findings. |

## Recent Experiments

| Time | ID | Status | Pass | Warn | Fail |
|---|---|---|---:|---:|---:|
| 2026-06-30T02:09:57Z | 4dc404bddb51 | RESEARCH_ONLY | 3 | 1 | 1 |

## Notes

- Experiment tracking records research evidence only.
- promotion_allowed is always false until separate live-readiness gates are implemented and approved.
- A PAPER_EVIDENCE_CANDIDATE status is not live-trading approval.
