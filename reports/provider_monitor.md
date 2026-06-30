# CryptoAI Provider Monitor

Generated: `2026-06-30T19:10:54Z`

## Summary

- Mode: `paper`
- Overall status: `WATCH`
- Providers: `5`
- Alerts: `4`
- Critical alerts: `0`

## Providers

| Chain | Type | Provider | Score | Current | Rolling | Required | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---|---|---:|---:|---|
| base | dex | Aerodrome | 100 | WATCH | OK | True | 0 | 1395.47 |  |
| base | dex | Uniswap V2 | 100 | WATCH | OK | True | 0 | 1396.34 |  |
| base | dex | Uniswap V3 | 99 | WATCH | OK | True | 0 | 1393.83 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 100 | WATCH | OK | False | 0 | 2758.78 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 99 | OK | OK | True | 0 | 31.13 |  |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| WATCH | base | dex | Aerodrome | Provider observation is stale at 1395.47 seconds old. |
| WATCH | base | dex | Uniswap V2 | Provider observation is stale at 1396.34 seconds old. |
| WATCH | base | dex | Uniswap V3 | Provider observation is stale at 1393.83 seconds old. |
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Provider observation is stale at 2758.78 seconds old. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
