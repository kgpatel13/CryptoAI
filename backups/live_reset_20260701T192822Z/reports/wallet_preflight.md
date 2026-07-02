# Wallet Preflight Report

Generated: `2026-07-01T19:24:23Z`
- Overall status: `WALLET_PREP_ACTION`
- Wallet preflight allowed: `False`
- Live trading approval: `False`
- Planned chain: `base`
- Planned USDC USD: `$450.0000`
- Planned ETH gas USD: `$50.0000`
- Planned total USD: `$500.0000`
- Blocked checks: `3`
- Action checks: `0`

## Checks

| Check | Status | Detail |
|---|---|---|
| live_trading_disabled | BLOCK | Live trading feature flag must stay disabled during wallet preparation. |
| kill_switch_enabled | BLOCK | Live kill switch must stay enabled during wallet preparation. |
| private_key_absent | BLOCK | Private key is configured; remove it during preflight preparation. |
| isolated_wallet_address | PASS | Isolated live wallet public address is configured. |
| wallet_isolation | PASS | Live wallet is separate from the main wallet. |
| planned_chain_base | PASS | Planned chain is Base. |
| chain_allowlist_base | PASS | Live chain allowlist is restricted to Base. |
| token_allowlist_usdc_weth | PASS | Live token allowlist includes USDC and WETH. |
| planned_wallet_ceiling | PASS | Planned funding is within the $500 tiny-pilot ceiling. |
| planned_gas_budget | PASS | Planned ETH gas budget is within preparation range. |
| configured_wallet_ceiling | PASS | Configured wallet ceiling is within tiny-pilot policy. |
| configured_trade_cap | PASS | Configured trade cap is within tiny-pilot policy. |
| configured_daily_loss | PASS | Configured daily loss cap is within tiny-pilot policy. |
| manual_confirmation_required | PASS | Manual confirmation is required. |
| transaction_simulation_required | PASS | Transaction simulation is required. |

## Notes

- Wallet Preflight is preparation-only and never approves live trading.
- Do not configure private keys until the transaction path, simulation gate, and manual review are complete.
- The first real-money pilot should use an isolated wallet on Base with a total wallet ceiling of $500 or less.
