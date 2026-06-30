# CryptoAI Paper Run Review

Generated: `2026-06-30T07:52:23Z`

## Summary

- Overall status: `SHADOW_REVIEW_CANDIDATE`
- Recommendation: `Review sustained paper evidence before any live-trading design decision.`
- Shadow decision: `REVIEW_READY`
- Live decision: `BLOCKED`
- Initial cash USD: `$1000.0000`
- Cash USD: `$1422.5483`
- Realized PnL USD: `$422.5483`
- Return %: `42.2548`
- Closed trades: `105`
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
| execution_shadow_ready | PASS | shadow_ready=2; status=SHADOW_REVIEW_READY |
| report_audit_clean | PASS | findings=0 |

## Findings

| Severity | Message |
|---|---|
| INFO | Paper run is profitable so far: $422.5483 across 105 closed trade(s). |

## Notes

- Paper Run Review is evidence-only and never enables live trading.
- Paper profit is useful only when execution realism and pool-depth evidence also improve.
- Live trading remains blocked until explicit live-readiness controls are implemented and evidence supports them.
