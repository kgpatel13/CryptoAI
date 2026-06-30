# CryptoAI Paper Run Review

Generated: `2026-06-30T15:22:41Z`

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
- Execution realism: `NO_OPPORTUNITIES` / `NONE`
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
| execution_shadow_ready | BLOCK | shadow_ready=0; status=NO_OPPORTUNITIES |
| report_audit_clean | PASS | blocking_findings=0; total_findings=25 |

## Findings

| Severity | Message |
|---|---|
| WATCH | No closed paper trades yet after fresh reset. |
| ACTION | Execution realism has zero shadow-ready opportunities; live trading remains blocked. |
| INFO | Report audit has 24 stale research finding(s); paper runtime gates are not blocked by research freshness. |
| SUMMARY | Blocked gates: execution_shadow_ready. |

## Notes

- Paper Run Review is evidence-only and never enables live trading.
- Paper profit is useful only when execution realism and pool-depth evidence also improve.
- Live trading remains blocked until explicit live-readiness controls are implemented and evidence supports them.
