# CryptoAI Provider Monitor

Generated: `2026-06-30T22:41:13Z`

## Summary

- Mode: `paper`
- Overall status: `WATCH`
- Providers: `5`
- Alerts: `1`
- Critical alerts: `0`

## Providers

| Chain | Type | Provider | Score | Current | Rolling | Required | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---|---|---:|---:|---|
| base | dex | Aerodrome | 100 | OK | OK | True | 0 | 64.73 |  |
| base | dex | Uniswap V2 | 100 | OK | OK | True | 0 | 65.88 |  |
| base | dex | Uniswap V3 | 99 | OK | OK | True | 0 | 62.23 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 100 | WATCH | OK | False | 0 | 15377.33 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 99 | OK | OK | True | 0 | 23.53 |  |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Provider observation is stale at 15377.33 seconds old. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
