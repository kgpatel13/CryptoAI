# CryptoAI Provider Monitor

Generated: `2026-07-01T19:24:23Z`

## Summary

- Mode: `paper`
- Overall status: `OK`
- Providers: `5`
- Alerts: `1`
- Critical alerts: `0`

## Providers

| Chain | Type | Provider | Score | Current | Rolling | Required | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---|---|---:|---:|---|
| base | dex | Aerodrome | 100 | OK | OK | True | 0 | 62.8 |  |
| base | dex | Uniswap V2 | 100 | OK | OK | True | 0 | 63.67 |  |
| base | dex | Uniswap V3 | 100 | OK | OK | True | 0 | 60.4 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 100 | WATCH | OK | False | 0 | 89968.04 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 97 | OK | OK | True | 0 | 15.69 |  |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Provider observation is stale at 89968.04 seconds old. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
