# CryptoAI Provider Monitor

Generated: `2026-06-29T13:25:38Z`

## Summary

- Mode: `paper`
- Overall status: `WATCH`
- Providers: `4`
- Alerts: `3`
- Critical alerts: `0`

## Providers

| Chain | Type | Provider | Score | Current | Rolling | Required | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---|---|---:|---:|---|
| base | dex | Uniswap V2 | 100 | OK | OK | True | 0 | 41.57 |  |
| base | dex | Aerodrome | 60 | WATCH | DEGRADED | True | 0 | 40.54 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 95 | OK | OK | True | 0 | 6.67 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 0 | WATCH | CRITICAL | False | 4 | 39063.22 | BadFunctionCallOutput: Could not transact with/call contract function, is contract deployed correctl |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| WATCH | base | dex | Aerodrome | Provider has fresh successful observations but rolling score 60 is still recovering. |
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Optional backup provider is unhealthy; same-chain required provider coverage is available. |
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Provider observation is stale at 39063.22 seconds old. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
