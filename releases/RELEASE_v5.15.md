# CryptoAI v5.15 - Isolated Wallet Preflight

## Summary

v5.15 adds a preparation-only wallet preflight report for the future tiny-live pilot.

The report validates the intended isolated wallet setup, Base-only scope, USDC/WETH token scope, planned `$450 USDC + $50 ETH gas` funding envelope, and required safety configuration before any private key or transaction path is introduced.

This release does not enable live trading, store private keys, sign transactions, simulate swaps, or send orders.

## Added

- `WalletPreflightService` for preparation-only wallet readiness checks.
- `reports/wallet_preflight.json` and `reports/wallet_preflight.md`.
- Risk & Controls dashboard action to generate Wallet Preflight.
- Report Audit coverage for wallet preflight outputs.
- Tests proving:
  - default preflight requires wallet configuration,
  - completed public-wallet configuration can become preflight-ready without a private key,
  - private-key presence, live-enabled state, or kill-switch-off state blocks preflight.

## Still Locked

- Live trading remains disabled.
- Live kill switch should remain enabled.
- Private keys should remain absent during preflight preparation.
- `WALLET_PREP_READY` is not live approval.
- The first live pilot still requires transaction simulation, manual review, tiny trade caps, and a dedicated isolated wallet.

## Next

- Generate Wallet Preflight after creating the isolated MetaMask public address.
- Keep paper evidence collection separate from funding preparation.
- Add transaction simulation evidence before any live pilot can be considered.
