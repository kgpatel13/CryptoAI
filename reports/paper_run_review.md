# CryptoAI Paper Run Review

Generated: `2026-07-01T06:07:58Z`

## Summary

- Overall status: `SHADOW_REVIEW_CANDIDATE`
- Recommendation: `Review sustained paper evidence before any live-trading design decision.`
- Shadow decision: `REVIEW_READY`
- Live decision: `BLOCKED`
- Initial cash USD: `$500.0000`
- Cash USD: `$894.5618`
- Realized PnL USD: `$394.5618`
- Return %: `78.9124`
- Closed trades: `1139`
- Losing trades: `0`
- Open positions: `0`
- Provider status: `OK`
- Pool depth status: `DEPTH_EVIDENCE_READY`
- Execution realism: `SHADOW_REVIEW_READY` / `MEDIUM`
- Live shadow gate: `SHADOW_ELIGIBLE_EVIDENCE`
- Live-shadow eligible trades: `18`
- Paper-only trades: `182`
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
| execution_shadow_ready | PASS | shadow_ready=1; status=SHADOW_REVIEW_READY |
| live_shadow_eligible | PASS | shadow_eligible=18; status=SHADOW_ELIGIBLE_EVIDENCE |
| report_audit_clean | PASS | blocking_findings=0; total_findings=26 |

## Findings

| Severity | Message |
|---|---|
| INFO | Paper run is profitable so far: $394.5618 across 1139 closed trade(s). |
| INFO | Report audit has 24 stale research finding(s); paper runtime gates are not blocked by research freshness. |

## Notes

- Paper Run Review is evidence-only and never enables live trading.
- Paper profit is useful only when execution realism and pool-depth evidence also improve.
- Live trading remains blocked until explicit live-readiness controls are implemented and evidence supports them.
