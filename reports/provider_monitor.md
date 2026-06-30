# CryptoAI Provider Monitor

Generated: `2026-06-30T23:30:04Z`

## Summary

- Mode: `paper`
- Overall status: `OK`
- Providers: `5`
- Alerts: `1`
- Critical alerts: `0`

## Providers

| Chain | Type | Provider | Score | Current | Rolling | Required | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---|---|---:|---:|---|
| base | dex | Aerodrome | 100 | OK | OK | True | 0 | 125.21 |  |
| base | dex | Uniswap V2 | 100 | OK | OK | True | 0 | 126.24 |  |
| base | dex | Uniswap V3 | 99 | OK | OK | True | 0 | 123.5 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 100 | WATCH | OK | False | 0 | 18308.6 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 99 | OK | OK | True | 0 | 4.86 |  |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Provider observation is stale at 18308.6 seconds old. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
