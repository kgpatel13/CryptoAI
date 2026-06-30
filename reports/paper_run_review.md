# CryptoAI Paper Run Review

Generated: `2026-06-30T08:03:43Z`

## Summary

- Overall status: `COLLECTING_PAPER_EVIDENCE`
- Recommendation: `Continue paper run until closed trade evidence exists.`
- Shadow decision: `BLOCKED`
- Live decision: `BLOCKED`
- Initial cash USD: `$500.0000`
- Cash USD: `$500.0000`
- Realized PnL USD: `$0.0000`
- Return %: `0.0000`
- Closed trades: `0`
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
| report_audit_clean | PASS | findings=0 |

## Findings

| Severity | Message |
|---|---|
| WATCH | No closed paper trades yet after fresh reset. |

## Notes

- Paper Run Review is evidence-only and never enables live trading.
- Paper profit is useful only when execution realism and pool-depth evidence also improve.
- Live trading remains blocked until explicit live-readiness controls are implemented and evidence supports them.
