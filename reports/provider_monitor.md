# CryptoAI Provider Monitor

Generated: `2026-06-29T23:16:16Z`

## Summary

- Mode: `paper`
- Overall status: `WATCH`
- Providers: `4`
- Alerts: `2`
- Critical alerts: `0`

## Providers

| Chain | Type | Provider | Score | Current | Rolling | Required | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---|---|---:|---:|---|
| base | dex | Uniswap V2 | 100 | OK | OK | True | 0 | 12.86 |  |
| base | dex | Aerodrome | 84 | OK | OK | True | 0 | 11.74 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 98 | OK | OK | True | 0 | 0.25 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 0 | WATCH | CRITICAL | False | 4 | 74501.16 | BadFunctionCallOutput: Could not transact with/call contract function, is contract deployed correctl |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Optional backup provider is unhealthy; same-chain required provider coverage is available. |
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Provider observation is stale at 74501.16 seconds old. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
