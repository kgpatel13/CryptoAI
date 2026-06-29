# CryptoAI v5.8 - Verified Base Uniswap V3 Quote Provider

## Summary

v5.8 adds the third Base ETH quote venue: Uniswap V3 through the official Base QuoterV2 deployment.

The purpose is better market coverage and cleaner evidence, not live trading. Production cost buffer, paper BUY threshold, and live execution remain unchanged.

## Added

- Base Uniswap V3 quote provider using QuoterV2.
- Official Base deployment constants:
  - Factory: `0x33128a8fC17869897dcE68Ed026d694621f6FDfD`
  - SwapRouter02: `0x2626664c2603336E57B271c5C0b26F421741e481`
  - QuoterV2: `0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a`
- Fee-tier probing for `500`, `3000`, and `10000`.
- QuoteService and QuoteManager registration for Uniswap V3.
- Quote Coverage Evidence and ETH Market Coverage integration.
- Paper Settings allow-list for Uniswap V3.
- Regression tests for address constants, registry wiring, provider support, and settings coverage.

## Safety

- Live trading remains disabled.
- Production buffer remains `0.30%`.
- Paper BUY threshold remains `0.30%`.
- The `0.20%` buffer remains research-only.
- Uniswap V3 quote errors are isolated and scored like other provider errors.

## Run

```bash
python -m app.diagnostics.quote_diagnostics
python -m app.research.quote_coverage_evidence_service
python -m app.research.eth_route_architecture_service
python -m app.research.eth_market_coverage_service
python -m app.operations.paper_settings_service
python -m app.reporting.report_audit
```

## Rollback

Remove the Uniswap V3 provider registration and restore Base DEX metadata to the prior two-provider profile. Existing reports can be regenerated safely because they are derived evidence.

