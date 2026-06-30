# Wallet Preflight Report

Generated: `2026-06-30T19:36:37Z`
- Overall status: `WALLET_PREP_ACTION`
- Wallet preflight allowed: `False`
- Live trading approval: `False`
- Planned chain: `base`
- Planned USDC USD: `$450.0000`
- Planned ETH gas USD: `$50.0000`
- Planned total USD: `$500.0000`
- Blocked checks: `0`
- Action checks: `5`

## Checks

| Check | Status | Detail |
|---|---|---|
| live_trading_disabled | PASS | Live trading feature flag is disabled. |
| kill_switch_enabled | PASS | Live kill switch is enabled. |
| private_key_absent | PASS | No private key is configured. |
| isolated_wallet_address | ACTION | Configure the isolated live wallet public address before funding. |
| wallet_isolation | ACTION | Live wallet must be separate from the main wallet. |
| planned_chain_base | PASS | Planned chain is Base. |
| chain_allowlist_base | PASS | Live chain allowlist is restricted to Base. |
| token_allowlist_usdc_weth | PASS | Live token allowlist includes USDC and WETH. |
| planned_wallet_ceiling | PASS | Planned funding is within the $500 tiny-pilot ceiling. |
| planned_gas_budget | PASS | Planned ETH gas budget is within preparation range. |
| configured_wallet_ceiling | ACTION | Set CRYPTOAI_MAX_LIVE_WALLET_USD to a value > 0 and <= 500 before any live pilot. |
| configured_trade_cap | ACTION | Set CRYPTOAI_MAX_LIVE_TRADE_USD to a small value, usually $25-$50, before any live pilot. |
| configured_daily_loss | ACTION | Set CRYPTOAI_MAX_DAILY_LOSS_USD to a value > $0 and no larger than the live trade cap. |
| manual_confirmation_required | PASS | Manual confirmation is required. |
| transaction_simulation_required | PASS | Transaction simulation is required. |

## Notes

- Wallet Preflight is preparation-only and never approves live trading.
- Do not configure private keys until the transaction path, simulation gate, and manual review are complete.
- The first real-money pilot should use an isolated wallet on Base with a total wallet ceiling of $500 or less.
