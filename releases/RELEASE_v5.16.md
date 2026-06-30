# CryptoAI v5.16 - Live Readiness Checklist and Paper Parity Profile

## Summary

v5.16 adds a single pre-live readiness checklist and a stricter paper profile for testing with the same hard limits planned for the first tiny-live pilot.

Paper trading can never exactly reproduce real execution. It cannot fully model failed transactions, nonce issues, RPC outages, mempool ordering, gas spikes, MEV, wallet signing, or pool movement between quote and swap. This release makes that explicit while forcing the paper profile to match the intended live wallet, trade-size, loss, chain, route, and audit constraints.

This release does not enable live trading, store private keys, sign transactions, or send orders.

## Added

- `LiveReadinessChecklistService` for a consolidated pre-live checklist.
- `reports/live_readiness_checklist.json` and `reports/live_readiness_checklist.md`.
- Risk & Controls dashboard action for generating the checklist.
- Reports tab integration for Wallet Preflight and Live Readiness Checklist.
- Report Audit coverage for live readiness checklist outputs.
- `live_parity_500` paper settings profile:
  - `$500` paper wallet ceiling,
  - `$50` max paper trade,
  - `$10` paper daily loss cap,
  - Base ETH routes only,
  - continuous scanning,
  - `0.30%` paper BUY threshold,
  - `HIGH` execution-cost confidence requirement.

## Checklist Areas

- stable paper trading,
- reconciled accounting and PnL,
- atomic arbitrage execution,
- provider health,
- execution-cost evidence,
- execution realism,
- report audit cleanliness,
- audit trail and tax/export evidence,
- wallet preflight,
- live safety still blocked,
- paper/live wallet and trade-cap parity.

## Still Locked

- Live trading remains disabled.
- Live kill switch remains ON during readiness review.
- Private keys remain absent during readiness review.
- `LIVE_REVIEW_READY` is not live approval.

## Next

- Apply the `live_parity_500` paper profile.
- Run paper trading again under `$50` max trade and `$10` daily loss cap.
- Review the Live Readiness Checklist after enough live-parity paper evidence accumulates.
