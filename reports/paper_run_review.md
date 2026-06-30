# CryptoAI Paper Run Review

Generated: `2026-06-30T08:24:31Z`

## Summary

- Overall status: `OPERATIONS_REVIEW`
- Recommendation: `Refresh operational evidence before shadow review.`
- Shadow decision: `BLOCKED`
- Live decision: `BLOCKED`
- Initial cash USD: `$500.0000`
- Cash USD: `$598.7553`
- Realized PnL USD: `$98.7553`
- Return %: `19.7511`
- Closed trades: `53`
- Losing trades: `0`
- Open positions: `0`
- Provider status: `OK`
- Pool depth status: `DEPTH_EVIDENCE_READY`
- Execution realism: `SHADOW_REVIEW_READY` / `MEDIUM`

## Gates

| Gate | Status | Message |
|---|---|---|
| pnl_reconciled | PASS | paper=RECONCILED; analytics=RECONCILED |
| no_open_positions | PASS | open_positions=0 |
| no_losing_closed_trades | PASS | losing_trades=0 |
| provider_ok | PASS | provider_status=OK |
| pool_depth_ready | PASS | depth_ready_routes=2; status=DEPTH_EVIDENCE_READY |
| execution_shadow_ready | PASS | shadow_ready=1; status=SHADOW_REVIEW_READY |
| report_audit_clean | BLOCK | findings=25 |

## Findings

| Severity | Message |
|---|---|
| INFO | Paper run is profitable so far: $98.7553 across 53 closed trade(s). |
| WATCH | High early return with a small trade sample; treat as paper-only until more evidence accumulates. |
| WATCH | Report audit has 25 finding(s); refresh missing/stale research reports as needed. |
| SUMMARY | Blocked gates: report_audit_clean. |

## Notes

- Paper Run Review is evidence-only and never enables live trading.
- Paper profit is useful only when execution realism and pool-depth evidence also improve.
- Live trading remains blocked until explicit live-readiness controls are implemented and evidence supports them.
