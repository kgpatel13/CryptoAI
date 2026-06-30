# CryptoAI v5.14 - Operational Evidence Gate Split

## Summary

v5.14 separates runtime-critical operational evidence from slower-moving research reports.

Paper/shadow review now stays focused on current accounting, provider health, execution realism, pool depth, and cost evidence. Stale research reports remain visible, but they no longer make a healthy paper run look operationally broken.

This release does not enable live trading, change paper BUY thresholds, change cost buffers, or relax trade-size caps.

## Changed

- Added report audit categories for operational, review, and research reports.
- Added `blocking_finding_count`, `operational_finding_count`, and `research_finding_count` to Report Audit.
- Updated Paper Run Review to block on operational findings instead of all stale research findings.
- Updated Live Safety evidence checks to use blocking operational findings while preserving hard wallet, kill-switch, and transaction-simulation gates.
- Reordered paper autopilot report generation so Report Audit refreshes before Paper Run Review consumes it.
- Reclassified paper settings as a configuration snapshot so stale timestamps remain visible without blocking paper/shadow review.

## Still Locked

- Live trading remains disabled by default.
- The live kill switch remains enabled by default.
- Real-money execution still requires wallet isolation, tiny trade caps, daily loss caps, transaction simulation, and manual review.
- `REVIEW_READY` is not live approval.

## Next

- Continue 24/7 paper trading after restarting the autopilot process so it loads this release.
- Watch execution realism and pool-depth status over multiple market windows.
- Do not fund more than the isolated tiny-pilot wallet ceiling when preparing for future live testing.
