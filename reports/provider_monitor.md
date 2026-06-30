# CryptoAI Provider Monitor

Generated: `2026-06-29T23:57:55Z`

## Summary

- Mode: `paper`
- Overall status: `WATCH`
- Providers: `5`
- Alerts: `2`
- Critical alerts: `0`

## Providers

| Chain | Type | Provider | Score | Current | Rolling | Required | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---|---|---:|---:|---|
| base | dex | Uniswap V2 | 100 | OK | OK | True | 0 | 10.07 |  |
| base | dex | Uniswap V3 | 100 | OK | OK | True | 0 | 7.49 |  |
| base | dex | Aerodrome | 87 | OK | OK | True | 0 | 9.07 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 99 | OK | OK | True | 0 | 0.21 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 0 | WATCH | CRITICAL | False | 4 | 76999.89 | BadFunctionCallOutput: Could not transact with/call contract function, is contract deployed correctl |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Optional backup provider is unhealthy; same-chain required provider coverage is available. |
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Provider observation is stale at 76999.89 seconds old. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
