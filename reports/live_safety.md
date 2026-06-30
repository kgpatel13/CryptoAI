# Live Safety Report

Generated: `2026-06-30T22:45:45Z`
- Overall status: `LIVE_BLOCKED`
- Guard allowed: `False`
- Guard reason: `Live trading feature flag is disabled.`
- Max live wallet USD: `500`
- Max live trade USD: `20`
- Max daily loss USD: `5`
- Blocked checks: `8` / `20`

## Checks

| Check | Status | Detail |
|---|---|---|
| live_feature_flag | BLOCK | Live trading feature flag is disabled. |
| kill_switch | BLOCK | Live kill switch is ON. |
| private_key | BLOCK | No private key is configured. Live trading remains blocked. |
| isolated_wallet_address | PASS | Isolated live wallet address is configured. |
| wallet_isolation | PASS | Live wallet is isolated from the configured main wallet. |
| wallet_ceiling | PASS | Max live wallet ceiling is within tiny-pilot policy. |
| trade_cap | PASS | Max live trade size is within tiny-pilot policy. |
| daily_loss_cap | PASS | Max daily loss cap is configured. |
| manual_confirmation | BLOCK | Manual confirmation is required; autonomous live execution is blocked. |
| chain_allowlist | PASS | Live chain allowlist is restricted to approved chains. |
| dex_allowlist | PASS | Live DEX allowlist is restricted to approved DEXs. |
| token_allowlist | PASS | Live token allowlist is restricted to approved tokens. |
| transaction_simulation | BLOCK | Transaction simulation is required and has not passed. |
| paper_shadow_review | BLOCK | Paper run is not yet ready for shadow review. |
| paper_closed_trades | PASS | Fresh paper run has enough closed trades. |
| execution_cost_confidence | BLOCK | Execution-cost confidence is MEDIUM; required HIGH. |
| execution_cost_samples | PASS | Execution-cost evidence has enough paper samples. |
| provider_health | PASS | Provider monitor is OK. |
| report_audit | PASS | Report audit has no blocking operational findings. |
| execution_realism | BLOCK | Execution realism must have shadow-ready evidence and zero live-ready approvals. |

## Notes

- Live Safety is a design and evidence gate only; it does not send transactions.
- The current platform remains paper/shadow only.
- The first real-money pilot should use a dedicated wallet with $500 or less total capital and a smaller per-trade cap.
