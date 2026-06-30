# CryptoAI Paper Run Review

Generated: `2026-06-30T23:16:54Z`

## Summary

- Overall status: `PAPER_PROFIT_NOT_SHADOW_READY`
- Recommendation: `Continue paper trading and improve pool-depth/execution realism before shadow review.`
- Shadow decision: `BLOCKED`
- Live decision: `BLOCKED`
- Initial cash USD: `$500.0000`
- Cash USD: `$539.0745`
- Realized PnL USD: `$39.0745`
- Return %: `7.8149`
- Closed trades: `942`
- Losing trades: `0`
- Open positions: `0`
- Provider status: `OK`
- Pool depth status: `DEPTH_EVIDENCE_READY`
- Execution realism: `NOT_SHADOW_READY` / `NONE`
- Live shadow gate: `NO_SHADOW_ELIGIBLE_TRADES`
- Live-shadow eligible trades: `0`
- Paper-only trades: `200`
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
| live_shadow_eligible | BLOCK | shadow_eligible=0; status=NO_SHADOW_ELIGIBLE_TRADES |
| report_audit_clean | PASS | blocking_findings=0; total_findings=25 |

## Findings

| Severity | Message |
|---|---|
| INFO | Paper run is profitable so far: $39.0745 across 942 closed trade(s). |
| ACTION | Execution realism has zero shadow-ready opportunities; live trading remains blocked. |
| ACTION | Live Shadow Gate has zero shadow-eligible paper trades; current paper PnL is paper-only evidence. |
| INFO | Report audit has 24 stale research finding(s); paper runtime gates are not blocked by research freshness. |
| SUMMARY | Blocked gates: execution_shadow_ready, live_shadow_eligible. |

## Notes

- Paper Run Review is evidence-only and never enables live trading.
- Paper profit is useful only when execution realism and pool-depth evidence also improve.
- Live trading remains blocked until explicit live-readiness controls are implemented and evidence supports them.
