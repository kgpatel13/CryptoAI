# CryptoAI Paper Run Review

Generated: `2026-06-30T17:53:09Z`

## Summary

- Overall status: `PAPER_PROFIT_NOT_SHADOW_READY`
- Recommendation: `Continue paper trading and improve pool-depth/execution realism before shadow review.`
- Shadow decision: `BLOCKED`
- Live decision: `BLOCKED`
- Initial cash USD: `$500.0000`
- Cash USD: `$504.9764`
- Realized PnL USD: `$4.9764`
- Return %: `0.9953`
- Closed trades: `31`
- Losing trades: `0`
- Open positions: `0`
- Provider status: `OK`
- Pool depth status: `DEPTH_EVIDENCE_READY`
- Execution realism: `NOT_SHADOW_READY` / `NONE`
- Report audit blocking findings: `0`
- Report audit research findings: `24`

## Gates

| Gate | Status | Message |
|---|---|---|
| pnl_reconciled | PASS | paper=RECONCILED; analytics=RECONCILED |
| no_open_positions | PASS | open_positions=0 |
| no_losing_closed_trades | PASS | losing_trades=0 |
| provider_ok | PASS | provider_status=OK |
| pool_depth_ready | PASS | depth_ready_routes=2; status=DEPTH_EVIDENCE_READY |
| execution_shadow_ready | BLOCK | shadow_ready=0; status=NOT_SHADOW_READY |
| report_audit_clean | PASS | blocking_findings=0; total_findings=25 |

## Findings

| Severity | Message |
|---|---|
| INFO | Paper run is profitable so far: $4.9764 across 31 closed trade(s). |
| ACTION | Execution realism has zero shadow-ready opportunities; live trading remains blocked. |
| INFO | Report audit has 24 stale research finding(s); paper runtime gates are not blocked by research freshness. |
| SUMMARY | Blocked gates: execution_shadow_ready. |

## Notes

- Paper Run Review is evidence-only and never enables live trading.
- Paper profit is useful only when execution realism and pool-depth evidence also improve.
- Live trading remains blocked until explicit live-readiness controls are implemented and evidence supports them.
