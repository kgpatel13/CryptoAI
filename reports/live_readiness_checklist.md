# Live Readiness Checklist

Generated: `2026-06-30T22:41:15Z`
- Overall status: `LIVE_REVIEW_NOT_READY`
- Live review ready: `False`
- Live trading approval: `False`
- Paper profile: `live_parity_500`
- Closed paper trades: `883`
- Paper cash USD: `$534.5250`
- Paper realized PnL USD: `$34.5250`
- Max live wallet USD: `$0`
- Max live trade USD: `$0`
- Max daily loss USD: `$5`
- Blocked checks: `1`
- Action checks: `8`
- Watch checks: `0`

## Checks

| Check | Status | Detail |
|---|---|---|
| stable_paper_trading | PASS | Closed paper trade sample meets the configured minimum. |
| paper_shadow_review_ready | ACTION | Paper Run Review must reach REVIEW_READY before live-pilot review. |
| paper_pnl_reconciled | PASS | Paper report and portfolio analytics PnL are reconciled. |
| no_open_positions | PASS | No open paper positions. |
| execution_engine_atomic | PASS | Recent paper fills are atomic arbitrage round trips. |
| risk_engine_validated | PASS | Risk engine evidence is present and losing-trade count is clean. |
| provider_health_ok | BLOCK | Provider Monitor must be OK. |
| execution_cost_confidence | ACTION | Execution-cost evidence confidence must be HIGH. |
| execution_realism_shadow_ready | ACTION | Execution realism must have shadow-ready evidence and zero live-ready approvals. |
| report_audit_clean | PASS | Report Audit has no blocking operational findings. |
| audit_trail_available | PASS | Paper orders and analytics trade journal are available. |
| transaction_tax_export_available | PASS | Trade journal/export evidence is available for tax/accounting records. |
| wallet_preflight_ready | ACTION | Wallet Preflight must be ready with an isolated public wallet and tiny-pilot caps. |
| transaction_simulation_passed | ACTION | Transaction Simulation must pass exact calldata and eth_call checks before live review. |
| live_safety_blocked | PASS | Live Safety remains blocked during readiness review. |
| live_feature_off | PASS | Live feature flag is off. |
| kill_switch_on | PASS | Live and paper kill switches are on. |
| private_key_absent | PASS | Private key is absent. |
| paper_live_wallet_parity | ACTION | Paper capital should be > $0 and no larger than the configured live wallet ceiling. |
| paper_live_trade_cap_parity | ACTION | Paper max notional and observed fills should be no larger than the configured live trade cap. |
| paper_live_daily_loss_parity | ACTION | Paper daily loss cap should be > $0 and no larger than the configured live daily loss cap. |
| base_eth_scope_only | PASS | Readiness review is restricted to Base ETH approved routes. |

## Notes

- Live Readiness Checklist is a human review gate and never enables live trading.
- Paper can use the same limits as the intended tiny-live pilot, but it cannot exactly reproduce gas spikes, failed transactions, MEV, mempool ordering, RPC outages, nonce issues, wallet signing, or pool movement between legs.
- Use a live-parity paper profile before tiny real-money testing: wallet ceiling <= $500, per-trade cap <= tiny-live cap, daily loss cap > $0, Base only, USDC/WETH only.
