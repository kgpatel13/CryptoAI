# CryptoAI Provider Monitor

Generated: `2026-07-01T06:24:49Z`

## Summary

- Mode: `paper`
- Overall status: `OK`
- Providers: `5`
- Alerts: `1`
- Critical alerts: `0`

## Providers

| Chain | Type | Provider | Score | Current | Rolling | Required | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---|---|---:|---:|---|
| base | dex | Aerodrome | 100 | OK | OK | True | 0 | 123.86 |  |
| base | dex | Uniswap V2 | 100 | OK | OK | True | 0 | 124.81 |  |
| base | dex | Uniswap V3 | 99 | OK | OK | True | 0 | 121.35 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 100 | WATCH | OK | False | 0 | 43193.36 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 99 | OK | OK | True | 0 | 66.94 |  |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Provider observation is stale at 43193.36 seconds old. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
