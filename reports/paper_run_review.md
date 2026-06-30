# CryptoAI Paper Run Review

Generated: `2026-06-30T07:47:20Z`

## Summary

- Overall status: `PAPER_PROFIT_NOT_SHADOW_READY`
- Recommendation: `Continue paper trading and improve pool-depth/execution realism before shadow review.`
- Shadow decision: `BLOCKED`
- Live decision: `BLOCKED`
- Initial cash USD: `$1000.0000`
- Cash USD: `$1370.8424`
- Realized PnL USD: `$370.8424`
- Return %: `37.0842`
- Closed trades: `93`
- Losing trades: `0`
- Open positions: `0`
- Provider status: `OK`
- Pool depth status: `DEPTH_EVIDENCE_WATCH`
- Execution realism: `NOT_SHADOW_READY` / `LOW`

## Gates

| Gate | Status | Message |
|---|---|---|
| pnl_reconciled | PASS | paper=RECONCILED; analytics=RECONCILED |
| no_open_positions | PASS | open_positions=0 |
| no_losing_closed_trades | PASS | losing_trades=0 |
| provider_ok | PASS | provider_status=OK |
| pool_depth_ready | BLOCK | depth_ready_routes=0; status=DEPTH_EVIDENCE_WATCH |
| execution_shadow_ready | BLOCK | shadow_ready=0; status=NOT_SHADOW_READY |
| report_audit_clean | PASS | findings=0 |

## Findings

| Severity | Message |
|---|---|
| INFO | Paper run is profitable so far: $370.8424 across 93 closed trade(s). |
| WATCH | High early return with a small trade sample; treat as paper-only until more evidence accumulates. |
| ACTION | Pool-depth ladder has zero depth-ready routes; paper profit is not executable-size evidence yet. |
| ACTION | Execution realism has zero shadow-ready opportunities; live trading remains blocked. |
| SUMMARY | Blocked gates: pool_depth_ready, execution_shadow_ready. |

## Notes

- Paper Run Review is evidence-only and never enables live trading.
- Paper profit is useful only when execution realism and pool-depth evidence also improve.
- Live trading remains blocked until explicit live-readiness controls are implemented and evidence supports them.
